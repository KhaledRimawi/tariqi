import os
import random
from datetime import datetime, timedelta, timezone

from ai_prompt_builder import AIPromptBuilder
from dotenv import load_dotenv
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

# Initialize AI Prompt Builder
ai_prompt_builder = AIPromptBuilder(mongo)

RADIUS_KM = float(os.getenv("RADIUS_IN_KM", "10"))

# Verify that the values exist
if not COLLECTION_DATA or not COLLECTION_LOCATIONS:
    raise ValueError("❌ COLLECTION_DATA or COLLECTION_LOCATIONS is missing in .env file")


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
    Enhanced AI endpoint that provides intelligent responses about checkpoint status
    with real-time data from MongoDB.
    Request format:
        { "prompt": "ما هي حالة حاجز قلنديا؟" }
    """
    try:
        data = request.get_json()
        user_prompt = data.get("prompt")

        if not user_prompt:
            return jsonify({"error": "No prompt provided"}), 400

        print("📝 User query: {user_prompt}")

        # Check if this is a checkpoint-related query
        if ai_prompt_builder.is_checkpoint_query(user_prompt):
            # Build smart prompt with MongoDB context
            enhanced_prompt = ai_prompt_builder.build_smart_prompt(user_prompt)
            print("🧠 Enhanced prompt built with checkpoint context")
        else:
            # Use regular prompt for general queries
            enhanced_prompt = f"""
أنت مساعد ذكي متخصص في الإجابة على الأسئلة باللغة العربية.

سؤال المستخدم: "{user_prompt}"

يرجى تقديم إجابة مفيدة ومناسبة. إذا كان السؤال متعلق بالحواجز أو الطرق،
أعلم المستخدم أنه يمكن السؤال عن حالة الحواجز بذكر اسم الحاجز مثل "ما هي حالة حاجز قلنديا؟"

