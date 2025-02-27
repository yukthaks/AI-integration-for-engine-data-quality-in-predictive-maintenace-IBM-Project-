import requests
import json
import time

API_KEY = "0_225xqiFf2vFvANXisoCOHyJwT0JKZF5_ccrFDPz8mP"  
IAM_URL = "https://iam.cloud.ibm.com/identity/token"
TOKEN_FILE = "iam_token.json"

def get_iam_token():
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    data = {"apikey": API_KEY, "grant_type": "urn:ibm:params:oauth:grant-type:apikey"}

    response = requests.post(IAM_URL, headers=headers, data=data)

    if response.status_code == 200:
        iam_token = response.json()["access_token"]
        expiration_time = time.time() + response.json()["expires_in"] - 60  

        with open(TOKEN_FILE, "w") as f:
            json.dump({"token": iam_token, "expires_at": expiration_time}, f)

        return iam_token
    else:
        print("Failed to get token:", response.text)
        return None

def read_cached_token():
    try:
        with open(TOKEN_FILE, "r") as f:
            data = json.load(f)
            if time.time() < data["expires_at"]:  
                return data["token"]
    except (FileNotFoundError, json.JSONDecodeError):
        return None

    return None

def get_token():
    token = read_cached_token()
    if not token:
        token = get_iam_token()
    return token

if __name__ == "__main__":
    print("Current IAM Token:", get_token())
