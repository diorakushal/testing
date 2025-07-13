import requests

APPLICATION_TOKEN = 'c39bd7aa-7884-413f-b834-a08c1d265e3e'
ADMIN_ACCESS_TOKEN = '8266355e-db6d-4196-b308-5a944bffd013'
BASE_URL = 'https://sandbox-api.marqeta.com/v3'

# Step 5: List all cards tied to a specific user
def list_user_cards(user_token):
    url = f"{BASE_URL}/cards/user/{user_token}"
    response = requests.get(url, auth=(APPLICATION_TOKEN, ADMIN_ACCESS_TOKEN))
    
    if response.status_code == 200:
        print("🎯 User's Cards:")
        for card in response.json().get("data", []):
            print("  🆔 Card Token:", card["token"])
            print("  🪪 Card Type:", card.get("card_product_token"))
            print("  🗓️ Created:", card.get("created_time"))
            print("  ✅ Active:", card.get("state"))
    else:
        print("❌ Error:", response.status_code, response.text)

# Replace this with the actual user_token that was printed in issue_card.py
if __name__ == "__main__":
    user_token = "<PUT_THE_USER_TOKEN_HERE>"  # Example: "3021b7d4-...etc..."
    list_user_cards(user_token)
