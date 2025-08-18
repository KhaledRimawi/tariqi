# Tariqi📍🤖 (Frontend)

This is the frontend for the **Tariqi** web application, a tool designed to help users navigate Palestine more safely and efficiently by providing real-time data on checkpoint statuses. This application is built with React.js.

## Table of Contents

- [About The Project](#about-the-project)
- [Key Features](#key-features)
- [Frontend Tech Stack](#frontend-tech-stack)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Installation & Setup](#installation--setup)
- [Available Scripts](#available-scripts)
- [Project Structure](#project-structure)
- [Interacting with the API](#interacting-with-the-api)
- [Environment Variables](#environment-variables)
- [Future Improvements](#future-improvements)

## About The Project

Movement within Palestine can often be unpredictable due to the presence of checkpoints. This project aims to mitigate this uncertainty by creating a centralized platform for real-time information. The frontend is responsible for presenting this data to the user through an intuitive and interactive web interface.

## Key Features

-   🗺️ **Real-Time Interactive Map**: Displays all known checkpoints on a map, color-coded by their current status (e.g., open, congested, closed).
-   🤖 **AI-Powered Chatbot**: Users can ask natural language questions about specific checkpoints or cities and receive instant status updates.
-   🔔 **Proximity Notifications**: The system can send push notifications to users when they approach a checkpoint, informing them of its current condition.
-   🔍 **Destination Search & Filtering**: Users can search for checkpoints by city, status, or name, and filter the results to find the information they need quickly.
-   📝 **User Feedback System**: A feedback feature allows users to report the status of a checkpoint directly, contributing to the accuracy of our data and helping the community.
-   📊 **Latest Updates Feed**: The homepage displays the most recent updates on checkpoint statuses, keeping users informed at a glance.

## Frontend Tech Stack

This application is built with React.js and communicates with a Python/Flask backend API for data.

-   **Framework:** **React.js**
-   **Routing:** **React Router**
-   **Styling:** **CSS + Bootstrap**
-   **Key Libraries:**
    -   `axios` or `fetch` for API communication.
    -   A mapping library like `Leaflet` or `Google Maps API`.
    -   `Bootstrap` for responsive design and UI components.

## Getting Started

Follow these instructions to get the frontend application running locally.

### Prerequisites

-   **Node.js and npm** (v16+ recommended). You can download them from [nodejs.org](https://nodejs.org/).
-   **Access to a running instance of the Tariqi backend API.** The URL for this API must be configured in the environment variables.

### Installation & Setup

1.  **Clone the repository:**
    ```bash
    git clone https://AI2025@dev.azure.com/AI2025/Project%20C/_git/Project%20C
    ```

2.  **Navigate to the frontend directory:**
    ```bash
    cd "Project C"/frontend
    ```

3.  **Install npm packages:**
    This will install all the necessary dependencies listed in `package.json`.
    ```bash
    npm install
    ```

4.  **Set up environment variables:**
    Create a file named `.env` in the `frontend/` root directory. See the [Environment Variables](#environment-variables) section for details.

5.  **Start the development server:**
    ```bash
    npm start
    ```
    The application will open automatically in your browser at `http://localhost:3000`.

## Available Scripts

In the project directory, you can run:

-   `npm start`: Runs the app in development mode.
-   `npm test`: Launches the test runner in interactive watch mode.
-   `npm run build`: Builds the app for production to the `build` folder.

## Project Structure

The `src` folder is organized as follows:

```text
src/
├── assets/         # Images, logos, and other static assets
├── cards/          # Reusable card components (e.g., CheckpointCard)
├── pages/          # Main page components (Home, MapPage, About, etc.)
│   ├── About.js
│   ├── ChatUI.js
│   ├── Home.js
│   └── MapPage.js
├── App.js          # Root component with React Router setup
├── index.js        # Main entry point of the application
├── navbar.js       # The main navigation bar component
└── ... (CSS files, tests, etc.)
```

## Interacting with the API

The frontend is responsible for fetching data from and displaying information provided by the backend API. Below are the key endpoints the application consumes:

| Method | Endpoint                             | Description                                                               |
| :----- | :----------------------------------- | :------------------------------------------------------------------------ |
| `GET`  | `/`                                  | Displays a welcome message and a list of all available endpoints.         |
| `GET`  | `/api/health`                        | Checks the connection status to MongoDB and provides collection counts.   |
| `GET`  | `/api/checkpoints/merged`            | **Main map endpoint.** Returns all checkpoints with their location and latest known status. |
| `GET`  | `/api/latest`                        | Gets the 5 most recently updated checkpoints.                             |
| `GET`  | `/api/near_location`                 | Finds checkpoints within a specified radius of a user's lat/lng.          |
| `GET`  | `/api/closest-checkpoint`            | Finds the single closest checkpoint to a user's lat/lng.                  |
| `GET`  | `/api/search/city/<city_name>`       | Searches for messages related to a specific city.                         |
| `GET`  | `/api/search/checkpoint/<cp_name>`   | Searches for messages related to a specific checkpoint.                   |
| `GET`  | `/api/search/status/<status>`        | Searches for messages with a specific status (e.g., "مفتوح").            |
| `GET`  | `/api/checkpoints/conditions`        | Gets the latest unique status for each checkpoint, with filtering options. |
| `GET`  | `/api/locations`                     | Returns the static geographical locations of all known checkpoints.       |

## Environment Variables

To connect the frontend to the backend API, create a `.env` file in the `frontend/` directory with the following variable:

```env
# The base URL for the backend API
REACT_APP_API_URL=http://127.0.0.1:5000
```

## Future Improvements

- **Native Mobile App:** Develop a React Native or Flutter application for a better mobile experience and more reliable push notifications.
- **Machine Learning Integration:** Use historical data to predict checkpoint statuses at certain times of the day or week.
- **UI/UX Enhancements:** Refine the user interface for better accessibility and a more modern look and feel.
- **User Authentication:** Allow users to create accounts to save favorite routes and receive personalized notifications.
