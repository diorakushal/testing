import streamlit as st
import streamlit_authenticator as stauth
import requests
import json
import os
import pandas as pd
import matplotlib.pyplot as plt
import io
from requests.auth import HTTPBasicAuth

# Set Streamlit page config
st.set_page_config(page_title="Smart Card Checkout Simulator", layout="centered")

# ========================
# 🔐 Auth Setup
# ========================
hashed_passwords = ['$2b$12$LQv6p0PK9ktArZPVXQsjWeAAFCD2nLftrar4uQDVuHYbYxpyzKqke']  # password: test123
credentials = {
    "usernames": {
        "kushal": {
            "name": "Kushal Diora",
            "password": hashed_passwords[0],
        }
    }
}
authenticator = stauth.Authenticate(
    credentials,
    "smartcard_auth",
    "smartcard_token",
    cookie_expiry_days=1
)

name, auth_status, username = authenticator.login("Login", location="main")

if auth_status is False:
    st.error("❌ Incorrect username or password.")
    st.stop()
elif auth_status is None:
    st.warning("🔐 Please enter your credentials.")
    st.stop()

authenticator.logout("Logout", location="sidebar")
st.sidebar.success(f"✅ Logged in as {name}")

# ========================
# 🔧 Load User Card Data
# ========================
BASE_DIR = os.getcwd()
USER_CARDS_PATH = os.path.join(BASE_DIR, "data", "user_cards.json")

if not os.path.exists(USER_CARDS_PATH):
    os.makedirs(os.path.dirname(USER_CARDS_PATH), exist_ok=True)
    with open(USER_CARDS_PATH, "w") as f:
        json.dump({
            "user_123": [
                {
                    "card_name": "Wells Fargo Reflect",
                    "token": "Wells_Fargo_Reflect_Card_668",
                    "rewards": {
                        "default": 3.0,
                        "Grocery Stores": 3.0,
                        "Restaurants": 2.0
                    }
                }
            ]
        }, f, indent=2)

with open(USER_CARDS_PATH) as f:
    users = json.load(f)

user_tokens = list(users.keys())

# =======================
# 🚀 Simulate Transaction
# =======================
st.title("📿 Smart Card Checkout Simulator")
st.header("🔪 Simulate Transaction")

with st.form("checkout_form"):
    user_token = st.selectbox("Select User", user_tokens)
    merchant = st.text_input("Merchant Name", "Whole Foods")
    mcc = st.text_input("Merchant Category Code (MCC)", "5411")
    amount = st.number_input("Transaction Amount ($)", min_value=0.01, step=0.01, value=50.00)
    submitted = st.form_submit_button("Simulate Transaction")

if submitted:
    st.info("Routing transaction...")
    try:
        resp = requests.post(
            "http://127.0.0.1:5000/route_transaction",
            headers={"Content-Type": "application/json"},
            json={
                "user_token": user_token,
                "amount": amount,
                "mcc": mcc,
                "merchant": merchant
            }
        )
        if resp.status_code == 200:
            result = resp.json()
            if "error" in result:
                st.error(f"❌ {result['error']}")
            else:
                reward = result['reward_percent']
                cashback = round(amount * reward / 100, 2)
                reward_icon = "🟢" if reward >= 3 else "🟠" if reward >= 2 else "🔴"
                st.success(f"✅ Routed to: {result['routed_to']}")
                st.write(f"**Category:** {result['category']}")
                st.write(f"**Reward Rate:** {reward_icon} {reward}%")
                st.write(f"**Estimated Cashback:** ${cashback:.2f}")
                st.code(f"Card Token: {result['card_token']}")
        else:
            st.error(f"❌ {resp.status_code} - {resp.json().get('error', 'Unknown error')}")
    except Exception as e:
        st.error(f"⚠️ Request failed: {e}")

# =========================
# ➕ Add New Card
# =========================
st.header("➕ Add New Card")
with st.form("add_card_form"):
    user_token_add = st.selectbox("Select User to Add Card", user_tokens, key="add_user")
    card_name = st.text_input("Card Name")
    card_token = st.text_input("Card Token")
    default_reward = st.number_input("Default Reward (%)", min_value=0.0, step=0.1)
    custom_categories = st.text_input("Custom Rewards (e.g. Grocery Stores:4, Restaurants:3)")
    add_submitted = st.form_submit_button("Add Card")

