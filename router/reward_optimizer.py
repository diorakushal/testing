# router/reward_optimizer.py

from router.mcc_utils import get_category_from_mcc

def get_reward_score(card, mcc, merchant, amount, timestamp=None):
    """
    Enhanced reward optimizer logic.
    Falls back to MCC category but can include other factors.
    Returns both the final reward rate and the category used.
    """
    category = get_category_from_mcc(mcc)
    rewards = card.get("rewards", {})

    # --- Base reward using MCC-derived category or default
    base = rewards.get(category, rewards.get("default", 0))

    # --- Merchant-specific override (e.g., Amazon)
    if merchant.lower() == "amazon" and "Amazon" in rewards:
        base = max(base, rewards["Amazon"])

    # --- Bonus for large purchases
    if amount > 100:
        base += 0.5  # flat 0.5% bonus for purchases over $100

    return round(base, 2), category
