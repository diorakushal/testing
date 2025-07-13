from router.router import route_transaction
import uuid
import time

def simulate_swipe(amount, mcc, merchant_name="Test Merchant"):
    print(f"\n💳 Simulating charge of ${amount:.2f} at {merchant_name} (MCC: {mcc})")

    selected_card = route_transaction(mcc, merchant_name, amount)

    if selected_card:
        log = {
            "transaction_id": str(uuid.uuid4()),
            "timestamp": time.ctime(),
            "amount": amount,
            "mcc": mcc,
            "merchant": merchant_name,
            "routed_to": selected_card["card_name"],
            "reward_percent": selected_card["reward_percent"],
            "simulated_card_token": selected_card["token"]
        }

        print("\n🧾 Transaction Summary:")
        for k, v in log.items():
            print(f"  {k}: {v}")
    else:
        print("❌ Transaction failed: No eligible card found.")

if __name__ == "__main__":
    simulate_swipe(9.99, "4899", "Spotify")
    simulate_swipe(204.3, "4111", "Lyft")
    simulate_swipe(55.49, "5812", "In-N-Out")
