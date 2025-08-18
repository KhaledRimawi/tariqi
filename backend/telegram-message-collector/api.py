#!/usr/bin/env python3
"""
Merged API Server for Telegram Messages & Checkpoint Locations
Includes search, filtering, geo-based queries, and MongoDB Atlas connection
"""

import os
from dotenv import load_dotenv
from flask import Flask, request, jsonify
from flask_pymongo import PyMongo
from datetime import datetime
from flask_cors import CORS
from geo_utils import haversine
from urllib.parse import unquote
from appsecrets import MONGO_CONNECTION_STRING

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
if not COLLECTION_DATA or not COLLECTION_LOCATIONS or not HOST or not PORT :
    raise ValueError("❌ COLLECTION_DATA or COLLECTION_LOCATIONS or RADIUS_IN_KM or HOST or PORT is missing in .env file")

# ---------------- Helper Functions ----------------
def prepare_doc(doc):
    """Convert ObjectId and datetime to serializable formats + attach lat/lng"""
    doc['_id'] = str(doc['_id'])
    if isinstance(doc.get('message_date'), datetime):
        doc['message_date'] = doc['message_date'].isoformat()
    city = doc.get('city_name')
    checkpoint = doc.get('checkpoint_name')
    if city and checkpoint:
        location = location_collection.find_one({"city": city, "checkpoint": checkpoint})
        if location:
            doc['lat'] = location.get('lat')
            doc['lng'] = location.get('lng')
    return doc

# ---------------- Root & Health ----------------
@app.route('/')
def home():
    return jsonify({
        "message": "🤝 Unified Team API - Ready for Integration!",
        "port": 5000,
        "collections": ["data", "CheckpointLocation"],
        "team_features": {
            "data_team": "MongoDB data collection & search",
            "position_team": "Geospatial & location services"
        },
        "endpoints": {
            "data_collection": [
                "/api/telegram-messages",
                "/api/data",
                "/api/data/show",
                "/api/data/city/<city>",
                "/api/data/checkpoint/<checkpoint>",
                "/api/data/status/<status>",
                "/api/data/search"
            ],
            "search_filtering": [
                "/api/search/city/<city_name>",
                "/api/search/checkpoint/<checkpoint_name>",
                "/api/search/status/<status>",
                "/api/checkpoints/conditions",
                "/api/checkpoints/filter"
            ],
            "position_location": [
                "/api/locations",
                "/api/near_location",
                "/api/closest-checkpoint",
                "/api/checkpoints/merged"
            ],
            "health": [
                "/api/health",
                "/api/latest"
            ]
        }
    })

