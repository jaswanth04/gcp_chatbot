import requests
import uuid
import time

query = "What is PMax?"
query = "How do I add a new campaign?"
query = "Are youtube shorts supported ?"
query = "What product are we discussing about now?"

questions = ["What is PMax?",
	"How do I add a new campaign?",
	"Are youtube shorts supported ?",
	"What product are we discussing about now?"]

session_id = str(uuid.uuid4())

url = 'http://127.0.0.1:8080/get-answer'

# request_url = f'{url}?query={query}'
# session_id = str(uuid.uuid4())
# session_id = "95af08ee-ddad-4d22-8635-40815d7b6f26"
# transaction_id = "4874236c-0101-4364-84bd-ce1bd0ee6f66" # Correct one
# transaction_id = "4874236c-0101-4364-84bd-ce1bd0ee6f43" # Error one
# question = "what is pmax?"

# with open('token', 'r') as token_file:
# 	token = token_file.read().strip()

for i, query in enumerate(questions):
	payload = {
		"session_id": session_id,
		"query": query
	}

	response = requests.post(url, json=payload)

	print(f'Query - {i}: {query}')
	print(response.json())
	# print(f'Response - {i}: {response.json()}')
	time.sleep(4)

close_url = 'http://127.0.0.1:8000/close'
close_response = requests.get(close_url)
print(close_response.status_code)
print(close_response.json())
# header = {
# 	"Authorization": f"Bearer {token}",
#     "Content-Type": "application/json"  # Adjust the content type as needed

# }
# response = requests.post(url, json=payload)

# response = requests.get(request_url, headers=header)

# print(response.status_code)
# print(response.json())
