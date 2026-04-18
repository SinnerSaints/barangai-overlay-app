# BarangAI Overlay App

A real-time AI support desktop application designed for Barangay officials. This floating overlay assistant provides instant access to AI guidance without disrupting workflows.

## Tech Stack

- **GUI:** PyQt6
- **Backend Auth:** Django
- **AI Service:** FastAPI
- **HTTP Client:** Requests
- **Screen Capture:** PyAutoGUI, PyGetWindow, Pillow
- **Config:** Python-Dotenv

## Installation & Setup

### 1. Clone Repository
``````bash
git clone https://github.com/SinnerSaints/barangai-overlay-app.git
cd BarangAI-Overlay
``````

### 2. Create Virtual Environment
``````bash
python -m venv venv
venv\Scripts\activate
``````

### 3. Install Dependencies
``````bash
pip install -r requirements.txt
``````

### 4. Configure Environment Variables
Create a `.env` file:
``````env
BACKEND_URL=http://backend-url
AI_SERVICE_URL=http://service-url
``````

## Running the App

``````bash
python main.py
``````

The application will launch with a login window. Enter your credentials to start using the assistant.

Features:
- Chat in the main window
- Click minimize to convert to a floating bubble
- Drag the bubble anywhere on screen
- Click bubble to restore full window
- Change language preferences