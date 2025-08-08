#!/usr/bin/env python3
"""
Alternative solution for testing SyncTunes without external tunnels
Creates a simple testing interface that simulates the OAuth flow
"""

from flask import Flask, request, render_template_string, redirect, url_for, session, flash
import os
import sys
sys.path.append('.')
from app import app as main_app
from spotify_auth import SPOTIFY_CLIENT_ID, get_spotify_auth_url
import logging

# Create test route that shows the OAuth URL for manual testing
@main_app.route('/test-oauth')
def test_oauth():
    """Test page for Spotify OAuth without external redirect"""
    if 'user_id' not in session:
        flash('Please login first', 'error')
        return redirect(url_for('login'))
    
    auth_url = get_spotify_auth_url(state=str(session['user_id']))
    
    test_html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>SyncTunes - OAuth Testing</title>
        <style>
            body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; 
                   max-width: 800px; margin: 0 auto; padding: 20px; background: #fff; color: #000; }
            .container { background: #f9f9f9; padding: 20px; border-radius: 8px; margin: 20px 0; }
            .auth-url { background: #000; color: #fff; padding: 15px; border-radius: 4px; 
                       word-break: break-all; font-family: monospace; }
            .steps { background: #fff; padding: 15px; border: 1px solid #ddd; border-radius: 4px; }
            .step { margin: 10px 0; padding: 10px; background: #f5f5f5; border-left: 4px solid #000; }
            .btn { background: #000; color: #fff; padding: 10px 20px; text-decoration: none; 
                   border-radius: 4px; display: inline-block; margin: 10px 0; }
            .btn:hover { background: #333; }
        </style>
    </head>
    <body>
        <h1>🎵 SyncTunes - OAuth Testing</h1>
        
        <div class="container">
            <h2>Manual OAuth Testing (Works Around External URL Issues)</h2>
            <p>Since external URLs aren't working, here's how to test Spotify OAuth manually:</p>
            
            <div class="steps">
                <div class="step">
                    <strong>Step 1:</strong> Click the Spotify authorization link below
                </div>
                <div class="step">
                    <strong>Step 2:</strong> Authorize the app in Spotify
                </div>
                <div class="step">
                    <strong>Step 3:</strong> You'll be redirected to the configured URL with a 'code' parameter
                </div>
                <div class="step">
                    <strong>Step 4:</strong> Copy the 'code' from the URL and paste it in the form below
                </div>
            </div>
            
            <h3>Spotify Authorization URL:</h3>
            <div class="auth-url">{{ auth_url }}</div>
            <a href="{{ auth_url }}" target="_blank" class="btn">🔗 Authorize with Spotify</a>
            
            <h3>Manual Code Entry:</h3>
            <form method="post" action="/manual-oauth">
                <input type="hidden" name="user_id" value="{{ session.user_id }}">
                <p>After authorizing, paste the 'code' parameter here:</p>
                <input type="text" name="code" placeholder="Paste authorization code here" 
                       style="width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 4px;">
                <br>
                <button type="submit" class="btn" style="border: none; cursor: pointer;">
                    ✅ Complete OAuth
                </button>
            </form>
        </div>
        
        <a href="/" class="btn">← Back to Dashboard</a>
    </body>
    </html>
    """
    
    return render_template_string(test_html, auth_url=auth_url, session=session)

@main_app.route('/manual-oauth', methods=['POST'])
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
        # Import here to avoid circular imports
        from spotify_auth import exchange_code_for_token, link_spotify_account
        
        # Exchange code for token
        token_data = exchange_code_for_token(code)
        if not token_data:
            flash('Failed to exchange code for token. Check if code is valid.', 'error')
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

if __name__ == '__main__':
    print("Starting SyncTunes with manual OAuth testing...")
    main_app.run(host='0.0.0.0', port=5000, debug=True)