from router.router import route_transaction

# Ultra-Expansive MCC List for Smart Card Routing Simulation
mcc_tests = {
    # 🍽️ Food & Beverage
    "5812": "Restaurants", "5813": "Bars", "5411": "Grocery Stores",
    "5422": "Meat Markets", "5462": "Bakeries", "5451": "Dairy Stores",

    # ✈️ Travel & Transportation
    "4511": "Airlines", "4111": "Commuter Transport", "4789": "Tolls & Parking",
    "4722": "Travel Agencies", "4411": "Cruises", "4112": "Rail", "4131": "Buses",

    # ⛽ Gas & Automotive
    "5541": "Gas Stations", "5533": "Auto Parts", "7512": "Car Rentals",
    "7538": "Auto Repair", "5532": "Tires",

    # 🛍️ Shopping
    "5311": "Dept Stores", "5942": "Book Stores", "5732": "Electronics",
    "5651": "Clothing", "5995": "Pet Shops", "5992": "Florists",

    # 💻 E-Commerce / Digital
    "5965": "Online Merchants", "5815": "Digital Goods", "4899": "Streaming",
    "4814": "Telecom",

    # 🎮 Entertainment
    "7832": "Movie Theaters", "7996": "Amusement Parks", "7997": "Gyms",

    # 🏠 Home & Utilities
    "5200": "Home Improvement", "4900": "Utilities",

    # 🏥 Health
    "5912": "Pharmacies", "8062": "Hospitals", "8011": "Doctors", "8042": "Chiropractors",

    # 🎓 Education
    "8220": "Universities",

    # 💸 Finance
    "6011": "ATM", "6051": "Crypto", "4829": "Wires", "6211": "Brokerage",

    # 👨‍💼 Services
    "8999": "Professional Services"
}

if __name__ == "__main__":
    for mcc, merchant in mcc_tests.items():
        amount = round(25 + (hash(mcc) % 175), 2)
        print(f"\n🧪 Simulating MCC {mcc} — {merchant} | Amount: ${amount}")
        result = route_transaction(mcc, merchant_name=merchant, amount=amount)

        if result:
            print(f"✅ Routed to {result['card_name']} — {result['reward_percent']}% back "
                  f"(Category: {result['category']}, Token: {result['card_token']})")
        else:
            print("❌ No eligible card found.")
