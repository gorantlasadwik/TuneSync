from flask import render_template, request, redirect, url_for, session, flash, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
import logging
from app import app
from database import (
    get_user_by_email, get_user_by_id, create_user, get_user_accounts,
    get_playlists_by_account, create_playlist, get_playlist_songs,
    create_sync_log, get_platform_by_name, add_song_to_playlist,
    get_or_create_song, add_platform_song, db
)
from spotify_auth import (
    get_spotify_auth_url, exchange_code_for_token, link_spotify_account,
    get_user_playlists, get_playlist_tracks
)
from youtube_music import (
    link_youtube_music_account, get_public_playlists, setup_ytmusic,
    sync_to_youtube_music
)

def _get_spotify_playlists(account):
    """Helper to get Spotify playlists."""
    try:
        spotify_playlists = get_user_playlists(account['auth_token'])
        return [{
            'id': p['id'],
            'name': p['name'],
            'description': p.get('description', ''),
            'track_count': p.get('tracks', {}).get('total', 0),
            'platform': 'Spotify',
            'account_id': account['userplatformaccount_id']
        } for p in spotify_playlists]
    except Exception as e:
        logging.error(f"Error fetching Spotify playlists for account {account['userplatformaccount_id']}: {e}")
        return []

def _get_youtube_music_playlists(account):
    """Helper to get YouTube Music playlists."""
    try:
        ytmusic = setup_ytmusic()
        if ytmusic:
            # Note: ytmusicapi doesn't support getting a user's library playlists without authentication
            # This is fetching public playlists as a demonstration
            yt_playlists = get_public_playlists(ytmusic, "Popular Music")
            return [{
                'id': p['playlistId'],
                'name': p['title'],
                'description': p.get('description', ''),
                'track_count': p.get('trackCount', 0),
                'platform': 'YouTube Music',
                'account_id': account['userplatformaccount_id']
            } for p in yt_playlists[:10]]
    except Exception as e:
        logging.error(f"Error fetching YouTube Music playlists for account {account['userplatformaccount_id']}: {e}")
    return []

@app.route('/')
def index():
    """Home page"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user = get_user_by_id(session['user_id'])
    if not user:
        session.clear()
        return redirect(url_for('login'))
    
    # Get user's linked accounts
    accounts = get_user_accounts(session['user_id'])
    linked_platform_ids = {acc['platform_id'] for acc in accounts}

    spotify_platform = get_platform_by_name('Spotify')
    youtube_platform = get_platform_by_name('YouTube Music')

    spotify_linked = spotify_platform and spotify_platform['platform_id'] in linked_platform_ids
    youtube_linked = youtube_platform and youtube_platform['platform_id'] in linked_platform_ids
    
    return render_template('index.html', user=user, 
                         spotify_linked=spotify_linked, 
                         youtube_linked=youtube_linked)

@app.route('/login', methods=['GET', 'POST'])
def login():
    """User login"""
    if request.method == 'POST':
        email = request.form.get('email', '')
        password = request.form.get('password', '')
        
        if not email or not password:
            flash('Email and password are required', 'error')
            return render_template('login.html')
        
        user = get_user_by_email(email)
        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['user_id']
            session['user_name'] = user['name']
            return redirect(url_for('index'))
        else:
            flash('Invalid email or password', 'error')
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    """User registration"""
    if request.method == 'POST':
        name = request.form.get('name', '')
        email = request.form.get('email', '')
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        
        if not all([name, email, password, confirm_password]):
            flash('All fields are required', 'error')
            return render_template('register.html')
        
        if password != confirm_password:
            flash('Passwords do not match', 'error')
            return render_template('register.html')
        
        if get_user_by_email(email):
            flash('Email already registered', 'error')
            return render_template('register.html')
        
        password_hash = generate_password_hash(password)
        user_id = create_user(name, email, password_hash)
        
        session['user_id'] = user_id
        session['user_name'] = name
        flash('Registration successful', 'success')
        return redirect(url_for('index'))
    
    return render_template('register.html')

@app.route('/logout')
def logout():
    """User logout"""
    session.clear()
    flash('Logged out successfully', 'success')
    return redirect(url_for('login'))

@app.route('/link-spotify')
def link_spotify():
    """Start Spotify OAuth process"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    auth_url = get_spotify_auth_url(state=str(session['user_id']))
    logging.info(f"Redirecting to Spotify auth URL: {auth_url}")
    return redirect(auth_url)

