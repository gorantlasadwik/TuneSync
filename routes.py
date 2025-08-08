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
    
    spotify_platform = get_platform_by_name('Spotify')
    spotify_linked = any(account for account in accounts 
                        if spotify_platform and 
                        account['platform_id'] == spotify_platform['platform_id'])
    
    youtube_platform = get_platform_by_name('YouTube Music')
    youtube_linked = any(account for account in accounts 
                        if youtube_platform and 
                        account['platform_id'] == youtube_platform['platform_id'])
    
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

@app.route('/api/spotify/callback')
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
    
    playlists_data = []
    
    for account in accounts:
        platform = None
        spotify_platform = get_platform_by_name('Spotify')
        youtube_platform = get_platform_by_name('YouTube Music')
        
        if spotify_platform and account['platform_id'] == spotify_platform['platform_id']:
            platform = 'Spotify'
        elif youtube_platform and account['platform_id'] == youtube_platform['platform_id']:
            platform = 'YouTube Music'
        
        if platform == 'Spotify':
            try:
                spotify_platform = get_platform_by_name('Spotify')
                if spotify_platform and account['platform_id'] == spotify_platform['platform_id']:
                    spotify_playlists = get_user_playlists(account['auth_token'])
                    for playlist in spotify_playlists:
                        playlists_data.append({
                            'id': playlist['id'],
                            'name': playlist['name'],
                            'description': playlist.get('description', ''),
                            'track_count': playlist.get('tracks', {}).get('total', 0),
                            'platform': 'Spotify',
                            'account_id': account['account_id']
                        })
            except Exception as e:
                logging.error(f"Error fetching Spotify playlists: {e}")
        
        elif platform == 'YouTube Music':
            try:
                youtube_platform = get_platform_by_name('YouTube Music')
                if youtube_platform and account['platform_id'] == youtube_platform['platform_id']:
                    ytmusic = setup_ytmusic()
                    if ytmusic:
                        yt_playlists = get_public_playlists(ytmusic, "Popular Music")
                        for playlist in yt_playlists[:10]:  # Limit to 10 public playlists
                            playlists_data.append({
                                'id': playlist['playlistId'],
                                'name': playlist['title'],
                                'description': playlist.get('description', ''),
                                'track_count': playlist.get('trackCount', 0),
                                'platform': 'YouTube Music',
                                'account_id': account['account_id']
                            })
            except Exception as e:
                logging.error(f"Error fetching YouTube Music playlists: {e}")
    
    return render_template('playlists.html', user=user, playlists=playlists_data)

@app.route('/sync')
def sync():
    """Sync page"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user = get_user_by_id(session['user_id'])
    accounts = get_user_accounts(session['user_id'])
    
    return render_template('sync.html', user=user, accounts=accounts)

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
    playlist_id = data.get('playlist_id')
    
    if not all([source_account_id, destination_account_id, playlist_id]):
        return jsonify({'success': False, 'error': 'Missing required parameters'}), 400
    
    try:
        # Get accounts
        accounts = get_user_accounts(session['user_id'])
        source_account = next((acc for acc in accounts if acc['account_id'] == int(source_account_id)), None)
        dest_account = next((acc for acc in accounts if acc['account_id'] == int(destination_account_id)), None)
        
        if not source_account or not dest_account:
            return jsonify({'success': False, 'error': 'Invalid account IDs'}), 400
        
        # Get platform information
        spotify_platform = get_platform_by_name('Spotify')
        youtube_platform = get_platform_by_name('YouTube Music')
        
        songs = []
        
        # Get tracks from source platform
        if spotify_platform and source_account['platform_id'] == spotify_platform['platform_id']:
            # Get tracks from Spotify
            spotify_tracks = get_playlist_tracks(source_account['auth_token'], playlist_id)
            songs = [{
                'name': track['name'],
                'artists': track['artists'],
                'album': track['album'],
                'duration_ms': track['duration_ms']
            } for track in spotify_tracks]
        
        if not songs:
            return jsonify({'success': False, 'error': 'No songs found in source playlist'}), 400
        
        songs_added = 0
        songs_not_found = 0
        
        # Sync to destination platform
        if youtube_platform and dest_account['platform_id'] == youtube_platform['platform_id']:
            # Sync to YouTube Music (search and match)
            sync_result = sync_to_youtube_music(songs)
            if sync_result['success']:
                songs_added = sync_result['total_found']
                songs_not_found = sync_result['total_not_found']
                
                # Store songs in database
                for found_song_data in sync_result['found_songs']:
                    original_song = found_song_data['original']
                    youtube_song = found_song_data['youtube_music']
                    
                    # Create/get song record
                    song_id = get_or_create_song(
                        title=original_song['name'],
                        artist=', '.join(original_song['artists']),
                        album=original_song['album'],
                        duration=original_song.get('duration_ms', 0) // 1000
                    )
                    
                    # Add platform song mapping for YouTube Music
                    add_platform_song(
                        song_id=song_id,
                        platform_id=youtube_platform['platform_id'],
                        platform_specific_id=youtube_song['videoId']
                    )
            else:
                return jsonify({'success': False, 'error': sync_result.get('error', 'Sync failed')}), 500
        
        # Create sync log
        create_sync_log(
            user_id=session['user_id'],
            source_account_id=source_account_id,
            destination_account_id=destination_account_id,
            playlist_id=0,  # We don't create actual playlists on YouTube Music
            total_songs=len(songs),
            songs_added=songs_added,
            songs_removed=0
        )
        
        return jsonify({
            'success': True,
            'message': f'Sync completed: {songs_added} songs matched, {songs_not_found} not found',
            'songs_added': songs_added,
            'songs_not_found': songs_not_found
        })
        
    except Exception as e:
        logging.error(f"Sync error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500
