from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from rag import Chatter
from pydantic import BaseModel


class ChatRequest(BaseModel):
	id: int
	query: str
app = FastAPI()



origins = [
    "http://localhost:9000",
    "http://127.0.0.1:9000",
    "http://localhost:8000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

chatter = Chatter("PMAX_FAQ.txt")

@app.get('/ping')
def ping():
	return {"ping": "Successful"}

@app.post('/query/')
def process_query(chat_request: ChatRequest):
	id = chat_request.id
	query = chat_request.query
	print(query)
	return {"id": id, 
			"response": chatter.get_response(query)}