@app.route('/api/health')
def health():
    try:
        count_data = data_collection.count_documents({})
        count_loc = location_collection.count_documents({})
        return jsonify({
            "status": "healthy",
            "mongodb": "connected",
            "total_data_documents": count_data,
            "total_location_documents": count_loc
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ---------------- Telegram Messages ----------------
@app.route('/api/telegram-messages')
def get_messages():
    try:
        messages = list(data_collection.find().sort('_id', -1))
        messages = [prepare_doc(m) for m in messages]
        return jsonify({"success": True, "count": len(messages), "messages": messages})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/latest')
def get_latest():
    try:
        messages = list(data_collection.find({
            "checkpoint_name": {"$nin": [None, "غير محدد"]}
        }).sort('_id', -1).limit(5))
        messages = [prepare_doc(m) for m in messages]
        return jsonify({"success": True, "count": len(messages), "latest_checkpoints": messages})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ---------------- Search Endpoints ----------------
@app.route('/api/search/city/<city_name>')
def search_by_city(city_name):
    try:
        city_name = unquote(city_name)
        messages = list(data_collection.find({"city_name": {"$regex": city_name, "$options": "i"}}).sort('_id', -1).limit(50))
        messages = [prepare_doc(m) for m in messages]
        return jsonify({"success": True, "search_type": "city", "search_term": city_name, "count": len(messages), "messages": messages})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/search/checkpoint/<checkpoint_name>')
def search_by_checkpoint(checkpoint_name):
    try:
        checkpoint_name = unquote(checkpoint_name)
        messages = list(data_collection.find({"checkpoint_name": {"$regex": checkpoint_name, "$options": "i"}}).sort('_id', -1).limit(50))
        messages = [prepare_doc(m) for m in messages]
        return jsonify({"success": True, "search_type": "checkpoint", "search_term": checkpoint_name, "count": len(messages), "messages": messages})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/search/status/<status>')
def search_by_status(status):
    try:
        status = unquote(status)
        messages = list(data_collection.find({"status": {"$regex": status, "$options": "i"}}).sort('_id', -1).limit(50))
        messages = [prepare_doc(m) for m in messages]
        return jsonify({"success": True, "search_type": "status", "search_term": status, "count": len(messages), "messages": messages})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ---------------- Checkpoint Conditions ----------------
@app.route('/api/checkpoints/conditions')
def get_checkpoint_conditions():
    try:
        city = request.args.get('city')
        status = request.args.get('status')
        direction = request.args.get('direction')
        checkpoint = request.args.get('checkpoint')

        match_stage = {
            "checkpoint_name": {"$nin": [None, "غير محدد"]},
            "status": {"$nin": [None, ""]}
        }
        if city:
            match_stage["city_name"] = {"$regex": city, "$options": "i"}
        if status:
            match_stage["status"] = {"$regex": status, "$options": "i"}
        if direction:
            match_stage["direction"] = {"$regex": direction, "$options": "i"}
        if checkpoint:
            match_stage["checkpoint_name"] = {"$regex": checkpoint, "$options": "i"}

        pipeline = [
            {"$match": match_stage},
            {"$sort": {"_id": -1}},
            {
                "$group": {
                    "_id": "$checkpoint_name",
                    "latest_status": {"$first": "$status"},
                    "latest_message": {"$first": "$original_message"},
                    "city": {"$first": "$city_name"},
                    "last_update": {"$first": "$message_date"},
                    "direction": {"$first": "$direction"}
                }
            },
            {"$sort": {"_id": 1}}
        ]
        conditions = list(data_collection.aggregate(pipeline))
        return jsonify({"success": True, "count": len(conditions), "checkpoints": conditions})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/checkpoints/filter')
def filter_checkpoints():
    try:
        city = request.args.get('city')
        status = request.args.get('status')
        checkpoint = request.args.get('checkpoint')
        limit = int(request.args.get('limit', 20))

        query = {"checkpoint_name": {"$nin": [None, "غير محدد"]}}
        if city:
            query["city_name"] = {"$regex": city, "$options": "i"}
        if status:
            query["status"] = {"$regex": status, "$options": "i"}
        if checkpoint:
            query["checkpoint_name"] = {"$regex": checkpoint, "$options": "i"}

        messages = list(data_collection.find(query).sort('_id', -1).limit(limit))
        messages = [prepare_doc(m) for m in messages]
        return jsonify({"success": True, "count": len(messages), "messages": messages})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ---------------- Merged Checkpoints with Location ----------------
@app.route('/api/checkpoints/merged', methods=['GET'])
def get_merged_checkpoints():
    locations = location_collection.find()
    merged_data = []
    for loc in locations:
        latest_status = data_collection.find_one({"checkpoint_name": loc.get("checkpoint")}, sort=[("message_date", -1)])
        merged_checkpoint = {
            "checkpoint_id": str(loc.get("_id")),
            "checkpoint_name": loc.get("checkpoint"),
            "city": loc.get("city"),
            "lat": loc.get("lat"),
            "lng": loc.get("lng"),
            "status": latest_status.get("status") if latest_status else "N/A",
            "direction": latest_status.get("direction") if latest_status else "N/A",
            "message_date": latest_status.get("message_date") if latest_status else "N/A",
        }
        merged_data.append(merged_checkpoint)
    return jsonify(merged_data)

# ---------------- Data Insert & Search ----------------
@app.route('/api/data', methods=['POST'])
def add_checkpoints():
    data = request.get_json()
    if not isinstance(data, list):
        return jsonify({"error": "Expected an array of objects"}), 400
    for item in data:
        required_keys = ['message_id', 'source_channel', 'original_message', 'checkpoint_name', 'city_name', 'status', 'direction', 'message_date']
        if not all(key in item for key in required_keys):
            return jsonify({"error": f"Missing required fields"}), 400
    result = data_collection.insert_many(data)
    return jsonify({"message": "✅ Data inserted successfully", "insertedCount": len(result.inserted_ids)}), 201
# GET all data
@app.route('/api/data/show', methods=['GET'])
def get_all_data():
    results = data_collection.find().sort("message_date", -1)
    return jsonify([prepare_doc(doc) for doc in results])
# GET by city
@app.route('/api/data/city/<city>', methods=['GET'])
def get_by_city(city):
    results = data_collection.find({"city_name": {'$regex': city, '$options': 'i'}}).sort("message_date", -1)
    return jsonify([prepare_doc(doc) for doc in results])

# GET by checkpoint
@app.route('/api/data/checkpoint/<checkpoint>', methods=['GET'])
def get_by_checkpoint_data(checkpoint):
    results = data_collection.find({"checkpoint_name": {'$regex': checkpoint, '$options': 'i'}}).sort("message_date", -1)
    return jsonify([prepare_doc(doc) for doc in results])

# GET by status
@app.route('/api/data/status/<status>', methods=['GET'])
def get_by_status_data(status):
    results = data_collection.find({"status": {'$regex': status, '$options': 'i'}}).sort("message_date", -1)
    return jsonify([prepare_doc(doc) for doc in results])


# GET with search params (city + status)
@app.route('/api/data/search', methods=['GET'])
def search_data():
    city = request.args.get('city')
    status = request.args.get('status')
    query = {}
    if city:
        query['city_name'] = {'$regex': city, '$options': 'i'}
    if status:
        query['status'] = {'$regex': status, '$options': 'i'}
    results = data_collection.find(query).sort("message_date", -1)
    return jsonify([prepare_doc(doc) for doc in results])

# ---------------- Location Insert & Nearby ----------------

# GET all locations
@app.route('/api/locations', methods=['GET'])
def get_locations():
    try:
        locations = list(location_collection.find({}, {'_id': 0}))
        return jsonify({
            "success": True, 
            "count": len(locations), 
            "locations": locations,
            "team_info": "🗺️ Position Team: Use this endpoint to get all checkpoint locations"
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# POST to add new locations
@app.route('/api/locations/add', methods=['POST'])
def add_locations():
    data = request.get_json()
    if not isinstance(data, list):
        return jsonify({"error": "Expected an array of objects"}), 400
    required_keys = ['city', 'checkpoint', 'lat', 'lng']
    for item in data:
        if not all(key in item for key in required_keys):
            return jsonify({"error": f"Missing required fields"}), 400
    result = location_collection.insert_many(data)
    return jsonify({"message": "✅ Location data inserted successfully", "insertedCount": len(result.inserted_ids)}), 201

@app.route('/api/near_location', methods=['GET'])
def get_nearby_checkpoints():
    try:
        user_lat = request.args.get('lat', type=float)
        user_lng = request.args.get('lng', type=float)
        radius = request.args.get('radius', default=10, type=float)
        
        if user_lat is None or user_lng is None:
            return jsonify({"error": "Missing lat/lng parameters"}), 400
            
        checkpoints = list(location_collection.find({"lat": {"$exists": True}, "lng": {"$exists": True}}))
        nearby = []
        for cp in checkpoints:
            cp_lat = cp.get("lat")
            cp_lng = cp.get("lng")
            dist = haversine(user_lat, user_lng, cp_lat, cp_lng)
            if dist <= radius:
                status_doc = data_collection.find_one({"checkpoint_name": cp.get("checkpoint"), "city_name": cp.get("city")}, sort=[("message_date", -1)])
                merged = {
                    "checkpoint": cp.get("checkpoint"),
                    "city": cp.get("city"),
                    "latitude": cp_lat,
                    "longitude": cp_lng,
                    "distance_km": round(dist, 2)
                }
                if status_doc:
                    merged["status"] = status_doc.get("status")
                    merged["direction"] = status_doc.get("direction")
                    merged["updatedAt"] = status_doc.get("message_date")
                nearby.append(merged)
        return jsonify({
            "success": True,
            "count": len(nearby),
            "checkpoints": nearby,
            "team_info": "🗺️ Position Team: Nearby checkpoints within specified radius"
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/closest-checkpoint', methods=['GET'])
def get_closest_checkpoint():
    try:
        lat = request.args.get('lat', type=float)
        lng = request.args.get('lng', type=float)
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
            {"checkpoint_name": closest_cp.get("checkpoint"), "city_name": closest_cp.get("city")}, 
            sort=[("message_date", -1)]
        )
        
        result = {
            "success": True,
            "checkpoint": closest_cp.get("checkpoint"),
            "city": closest_cp.get("city"),
            "latitude": closest_cp.get("lat"),
            "longitude": closest_cp.get("lng"),
            "distance_km": round(min_dist, 2),
            "team_info": "🗺️ Position Team: Closest checkpoint to specified coordinates"
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
