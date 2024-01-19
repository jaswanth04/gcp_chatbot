import requests

filename = "token-1"

with open(filename, 'r') as token_file:
    token = token_file.read().strip()

url = "https://chatter-rag-abuwvk2glq-as.a.run.app/query"

headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"  # Adjust the content type as needed
}



payload = {
    "id": 0,
    "query": "Who are you?"
}

response = requests.post(url, headers=headers, json=payload)
# response = requests.get(url, headers=headers)

print(response)
print(response.status_code)
print(response.json())
