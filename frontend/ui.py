import streamlit as st
import streamlit_authenticator as stauth
import requests
import json
import os
import pandas as pd
import matplotlib.pyplot as plt
import io
from requests.auth import HTTPBasicAuth
from bin_lookup import lookup_bin

# ========================
# 📄 Page Config + Styles
# ========================
st.set_page_config(
    page_title="Smart Card Checkout Simulator",
    layout="centered",
    initial_sidebar_state="expanded"
)

# Inject custom style
with open("style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


# ========================
# 🔐 Auth Setup
# ========================
hashed_passwords = stauth.Hasher(['test123']).generate()

credentials = {
    "usernames": {
        "kushal": {
            "name": "Kushal Diora",
            "password": hashed_passwords[0]
        }
    }
}

authenticator = stauth.Authenticate(
    credentials,
    "smartcard_auth",
    "smartcard_token",
    cookie_expiry_days=1
)

name, auth_status, username = authenticator.login("Login", "main")

if auth_status == False:
    st.error("❌ Incorrect username or password.")
    st.stop()
elif auth_status == None:
    st.warning("🔐 Please enter your credentials.")
    st.stop()

authenticator.logout("Logout", "sidebar")
st.sidebar.success(f"✅ Logged in as {name}")

# ========================
# 📁 Load or Create Card Data
# ========================
USER_CARDS_PATH = os.path.join("data", "user_cards.json")
REWARDS_DB_PATH = "rewards_db.json"

if not os.path.exists(USER_CARDS_PATH):
    os.makedirs(os.path.dirname(USER_CARDS_PATH), exist_ok=True)
    with open(USER_CARDS_PATH, "w") as f:
        json.dump({"user_123": []}, f, indent=2)

with open(USER_CARDS_PATH) as f:
    users = json.load(f)

user_tokens = list(users.keys())

if os.path.exists(REWARDS_DB_PATH):
    with open(REWARDS_DB_PATH) as f:
        reward_db = json.load(f)
else:
    reward_db = {}

BASE_API = "https://testing-1-92pt.onrender.com"

# =======================
# 🚀 Simulate Transaction
# =======================
st.title("📏 Smart Card Checkout Simulator")
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
            f"{BASE_API}/route_transaction",
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
# ➕ Add New Card with BIN Lookup
# =========================
st.header("➕ Add New Card")
with st.form("add_card_form"):
    user_token_add = st.selectbox("Select User", user_tokens, key="add_user")
    name_on_card = st.text_input("Name on Card", placeholder="e.g. Kushal Diora")
    card_number = st.text_input("Card Number (only first 6 digits used for BIN lookup)", placeholder="e.g. 414709")
    expiration = st.text_input("Expiration Date", placeholder="MM/YY")
    cvv = st.text_input("CVV", type="password", placeholder="***")
    card_token = st.text_input("Card Token (nickname)", placeholder="e.g. Chase_Flex_123")
    add_submitted = st.form_submit_button("Add Card")

if add_submitted:
    try:
        bin_value = card_number[:6]
        card_name = "Unknown Card"
        rewards = {"default": 1.0}

        if len(bin_value) == 6:
            bin_data = lookup_bin(bin_value)
            if bin_data:
                scheme = bin_data.get("scheme", "").title()
                bank = bin_data.get("bank", {}).get("name", "")
                brand = bin_data.get("brand", "")
                card_name = f"{bank} {brand}".strip() or scheme or "Unknown Card"

                normalize = {
                    "Chase Bank Freedom Flex": "Chase Freedom Flex",
                    "Wells Fargo Bank, N.A. World Elite Mastercard Card": "Wells Fargo Autograph",
                    "American Express": "Amex Gold",
                    "Discover Card": "Discover it Cashback",
                    "Capital One, National Association Visa Traditional": "Capital One SavorOne"
                }
                card_name = normalize.get(card_name, card_name)

                matched = reward_db.get(card_name)
                if matched:
                    rewards.update(matched)
                    st.success(f"🔍 Matched card: {card_name}")
                    st.json(matched)
                else:
                    st.warning(f"No reward structure found in DB for card: `{card_name}`")
            else:
                st.warning("BIN lookup failed.")
        else:
            st.error("Please enter at least the first 6 digits of the card.")

        new_card = {
            "card_name": card_name,
            "token": card_token,
            "name_on_card": name_on_card,
            "expiration": expiration,
            "cvv": "***",
            "rewards": rewards
        }

        users[user_token_add].append(new_card)
        with open(USER_CARDS_PATH, "w") as f:
            json.dump(users, f, indent=2)
        st.success(f"✅ Card '{card_name}' added and rewards attached.")
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
            f"{BASE_API}/api/history",
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
# 📊 Analytics & Export Logs
# ===============================
st.header("📊 Analytics & Export Logs")
with st.form("analytics_form"):
    user_token_analytics = st.selectbox("Select User", user_tokens, key="analytics_user")
    analytics_submitted = st.form_submit_button("Run Analytics")

if analytics_submitted:
    try:
        resp = requests.get(
            f"{BASE_API}/api/history",
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
                st.subheader(f"📟 {card['card_name']}")
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
