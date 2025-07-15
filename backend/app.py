import json
import base64
import os
from flask import Flask, request, jsonify
from functools import wraps
from datetime import datetime, timezone
from dotenv import load_dotenv
from router.reward_optimizer import get_reward_score

# === Init ===
app = Flask(__name__)
load_dotenv()

# === Paths ===
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
LOG_PATH = os.path.join(DATA_DIR, "transactions.log")
USER_CARDS_PATH = os.path.join(DATA_DIR, "user_cards.json")

# Ensure data directory and log file exist
os.makedirs(DATA_DIR, exist_ok=True)
if not os.path.exists(LOG_PATH):
    open(LOG_PATH, "w").close()

# === Auth ===
EXPECTED_USERNAME = os.getenv("USERNAME", "Gateway JIT Funding")
EXPECTED_PASSWORD = os.getenv("PASSWORD", "Kushal@13Kushal@13Kushal@13")

def require_basic_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Basic "):
            return jsonify({"error": "Unauthorized"}), 401
        try:
            encoded = auth_header.split(" ")[1]
            decoded = base64.b64decode(encoded).decode("utf-8")
            username, password = decoded.split(":", 1)
        except Exception:
            return jsonify({"error": "Invalid auth format"}), 401
        if username != EXPECTED_USERNAME or password != EXPECTED_PASSWORD:
            return jsonify({"error": "Forbidden"}), 403
        return f(*args, **kwargs)
    return decorated

# === Load User Cards ===
def load_user_cards():
    try:
        with open(USER_CARDS_PATH, "r") as f:
            return json.load(f)
    except Exception as e:
        print(f"❌ Error loading user_cards.json: {e}")
        return {}

# === Routes ===

@app.route('/api/funding', methods=['POST'])
@require_basic_auth
def handle_funding():
    print("📬 Webhook hit!")
    data = request.json or {}
    txn = data.get('transaction', {})
    mid = txn.get('mid', {})
    mcc = str(mid.get('mcc')).strip() if mid.get('mcc') else None
    merchant = mid.get('merchant_name', 'Unknown')
    amount = float(txn.get('amount', 0))
    user_token = data.get("user_token", "user_123")

    if not mcc:
        return jsonify({"error": "Missing MCC"}), 400

    user_cards = load_user_cards().get(user_token, [])
    best_card = None
    best_reward = 0.0
    best_category = "Unknown"

    for card in user_cards:
        reward_rate, category = get_reward_score(card, mcc, merchant, amount)
        print(f"  💳 {card['card_name']} — {category}: {reward_rate}%")
        if reward_rate > best_reward:
            best_reward = reward_rate
            best_card = card
            best_category = category

    if best_card:
        print(f"✅ Routed to: {best_card['card_name']} — {best_reward}% back (Category: {best_category})")
        log_entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "user_token": user_token,
            "merchant": merchant,
            "mcc": mcc,
            "category": best_category,
            "amount": amount,
            "card": best_card['card_name'],
            "reward_percent": best_reward,
            "card_token": best_card['token']
        }
        try:
            with open(LOG_PATH, "a") as logfile:
                logfile.write(json.dumps(log_entry) + "\n")
        except Exception as e:
            print(f"❌ Error writing to log: {e}")

        return jsonify({
            "funding": {"amount": amount, "currency_code": "USD"},
            "funding_source_token": best_card['token'],
            "user_token": user_token,
            "state": "APPROVED"
        })

    return jsonify({"error": "No eligible card found"}), 400

@app.route('/route_transaction', methods=['POST'])
def route_transaction():
    data = request.get_json() or {}
    user_token = data.get("user_token")
    amount = data.get("amount")
    mcc = str(data.get("mcc")).strip() if data.get("mcc") else None
    merchant = data.get("merchant", "Unknown")

    if not user_token or not amount or not mcc:
        return jsonify({"error": "Missing fields"}), 400

    user_cards = load_user_cards().get(user_token, [])
    best_card = None
    best_reward = 0.0
    best_category = "Unknown"

    for card in user_cards:
        reward_rate, category = get_reward_score(card, mcc, merchant, amount)
        print(f"  💳 {card['card_name']} — {category}: {reward_rate}%")
        if reward_rate > best_reward:
            best_reward = reward_rate
            best_card = card
            best_category = category

    if best_card:
        print(f"✅ Routed to: {best_card['card_name']} — {best_reward}% back (Category: {best_category})")
        return jsonify({
            "routed_to": best_card["card_name"],
            "reward_percent": best_reward,
            "category": best_category,
            "card_token": best_card["token"],
            "amount": float(amount),
            "mcc": mcc,
            "merchant": merchant
        })

    return jsonify({"error": "No eligible card found"}), 400

@app.route('/api/history', methods=['GET'])
@require_basic_auth
def get_transaction_history():
    user_token = request.args.get('user_token')
    if not user_token:
        return jsonify({"error": "Missing user_token"}), 400

    try:
        with open(LOG_PATH, "r") as logfile:
            lines = logfile.readlines()
    except Exception as e:
        return jsonify({"error": f"Failed to read log: {str(e)}"}), 500

    recent = [
        json.loads(line) for line in reversed(lines)
        if json.loads(line).get("user_token") == user_token
    ]

    return jsonify({
        "user_token": user_token,
        "transactions": recent[:10]
    })

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "ok", "timestamp": datetime.utcnow().isoformat()})

# === Error Handlers ===
@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "Route not found"}), 404

@app.errorhandler(500)
def server_error(e):
    return jsonify({"error": "Internal server error"}), 500

# === Dev mode ===
def print_routes():
    print("\n📋 Registered routes:")
    for rule in app.url_map.iter_rules():
        print(f"{rule.endpoint:25s} --> {rule}")

if __name__ == '__main__':
    print_routes()
    app.run(host="0.0.0.0", port=5000)
