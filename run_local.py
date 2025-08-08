#!/usr/bin/env python3
"""
SyncTunes Local Development Runner
Handles the Spotify localhost limitation by providing setup instructions
"""

import os
import sys
from app import app

def main():
    print("=" * 60)
    print("🎵 SyncTunes - Local Development Server")
    print("=" * 60)
    
    # Check if redirect URI is set for localhost
    redirect_uri = os.getenv('REDIRECT_URI', '')
    
    if 'localhost' in redirect_uri or '127.0.0.1' in redirect_uri:
        print("⚠️  WARNING: Spotify doesn't allow localhost redirect URIs")
        print("\n📋 To test Spotify OAuth locally:")
        print("1. Install ngrok: https://ngrok.com/download")
        print("2. Run: ngrok http 5000")
        print("3. Update REDIRECT_URI to your ngrok HTTPS URL")
        print("4. Add the ngrok URL to your Spotify app settings")
        print("\n" + "="*60)
    
    print(f"🚀 Starting SyncTunes on http://localhost:5000")
    print(f"📍 Current redirect URI: {redirect_uri}")
    print("🔗 Access at: http://localhost:5000")
    print("❤️  Health check: http://localhost:5000/health")
    print("=" * 60)
    
    try:
        # Run the Flask app
        port = int(os.environ.get('PORT', 5000))
        app.run(host='0.0.0.0', port=port, debug=True)
    except KeyboardInterrupt:
        print("\n👋 SyncTunes stopped. Thanks for using SyncTunes!")
    except Exception as e:
        print(f"❌ Error starting SyncTunes: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()