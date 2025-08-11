from flask import Flask, request, jsonify
from flask_pymongo import PyMongo
from bson import ObjectId
from datetime import datetime, timedelta
from flask_cors import CORS
from geo_utils import haversine  # ⬅️ Import the utility


app = Flask(__name__)
CORS(app)

# MongoDB Atlas URI
app.config["MONGO_URI"] = "mongodb+srv://AiTeamC:AI%23TeamC123@cluster0.904co68.mongodb.net/TeamC?retryWrites=true&w=majority"
mongo = PyMongo(app)

# Use separate collection objects for each collection
data_collection = mongo.db.data
location_collection = mongo.db.CheckpointLocation

RADIUS_KM = 5
# --------------------- ROUTES For Data---------------------
# Helper function to prepare a document for JSON serialization

# GET a merged list of all checkpoints with their latest status
@app.route('/api/checkpoints/merged', methods=['GET'])
def get_merged_checkpoints():
    locations = location_collection.find()
    merged_data = []

    for loc in locations:
        latest_status = data_collection.find_one(
            {"checkpoint_name": loc.get("checkpoint")},
            sort=[("message_date", -1)]
        )
        
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

# POST: Add multiple checkpoint documents to the 'data' collection
@app.route('/api/data', methods=['POST'])
def add_checkpoints():
    data = request.get_json()
    if not isinstance(data, list):
        return jsonify({"error": "Expected an array of objects"}), 400
    for item in data:
        required_keys = ['message_id', 'source_channel', 'original_message', 'checkpoint_name', 'city_name', 'status', 'direction', 'message_date']
        if not all(key in item for key in required_keys):
            return jsonify({"error": f"Missing one or more required fields: {required_keys}"}), 400
    result = data_collection.insert_many(data)
    return jsonify({
        "message": "✅ Data inserted successfully",
        "insertedCount": len(result.inserted_ids),
        "insertedIds": [str(_id) for _id in result.inserted_ids]
    }), 201

# GET all data
@app.route('/api/data/show', methods=['GET'])
def get_all_data():
    results = data_collection.find().sort("message_date", -1)
    data = [prepare_doc(doc) for doc in results]
    return jsonify(data)

# GET by city
@app.route('/api/data/city/<city>', methods=['GET'])
def get_by_city(city):
    results = data_collection.find({"city_name": {'$regex': city, '$options': 'i'}}).sort("message_date", -1)
    data = [prepare_doc(doc) for doc in results]
    return jsonify(data)

# GET by checkpoint
@app.route('/api/data/checkpoint/<checkpoint>', methods=['GET'])
def get_by_checkpoint(checkpoint):
    results = data_collection.find({"checkpoint_name": {'$regex': checkpoint, '$options': 'i'}}).sort("message_date", -1)
    data = [prepare_doc(doc) for doc in results]
    return jsonify(data)

# GET by status
@app.route('/api/data/status/<status>', methods=['GET'])
def get_by_status(status):
    results = data_collection.find({"status": {'$regex': status, '$options': 'i'}}).sort("message_date", -1)
    data = [prepare_doc(doc) for doc in results]
    return jsonify(data)

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
    data = [prepare_doc(doc) for doc in results]
    return jsonify(data)

### to get nearby checkpoints depending 

@app.route('/api/near_location', methods=['GET', 'POST'])
def get_nearby_checkpoints():
    data = request.get_json()
    user_lat = data.get("latitude")
    user_lng = data.get("longitude")

    radius_km = RADIUS_KM

    if user_lat is None or user_lng is None:
        return jsonify({"error": "Missing lat/lng"}), 400

    checkpoints = list(location_collection.find({
        "lat": {"$exists": True},
        "lng": {"$exists": True}
    }))
    nearby = []

    print(f"📍User location: ({user_lat}, {user_lng})")
    

    for cp in checkpoints:
        cp_lat = cp.get("lat")
        cp_lng = cp.get("lng")
        if cp_lat is None or cp_lng is None:
            continue

        dist = haversine(user_lat, user_lng, cp_lat, cp_lng)
        if dist > radius_km:
            continue  # Skip if too far

        #  Only proceed if within radius
        status_doc = data_collection.find_one({
            "checkpoint_name": cp.get("checkpoint"),
            "city_name": cp.get("city")
        }, sort=[("message_date", -1)])

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
        print(f"📦 Found nearby: {nearby}")


    return jsonify(nearby)


# Helper to convert ObjectId to str
def prepare_doc(doc):
    doc['_id'] = str(doc['_id'])

    # Convert datetime
    if isinstance(doc.get('message_date'), datetime):
        doc['message_date'] = doc['message_date'].isoformat()

    # Try to find matching location
    city = doc.get('city_name')
    checkpoint = doc.get('checkpoint_name')
    if city and checkpoint:
        location = location_collection.find_one({
            "city": city,
            "checkpoint": checkpoint
        })

        if location:
            doc['lat'] = location.get('lat')
            doc['lng'] = location.get('lng')

    return doc


# --------------------- ROUTES For Checkpoint Location ---------------------

# POST: Add multiple checkpoint location documents
@app.route('/api/locations', methods=['POST'])
def add_locations():
    data = request.get_json()

    if not isinstance(data, list):
        return jsonify({"error": "Expected an array of objects"}), 400

    required_keys = ['city', 'checkpoint', 'lat', 'lng']
    for item in data:
        if not all(key in item for key in required_keys):
            return jsonify({"error": f"Missing one or more required fields: {required_keys}"}), 400

    result = location_collection.insert_many(data)

    return jsonify({
        "message": "✅ Location data inserted successfully",
        "insertedCount": len(result.inserted_ids),
        "insertedIds": [str(_id) for _id in result.inserted_ids]
    }), 201

@app.route('/api/closest-checkpoint', methods=['GET'])
def get_closest_checkpoint():
    lat = request.args.get('lat', type=float)
    lon = request.args.get('lon', type=float)

    if lat is None or lon is None:
        return jsonify({"error": "Missing lat or lon"}), 400

    checkpoints = list(location_collection.find({
        "lat": {"$exists": True},
        "lng": {"$exists": True}
    }))

    min_dist = None
    closest_cp = None

    for cp in checkpoints:
        cp_lat = cp.get("lat")
        cp_lng = cp.get("lng")
        dist = haversine(lat, lon, cp_lat, cp_lng) * 1000  # in meters

        if min_dist is None or dist < min_dist:
            min_dist = dist
            closest_cp = cp

    if closest_cp is None:
        return jsonify({"error": "No checkpoints found"}), 404

    return jsonify({
        "checkpoint": closest_cp.get("checkpoint"),
        "city": closest_cp.get("city"),
        "lat": closest_cp.get("lat"),
        "lon": closest_cp.get("lng"),
        "distance_m": round(min_dist, 2)
    })


# --------------------- SERVER ---------------------
if __name__ == '__main__':
    app.run(debug=True)