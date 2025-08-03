import json
import os
from pymongo import MongoClient
from datetime import datetime

# ✅ MongoDB Atlas connection string (password encoded)
uri = "mongodb+srv://AiTeamC:AI%23TeamC123@cluster0.904co68.mongodb.net/?retryWrites=true&w=majority"
client = MongoClient(uri)
db = client["TeamC"]  # Database name
collection = db["data"]  # Collection name

try:
    # 📂 Load JSON data from 'mock_checkpoints_data.json' in the same directory
    file_name = 'mock_checkpoints_data.json'
    file_path = os.path.join(os.path.dirname(__file__), file_name)

    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # 🕒 Convert 'updatedAt' to datetime objects if present
    for doc in data:
        if 'updatedAt' in doc:
            try:
                doc['updatedAt'] = datetime.fromisoformat(doc['updatedAt'].replace('Z', '+00:00'))
            except Exception as e:
                print(f"⚠️ Failed to parse date: {doc.get('updatedAt')} — {e}")
                doc['updatedAt'] = None

    print(f"📦 Sample data: {data[:2]}")

    # 📤 Insert data into MongoDB
    result = collection.insert_many(data)
    print(f"✅ Data inserted successfully: {len(result.inserted_ids)} documents")

except Exception as e:
    print("❌ Error:", e)

finally:
    client.close()
