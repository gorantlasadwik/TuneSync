# SyncTunes Deployment Instructions

## Current Issue
The SyncTunes application is fully functional but experiencing external URL routing issues through Replit's proxy. The Flask app runs perfectly on localhost:5000 but external HTTPS access returns 404.

## Solution Options

### Option 1: Use Replit Deployment (Recommended)
1. Click the "Deploy" button in Replit
2. Wait for deployment to complete
3. Get the deployment URL (e.g., https://synctunes-12345.replit.app)
4. Update Spotify app redirect URI to: `{deployment_url}/api/spotify/callback`
5. Update REDIRECT_URI environment variable to match

### Option 2: Local Development
1. Run the app locally: `python main.py`
2. Use ngrok or similar tunnel: `ngrok http 5000`
3. Update Spotify redirect URI to ngrok URL + `/api/spotify/callback`

### Option 3: Port Forwarding
1. Ensure the current Replit URL works by:
   - Checking port configuration
   - Verifying external port mapping
   - Testing with simple routes first

## Current Configuration
- App runs on: http://0.0.0.0:5000
- Expected external URL: https://synctunes--1754663549838-start-application.replit.app
- Spotify Client ID: 6ebe47c28c...
- Current redirect URI: Set in environment variables

## Testing Steps
1. Test local access: `curl http://localhost:5000/`
2. Test external access: `curl https://synctunes--1754663549838-start-application.replit.app/`
3. If external fails, use deployment option

The application code is complete and working - only the external URL access needs to be resolved.