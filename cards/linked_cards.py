from router.mcc_utils import get_category_from_mcc  # ✅ Centralized MCC logic

# Sample LinkedCard class
class LinkedCard:
    def __init__(self, name, token, rewards_by_category):
        self.name = name
        self.token = token
        self.rewards_by_category = rewards_by_category

    def get_reward_percent(self, mcc_code):
        category = get_category_from_mcc(mcc_code)
        return self.rewards_by_category.get(category, self.rewards_by_category.get("Other", 0))

    def get_category(self, mcc_code):
        return get_category_from_mcc(mcc_code)

# ✅ Your cards
linked_cards = [
    LinkedCard(
        name="Amex Gold",
        token="amex_gold_token_123",
        rewards_by_category={
            "Restaurants": 4,            # 4X on dining
            "Grocery Stores": 4,         # 4X at U.S. supermarkets
            "Airlines/Travel Agencies": 3,
            "Other": 1
        }
    ),
    LinkedCard(
        name="Chase Freedom Unlimited",
        token="chase_freedom_token_456",
        rewards_by_category={
            "Restaurants": 3,            # 3% on dining
            "Travel": 5,                 # 5% on travel via Chase Travel
            "Pharmacies": 3,             # ✅ MCC 5912 → Pharmacies → 3%
            "Other": 1.5
        }
    ),
    LinkedCard(
        name="Citi Double Cash",
        token="citi_double_token_789",
        rewards_by_category={
            "Airlines/Travel Agencies": 5,
            "Other": 2
        }
    )
]
