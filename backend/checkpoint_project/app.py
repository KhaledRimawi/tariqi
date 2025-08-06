from flask import Flask, request, jsonify
from flask_pymongo import PyMongo
from bson import ObjectId
from datetime import datetime
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# MongoDB Atlas URI
app.config["MONGO_URI"] = "mongodb+srv://AiTeamC:AI%23TeamC123@cluster0.904co68.mongodb.net/TeamC?retryWrites=true&w=majority"
mongo = PyMongo(app)

# Use 'data' collection like in Node.js
collection = mongo.db.data

# --------------------- ROUTES ---------------------

# GET one random checkpoint
@app.route('/api/checkpoints/random', methods=['GET'])
def get_random_checkpoint():
    pipeline = [{'$sample': {'size': 1}}]  # MongoDB aggregation to get random document
    result = list(collection.aggregate(pipeline))
    
    if result:
        doc = prepare_doc(result[0])
        return jsonify(doc)
    else:
        return jsonify({"message": "No data found"}), 404

# GET all data
@app.route('/api/data/show', methods=['GET'])
def get_all_data():
    results = collection.find().sort("updatedAt", -1)
    data = [prepare_doc(doc) for doc in results]
    return jsonify(data)

# GET by city
@app.route('/api/data/city/<city>', methods=['GET'])
def get_by_city(city):
    results = collection.find({"city": {'$regex': city, '$options': 'i'}}).sort("updatedAt", -1)
    data = [prepare_doc(doc) for doc in results]
    return jsonify(data)

# GET by checkpoint
@app.route('/api/data/checkpoint/<checkpoint>', methods=['GET'])
def get_by_checkpoint(checkpoint):
    results = collection.find({"checkpoint": {'$regex': checkpoint, '$options': 'i'}}).sort("updatedAt", -1)
    data = [prepare_doc(doc) for doc in results]
    return jsonify(data)

# GET by status
@app.route('/api/data/status/<status>', methods=['GET'])
def get_by_status(status):
    results = collection.find({"status": {'$regex': status, '$options': 'i'}}).sort("updatedAt", -1)
    data = [prepare_doc(doc) for doc in results]
    return jsonify(data)

# GET with search params (city + status)
@app.route('/api/data/search', methods=['GET'])
def search_data():
    city = request.args.get('city')
    status = request.args.get('status')

    query = {}
    if city:
        query['city'] = {'$regex': city, '$options': 'i'}
    if status:
        query['status'] = {'$regex': status, '$options': 'i'}

    results = collection.find(query).sort("updatedAt", -1)
    data = [prepare_doc(doc) for doc in results]
    return jsonify(data)

# DELETE all data
@app.route('/api/data', methods=['DELETE'])
def delete_all_data():
    result = collection.delete_many({})
    return jsonify({"message": "✅ All data deleted", "deletedCount": result.deleted_count})

# Helper to convert ObjectId to str
def prepare_doc(doc):
    doc['_id'] = str(doc['_id'])
    if isinstance(doc.get('updatedAt'), datetime):
        doc['updatedAt'] = doc['updatedAt'].isoformat()
    return doc

# --------------------- SERVER ---------------------
if __name__ == '__main__':
    app.run(port=5000, debug=True)
