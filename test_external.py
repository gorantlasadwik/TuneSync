#!/usr/bin/env python3
import requests

url = "https://synctunes--1754663549838-start-application.replit.app/"
try:
    response = requests.get(url, timeout=10)
    print(f"Status: {response.status_code}")
    print(f"Headers: {dict(response.headers)}")
    print(f"Content: {response.text[:200]}")
except Exception as e:
    print(f"Error: {e}")