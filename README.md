# 🗺️ Tariqi — طريقي

**Tariqi** (طريقي — "My Road") is a real-time Palestinian checkpoint monitoring platform. It collects live reports from Telegram channels, stores them in a database, and presents checkpoint status to users through an interactive web application with an AI-powered chatbot.

---

## 🌟 Features

- 📡 **Live Telegram Collection** — Automatically fetches checkpoint-related messages from Telegram channels using Azure Functions
- 🗺️ **Interactive Map** — Visualizes active checkpoints across Palestine on a live map
- 🤖 **AI Chatbot** — Ask about checkpoint status in Arabic; powered by OpenAI GPT with real-time MongoDB context
- 🔔 **Push Notifications** — Subscribe to checkpoint alerts
- 🎙️ **Voice Chat Bot** — Voice-based checkpoint queries
- 🔐 **Authentication** — Microsoft Azure AD (MSAL) login

---

## 🏗️ Architecture

```
Telegram Channels
      │
      ▼
Azure Functions (telegram-consumer)
  - Collects & filters messages
      │
      ▼
MongoDB Atlas (cloud database)
      │
      ▼
Flask REST API (backend/api)
  - Checkpoint queries
  - AI prompt builder (OpenAI)
  - Geo-location (Haversine)
      │
      ▼
React Frontend (frontend/)
  - Map, Chatbot, Notifications
  - Hosted on Azure Static Web Apps
```

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Frontend | React, React Router, Leaflet (Map) |
| Backend API | Python, Flask, Flask-PyMongo |
| AI | OpenAI GPT (via Azure OpenAI) |
| Database | MongoDB Atlas |
| Data Collection | Python Telethon + Azure Functions (Timer Trigger) |
| Auth | Microsoft MSAL / Azure AD |
| Secrets | Azure Key Vault |
| Hosting | Azure Static Web Apps + Azure Functions |
| CI/CD | GitHub Actions / Azure Pipelines |

---

## 📁 Project Structure

```
tariqi/
├── frontend/               # React web application
│   └── src/
│       ├── pages/          # Home, Map, About, VoiceChatBot, Feedback
│       ├── components/     # DarkModeToggle, etc.
│       ├── cards/          # CheckpointCard, Cards
│       └── contexts/       # DarkModeContext
│
└── backend/
    ├── api/                # Flask REST API
    │   ├── api.py          # Main API routes
    │   ├── ai_prompt_builder.py  # GPT context builder
    │   ├── geo_utils.py    # Haversine distance helper
    │   └── openai_client.py
    │
    └── telegram-consumer/  # Azure Function — data collector
        ├── function_app.py
        ├── telegram_collector.py
        ├── mongodb.py
        └── consumer.py
```

---

## 🚀 Getting Started

### Prerequisites

- Python 3.10+
- Node.js 18+
- MongoDB Atlas cluster
- Azure subscription (Key Vault, Functions, Static Web Apps)
- Telegram API credentials (`api_id`, `api_hash`)
- OpenAI API key

### Backend API

```bash
cd backend/api
pip install -r requirements.txt
flask run
```

### Telegram Consumer (local)

```bash
cd backend/telegram-consumer
pip install -r requirements.txt
func host start
```

### Frontend

```bash
cd frontend
npm install
npm start
```

---

## 🔑 Environment Variables

| Variable | Description |
|---|---|
| `MONGO_CONNECTION_STRING_KEY` | Key Vault secret name for MongoDB URI |
| `MONGO_COLLECTION_DATA` | MongoDB messages collection name |
| `MONGO_COLLECTION_LOCATIONS` | MongoDB checkpoints/locations collection |
| `TELEGRAM_API_ID` | Telegram API ID |
| `TELEGRAM_CHANNELS` | Comma-separated Telegram channel list |
| `RADIUS_IN_KM` | Search radius for nearby checkpoints |

Secrets (API keys, connection strings, phone numbers) are stored securely in **Azure Key Vault**.

---
## 🎬 Live System Demo

Click below to watch the full demonstration of Tariqi in action:

[![Watch Tariqi Demo](https://img.youtube.com/vi/ztqZMUrvAH8/maxresdefault.jpg)](https://www.youtube.com/watch?v=ztqZMUrvAH8)




