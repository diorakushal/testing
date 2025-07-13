# router/mcc_utils.py

MCC_CATEGORIES = {
    "5812": "Restaurants",
    "5411": "Grocery Stores",
    "4511": "Airlines/Travel Agencies",
    "4722": "Airlines/Travel Agencies",
    "4111": "Travel",
    "5541": "Gas Stations",
    "5311": "Department Stores",
    "5942": "Book Stores",
    "5999": "Misc Retail Stores",
    "5732": "Electronics Stores",
    "5651": "Clothing Stores",
    "5965": "Internet Merchants",
    "5815": "Digital Goods (General)",
    "4899": "Cable/Streaming",
    "4814": "Telecom Services",
    "7832": "Movie Theaters",
    "7996": "Amusement Parks",
    "7997": "Gyms/Fitness Clubs",
    "5200": "Home Improvement",
    "4900": "Utilities",
    "5912": "Pharmacies",
    "8062": "Hospitals",
    "8011": "Doctors",
    "8220": "Colleges & Universities",
    "6011": "ATM Withdrawals",
    "6051": "Quasi-Cash (Crypto)",
    "4829": "Wire Transfers",
    "6211": "Security Brokers",
    "8999": "Professional Services"
}

def get_category_from_mcc(mcc_code):
    mcc_str = str(mcc_code).strip()
    category = MCC_CATEGORIES.get(mcc_str)
    if not category:
        print(f"⚠️ MCC '{mcc_str}' not found in MCC_CATEGORIES")
        return "Unknown"
    return category
