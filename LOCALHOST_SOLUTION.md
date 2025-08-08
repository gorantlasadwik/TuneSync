# SyncTunes - Localhost Solution (Spotify Doesn't Allow localhost)

## The Problem
Spotify Developer Console doesn't allow `localhost` or `127.0.0.1` in redirect URIs for security reasons. This means you can't test OAuth locally with standard localhost URLs.

## Solution: Use ngrok (Tunnel Service)

### Step 1: Install ngrok
```bash
# Download from https://ngrok.com/download
# Or using package managers:
brew install ngrok          # macOS
choco install ngrok         # Windows
sudo apt install ngrok      # Linux
```

### Step 2: Run Your App Locally
```bash
python main.py
# App runs on http://localhost:5000
```

### Step 3: Create Public Tunnel
```bash
# In a new terminal
ngrok http 5000
```

You'll get output like:
```
Forwarding  https://abc123.ngrok.io -> http://localhost:5000
```

### Step 4: Update Spotify Redirect URI
In your Spotify Developer Dashboard:
- Add: `https://abc123.ngrok.io/api/spotify/callback`
- Keep your existing Replit URL as backup

### Step 5: Update Environment Variable
```bash
export REDIRECT_URI=https://abc123.ngrok.io/api/spotify/callback
```

### Alternative: Use the Replit URL Locally
Since Spotify is already configured for the Replit URL, you can:

1. Run app locally: `python main.py`
2. Set environment variable to use Replit URL:
```bash
export REDIRECT_URI=https://synctunes--1754663549838-start-application.replit.app/api/spotify/callback
```
3. The OAuth will redirect to Replit URL, but you can manually copy the callback URL and test locally

## Why This Works
- ngrok creates a secure HTTPS tunnel to your localhost
- Spotify accepts the ngrok HTTPS URL
- Your local app receives all the OAuth callbacks properly
- Full functionality testing locally with real Spotify integration