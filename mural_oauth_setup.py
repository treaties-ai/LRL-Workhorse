#!/usr/bin/env python3
"""
Mural OAuth Setup - Gets access token through authorization code flow
"""

import webbrowser
import http.server
import socketserver
import urllib.parse
import requests
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv('.env')

CLIENT_ID = os.getenv('MURAL_CLIENT_ID')
CLIENT_SECRET = os.getenv('MURAL_CLIENT_SECRET')
REDIRECT_URI = "http://localhost:8081/callback"
PORT = 8081

print("\n" + "="*60)
print("MURAL OAUTH SETUP - GET ACCESS TOKEN")
print("="*60)

# Step 1: Generate authorization URL (with trailing slash as per MURAL's official sample)
auth_url = f"https://app.mural.co/api/public/v1/authorization/oauth2/"
params = {
    "client_id": CLIENT_ID,
    "redirect_uri": REDIRECT_URI,
    "response_type": "code",
    "scope": "murals:read murals:write"
}
full_auth_url = f"{auth_url}?{urllib.parse.urlencode(params)}"

print("\n📝 Instructions:")
print("1. I'll open your browser to authorize the Mural app")
print("2. Log in to Mural if needed")
print("3. Click 'Allow' to authorize the app")
print("4. You'll be redirected back here automatically")
print("\nOpening browser...")

# Global variable to store the code
auth_code = None

class CallbackHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        global auth_code
        
        # Parse the authorization code from the callback
        if self.path.startswith('/callback'):
            query = urllib.parse.urlparse(self.path).query
            params = urllib.parse.parse_qs(query)
            
            if 'code' in params:
                auth_code = params['code'][0]
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                html_content = """
                    <html>
                    <body style="font-family: sans-serif; padding: 40px;">
                        <h1>✅ Authorization Successful!</h1>
                        <p>You can close this window and return to the terminal.</p>
                    </body>
                    </html>
                """
                self.wfile.write(html_content.encode('utf-8'))
            else:
                self.send_response(400)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                self.wfile.write(b"<h1>Authorization failed</h1>")
    
    def log_message(self, format, *args):
        pass  # Suppress server logs

# Open browser for authorization
webbrowser.open(full_auth_url)

# Start local server to receive callback
print("\n⏳ Waiting for authorization callback...")
with socketserver.TCPServer(("", PORT), CallbackHandler) as httpd:
    while auth_code is None:
        httpd.handle_request()

print(f"\n✓ Received authorization code: {auth_code[:20]}...")

# Step 2: Exchange code for access token
print("\n🔄 Exchanging code for access token...")
token_url = "https://app.mural.co/api/public/v1/authorization/oauth2/token/"
token_data = {
    "grant_type": "authorization_code",
    "code": auth_code,
    "redirect_uri": REDIRECT_URI,
    "client_id": CLIENT_ID,
    "client_secret": CLIENT_SECRET
}

response = requests.post(token_url, data=token_data)

if response.status_code == 200:
    token_info = response.json()
    access_token = token_info.get('access_token')
    refresh_token = token_info.get('refresh_token', '')
    
    print("\n✅ SUCCESS! Access token obtained!")
    print(f"Access Token: {access_token[:30]}...")
    
    # Save tokens to .env file
    print("\n💾 Saving tokens to .env file...")
    
    # Read current .env
    with open('.env', 'r') as f:
        lines = f.readlines()
    
    # Add or update MURAL_ACCESS_TOKEN
    token_found = False
    refresh_found = False
    new_lines = []
    
    for line in lines:
        if line.startswith('MURAL_ACCESS_TOKEN='):
            new_lines.append(f'MURAL_ACCESS_TOKEN={access_token}\n')
            token_found = True
        elif line.startswith('MURAL_REFRESH_TOKEN='):
            new_lines.append(f'MURAL_REFRESH_TOKEN={refresh_token}\n')
            refresh_found = True
        else:
            new_lines.append(line)
    
    if not token_found:
        # Add after MURAL_REDIRECT_URL line
        for i, line in enumerate(new_lines):
            if line.startswith('MURAL_REDIRECT_URL='):
                new_lines.insert(i + 1, f'MURAL_ACCESS_TOKEN={access_token}\n')
                break
    
    if not refresh_found and refresh_token:
        for i, line in enumerate(new_lines):
            if line.startswith('MURAL_ACCESS_TOKEN='):
                new_lines.insert(i + 1, f'MURAL_REFRESH_TOKEN={refresh_token}\n')
                break
    
    # Write back
    with open('.env', 'w') as f:
        f.writelines(new_lines)
    
    print("✓ Tokens saved to .env file")
    print("\n" + "="*60)
    print("SETUP COMPLETE!")
    print("="*60)
    print("\nYou can now run the test scripts to create sticky notes on your Mural board.")
    print("The access token has been saved and will be used automatically.")
    
else:
    print(f"\n❌ Failed to get access token: {response.status_code}")
    print(f"Response: {response.text}")
