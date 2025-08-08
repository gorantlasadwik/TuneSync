from datetime import datetime
import threading
from typing import Dict, List, Optional, Any

# Thread-safe in-memory database implementation
class InMemoryDatabase:
    def __init__(self):
        self.lock = threading.RLock()
        self.tables = {
            'User_': [],
            'Admin': [],
            'Platform': [],
            'UserPlatformAccount': [],
            'Playlist': [],
            'Song': [],
            'PlatformSong': [],
            'PlaylistSong': [],
            'SyncLog': []
        }
        self.auto_increment_counters = {
            'User_': 1,
            'Admin': 1,
            'Platform': 1,
            'UserPlatformAccount': 1,
            'Playlist': 1,
            'Song': 1,
            'PlatformSong': 1,
            'SyncLog': 1
        }
        
    def insert(self, table: str, data: Dict[str, Any]) -> int:
        """Insert a record and return the auto-generated ID"""
        with self.lock:
            # Generate auto-increment ID
            if table in self.auto_increment_counters:
                id_field = f"{table.lower()}_id" if table != 'User_' else 'user_id'
                if table == 'Admin':
                    id_field = 'admin_id'
                
                record = data.copy()
                record[id_field] = self.auto_increment_counters[table]
                self.auto_increment_counters[table] += 1
                
                self.tables[table].append(record)
                return record[id_field]
            else:
                # For tables without auto-increment
                self.tables[table].append(data)
                return 0
    
    def select(self, table: str, where: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Select records from a table"""
        with self.lock:
            records = self.tables.get(table, [])
            if where is None:
                return records.copy()
            
            filtered = []
            for record in records:
                match = True
                for key, value in where.items():
                    if record.get(key) != value:
                        match = False
                        break
                if match:
                    filtered.append(record)
            return filtered
    
    def update(self, table: str, data: Dict[str, Any], where: Dict[str, Any]) -> int:
        """Update records in a table"""
        with self.lock:
            updated_count = 0
            records = self.tables.get(table, [])
            for record in records:
                match = True
                for key, value in where.items():
                    if record.get(key) != value:
                        match = False
                        break
                if match:
                    record.update(data)
                    updated_count += 1
            return updated_count
    
    def delete(self, table: str, where: Dict[str, Any]) -> int:
        """Delete records from a table"""
        with self.lock:
            records = self.tables.get(table, [])
            to_remove = []
            for i, record in enumerate(records):
                match = True
                for key, value in where.items():
                    if record.get(key) != value:
                        match = False
                        break
                if match:
                    to_remove.append(i)
            
            # Remove in reverse order to maintain indices
            for i in reversed(to_remove):
                records.pop(i)
            
            return len(to_remove)

# Global database instance
db = InMemoryDatabase()

def init_database():
    """Initialize the database with default platforms"""
    # Insert default platforms
    db.insert('Platform', {
        'platform_name': 'Spotify',
        'api_details': 'Spotify Web API with OAuth 2.0'
    })
    
    db.insert('Platform', {
        'platform_name': 'YouTube Music',
        'api_details': 'YouTube Music API via ytmusicapi'
    })

def get_user_by_email(email: str) -> Optional[Dict[str, Any]]:
    """Get user by email"""
    users = db.select('User_', {'email': email})
    return users[0] if users else None

def get_user_by_id(user_id: int) -> Optional[Dict[str, Any]]:
    """Get user by ID"""
    users = db.select('User_', {'user_id': user_id})
    return users[0] if users else None

def create_user(name: str, email: str, password_hash: str) -> int:
    """Create a new user"""
    return db.insert('User_', {
        'name': name,
        'email': email,
        'password': password_hash
    })

def get_platform_by_name(platform_name: str) -> Optional[Dict[str, Any]]:
    """Get platform by name"""
    platforms = db.select('Platform', {'platform_name': platform_name})
    return platforms[0] if platforms else None

def get_user_accounts(user_id: int) -> List[Dict[str, Any]]:
    """Get all platform accounts for a user"""
    return db.select('UserPlatformAccount', {'user_id': user_id})

def create_user_platform_account(user_id: int, platform_id: int, username: str, auth_token: str) -> int:
    """Create a user platform account"""
    return db.insert('UserPlatformAccount', {
        'user_id': user_id,
        'platform_id': platform_id,
        'username_on_platform': username,
        'auth_token': auth_token
    })

def get_playlists_by_account(account_id: int) -> List[Dict[str, Any]]:
    """Get all playlists for an account"""
    return db.select('Playlist', {'account_id': account_id})

def create_playlist(account_id: int, name: str, description: str = "") -> int:
    """Create a new playlist"""
    return db.insert('Playlist', {
        'account_id': account_id,
        'name': name,
        'description': description,
        'last_updated': datetime.now().isoformat()
    })

def get_or_create_song(title: str, artist: str, album: str = "", duration: int = 0) -> int:
    """Get existing song or create new one"""
    songs = db.select('Song', {'title': title, 'artist': artist, 'album': album})
    if songs:
        return songs[0]['song_id']
    
    return db.insert('Song', {
        'title': title,
        'artist': artist,
        'album': album,
        'duration': duration
    })

def add_platform_song(song_id: int, platform_id: int, platform_specific_id: str) -> int:
    """Add platform-specific song mapping"""
    # Check if mapping already exists
    existing = db.select('PlatformSong', {
        'song_id': song_id,
        'platform_id': platform_id,
        'platform_specific_id': platform_specific_id
    })
    if existing:
        return existing[0]['platform_song_id']
    
    return db.insert('PlatformSong', {
        'song_id': song_id,
        'platform_id': platform_id,
        'platform_specific_id': platform_specific_id
    })

def add_song_to_playlist(playlist_id: int, song_id: int) -> None:
    """Add song to playlist"""
    # Check if song is already in playlist
    existing = db.select('PlaylistSong', {'playlist_id': playlist_id, 'song_id': song_id})
    if not existing:
        db.insert('PlaylistSong', {
            'playlist_id': playlist_id,
            'song_id': song_id,
            'added_at': datetime.now().isoformat()
        })

def create_sync_log(user_id: int, source_account_id: int, destination_account_id: int, 
                   playlist_id: int, total_songs: int, songs_added: int, songs_removed: int) -> int:
    """Create a sync log entry"""
    return db.insert('SyncLog', {
        'user_id': user_id,
        'source_account_id': source_account_id,
        'destination_account_id': destination_account_id,
        'playlist_id': playlist_id,
        'total_songs_synced': total_songs,
        'songs_added': songs_added,
        'songs_removed': songs_removed,
        'timestamp': datetime.now().isoformat()
    })

def get_playlist_songs(playlist_id: int) -> List[Dict[str, Any]]:
    """Get all songs in a playlist with song details"""
    playlist_songs = db.select('PlaylistSong', {'playlist_id': playlist_id})
    songs_with_details = []
    
    for ps in playlist_songs:
        songs = db.select('Song', {'song_id': ps['song_id']})
        if songs:
            song_data = songs[0].copy()
            song_data['added_at'] = ps['added_at']
            songs_with_details.append(song_data)
    
    return songs_with_details