@app.route('/test-oauth')
def test_oauth():
    """Manual OAuth testing page"""
    if 'user_id' not in session:
        flash('Please login first', 'error')
        return redirect(url_for('login'))
    
    auth_url = get_spotify_auth_url(state=str(session['user_id']))
    return render_template('test_oauth.html', auth_url=auth_url)

@app.route('/manual-oauth', methods=['POST'])
def manual_oauth():
    """Manual OAuth completion for testing"""
    code = request.form.get('code', '').strip()
    user_id = request.form.get('user_id')
    
    if not code:
        flash('Please provide the authorization code', 'error')
        return redirect(url_for('test_oauth'))
    
    if not user_id:
        flash('Invalid user session', 'error')
        return redirect(url_for('login'))
    
    try:
        # Exchange code for token
        token_data = exchange_code_for_token(code)
        if not token_data:
            flash('Failed to exchange code for token. Make sure the code is copied correctly.', 'error')
            return redirect(url_for('test_oauth'))
        
        # Link account
        if link_spotify_account(int(user_id), token_data['access_token']):
            flash('Spotify account linked successfully!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Failed to link Spotify account', 'error')
            return redirect(url_for('test_oauth'))
            
    except Exception as e:
        logging.error(f"Manual OAuth error: {e}")
        flash(f'OAuth error: {str(e)}', 'error')
        return redirect(url_for('test_oauth'))

@app.route('/api/spotify/callback', methods=['GET', 'POST'])
def spotify_callback():
    """Handle Spotify OAuth callback"""
    logging.info(f"Spotify callback received with args: {request.args}")
    
    code = request.args.get('code')
    state = request.args.get('state')
    error = request.args.get('error')
    
    if error:
        logging.error(f"Spotify authorization error: {error}")
        flash(f'Spotify authorization failed: {error}', 'error')
        return redirect(url_for('index'))
    
    if not code or not state:
        logging.error("Missing code or state in callback")
        flash('Invalid callback parameters', 'error')
        return redirect(url_for('index'))
    
    try:
        user_id = int(state)
        logging.info(f"Processing callback for user_id: {user_id}")
    except ValueError:
        logging.error(f"Invalid state parameter: {state}")
        flash('Invalid state parameter', 'error')
        return redirect(url_for('index'))
    
    # Exchange code for token
    token_data = exchange_code_for_token(code)
    if not token_data:
        logging.error("Failed to exchange code for token")
        flash('Failed to get access token', 'error')
        return redirect(url_for('index'))
    
    # Link account
    if link_spotify_account(user_id, token_data['access_token']):
        logging.info("Spotify account linked successfully")
        flash('Spotify account linked successfully', 'success')
    else:
        logging.error("Failed to link Spotify account")
        flash('Failed to link Spotify account', 'error')
    
    return redirect(url_for('index'))

@app.route('/link-youtube-music', methods=['POST'])
def link_youtube_music():
    """Link YouTube Music account (public access)"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    if link_youtube_music_account(session['user_id']):
        flash('YouTube Music access enabled', 'success')
    else:
        flash('Failed to enable YouTube Music access', 'error')
    
    return redirect(url_for('index'))

@app.route('/playlists')
def playlists():
    """Show user playlists"""
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user = get_user_by_id(session['user_id'])
    accounts = get_user_accounts(session['user_id'])
    
    spotify_platform = get_platform_by_name('Spotify')
    youtube_platform = get_platform_by_name('YouTube Music')

    playlists_data = []
    for account in accounts:
        if spotify_platform and account['platform_id'] == spotify_platform['platform_id']:
            playlists_data.extend(_get_spotify_playlists(account))
        elif youtube_platform and account['platform_id'] == youtube_platform['platform_id']:
            playlists_data.extend(_get_youtube_music_playlists(account))

    return render_template('playlists.html', user=user, playlists=playlists_data)

@app.route('/sync')
def sync():
    """Sync page"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user = get_user_by_id(session['user_id'])
    accounts = get_user_accounts(session['user_id'])
    
    return render_template('sync.html', user=user, accounts=accounts)

