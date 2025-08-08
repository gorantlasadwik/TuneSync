#!/usr/bin/env python3
"""
Setup ngrok tunnel for SyncTunes Spotify OAuth testing
"""
import subprocess
import time
import requests
import json
import os

def setup_ngrok():
    print("Setting up ngrok tunnel for SyncTunes...")
    
    # Kill any existing ngrok processes
    try:
        subprocess.run(['pkill', 'ngrok'], capture_output=True)
        time.sleep(2)
    except:
        pass
    
    # Start ngrok
    print("Starting ngrok tunnel on port 5000...")
    process = subprocess.Popen(
        ['./ngrok', 'http', '5000', '--log=stdout'],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    # Wait for ngrok to start
    time.sleep(5)
    
    try:
        # Get tunnel info
        response = requests.get('http://localhost:4040/api/tunnels', timeout=5)
        tunnels = response.json()
        
        if tunnels and 'tunnels' in tunnels and tunnels['tunnels']:
            public_url = tunnels['tunnels'][0]['public_url']
            print(f"✅ Ngrok tunnel created: {public_url}")
            print(f"🔗 SyncTunes accessible at: {public_url}")
            print(f"📋 Spotify redirect URI: {public_url}/api/spotify/callback")
            
            return public_url
        else:
            print("❌ No tunnels found")
            return None
            
    except Exception as e:
        print(f"❌ Error getting tunnel info: {e}")
        return None

if __name__ == '__main__':
    url = setup_ngrok()
    if url:
        print("\n" + "="*60)
        print("🎵 SyncTunes with ngrok tunnel is ready!")
        print(f"🌐 Access at: {url}")
        print("📝 Add this to Spotify redirect URIs:")
        print(f"   {url}/api/spotify/callback")
        print("="*60)
    else:
        print("❌ Failed to set up ngrok tunnel")