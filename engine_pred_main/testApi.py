import requests
from iam_auth import get_iam_token  

PREDICTION_URL = "https://eu-de.ml.cloud.ibm.com/ml/v4/deployments/89a96b10-e9f0-4a92-90b9-a6c084ea6375/predictions?version=2021-05-01"

headers = {
    "Authorization": f"Bearer {get_iam_token()}",
    "Content-Type": "application/json"
}

test_payload = {
    "input_data": [
        {
            "fields": ["Engine rpm", "Lub oil pressure", "Fuel pressure", "Coolant pressure", "lub oil temp", "Coolant temp"],
            "values": [[1200, 50, 80, 30, 90, 75]]
        }
    ]
}

response = requests.post(PREDICTION_URL, headers=headers, json=test_payload)

print("Response Status Code:", response.status_code)
print("Response Body:", response.text)
