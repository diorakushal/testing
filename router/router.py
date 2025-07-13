import json
from cards.linked_cards import MCC_CATEGORIES

# Main routing function
def route_transaction(mcc_code, user_cards):
    best_card = None
    highest_reward = -1

    print(f"\n\ud83d\udccd MCC {mcc_code} \u2192 {MCC_CATEGORIES.get(mcc_code, 'Unknown')}")
    category = MCC_CATEGORIES.get(mcc_code, "Other")

    for card in user_cards:
        rewards = card.get("rewards", {})
        reward = rewards.get(category, rewards.get("default", 0))
        print(f"  \ud83d\udcb3 {card['card_name']}: {reward}% back")
        if reward > highest_reward:
            highest_reward = reward
            best_card = card

    if best_card:
        print(f"\n\u2705 Route to: {best_card['card_name']} ({best_card['token']}) \u2014 {highest_reward}% reward")
        return {
            "routed_to": best_card["card_name"],
            "card_token": best_card["token"],
            "reward_percent": highest_reward,
            "category": category
        }
    else:
        print("\u274c No suitable card found.")
        return {
            "error": "No suitable card found"
        }