تأكد من الرد باللغة العربية فقط.
            """.strip()

        # Get AI response using the enhanced prompt
        ai_response = get_gpt_response(enhanced_prompt)

        print("✅ AI response generated successfully")

        return jsonify(
            {
                "success": True,
                "prompt": user_prompt,
                "response": ai_response,
                "enhanced": ai_prompt_builder.is_checkpoint_query(user_prompt),
            }
        )

    except Exception as e:
        print(f"❌ Error in ask_ai: {e}")
        return jsonify({"error": str(e)}), 500


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


# ---------------- User on the frontend (Map.js) & (Destination Search) pages ----------------
@app.route("/api/checkpoints/query", methods=["GET"])
def search_road_conditions():
    """
    Query checkpoints.

    Modes:
    - all=true  -> start from locations (every checkpoint with lat/lng), join the latest status from data.
                   Supports filters: checkpoint, city, status, direction, ago, top.
    """
    try:
        checkpoint_name = request.args.get("checkpoint", "")
        city_name = request.args.get("city", "")
        status = request.args.get("status", "")
        direction = request.args.get("direction", "")
        ago_filter = request.args.get("ago", "")
        top_filter = request.args.get("top", "")
        latest_flag = request.args.get("latest", "false").lower() == "true"
        with_location = request.args.get("with_location", "false").lower() == "true"
        all_flag = request.args.get("all", "false").lower() == "true"

        if all_flag:
            ago_cutoff = None
            if ago_filter:
                try:
                    ago_value = int(ago_filter)
                    if ago_value < 0:
                        return jsonify({"error": "Ago value must be a positive integer."}), 400
                    ago_cutoff = datetime.utcnow() - timedelta(minutes=ago_value)
                except ValueError:
                    return jsonify({"error": "Invalid value for 'ago'. Please use a positive integer."}), 400

            match_locs = {"lat": {"$exists": True}, "lng": {"$exists": True}}
            if checkpoint_name:
                match_locs["checkpoint"] = {"$regex": checkpoint_name.strip('"'), "$options": "i"}
            if city_name:
                match_locs["city"] = {"$regex": city_name.strip('"'), "$options": "i"}

            lookup_pipeline = [
                {
                    "$match": {
                        "$expr": {"$and": [{"$eq": ["$city_name", "$$cty"]}, {"$eq": ["$checkpoint_name", "$$cp"]}]}
                    }
                }
            ]
            if ago_cutoff:
                lookup_pipeline.append({"$match": {"message_date": {"$gte": ago_cutoff}}})
            lookup_pipeline.extend([{"$sort": {"message_date": -1}}, {"$limit": 1}])

            pipeline = [
                {"$match": match_locs},
                {
                    "$lookup": {
                        "from": COLLECTION_DATA,  # name of your data collection from .env
                        "let": {"cty": "$city", "cp": "$checkpoint"},
                        "pipeline": lookup_pipeline,
                        "as": "latest",
                    }
                },
                {"$unwind": {"path": "$latest", "preserveNullAndEmptyArrays": True}},
            ]

            # post-filters on the joined latest status
            post_match = {}
            if status:
                post_match["latest.status"] = {"$regex": status.strip('"'), "$options": "i"}
            if direction:
                post_match["latest.direction"] = {"$regex": direction.strip('"'), "$options": "i"}
            if post_match:
                pipeline.append({"$match": post_match})

            pipeline.append(
                {
                    "$project": {
                        "_id": 0,
                        "checkpoint_name": "$checkpoint",
                        "city_name": "$city",
                        "lat": 1,
                        "lng": 1,
                        "status": "$latest.status",
                        "direction": "$latest.direction",
                        "message": "$latest.message",
                        "message_date": "$latest.message_date",
                    }
                }
            )

            #  top limit
            if top_filter:
                try:
                    n = int(top_filter)
                    if n > 0:
                        pipeline.append({"$limit": n})
                except ValueError:
                    return jsonify({"error": "Invalid value for 'top'. Please use a positive integer."}), 400

            docs = list(location_collection.aggregate(pipeline))

            # Serialize message_date
            out = []
            for d in docs:
                md = d.get("message_date")
                if isinstance(md, datetime):
                    d["message_date"] = md.isoformat()
                out.append(d)

            return jsonify({"results": out, "count": len(out)}), 200

        mongo_filter = {}
        if ago_filter:
            try:
                ago_value = int(ago_filter)
                if ago_value < 0:
                    return jsonify({"error": "Ago value must be a positive integer."}), 400
                cutoff_time = datetime.utcnow() - timedelta(minutes=ago_value)
                mongo_filter["message_date"] = {"$gte": cutoff_time}
            except ValueError:
                return jsonify({"error": "Invalid value for 'ago'. Please use a positive integer."}), 400

        if checkpoint_name:
            mongo_filter["checkpoint_name"] = {"$regex": checkpoint_name.strip('"'), "$options": "i"}
        if city_name:
            mongo_filter["city_name"] = {"$regex": city_name.strip('"'), "$options": "i"}
        if status:
            mongo_filter["status"] = {"$regex": status.strip('"'), "$options": "i"}
        if direction:
            mongo_filter["direction"] = {"$regex": direction.strip('"'), "$options": "i"}

        sort_order = [("message_date", -1)]

        limit = 0
        if top_filter:
            try:
                limit = int(top_filter)
                if limit < 1:
                    return jsonify({"error": "Top value must be a positive integer greater than 0."}), 400
            except ValueError:
                return jsonify({"error": "Invalid value for 'top'. Please use a positive integer."}), 400

        messages = list(data_collection.find(mongo_filter).sort(sort_order).limit(limit))

        if latest_flag:
            seen = set()
            reduced = []
            for d in messages:
                key = (d.get("city_name"), d.get("checkpoint_name"))
                if key not in seen:
                    seen.add(key)
                    reduced.append(d)
            messages = reduced

        if with_location and messages:
            wanted_pairs = []
            pair_set = set()
            for m in messages:
                c = m.get("city_name")
                cp = m.get("checkpoint_name")
                if c and cp:
                    key = (c, cp)
                    if key not in pair_set:
                        pair_set.add(key)
                        wanted_pairs.append({"city": c, "checkpoint": cp})

            if wanted_pairs:
                loc_cursor = location_collection.find({"$or": wanted_pairs})
                loc_map = {
                    (loc.get("city"), loc.get("checkpoint")): (loc.get("lat"), loc.get("lng")) for loc in loc_cursor
                }
            else:
                loc_map = {}

            for m in messages:
                key = (m.get("city_name"), m.get("checkpoint_name"))
                if key in loc_map:
                    m["lat"], m["lng"] = loc_map[key]

        out = []
        for msg in messages:
            item = {
                "_id": str(msg.get("_id")),
                "checkpoint_name": msg.get("checkpoint_name"),
                "city_name": msg.get("city_name"),
                "status": msg.get("status"),
                "direction": msg.get("direction"),
                "message": msg.get("message"),
                "message_date": (
                    msg.get("message_date").isoformat()
                    if isinstance(msg.get("message_date"), datetime)
                    else msg.get("message_date")
                ),
            }
            if "lat" in msg:
                item["lat"] = msg["lat"]
            if "lng" in msg:
                item["lng"] = msg["lng"]
            out.append(item)

        return jsonify({"results": out, "count": len(out)}), 200

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


def start_api_server():
    print("\n🤝 Team Integration Ready!")
    port = int(os.getenv("PORT", 5000))
    # Always bind to 0.0.0.0 so it works both locally and in Azure
    app.run(host="0.0.0.0", port=port, debug=False, use_reloader=False)


if __name__ == "__main__":
    start_api_server()
