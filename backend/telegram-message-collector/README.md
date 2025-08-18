# Tariqi📍🤖 – Backend

## Telegram Message Collector Folder – Backend
This is the backend service for the **Tariqi** project.  
It collects messages from multiple Telegram channels/groups, processes them, and stores them in MongoDB.  
The backend integrates with **Azure Key Vault** for securely managing secrets (Telegram session, API credentials, etc.).

---

## 📂 Project Structure
```
telegram-message-collector/
├── api.py                  # API routes and endpoints
├── appsecrets.py           # Handles secrets retrieval (Azure Key Vault)
├── geo_utils.py            # Geolocation helper functions
├── main.py                 # Backend entry point
├── mongodb_handler.py      # MongoDB connection and data operations
├── multi_channel_collector.py # Collects messages from multiple channels
├── telegram_consumer.py    # Telegram client consumer logic
├── requirements.txt        # Python dependencies
└── .env                    # Local environment variables
```
---

## 🚀 Prerequisites

Make sure you have installed the following:

- Python 3.9+
- Pip (Python package manager)
- [Azure CLI](https://learn.microsoft.com/en-us/cli/azure/install-azure-cli-windows?view=azure-cli-latest&pivots=msi) (for accessing Key Vault secrets)
- MongoDB (local or cloud instance, e.g., MongoDB Atlas)

---
### Backend
---
- **Language:** Python 3
- **Framework:** Flask
- **Database:** MongoDB (using MongoDB Atlas)
- **Libraries:**
  - **Telethon:** Interact with the Telegram API and scrape channel messages
  - **Flask-PyMongo:** Connect the Flask application with MongoDB
  - **python-dotenv:** Manage environment variables
  - **Flask-CORS:** Handle Cross-Origin Resource Sharing for the API

## ⚙️ Setup

Clone the repository:

```bash
git clone <your-repo-url>
cd telegram-message-collector

```

## Install Dependencies

```bash
pip install -r requirements.txt
```

## 🔑 Azure Key Vault Setup

Login to Azure:

```bash
az login
```
Set subscription: choose the number of the subscription or use the following command :
```bash
az account set --subscription "<subscription-id>"
```
Access your Key Vault secrets (optional):
```bash
az keyvault secret list --vault-name <your-keyvault-name>
```
The backend retrieves secrets via appsecrets.py.

## Running the Backend

Start the backend:
```bash
python main.py
```