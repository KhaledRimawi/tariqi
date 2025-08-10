from flask import Flask, request, jsonify
from flask_pymongo import PyMongo
from bson import ObjectId
from datetime import datetime, timedelta
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# MongoDB Atlas URI
app.config["MONGO_URI"] = "mongodb+srv://AiTeamC:AI%23TeamC123@cluster0.904co68.mongodb.net/TeamC?retryWrites=true&w=majority"
mongo = PyMongo(app)

# Use separate collection objects for each collection
data_collection = mongo.db.data
location_collection = mongo.db.CheckpointLocation

# Helper function to prepare a document for JSON serialization
def prepare_doc(doc):
    if '_id' in doc:
        doc['_id'] = str(doc['_id'])
    
    # Convert datetime objects to ISO format string
    if isinstance(doc.get('message_date'), datetime):
        doc['message_date'] = doc['message_date'].isoformat()
    
    # Try to find matching location data and add lat/lng
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

# --------------------- NEW AND CORRECTED ROUTES ---------------------

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

# --------------------- ROUTES For Data ---------------------

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

# GET one random checkpoint from the 'CheckpointLocation' collection
@app.route('/api/checkpoints/random', methods=['GET'])
def get_random_checkpoint():
    pipeline = [{'$sample': {'size': 1}}]
    result = list(location_collection.aggregate(pipeline))
    if result:
        doc = prepare_doc(result[0])
        return jsonify(doc)
    else:
        return jsonify({"message": "No data found"}), 404

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

# --------------------- SERVER ---------------------
if __name__ == '__main__':
    app.run(debug=True)