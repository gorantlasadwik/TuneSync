#!/usr/bin/env python3
"""
Create alternative OAuth solution using common redirect URIs
"""
import sys
sys.path.append('.')

common_redirects = [
    "http://localhost:8080/callback",
    "http://localhost:3000/callback", 
    "http://localhost:5000/callback",
    "https://example.com/callback",
    "urn:ietf:wg:oauth:2.0:oob"
]

def show_alternative_configs():
    """Show alternative configurations for different redirect URIs"""
    print("="*60)
    print("ALTERNATIVE OAUTH CONFIGURATIONS")
    print("="*60)
    print()
    print("If you can't add our redirect URI to Spotify, try these common ones:")
    print()
    
    for i, redirect in enumerate(common_redirects, 1):
        print(f"Option {i}: {redirect}")
        print(f"  - Check if this is already in your Spotify app")
        print(f"  - If yes, I can configure our app to use it")
        print()
    
    print("Most Common Development Redirect URIs:")
    print("✓ http://localhost:8080/callback")
    print("✓ http://localhost:3000/callback") 
    print("✓ https://example.com/callback")
    print()
    print("Tell me which redirect URI is currently configured in your")
    print("Spotify app, and I'll update SyncTunes to match it!")

if __name__ == '__main__':
    show_alternative_configs()