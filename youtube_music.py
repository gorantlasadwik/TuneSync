import os
from typing import Optional, Dict, Any, List
from ytmusicapi import YTMusic
from database import db, get_platform_by_name, create_user_platform_account, get_user_accounts
import logging

def setup_ytmusic() -> Optional[YTMusic]:
    """Setup YTMusic client"""
    try:
        # For public access, we don't need authentication headers
        # This allows us to search and access public playlists
        ytmusic = YTMusic()
        return ytmusic
    except Exception as e:
        logging.error(f"Error setting up YTMusic: {e}")
        return None

def search_song(ytmusic: YTMusic, query: str) -> Optional[Dict[str, Any]]:
    """Search for a song on YouTube Music"""
    try:
        results = ytmusic.search(query, filter="songs", limit=1)
        if results:
            song = results[0]
            return {
                'videoId': song.get('videoId'),
                'title': song.get('title'),
                'artists': [artist.get('name') for artist in song.get('artists', [])],
                'album': song.get('album', {}).get('name', '') if song.get('album') else '',
                'duration': song.get('duration_seconds', 0)
            }
    except Exception as e:
        logging.error(f"Error searching song on YouTube Music: {e}")
    
    return None

def get_public_playlists(ytmusic: YTMusic, query: str = "Top Songs") -> List[Dict[str, Any]]:
    """Get public playlists from YouTube Music"""
    try:
        results = ytmusic.search(query, filter="playlists", limit=10)
        playlists = []
        
        for playlist in results:
            playlists.append({
                'playlistId': playlist.get('browseId'),
                'title': playlist.get('title'),
                'description': playlist.get('description', ''),
                'trackCount': playlist.get('videoCount', 0),
                'thumbnails': playlist.get('thumbnails', [])
            })
        
        return playlists
    except Exception as e:
        logging.error(f"Error getting public playlists: {e}")
        return []

def get_playlist_tracks(ytmusic: YTMusic, playlist_id: str) -> List[Dict[str, Any]]:
    """Get tracks from a YouTube Music playlist"""
    try:
        playlist = ytmusic.get_playlist(playlist_id, limit=None)
        tracks = []
        
        for track in playlist.get('tracks', []):
            if track.get('videoId'):
                tracks.append({
                    'videoId': track['videoId'],
                    'title': track.get('title'),
                    'artists': [artist.get('name') for artist in track.get('artists', [])],
                    'album': track.get('album', {}).get('name', '') if track.get('album') else '',
                    'duration': track.get('duration_seconds', 0)
                })
        
        return tracks
    except Exception as e:
        logging.error(f"Error getting playlist tracks: {e}")
        return []

def create_search_query(title: str, artists: List[str], album: str = "") -> str:
    """Create a search query for YouTube Music"""
    artist_str = " ".join(artists) if artists else ""
    query_parts = [part for part in [title, artist_str] if part.strip()]
    return " ".join(query_parts)

def link_youtube_music_account(user_id: int, username: str = "public_access") -> bool:
    """Link YouTube Music account to user (public access)"""
    # Get YouTube Music platform
    yt_platform = get_platform_by_name('YouTube Music')
    if not yt_platform:
        return False
    
    # Check if account already linked
    existing_accounts = get_user_accounts(user_id)
    for account in existing_accounts:
        if (account['platform_id'] == yt_platform['platform_id'] and 
            account['username_on_platform'] == username):
            return True
    
    # Create new account link (public access)
    create_user_platform_account(
        user_id=user_id,
        platform_id=yt_platform['platform_id'],
        username=username,
        auth_token="public_access"
    )
    
    return True

def sync_to_youtube_music(songs: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Sync songs to YouTube Music (search and match)"""
    ytmusic = setup_ytmusic()
    if not ytmusic:
        return {"success": False, "error": "Failed to setup YouTube Music client"}
    
    found_songs = []
    not_found = []
    
    for song in songs:
        # Create search query
        artists = song.get('artists', [])
        if isinstance(artists, str):
            artists = [artists]
        
        query = create_search_query(
            title=song.get('name', song.get('title', '')),
            artists=artists,
            album=song.get('album', '')
        )
        
        # Search for the song
        found_song = search_song(ytmusic, query)
        if found_song:
            found_songs.append({
                'original': song,
                'youtube_music': found_song
            })
        else:
            not_found.append(song)
    
    return {
        "success": True,
        "found_songs": found_songs,
        "not_found": not_found,
        "total_found": len(found_songs),
        "total_not_found": len(not_found)
    }
