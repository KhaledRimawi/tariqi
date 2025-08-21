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
├── .env                    # Local environment variables
├── format.py               # Formats code with black and isort
└── build.py                # Runs flake8 and compileall (lint + build check)
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

- **Language:** Python 3
- **Framework:** Flask
- **Database:** MongoDB (using MongoDB Atlas)
- **Libraries:**
  - **Telethon:** Interact with the Telegram API and scrape channel messages
  - **Flask-PyMongo:** Connect the Flask application with MongoDB
  - **python-dotenv:** Manage environment variables
  - **Flask-CORS:** Handle Cross-Origin Resource Sharing for the API

---

## ⚙️ Setup

### 1. Clone the Repository

```bash
git clone <your-repo-url>
cd telegram-message-collector
```

### 2. Install Runtime Dependencies

```bash
pip install -r requirements.txt
```

### 3. Install Developer Tools (One-Time Only)

To enable formatting and linting tools locally:

```bash
pip install flake8 black isort
```

---

## 🧼 Code Formatting

Use the `format.py` script to format your Python code automatically:

```bash
python format.py
```

This script runs:

- `black` – formats code for consistency
- `isort` – organizes import statements

➡️ **Please run this regularly**, especially before committing changes.

---

## 🧪 Linting & Build Check

Use the `build.py` script to:

- Lint your code with `flake8`
- Perform a syntax check with `compileall`

```bash
python build.py
```

✅ This helps catch issues early and should match the checks run in CI/CD.

---

## 🔑 Azure Key Vault Setup

### Option 1 – Using `DefaultAzureCredential` (older method)

Login to Azure:

```bash
az login
```

Set subscription (choose number or use command):

```bash
az account set --subscription "<subscription-id>"
```

(Optional) View secrets:

```bash
az keyvault secret list --vault-name <your-keyvault-name>
```

Secrets are fetched automatically via `appsecrets.py`.

---

### Option 2 – Using `ClientSecretCredential` 

This requires an Azure AD App Registration.

1. Go to your Key Vault and find the secret named `AppSecret`.
2. Copy the **secret value** (not the identifier).
3. Save it to your **local environment variables**.

#### Set Environment Variable:
you can use : 
**PowerShell:**
```powershell
setx AppSecret "<secret-value>"
```
or 
**Windows GUI:**
- Win + R → `sysdm.cpl` or simply search for `Environment variables`
- Advanced → Environment Variables
- Add: `AppSecret = <your-secret>`
- Restart your terminal or IDE

---

## ▶️ Running the Backend

To start the backend server locally:

```bash
python main.py
```

Make sure you’ve set up your `.env` file and have access to the required secrets from Azure Key Vault.
