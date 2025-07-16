import requests

def lookup_bin(bin_number: str) -> dict:
    if len(bin_number) < 6:
        return None
    try:
        resp = requests.get(f"https://lookup.binlist.net/{bin_number[:8]}")
        if resp.status_code == 200:
            return resp.json()
        return None
    except Exception as e:
        print(f"BIN lookup failed: {e}")
        return None
