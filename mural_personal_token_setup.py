#!/usr/bin/env python3
"""
Setup Mural API with Personal Access Token
Much simpler than OAuth - just get a token from Mural settings
"""

import os
import json
import requests
from dotenv import load_dotenv

print("\n" + "="*60)
print("MURAL PERSONAL ACCESS TOKEN SETUP")
print("="*60)

print("""
📋 Instructions to get your Personal Access Token:

1. Go to https://app.mural.co
2. Click on your profile icon (top right)
3. Go to Settings
4. Look for "Developer" or "API" or "Personal Access Tokens" section
5. Click "Create new token" or "Generate token"
6. Give it a name (e.g., "API Testing")
7. Copy the token (you won't see it again!)

""")

token = input("Paste your Personal Access Token here: ").strip()

if not token:
    print("❌ No token provided")
    exit(1)

print("\n🔍 Testing the token...")

# Test the token
headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}

# Test with a simple API call to get user info
test_url = "https://api.mural.co/api/v0/users/me"

try:
    response = requests.get(test_url, headers=headers, timeout=10)
    
    if response.status_code == 200:
        user_data = response.json()
        print(f"✅ Token is valid! Authenticated as: {user_data.get('firstName', 'User')} {user_data.get('lastName', '')}")
        
        # Save the token to .env file
        print("\n💾 Saving token to .env file...")
        
        env_path = "lrl-workhorse/.env"
        if os.path.exists(".env"):
            env_path = ".env"
        
        # Read existing .env or create new
        env_lines = []
        if os.path.exists(env_path):
            with open(env_path, 'r') as f:
                env_lines = f.readlines()
        
        # Update or add MURAL_ACCESS_TOKEN
        token_found = False
        new_lines = []
        
        for line in env_lines:
            if line.startswith('MURAL_ACCESS_TOKEN='):
                new_lines.append(f'MURAL_ACCESS_TOKEN={token}\n')
                token_found = True
            else:
                new_lines.append(line)
        
        if not token_found:
            new_lines.append(f'MURAL_ACCESS_TOKEN={token}\n')
        
        # Write back
        with open(env_path, 'w') as f:
            f.writelines(new_lines)
        
        print(f"✅ Token saved to {env_path}")
        
        # Now let's create a simple test to verify everything works
        print("\n🎨 Creating a test sticky note on your board...")
        
        # Load board info from config
        with open('mural_config.json', 'r') as f:
            config = json.load(f)
        
        workspace_id = config.get('workspace_id', 'root7380')
        board_id = config.get('board_id', '1754493659737')
        
        # Create a sticky note
        create_url = f"https://api.mural.co/api/v0/murals/{workspace_id}.{board_id}/widgets"
        
        sticky_data = {
            "type": "sticky-note",
            "text": "✅ Mural API Connected!",
            "x": 400,
            "y": 300,
            "width": 200,
            "height": 200,
            "style": {
                "backgroundColor": "#2ECC71",
                "fontSize": 18
            }
        }
        
        response = requests.post(create_url, headers=headers, json=sticky_data, timeout=10)
        
        if response.status_code in [200, 201]:
            widget = response.json()
            print(f"✅ Test sticky note created successfully!")
            
            board_url = f"https://app.mural.co/t/{workspace_id}/m/{workspace_id}/{board_id}"
            print(f"\n🎯 Check your board: {board_url}")
            print("\nYou should see a green sticky note that says '✅ Mural API Connected!'")
            
        else:
            print(f"⚠️ Couldn't create test sticky note: {response.status_code}")
            print(f"Response: {response.text[:200]}")
            print("\nBut your token is valid! You can still use it for API calls.")
        
        print("\n" + "="*60)
        print("SETUP COMPLETE!")
        print("="*60)
        print("\nYou can now run any of the test scripts:")
        print("  • python3 mural_simple_test.py")
        print("  • python3 mural_robust_test.py")
        print("  • python3 mural_real_test.py")
        
    else:
        print(f"❌ Token is invalid. Status: {response.status_code}")
        print(f"Response: {response.text[:200]}")
        print("\nPlease make sure you:")
        print("1. Created a Personal Access Token in Mural settings")
        print("2. Copied it correctly (no extra spaces)")
        print("3. The token hasn't expired")
        
except Exception as e:
    print(f"❌ Error testing token: {e}")
    print("\nPlease check your internet connection and try again.")
