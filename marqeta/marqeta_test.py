import requests

# Your sandbox credentials
APPLICATION_TOKEN = 'c39bd7aa-7884-413f-b834-a08c1d265e3e'
ADMIN_ACCESS_TOKEN = '8266355e-db6d-4196-b308-5a944bffd013'
BASE_URL = 'https://sandbox-api.marqeta.com/v3'

# Test: List Card Products
def list_card_products():
    url = f"{BASE_URL}/cardproducts?sort_by=-lastModifiedTime"
    response = requests.get(
        url,
        headers={"Content-Type": "application/json"},
        auth=(APPLICATION_TOKEN, ADMIN_ACCESS_TOKEN)
    )
    print("Status Code:", response.status_code)
    print("Response:", response.json())

if __name__ == '__main__':
    list_card_products()
