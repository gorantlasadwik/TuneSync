# SyncTunes

A web application for synchronizing playlists between Spotify and YouTube Music.

## Features

- **User Authentication**: Secure user registration and login system
- **Platform Integration**: Connect Spotify and YouTube Music accounts
- **Playlist Management**: View playlists from all connected platforms
- **Playlist Synchronization**: Sync playlists between Spotify and YouTube Music
- **Sync Logging**: Track sync history and statistics
- **In-Memory Database**: Custom SQL schema implementation in server memory

## Technology Stack

- **Backend**: Python 3, Flask
- **Database**: In-memory database with SQL schema structure
- **Frontend**: HTML5, CSS3, Vanilla JavaScript
- **APIs**: Spotify Web API, YouTube Music API (ytmusicapi)
- **Authentication**: Spotify OAuth 2.0

## Installation

1. Clone the repository and navigate to the project directory
2. Install required dependencies:
   ```bash
   pip install flask requests ytmusicapi python-dotenv werkzeug
   ```

3. Set up environment variables in `.env` file:
   ```
   SPOTIFY_CLIENT_ID= Get it from Spotify for Developers
   SPOTIFY_CLIENT_SECRET= Get it from Spotify for Developers
   REDIRECT_URI=http://localhost:5000/api/spotify/callback
   SESSION_SECRET=synctunes-secret-key-2025-production
   ```

## Running the Application

1. Start the Flask server:
   ```bash
   python main.py
   ```

2. Open your web browser and navigate to `http://localhost:5000`

3. Register a new account or login with existing credentials

4. Link your Spotify account using OAuth 2.0

5. Enable YouTube Music access for searching and matching songs

6. Start syncing playlists between platforms

## Database Schema

The application implements a complete SQL schema in server memory:

- **User_**: User accounts and authentication
- **Admin**: Administrator accounts
- **Platform**: Music streaming platform information
- **UserPlatformAccount**: Links users to their platform accounts
- **Playlist**: Playlist information and metadata
- **Song**: Song catalog with title, artist, album, duration
- **PlatformSong**: Platform-specific song mappings
- **PlaylistSong**: Many-to-many relationship between playlists and songs
- **SyncLog**: Detailed logging of sync operations

## API Endpoints

- `GET /` - Home page with platform linking options
- `GET /login` - User login page
- `POST /login` - Process login credentials
- `GET /register` - User registration page
- `POST /register` - Process user registration
- `GET /logout` - User logout
- `GET /link-spotify` - Initiate Spotify OAuth flow
- `GET /api/spotify/callback` - Spotify OAuth callback
- `POST /link-youtube-music` - Enable YouTube Music access
- `GET /playlists` - View all user playlists
- `GET /sync` - Playlist synchronization interface
- `POST /api/sync` - Process playlist synchronization

## How It Works

### Spotify Integration
1. Users authenticate via Spotify OAuth 2.0
2. Access tokens are stored in UserPlatformAccount table
3. Playlists and tracks are fetched using Spotify Web API
4. Songs are stored with platform-specific IDs

### YouTube Music Integration
1. Uses ytmusicapi library for public access
2. Searches for songs by title, artist, and album
3. Matches Spotify tracks with YouTube Music equivalents
4. Provides sync statistics and detailed results

### Sync Process
1. Select source playlist (Spotify) and destination platform (YouTube Music)
2. Fetch all tracks from source playlist
3. Search for each track on destination platform
4. Log successful matches and failed searches
5. Store sync results in SyncLog table

## Security Features

- Password hashing using Werkzeug security
- Session management with secure secret keys
- OAuth 2.0 integration for external platform access
- Input validation and error handling
- Protection against common web vulnerabilities

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

This project is for educational and personal use. Please ensure compliance with Spotify and YouTube Music API terms of service.
