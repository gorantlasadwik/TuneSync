#!/usr/bin/env python3
"""
Demonstrate the complete OAuth solution working
"""
import sys
sys.path.append('.')

from database import create_user, get_user_by_email
from werkzeug.security import generate_password_hash
import logging

logging.basicConfig(level=logging.INFO)

def create_demo_account():
    """Create a demo account and simulate Spotify connection"""
    print("Creating demo account with simulated Spotify connection...")
    
    # Create test user
    email = "demo@example.com"
    password = "demo123"
    
    # Check if user exists
    user = get_user_by_email(email)
    if not user:
        print(f"Creating user: {email}")
        password_hash = generate_password_hash(password)
        user_id = create_user("Demo User", email, password_hash)
        print(f"Created user with ID: {user_id}")
    else:
        user_id = user['user_id']
        print(f"User already exists with ID: {user_id}")
    
    return user_id, email, password

def show_oauth_instructions():
    """Show instructions for OAuth testing"""
    user_id, email, password = create_demo_account()
    
    print("\n" + "="*60)
    print("🎵 SyncTunes OAuth Testing Instructions")
    print("="*60)
    
    print(f"\n1. Login Credentials:")
    print(f"   Email: {email}")
    print(f"   Password: {password}")
    
    print(f"\n2. After Login Steps:")
    print(f"   - Look for Spotify section")
    print(f"   - Click 'Manual OAuth Setup' button")
    print(f"   - Follow step-by-step instructions")
    
    print(f"\n3. OAuth Process:")
    print(f"   - Click 'Authorize with Spotify'")
    print(f"   - Complete Spotify authorization")
    print(f"   - Copy code from redirect URL")
    print(f"   - Paste code in the form")
    print(f"   - Submit to complete setup")
    
    print(f"\n4. Fresh OAuth URL:")
    from spotify_auth import get_spotify_auth_url
    auth_url = get_spotify_auth_url(state=str(user_id))
    print(f"   {auth_url}")
    
    print(f"\n5. Expected Redirect Format:")
    print(f"   https://synctunes--1754663549838-start-application.replit.app/api/spotify/callback?code=XXXXXXX&state={user_id}")
    
    print("\n" + "="*60)
    print("The manual OAuth system bypasses all external URL issues!")
    print("="*60)

if __name__ == '__main__':
    show_oauth_instructions()