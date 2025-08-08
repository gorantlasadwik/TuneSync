#!/usr/bin/env python3
"""
Process the Spotify OAuth code manually
"""
import sys
sys.path.append('.')

from spotify_auth import exchange_code_for_token, link_spotify_account
from database import get_user_by_email, create_user
from werkzeug.security import generate_password_hash
import logging

logging.basicConfig(level=logging.DEBUG)

def process_oauth_code():
    # The OAuth code from your URL
    code = "AQCBqyb1uf8jXJAV5qJKQVISZlRZ6a_QZp1aLlr282LNKv-WDsxaqf6w1x17v5a-8oP1TNlILUCK4NvKOETKNQDPLY1vcuxU4rM5ipXzXGUiLWoT405vEmjP_3sLPaGFJ0tDzN6jSJx58xM2VmvOnqEMelD4gV_4iXk_xYKe5aDgK-T3LR3SBxb9bB-jmAXNcAbhl7aeESX_-sodK_bi5LLEEhFpI_jEN26S4bravuBRJReyUgfh3YI5RyoQNUInSAY7lsiuhSFiiTUBtVIlvt2teYD45u2eDcuptCvKbID_GcVW6tN8Z2V2POVJ7hVbe-HsJzuQvZhfElrXIMxb3WMVvY1u1FFsHmQWMysRMomuglSKDgup-LjWipTdDE_gZS-dznWQ4Gr3R3O-cCTjKj8p1wrIED8vQ--1-0TcNw"
    
    print("Processing Spotify OAuth code...")
    print(f"Code: {code[:50]}...")
    
    # Step 1: Exchange code for token
    print("\nStep 1: Exchanging code for access token...")
    token_data = exchange_code_for_token(code)
    
    if not token_data:
        print("❌ Failed to exchange code for token")
        return False
    
    print("✅ Successfully got access token")
    print(f"Token type: {token_data.get('token_type', 'N/A')}")
    print(f"Scope: {token_data.get('scope', 'N/A')}")
    
    # Step 2: Create/get test user
    print("\nStep 2: Setting up test user...")
    user = get_user_by_email("demo@test.com")
    if not user:
        print("Creating test user...")
        password_hash = generate_password_hash("password")
        user_id = create_user("Demo User", "demo@test.com", password_hash)
        print(f"✅ Created user with ID: {user_id}")
    else:
        user_id = user['user_id']
        print(f"✅ Found existing user with ID: {user_id}")
    
    # Step 3: Link Spotify account
    print("\nStep 3: Linking Spotify account...")
    if link_spotify_account(user_id, token_data['access_token']):
        print("✅ Spotify account linked successfully!")
        return True
    else:
        print("❌ Failed to link Spotify account")
        return False

if __name__ == '__main__':
    success = process_oauth_code()
    if success:
        print("\n🎉 OAuth process completed successfully!")
        print("You can now log in with demo@test.com / password and see connected Spotify account")
    else:
        print("\n❌ OAuth process failed")