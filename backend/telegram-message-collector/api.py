#!/usr/bin/env python3
"""
Merged API Server for Telegram Messages & Checkpoint Locations
Includes search, filtering, geo-based queries, and MongoDB Atlas connection
"""

import os
from datetime import datetime

from dotenv import load_dotenv
from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_pymongo import PyMongo

from appsecrets import MONGO_CONNECTION_STRING
from geo_utils import haversine

# Loads values from .env file
load_dotenv()
app = Flask(__name__)

CORS(app)

# MongoDB Atlas Connection
app.config["MONGO_URI"] = MONGO_CONNECTION_STRING
mongo = PyMongo(app)


# Reading variables from the environment
COLLECTION_DATA = os.getenv("MONGO_COLLECTION_DATA")
COLLECTION_LOCATIONS = os.getenv("MONGO_COLLECTION_LOCATIONS")
HOST = os.getenv("FLASK_HOST")
PORT = int(os.getenv("FLASK_PORT"))
DEBUG = os.getenv("FLASK_DEBUG").lower() == "true"


# Collections
data_collection = mongo.db[COLLECTION_DATA]
location_collection = mongo.db[COLLECTION_LOCATIONS]

RADIUS_KM = float(os.getenv("RADIUS_IN_KM"))

# Verify that the values exist
if not COLLECTION_DATA or not COLLECTION_LOCATIONS or not HOST or not PORT:
    raise ValueError(
        "❌ COLLECTION_DATA or COLLECTION_LOCATIONS or RADIUS_IN_KM or HOST or PORT is missing in .env file"
    )


# ---------------- Helper Functions ----------------
def prepare_doc(doc):
    """Convert ObjectId and datetime to serializable formats + attach lat/lng"""
    doc["_id"] = str(doc["_id"])
    if isinstance(doc.get("message_date"), datetime):
        doc["message_date"] = doc["message_date"].isoformat()
    city = doc.get("city_name")
    checkpoint = doc.get("checkpoint_name")
    if city and checkpoint:
        location = location_collection.find_one({"city": city, "checkpoint": checkpoint})
        if location:
            doc["lat"] = location.get("lat")
            doc["lng"] = location.get("lng")
    return doc


# ---------------- Root & Health ----------------
@app.route("/")
def home():
    return jsonify(
        {
            "message": "🤝 Unified Team API - Ready for Integration!",
            "port": 5000,
            "collections": ["data", "CheckpointLocation"],
            "team_features": {
                "data_team": "MongoDB data collection & search",
                "position_team": "Geospatial & location services",
            },
            "endpoints": {
                "position_location": [
                    "/api/near_location",
                    "/api/closest-checkpoint",
                    "/api/checkpoints/merged",
                ],
            },
        }
    )


# ---------------- User on the frontend (Map.js) page ----------------
@app.route("/api/checkpoints/merged", methods=["GET"])
def get_merged_checkpoints():
    locations = location_collection.find()
    merged_data = []
    for loc in locations:
        latest_status = data_collection.find_one(
            {"checkpoint_name": loc.get("checkpoint")},
            sort=[("message_date", -1)],
        )
        merged_checkpoint = {
            "checkpoint_id": str(loc.get("_id")),
            "checkpoint_name": loc.get("checkpoint"),
            "city": loc.get("city"),
            "lat": loc.get("lat"),
            "lng": loc.get("lng"),
            "status": latest_status.get("status") if latest_status else "N/A",
            "direction": (latest_status.get("direction") if latest_status else "N/A"),
            "message_date": (latest_status.get("message_date") if latest_status else "N/A"),
        }
        merged_data.append(merged_checkpoint)
    return jsonify(merged_data)


# ---------------- User on the frontend (PushNotificationSetup.js) page ----------------
@app.route("/api/near_location", methods=["GET"])
def get_nearby_checkpoints():
    try:
        user_lat = request.args.get("latitude", type=float)
        user_lng = request.args.get("longitude", type=float)

        if user_lat is None or user_lng is None:
            return jsonify({"error": "Missing latitude or longitude"}), 400

        radius_km = RADIUS_KM  # read from .env

        checkpoints = list(location_collection.find({"lat": {"$exists": True}, "lng": {"$exists": True}}))

        nearby = []
        for cp in checkpoints:
            cp_lat = cp.get("lat")
            cp_lng = cp.get("lng")
            if cp_lat is None or cp_lng is None:
                continue

            dist = haversine(user_lat, user_lng, cp_lat, cp_lng)
            if dist > radius_km:
                continue

            status_doc = data_collection.find_one(
                {"checkpoint_name": cp.get("checkpoint"), "city_name": cp.get("city")}, sort=[("message_date", -1)]
            )

            merged = {
                "checkpoint": cp.get("checkpoint"),
                "city": cp.get("city"),
                "latitude": cp_lat,
                "longitude": cp_lng,
                "distance_km": round(dist, 2),
            }

            if status_doc:
                merged["status"] = status_doc.get("status")
                merged["direction"] = status_doc.get("direction")
                merged["updatedAt"] = status_doc.get("message_date")

            nearby.append(merged)

        return jsonify({"success": True, "count": len(nearby), "checkpoints": nearby})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ---------------- User on the frontend (FeedbackNotification .js) page ----------------
@app.route("/api/closest-checkpoint", methods=["GET"])
def get_closest_checkpoint():
    try:
        lat = request.args.get("lat", type=float)
        lng = request.args.get("lng", type=float)
        if lat is None or lng is None:
            return jsonify({"error": "Missing lat or lng parameters"}), 400

        checkpoints = list(location_collection.find({"lat": {"$exists": True}, "lng": {"$exists": True}}))
        min_dist = None
        closest_cp = None

        for cp in checkpoints:
            cp_lat = cp.get("lat")
            cp_lng = cp.get("lng")
            dist = haversine(lat, lng, cp_lat, cp_lng)
            if min_dist is None or dist < min_dist:
                min_dist = dist
                closest_cp = cp

        if not closest_cp:
            return jsonify({"error": "No checkpoints found"}), 404

        # Get latest status for this checkpoint
        status_doc = data_collection.find_one(
            {
                "checkpoint_name": closest_cp.get("checkpoint"),
                "city_name": closest_cp.get("city"),
            },
            sort=[("message_date", -1)],
        )

        result = {
            "success": True,
            "checkpoint": closest_cp.get("checkpoint"),
            "city": closest_cp.get("city"),
            "latitude": closest_cp.get("lat"),
            "longitude": closest_cp.get("lng"),
            "distance_km": round(min_dist, 2),
            "team_info": "🗺️ Position Team: Closest checkpoint to specified coordinates",
        }

        if status_doc:
            result["status"] = status_doc.get("status")
            result["last_update"] = status_doc.get("message_date")

        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ---------------- Server Function ----------------
def start_api_server(port=None, host=None):
    """Start the API server using environment variables as defaults"""
    # Use environment variables if no parameters provided
    if port is None:
        port = PORT
    if host is None:
        host = HOST
    print("🚀 Starting Unified API Server...")
    print(f"🌐 API will run on: http://{host}:{port}")
    print("\n📋 All Endpoints Available:")
    print("  📊 Data Collection & Search")
    print("  📍 Location & Position Services")
    print("  🔍 Checkpoint Monitoring")
    print("  🗺️ Geospatial Queries")
    print("\n🤝 Team Integration Ready!")
    app.run(host=host, port=port, debug=False, use_reloader=False)


if __name__ == "__main__":
    start_api_server()
