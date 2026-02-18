# DriveBy.AI: Advanced Driver Monitoring System 🚗👁️

A robust, real-time driver monitoring solution designed to prevent accidents caused by fatigue and drowsiness. DriveBy.AI utilizes computer vision and machine learning across a distributed architecture to detect signs of fatigue (like closed eyes and yawning) and emotional distress, alerting drivers instantly and notifying family members remotely.

## 🌟 Key Features

*   **Real-time Fatigue Detection**: Monitors eye closure duration (PERCLOS) and yawn frequency using MediaPipe Face Mesh.
*   **Emotion Recognition**: Detects negative emotions (Investigative) that may contribute to unsafe driving.
*   **Instant Alerts**: Triggers loud audio alarms and visual warnings for the driver when fatigue scores exceed critical thresholds.
*   **Family Dashboard**: A live web dashboard for family members to monitor the driver's status in real-time.
*   **Historical Tracking**: Logs fatigue events and emotional states for post-trip analysis.
*   **Secure Authentication**: Role-based access control for Drivers and Family members.

## 📸 Screenshots

### 1. Driver Dashboard (Family Monitor)
*(Place your dashboard screenshot here: `assets/dashboard_screenshot.png`)*
> The dashboard provides a live view of the driver's fatigue score, emotion, and current status.

### 2. AI Engine HUD (Driver View)
*(Place your AI engine screenshot here: `assets/monitor_screenshot.png`)*
> The local AI engine displays real-time metrics including EAR (Eye Aspect Ratio) and MAR (Mouth Aspect Ratio).

## 🛠️ Technology Stack

### Backend (API & Database)
*   **Framework**: FastAPI (Python)
*   **Database**: PostgreSQL (via Docker) or SQLite (Dev)
*   **ORM**: SQLAlchemy
*   **Authentication**: JWT (JSON Web Tokens)
*   **Communication**: WebSocket for real-time data streaming

### AI Engine (Edge/Local)
*   **Core**: Python
*   **Computer Vision**: OpenCV, MediaPipe
*   **ML Models**: PyTorch, FER (Facial Expression Recognition)
*   **Audio**: Pygame

### Frontend (User Interface)
*   **Framework**: React (Vite)
*   **Styling**: TailwindCSS
*   **Charts**: Recharts
*   **State Management**: React Context API

## 🚀 Setup & Installation

### Prerequisites
*   Python 3.10+ (Recommended for AI Engine compatibility)
*   Node.js 18+
*   Docker & Docker Compose (Optional, for production DB)

### 1. Backend Setup
```bash
cd backend
# Create virtual environment (optional) and install dependencies
pip install -r requirements.txt
# Run the server
python main.py
```
*Server runs on: http://localhost:8000*

### 2. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```
*Dashboard runs on: http://localhost:5173*

### 3. AI Engine Setup (Driver Device)
Ensure a webcam is connected.
```bash
cd driver_ai
# Create a dedicated virtual environment (Python 3.10 recommended)
pip install -r requirements.txt
# Run the engine
python main.py <email> <password>
```
*Or use the provided `start_driver.bat` script on Windows.*

## 📖 Usage Guide

1.  **Register Users**: Open the Frontend URL and register a **Driver** account and a **Family** account.
2.  **Start Monitoring**: Launch the AI Engine on the driver's machine and log in with the Driver credentials.
3.  **Real-time Tracking**: Log in to the Frontend with the Family account to see live updates.
4.  **Thresholds**:
    *   **Alert Trigger**: Fatigue Score > 80
    *   **Eyes Closed**: EAR < 0.20
    *   **Yawning**: MAR > 0.60

## 📦 Project Structure

*   **/backend**: API Server and Database models.
*   **/frontend**: React-based dashboard application.
*   **/driver_ai**: Computer vision logic and alertness monitoring.

## 📄 License
MIT License - DriveBy.AI Team
