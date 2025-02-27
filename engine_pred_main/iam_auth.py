import requests
import json
import time


IAM_URL = "https://iam.cloud.ibm.com/identity/token"

API_KEY = "0_225xqiFf2vFvANXisoCOHyJwT0JKZF5_ccrFDPz8mP"

iam_token = None
expires_at = 0  
def get_iam_token():
    global iam_token, expires_at

    if iam_token and time.time() < expires_at:
        print("Using cached IAM token")
        return iam_token

    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    data = {"apikey": API_KEY, "grant_type": "urn:ibm:params:oauth:grant-type:apikey"}

    response = requests.post(IAM_URL, headers=headers, data=data)

    if response.status_code == 200:
        token_data = response.json()
        iam_token = token_data["access_token"]
        expires_in = token_data.get("expires_in", 3600)  
        expires_at = time.time() + expires_in - 60  

        with open("iam_token.json", "w") as f:
            json.dump({"token": iam_token, "expires_at": expires_at}, f)

        print("New IAM token fetched and saved.")
        return iam_token
    else:
        print("Failed to get IAM token:", response.text)
        return None

if __name__ == "__main__":
    print("🔍 Fetching IAM token...")
    token = get_iam_token()
    if token:
        print(f"Token: {token[:50]}... (truncated)")
    else:
        print("Token fetch failed!")
