#!/usr/bin/env python3
"""
Debug OAuth configuration and test token exchange
"""
import sys
sys.path.append('.')

from spotify_auth import SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET, REDIRECT_URI
import requests
import base64
import logging

logging.basicConfig(level=logging.DEBUG)

def debug_oauth_config():
    """Debug the current OAuth configuration"""
    print("="*60)
    print("SPOTIFY OAUTH CONFIGURATION DEBUG")
    print("="*60)
    
    print(f"Client ID: {SPOTIFY_CLIENT_ID}")
    print(f"Client Secret: {SPOTIFY_CLIENT_SECRET[:10]}...")
    print(f"Redirect URI: {REDIRECT_URI}")
    print()
    
    print("WHAT TO CHECK IN SPOTIFY DEVELOPER DASHBOARD:")
    print("1. Go to: https://developer.spotify.com/dashboard")
    print(f"2. Find app with Client ID: {SPOTIFY_CLIENT_ID}")
    print("3. Check 'Redirect URIs' section")
    print("4. Must contain EXACTLY:")
    print(f"   {REDIRECT_URI}")
    print()
    
    print("COMMON REDIRECT URI ISSUES:")
    print("❌ http://... (must be https://)")
    print("❌ Extra trailing slash")
    print("❌ Different domain/port")
    print("❌ Case sensitivity")
    print()
    
    print("QUICK TEST:")
    print("If redirect URI is correctly configured, the 400 error should stop.")
    print("If you still get 400 error, the redirect URI in Spotify dashboard")
    print("doesn't match what we're sending.")

if __name__ == '__main__':
    debug_oauth_config()