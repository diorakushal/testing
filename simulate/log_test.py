try:
    with open("data/transactions.log", "a") as f:
        f.write("✅ Log test successful\n")
    print("✅ transactions.log written")
except Exception as e:
    print(f"❌ Write failed: {e}")
