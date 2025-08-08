import os
import requests
import base64
import urllib.parse
import logging
from typing import Optional, Dict, Any, List
from database import db, get_platform_by_name, create_user_platform_account, get_user_accounts

# Spotify API configuration
SPOTIFY_CLIENT_ID = os.getenv('SPOTIFY_CLIENT_ID', '6ebe47c28c0c462a9465a17a8c337e4e')
SPOTIFY_CLIENT_SECRET = os.getenv('SPOTIFY_CLIENT_SECRET', '8647e906b0624e16823613a61fe318c8')
REDIRECT_URI = os.getenv('REDIRECT_URI', 'http://localhost:5000/api/spotify/callback')

SPOTIFY_AUTH_URL = 'https://accounts.spotify.com/authorize'
SPOTIFY_TOKEN_URL = 'https://accounts.spotify.com/api/token'
SPOTIFY_API_URL = 'https://api.spotify.com/v1'

def get_spotify_auth_url(state: str = "") -> str:
    """Get Spotify authorization URL"""
    scope = 'playlist-read-private playlist-read-collaborative playlist-modify-public playlist-modify-private user-read-private user-read-email'
    
    params = {
        'client_id': SPOTIFY_CLIENT_ID,
        'response_type': 'code',
        'redirect_uri': REDIRECT_URI,
        'scope': scope,
        'show_dialog': 'true'
    }
    
    if state:
        params['state'] = state
    
    logging.info(f"DEBUG: Using redirect URI: {REDIRECT_URI}")
    return f"{SPOTIFY_AUTH_URL}?{urllib.parse.urlencode(params)}"

def exchange_code_for_token(code: str) -> Optional[Dict[str, Any]]:
    """Exchange authorization code for access token"""
    auth_string = f"{SPOTIFY_CLIENT_ID}:{SPOTIFY_CLIENT_SECRET}"
    auth_bytes = auth_string.encode('utf-8')
    auth_base64 = base64.b64encode(auth_bytes).decode('utf-8')
    
    headers = {
        'Authorization': f'Basic {auth_base64}',
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    
    data = {
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': REDIRECT_URI
    }
    
    try:
        response = requests.post(SPOTIFY_TOKEN_URL, headers=headers, data=data)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"Error exchanging code for token: {e}")
        return None

def get_user_profile(access_token: str) -> Optional[Dict[str, Any]]:
    """Get Spotify user profile"""
    headers = {'Authorization': f'Bearer {access_token}'}
    
    try:
        response = requests.get(f"{SPOTIFY_API_URL}/me", headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"Error getting user profile: {e}")
        return None

def get_user_playlists(access_token: str) -> List[Dict[str, Any]]:
    """Get user's Spotify playlists"""
    headers = {'Authorization': f'Bearer {access_token}'}
    playlists = []
    url = f"{SPOTIFY_API_URL}/me/playlists?limit=50"
    
    try:
        while url:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            data = response.json()
            playlists.extend(data.get('items', []))
            url = data.get('next')
        
        return playlists
    except requests.RequestException as e:
        print(f"Error getting playlists: {e}")
        return []

def get_playlist_tracks(access_token: str, playlist_id: str) -> List[Dict[str, Any]]:
    """Get tracks from a Spotify playlist"""
    headers = {'Authorization': f'Bearer {access_token}'}
    tracks = []
    url = f"{SPOTIFY_API_URL}/playlists/{playlist_id}/tracks?limit=100"
    
    try:
        while url:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            data = response.json()
            
            for item in data.get('items', []):
                track = item.get('track')
                if track and track.get('type') == 'track':
                    tracks.append({
                        'id': track['id'],
                        'name': track['name'],
                        'artists': [artist['name'] for artist in track['artists']],
                        'album': track['album']['name'],
                        'duration_ms': track.get('duration_ms', 0)
                    })
            
            url = data.get('next')
        
        return tracks
    except requests.RequestException as e:
        print(f"Error getting playlist tracks: {e}")
        return []

def create_playlist(access_token: str, user_id: str, name: str, description: str = "") -> Optional[Dict[str, Any]]:
    """Create a new Spotify playlist"""
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    
    data = {
        'name': name,
        'description': description,
        'public': False
    }
    
    try:
        response = requests.post(f"{SPOTIFY_API_URL}/users/{user_id}/playlists", 
                               headers=headers, json=data)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"Error creating playlist: {e}")
        return None

def add_tracks_to_playlist(access_token: str, playlist_id: str, track_uris: List[str]) -> bool:
    """Add tracks to a Spotify playlist"""
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    
    # Spotify allows max 100 tracks per request
    chunk_size = 100
    
    try:
        for i in range(0, len(track_uris), chunk_size):
            chunk = track_uris[i:i + chunk_size]
            data = {'uris': chunk}
            
            response = requests.post(f"{SPOTIFY_API_URL}/playlists/{playlist_id}/tracks",
                                   headers=headers, json=data)
            response.raise_for_status()
        
        return True
    except requests.RequestException as e:
        print(f"Error adding tracks to playlist: {e}")
        return False

def search_track(access_token: str, query: str) -> Optional[Dict[str, Any]]:
    """Search for a track on Spotify"""
    headers = {'Authorization': f'Bearer {access_token}'}
    params = {
        'q': query,
        'type': 'track',
        'limit': 1
    }
    
    try:
        response = requests.get(f"{SPOTIFY_API_URL}/search", headers=headers, params=params)
        response.raise_for_status()
        data = response.json()
        
        tracks = data.get('tracks', {}).get('items', [])
        return tracks[0] if tracks else None
    except requests.RequestException as e:
        print(f"Error searching track: {e}")
        return None

def link_spotify_account(user_id: int, access_token: str) -> bool:
    """Link Spotify account to user"""
    # Get user profile
    profile = get_user_profile(access_token)
    if not profile:
        return False
    
    # Get Spotify platform
    spotify_platform = get_platform_by_name('Spotify')
    if not spotify_platform:
        return False
    
    # Check if account already linked
    existing_accounts = get_user_accounts(user_id)
    for account in existing_accounts:
        if (account['platform_id'] == spotify_platform['platform_id'] and 
            account['username_on_platform'] == profile['id']):
            # Update token
            db.update('UserPlatformAccount', 
                     {'auth_token': access_token},
                     {'account_id': account['account_id']})
            return True
    
    # Create new account link
    create_user_platform_account(
        user_id=user_id,
        platform_id=spotify_platform['platform_id'],
        username=profile['id'],
        auth_token=access_token
    )
    
    return True
