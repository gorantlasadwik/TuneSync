# SyncTunes - Local Development Setup

## Prerequisites
- Python 3.11 or higher
- Git (to clone the repository)

## Step 1: Download the Project
If you have the files locally, skip to Step 2. Otherwise:
```bash
# Download all project files to your local machine
# Copy all .py files, templates/, static/, and other project files
```

## Step 2: Install Dependencies
```bash
# Navigate to project directory
cd synctunes

# Install required packages
pip install flask flask-sqlalchemy gunicorn psycopg2-binary python-dotenv requests werkzeug ytmusicapi email-validator
```

## Step 3: Set Environment Variables
Create a `.env` file in the project root:
```bash
# .env file content
SESSION_SECRET=your-secret-key-here
SPOTIFY_CLIENT_ID=6ebe47c28c0c462a9465a17a8c337e4e
SPOTIFY_CLIENT_SECRET=8647e906b0624e16823613a61fe318c8
REDIRECT_URI=http://localhost:5000/api/spotify/callback
```

## Step 4: Update Spotify Developer Settings
In your Spotify Developer Dashboard:
1. Go to your app settings
2. Add `http://localhost:5000/api/spotify/callback` to Redirect URIs
3. Save changes

## Step 5: Run the Application
```bash
# Method 1: Direct Flask
python main.py

# Method 2: Using gunicorn (recommended)
gunicorn --bind 0.0.0.0:5000 --reload main:app
```

## Step 6: Access the Application
Open your browser and go to:
- **http://localhost:5000** - Main application
- **http://localhost:5000/health** - Health check

## Features Available Locally
- ✅ User registration and login
- ✅ Spotify OAuth integration (after updating redirect URI)
- ✅ YouTube Music integration
- ✅ Playlist viewing and synchronization
- ✅ All database operations (in-memory)

## Troubleshooting
- If Spotify OAuth fails: Ensure redirect URI is added to Spotify app
- If port 5000 is busy: Change port in main.py
- If dependencies fail: Use `pip install --upgrade` for each package

The app will run exactly as it does in Replit, with full functionality.