if add_submitted:
    try:
        new_card = {
            "card_name": card_name,
            "token": card_token,
            "rewards": {"default": default_reward}
        }
        if custom_categories:
            for pair in custom_categories.split(","):
                key, val = pair.strip().split(":")
                new_card["rewards"][key.strip()] = float(val)

        users[user_token_add].append(new_card)
        with open(USER_CARDS_PATH, "w") as f:
            json.dump(users, f, indent=2)
        st.success(f"✅ Added card '{card_name}' for {user_token_add}")
    except Exception as e:
        st.error(f"❌ Failed to add card: {e}")

# =========================
# 📜 View Past Transactions
# =========================
st.header("📜 View Past Transactions")
with st.form("view_history_form"):
    user_token_history = st.selectbox("Select User", user_tokens, key="history_user")
    history_submitted = st.form_submit_button("Fetch History")

if history_submitted:
    try:
        resp = requests.get(
            "http://127.0.0.1:5000/api/history",
            params={"user_token": user_token_history},
            auth=HTTPBasicAuth("Gateway JIT Funding", "Kushal@13Kushal@13Kushal@13")
        )
        if resp.status_code == 200:
            data = resp.json()
            transactions = data.get("transactions", [])
            if transactions:
                st.success(f"📄 Showing {len(transactions)} recent transactions:")
                for tx in transactions:
                    st.markdown(f"""
• 🕒 **{tx['timestamp']}**
• 🏍️ *{tx['merchant']}* — ${tx['amount']}
• 💳 **{tx['card']}** ({tx['reward_percent']}% back)
• 📂 Category: `{tx['category']}`
---
""")
            else:
                st.info("No transactions found.")
        else:
            st.error(f"❌ {resp.status_code} - {resp.json().get('error')}")
    except Exception as e:
        st.error(f"⚠️ Request failed: {e}")

# ===============================
# 📊 Analytics & Export Section
# ===============================
st.header("📊 Analytics & Export Logs")
with st.form("analytics_form"):
    user_token_analytics = st.selectbox("Select User", user_tokens, key="analytics_user")
    analytics_submitted = st.form_submit_button("Run Analytics")

if analytics_submitted:
    try:
        resp = requests.get(
            "http://127.0.0.1:5000/api/history",
            params={"user_token": user_token_analytics},
            auth=HTTPBasicAuth("Gateway JIT Funding", "Kushal@13Kushal@13Kushal@13")
        )
        if resp.status_code != 200:
            st.error(f"❌ Failed to fetch data: {resp.text}")
        else:
            tx_data = resp.json().get("transactions", [])
            if not tx_data:
                st.info("No transactions available.")
            else:
                df = pd.DataFrame(tx_data)
                df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce").dropna()
                df = df.sort_values("timestamp", ascending=False)

                st.write("📄 Raw Data:")
                st.dataframe(df)

                df["cashback"] = df["amount"] * df["reward_percent"] / 100
                summary = df.groupby("category")["cashback"].sum().sort_values(ascending=False)

                st.write("💰 Total Cashback by Category:")
                fig, ax = plt.subplots()
                summary.plot(kind="bar", ax=ax)
                ax.set_ylabel("Cashback ($)")
                ax.set_xlabel("Category")
                st.pyplot(fig)

                csv_buffer = io.StringIO()
                df.to_csv(csv_buffer, index=False)
                st.download_button(
                    label="⬇️ Download CSV of Transactions",
                    data=csv_buffer.getvalue(),
                    file_name="transaction_history.csv",
                    mime="text/csv"
                )
    except Exception as e:
        st.error(f"⚠️ Error: {e}")

# ==========================
# 💳 My Cards - Visual View
# ==========================
st.header("💳 My Cards")
with st.form("view_cards_form"):
    selected_user = st.selectbox("Select User", user_tokens, key="view_cards_user")
    view_cards_submitted = st.form_submit_button("View Cards")

if view_cards_submitted:
    try:
        with open(USER_CARDS_PATH) as f:
            user_data = json.load(f)
        cards = user_data.get(selected_user, [])
        if not cards:
            st.info("This user has no saved cards.")
        else:
            for card in cards:
                st.subheader(f"📿 {card['card_name']}")
                token_masked = f"••••_{card['token'][-1]}"
                st.write(f"🔑 Token: `{token_masked}`")

                rewards = card.get("rewards", {})
                default = rewards.get("default", 0)
                st.write(f"💸 Default Reward: `{default}%`")

                custom = {k: v for k, v in rewards.items() if k != "default"}
                if custom:
                    st.write("🏷️ Custom Categories:")
                    for cat, pct in custom.items():
                        st.markdown(f"- **{cat}**: `{pct}%`")
                st.markdown("---")
    except Exception as e:
        st.error(f"⚠️ Failed to load cards: {e}")
