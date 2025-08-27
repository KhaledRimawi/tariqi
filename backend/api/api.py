import os
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv
import random
from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_pymongo import PyMongo
from geo_utils import haversine
from keyvault_client import get_secret
from openai_client import get_gpt_response

load_dotenv()

app = Flask(__name__)
CORS(app)

# MongoDB Atlas Connection
app.config["MONGO_URI"] = get_secret(os.getenv("MONGO_CONNECTION_STRING_KEY"))
mongo = PyMongo(app)

# Reading variables from the environment
COLLECTION_DATA = os.getenv("MONGO_COLLECTION_DATA")
COLLECTION_LOCATIONS = os.getenv("MONGO_COLLECTION_LOCATIONS")


# Collections
data_collection = mongo.db[COLLECTION_DATA]
location_collection = mongo.db[COLLECTION_LOCATIONS]

RADIUS_KM = float(os.getenv("RADIUS_IN_KM"))

# Verify that the values exist
if not COLLECTION_DATA or not COLLECTION_LOCATIONS:
    raise ValueError(
        "❌ COLLECTION_DATA or COLLECTION_LOCATIONS or RADIUS_IN_KM or HOST or " "PORT is missing in .env file"
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
                    "/api/checkpoints/query",
                ],
                "ai_chat": ["/api/ask-ai"],
            },
        }
    )


# ---------------- AI Chat Endpoint ----------------
@app.route("/api/ask-ai", methods=["POST"])
def ask_ai():
    """
    Endpoint to send a user prompt to Azure OpenAI and return the GPT response.
    Request format:
        { "prompt": "Your question here" }
    """
    try:
        data = request.get_json()
        user_prompt = data.get("prompt")

        if not user_prompt:
            return jsonify({"error": "No prompt provided"}), 400

        # Call the function from client.py
        answer = get_gpt_response(user_prompt)

        return jsonify({"success": True, "prompt": user_prompt, "response": answer})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


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
            "status": (latest_status.get("status") if latest_status else "N/A"),
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
                {"checkpoint_name": cp.get("checkpoint"), "city_name": cp.get("city")},
                sort=[("message_date", -1)],
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
            "team_info": ("🗺️ Position Team: Closest checkpoint to specified coordinates"),
        }

        if status_doc:
            result["status"] = status_doc.get("status")
            result["last_update"] = status_doc.get("message_date")

        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ---------------- User on the frontend (Map.js) & (Dwstination Search) pages ----------------
@app.route("/api/checkpoints/query", methods=["GET"])
def search_road_conditions():
    """
    API to query road conditions with multiple optional filters.
    Filters are applied in the order: ago -> others -> top.
    """
    try:
        checkpoint_name = request.args.get("checkpoint", "")
        city_name = request.args.get("city", "")
        status = request.args.get("status", "")
        direction = request.args.get("direction", "")
        ago_filter = request.args.get("ago", "")
        top_filter = request.args.get("top", "")

        # Build the MongoDB query filter
        mongo_filter = {}

        # ago filter first if it exists
        if ago_filter:
            try:
                ago_value = int(ago_filter)
                if ago_value < 0:
                    return jsonify({"error": "Ago value must be a positive integer."}), 400

                cutoff_time = datetime.utcnow() - timedelta(minutes=ago_value)

                mongo_filter["message_date"] = {"$gte": cutoff_time}
            except ValueError:
                return jsonify({"error": ("Invalid value for 'ago'. Please use a positive integer.")}), 400

        #  Apply all other filters
        if checkpoint_name:
            mongo_filter["checkpoint_name"] = {"$regex": checkpoint_name.strip('"'), "$options": "i"}
        if city_name:
            mongo_filter["city_name"] = {"$regex": city_name.strip('"'), "$options": "i"}
        if status:
            mongo_filter["status"] = {"$regex": status.strip('"'), "$options": "i"}
        if direction:
            mongo_filter["direction"] = {"$regex": direction.strip('"'), "$options": "i"}

        sort_order = [("message_date", -1)]

        #  Apply the 'top' filter as a limit after all other filters are applied
        limit = 0
        if top_filter:
            try:
                limit = int(top_filter)
                if limit < 1:
                    return jsonify({"error": ("Top value must be a positive integer greater than 0.")}), 400
            except ValueError:
                return jsonify({"error": ("Invalid value for 'top'. Please use a positive integer.")}), 400

        messages = list(data_collection.find(mongo_filter).sort(sort_order).limit(limit))

        for msg in messages:
            msg["_id"] = str(msg["_id"])
            if isinstance(msg.get("message_date"), datetime):
                msg["message_date"] = msg["message_date"].isoformat()

        return jsonify({"results": messages, "count": len(messages)})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    # ---------------- User Feedback ----------------


@app.route("/api/feedback", methods=["POST"])
def submit_feedback():
    try:
        data = request.get_json()

        print("Received feedback:", data, flush=True)
        print("Latitude:", data.get("latitude"), "Longitude:", data.get("longitude"), flush=True)

        if not data or "message" not in data or "latitude" not in data or "longitude" not in data:
            return jsonify({"error": ("Missing 'message', 'latitude' or 'longitude' field")}), 400

        user_lat = data["latitude"]
        user_lng = data["longitude"]
        message = data["message"]
        status = data["status"]
        direction = data["direction"]

        # ---------------- Find closest checkpoint ----------------
        checkpoints = list(location_collection.find({"lat": {"$exists": True}, "lng": {"$exists": True}}))
        closest_cp, min_dist = None, None

        for cp in checkpoints:
            cp_lat = cp.get("lat")
            cp_lng = cp.get("lng")
            dist = haversine(user_lat, user_lng, cp_lat, cp_lng)
            if min_dist is None or dist < min_dist:
                min_dist = dist
                closest_cp = cp

        print("Closest checkpoint found:", closest_cp, flush=True)

        if not closest_cp:
            return jsonify({"error": "No checkpoint found"}), 404

        # ---------------- Build feedback document ----------------
        feedback_doc = {
            "message_id": random.randint(1_000_000, 9_999_999),
            "source_channel": "user_feedback",
            "original_message": message,
            "checkpoint_name": closest_cp.get("checkpoint"),
            "city_name": closest_cp.get("city"),
            "status": status,
            "direction": direction,
            "message_date": datetime.now(timezone.utc),
        }

        print("Feedback document to insert:", feedback_doc, flush=True)

        inserted_id = data_collection.insert_one(feedback_doc).inserted_id
        print("✅ Inserted Feedback into collection:", data_collection.name, "with _id:", inserted_id, flush=True)

        return (
            jsonify(
                {
                    "success": True,
                    "id": str(inserted_id),
                    "checkpoint": closest_cp.get("checkpoint"),
                    "city": closest_cp.get("city"),
                    "status": status,
                    "direction": direction,
                }
            ),
            201,
        )

    except Exception as e:
        print("❌ Error inserting feedback:", str(e), flush=True)
        return jsonify({"error": str(e)}), 500


# ---------------- Server Function ----------------
def start_api_server():
    print("\n🤝 Team Integration Ready!")
    port = int(os.getenv("PORT", 5000))
    # Always bind to 0.0.0.0 so it works both locally and in Azure
    app.run(host="0.0.0.0", port=port, debug=False, use_reloader=False)


if __name__ == "__main__":
    start_api_server()
