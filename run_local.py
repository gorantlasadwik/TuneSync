#!/usr/bin/env python3
"""
Run SyncTunes locally with localhost OAuth configuration
"""
import os
import sys
from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash

# Set localhost configuration
os.environ['REDIRECT_URI'] = 'http://localhost:5000/api/spotify/callback'

# Import after setting environment
sys.path.append('.')
from database import *
from spotify_auth import *
from youtube_music import *
import routes

def create_localhost_app():
    """Create Flask app configured for localhost"""
    app = Flask(__name__)
    app.secret_key = os.environ.get('SESSION_SECRET', 'dev-secret-key-for-localhost')
    
    # Register all routes
    from routes import register_routes
    register_routes(app)
    
    print("="*60)
    print("🎵 SyncTunes - Localhost Configuration")
    print("="*60)
    print("App running on: http://localhost:5000")
    print("OAuth redirect: http://localhost:5000/api/spotify/callback")
    print("")
    print("Spotify Dashboard Settings Needed:")
    print("- Add redirect URI: http://localhost:5000/api/spotify/callback")
    print("- Client ID: 6ebe47c28c0c462a9465a17a8c337e4e")
    print("")
    print("Test Account:")
    print("- Email: demo@example.com")
    print("- Password: demo123")
    print("="*60)
    
    return app

if __name__ == '__main__':
    app = create_localhost_app()
    app.run(host='localhost', port=5000, debug=True)