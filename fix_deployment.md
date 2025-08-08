# How to Fix Spotify OAuth - Step by Step

## Method 1: Fix Spotify Dashboard (Recommended)

### Step 1: Access Spotify Developer Dashboard
1. Go to: **https://developer.spotify.com/dashboard**
2. Log in with your Spotify account
3. Find your app with Client ID: **6ebe47c28c0c462a9465a17a8c337e4e**

### Step 2: Edit App Settings
1. Click on your app name
2. Click **"App Settings"** button (top right)
3. Scroll down to **"Redirect URIs"** section

### Step 3: Add the Correct Redirect URI
1. In the "Redirect URIs" box, add this exact URL:
   ```
   https://synctunes--1754663549838-start-application.replit.app/api/spotify/callback
   ```
2. Click **"Save"** at the bottom

### Step 4: Test Again
1. Go back to SyncTunes app
2. Login with: demo@example.com / demo123
3. Click "Manual OAuth Setup"
4. Get fresh authorization code
5. Use manual OAuth form - should work now!

---

## Method 2: Alternative Domain Solution (If you can't change Spotify)

If you cannot modify your Spotify app settings, I can:
1. Create a localhost version that works immediately
2. Use a different deployment domain
3. Set up ngrok tunnel for testing

---

## Method 3: Quick Test with Localhost

Want to test immediately? I can set up a localhost version that bypasses all domain issues.

## Which method would you prefer?