# Spotify OAuth Redirect URI Issue - SOLUTION

## Root Cause
The 400 "Bad Request" error indicates a **redirect URI mismatch** between:
1. What's configured in your Spotify Developer Dashboard
2. What our application sends in the token exchange request

## Current Configuration
- **App sends**: `https://synctunes--1754663549838-start-application.replit.app/api/spotify/callback`
- **Spotify expects**: Whatever is configured in your developer dashboard

## SOLUTION: Fix the Redirect URI in Spotify Developer Dashboard

### Step 1: Go to Spotify Developer Dashboard
1. Visit: https://developer.spotify.com/dashboard
2. Click on your app (Client ID: 6ebe47c28c0c462a9465a17a8c337e4e)
3. Go to "App Settings"

### Step 2: Update Redirect URI
In the "Redirect URIs" section, make sure you have **EXACTLY**:
```
https://synctunes--1754663549838-start-application.replit.app/api/spotify/callback
```

**Important**: 
- No trailing slash
- Exact case matching
- Must be HTTPS (not HTTP)

### Step 3: Save Settings
Click "Save" in the Spotify dashboard.

### Step 4: Test Again
1. Get a fresh authorization code (codes expire in 10 minutes)
2. Use the manual OAuth form with the new code
3. Should work immediately after fixing the redirect URI

## Alternative: Change App Configuration
If you can't modify the Spotify app, tell me what redirect URI is currently configured in your Spotify dashboard, and I'll update the app to match it.

## Why This Happens
Spotify requires exact matching of redirect URIs for security. Even small differences like:
- `http` vs `https`
- trailing slash differences
- port number differences
- domain case differences

Will cause a 400 error during token exchange.