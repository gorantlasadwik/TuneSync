#!/usr/bin/env python3
"""
Test the OAuth code directly without UI
"""
import sys
sys.path.append('.')

from spotify_auth import exchange_code_for_token, link_spotify_account
from database import get_user_by_email, create_user
from werkzeug.security import generate_password_hash
import logging

logging.basicConfig(level=logging.INFO)

def process_fresh_code():
    """Process the fresh OAuth code you just provided"""
    # Fresh code from your URL
    code = "AQA6c7Ckwbq8GsTnxb5MaVpDFveCxS0WA162MG9WuLfQEfORnOU_w_alxiSSCN65QlJOwnr4EtGHRKFtCAzU_x0vHZeuEexQNLFYf1ZFc0K0MYm8qHu6tvTTiq-do2jIxois-SJk95IsBv90_0D-MuF66OQmuPowFVth1UUdu-RAQvIu8HsEWtOITgO6VzPKWK8X606hZ8p-CMuc_l5otRy-7FaHjWf3p8kyNWcvyd-sq29p2N6AzK-CSFdgcvpSRaRTAb4q_wXVeTyS9NPYlmNJrhtBk90g7YsLVUlcohmdhqJ50vDlf_yNav_SYj8lIF4XsHecxI7EQBwnR8peHhtReoCIRb2HWBopGWOtBTetPIlt9g0IxAKX6Te-CIIed8Qhj8S_tigQhx82YymKMKiuaW2VKL5RBYQsu0rxNQ"
    
    print("Processing fresh Spotify OAuth code...")
    print(f"Code length: {len(code)} characters")
    
    # Step 1: Exchange code for token
    print("\n🔄 Exchanging code for access token...")
    token_data = exchange_code_for_token(code)
    
    if not token_data:
        print("❌ Token exchange failed - checking for detailed error logs above")
        return False
    
    print("✅ Token exchange successful!")
    print(f"Token type: {token_data.get('token_type', 'N/A')}")
    print(f"Scope: {token_data.get('scope', 'N/A')}")
    
    # Step 2: Ensure test user exists
    print("\n👤 Setting up user account...")
    user = get_user_by_email("demo@example.com")
    if not user:
        password_hash = generate_password_hash("demo123")
        user_id = create_user("Demo User", "demo@example.com", password_hash)
        print(f"✅ Created user with ID: {user_id}")
    else:
        user_id = user['user_id']
        print(f"✅ Using existing user ID: {user_id}")
    
    # Step 3: Link Spotify account
    print("\n🎵 Linking Spotify account...")
    if link_spotify_account(user_id, token_data['access_token']):
        print("✅ Spotify account linked successfully!")
        print("\n🎉 OAUTH SETUP COMPLETE!")
        print("You can now:")
        print("- Login to SyncTunes with: demo@example.com / demo123")
        print("- View connected Spotify account")
        print("- Access your Spotify playlists")
        print("- Sync with YouTube Music")
        return True
    else:
        print("❌ Failed to link Spotify account")
        return False

if __name__ == '__main__':
    success = process_fresh_code()
    if not success:
        print("\n🔧 If this fails, the redirect URI needs to be fixed in Spotify dashboard")
        print("Add: https://synctunes--1754663549838-start-application.replit.app/api/spotify/callback")