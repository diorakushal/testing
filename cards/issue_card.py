import requests
import uuid
import time

# Marqeta sandbox credentials
APPLICATION_TOKEN = 'c39bd7aa-7884-413f-b834-a08c1d265e3e'
ADMIN_ACCESS_TOKEN = '8266355e-db6d-4196-b308-5a944bffd013'
BASE_URL = 'https://sandbox-api.marqeta.com/v3'

def create_cardholder():
    user_token = str(uuid.uuid4())
    email = f"kushal+{user_token[:8]}@example.com"
    payload = {
        "token": user_token,
        "first_name": "Kushal",
        "last_name": "Diora",
        "email": email,
        "active": True
    }
    url = f"{BASE_URL}/users"
    response = requests.post(url, json=payload, auth=(APPLICATION_TOKEN, ADMIN_ACCESS_TOKEN))
    print("👤 Cardholder created:", response.status_code)
    print("🪪 USER TOKEN:", user_token)
    print("📧 Email:", email)
    print("🔁 Create User Response:", response.json())
    return user_token


# Step 2: Issue a virtual card
def issue_virtual_card(user_token):
    card_token = str(uuid.uuid4())
    payload = {
        "user_token": user_token,
        "card_product_token": "9f6ecc5e-2b54-4c8e-8bfe-0e98508b92bf",
        "token": card_token
    }
    url = f"{BASE_URL}/cards"
    response = requests.post(url, json=payload, auth=(APPLICATION_TOKEN, ADMIN_ACCESS_TOKEN))
    print("💳 Card issued:", response.status_code)
    print("📦 CARD TOKEN:", card_token)
    print("🔁 Card Response:", response.json())
    return card_token

# Step 3: Retrieve full PAN, CVV, and Expiration
def get_sensitive_card_data(card_token):
    url = f"{BASE_URL}/cards/{card_token}/pan"
    response = requests.get(url, auth=(APPLICATION_TOKEN, ADMIN_ACCESS_TOKEN))
    if response.status_code == 200:
        data = response.json()
        print("\n🔐 CARD DETAILS")
        print("Card Number (PAN):", data.get("pan"))
        print("Expiration:", data.get("expiration"))
        print("CVV:", data.get("cvv_number"))
    else:
        print("❌ Failed to retrieve card info:", response.status_code, response.text)

if __name__ == "__main__":
    user_token = create_cardholder()
    time.sleep(1.5)  # Give time for the user to be registered
    card_token = issue_virtual_card(user_token)
    time.sleep(1.5)  # Wait to ensure the card is generated
    get_sensitive_card_data(card_token)