def _get_songs_from_spotify_playlist(auth_token, playlist_id):
    """Fetches songs from a Spotify playlist."""
    try:
        spotify_tracks = get_playlist_tracks(auth_token, playlist_id)
        if spotify_tracks is None:
            return None
        return [{
            'name': track['name'],
            'artists': track['artists'],
            'album': track['album'],
            'duration_ms': track['duration_ms']
        } for track in spotify_tracks]
    except Exception as e:
        logging.error(f"Error fetching Spotify playlist tracks: {e}")
        return None

def _sync_to_youtube_and_log(songs, youtube_platform_id):
    """Syncs songs to YouTube Music and logs them in the database."""
    sync_result = sync_to_youtube_music(songs)
    if not sync_result['success']:
        return {'success': False, 'error': sync_result.get('error', 'Sync failed')}

    for found_song_data in sync_result['found_songs']:
        original_song = found_song_data['original']
        youtube_song = found_song_data['youtube_music']

        song_id = get_or_create_song(
            title=original_song['name'],
            artist=', '.join(original_song['artists']),
            album=original_song['album'],
            duration=original_song.get('duration_ms', 0) // 1000
        )

        add_platform_song(
            song_id=song_id,
            platform_id=youtube_platform_id,
            platform_specific_id=youtube_song['videoId']
        )

    return {
        'success': True,
        'songs_added': sync_result['total_found'],
        'songs_not_found': sync_result['total_not_found']
    }

@app.route('/api/sync', methods=['POST'])
def api_sync():
    """Sync playlists between platforms"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'error': 'Not logged in'}), 401
    
    data = request.get_json()
    if not data:
        return jsonify({'success': False, 'error': 'Invalid JSON data'}), 400
    
    source_account_id = data.get('source_account_id')
    destination_account_id = data.get('destination_account_id')
    playlist_id_str = data.get('playlist_id') # This is spotify's playlist id
    
    if not all([source_account_id, destination_account_id, playlist_id_str]):
        return jsonify({'success': False, 'error': 'Missing required parameters'}), 400
    
    try:
        user_id = session['user_id']
        accounts = get_user_accounts(user_id)

        source_account = next((acc for acc in accounts if acc['userplatformaccount_id'] == int(source_account_id)), None)
        dest_account = next((acc for acc in accounts if acc['userplatformaccount_id'] == int(destination_account_id)), None)
        
        if not source_account or not dest_account:
            return jsonify({'success': False, 'error': 'Invalid account IDs'}), 400

        spotify_platform = get_platform_by_name('Spotify')
        youtube_platform = get_platform_by_name('YouTube Music')
        
        songs = []
        if spotify_platform and source_account['platform_id'] == spotify_platform['platform_id']:
            songs = _get_songs_from_spotify_playlist(source_account['auth_token'], playlist_id_str)

        if songs is None:
            return jsonify({'success': False, 'error': 'Failed to fetch songs from source playlist'}), 500
        if not songs:
            return jsonify({'success': False, 'error': 'No songs found in source playlist'}), 400

        result = {'success': False, 'error': 'Destination platform not supported'}
        if youtube_platform and dest_account['platform_id'] == youtube_platform['platform_id']:
            result = _sync_to_youtube_and_log(songs, youtube_platform['platform_id'])

        if not result['success']:
            return jsonify(result), 500

        # For now, we will not create a playlist in our DB, so playlist_id is 0.
        # This is a limitation of the current design.
        create_sync_log(
            user_id=user_id,
            source_account_id=int(source_account_id),
            destination_account_id=int(destination_account_id),
            playlist_id=0, # Hardcoded, as we don't store a local copy of the playlist
            total_songs=len(songs),
            songs_added=result['songs_added'],
            songs_removed=0
        )
        
        return jsonify({
            'success': True,
            'message': f"Sync completed: {result['songs_added']} songs matched, {result['songs_not_found']} not found",
            'songs_added': result['songs_added'],
            'songs_not_found': result['songs_not_found']
        })

    except Exception as e:
        logging.error(f"Sync error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500
