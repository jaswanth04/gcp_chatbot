from fastapi import FastAPI, HTTPException
from chatter_1 import Chatter
import asyncio
from langchain.embeddings import GooglePalmEmbeddings
import os
from pydantic import BaseModel, validator
# from logger import logger
import logging
from fastapi.logger import logger
from reaction import add_reaction
from recommendation import generate_recommendations
from fastapi.middleware.cors import CORSMiddleware


gunicorn_logger = logging.getLogger('gunicorn.error')

logger.handlers = gunicorn_logger.handlers
# logger.setLevel(gunicorn_logger.level)
logger.setLevel(logging.DEBUG)




class QueryRequest(BaseModel):
	session_id: str
	query: str

class RecommendationRequest(BaseModel):
	user_id: str


class ReactionRequest(BaseModel):
	session_id: str
	transaction_id: str
	reaction: int

	@validator('reaction')
	def reaction_check(cls, v):
		if (v == 0) or (v == 1) or (v == -1):
			pass
		else:
			raise ValueError('Reaction is value other than 0 or 1')
		return v

app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


chatter = Chatter()

@app.get("/")
async def index():
	# await pg_connector.connect()
	logger.info("Ping initiated")
	return {"ping": "Successful"}

@app.post("/get-answer")
async def get_answer(request: QueryRequest):

	logger.debug(f"Session id: {request.session_id}")
	logger.debug(f"query: {request.query}")
	try:
		response = await chatter.get_answer(request.session_id, request.query)
	except Exception as e:
		raise HTTPException(status_code=500, detail=str(e))

	return response

@app.get("/get-embedding")
async def get_embedding(query: str):

	print(query)
	session_id = '5a938729-54a7-465f-b646-dc52a0078c59'

	matches = await chatter.get_answer(session_id, query)

	print(matches)

	return {"result": "Received embeddings!!"}

@app.post("/add-reaction")
def update_reaction(reaction_request: ReactionRequest):
	session_id = reaction_request.session_id
	transaction_id = reaction_request.transaction_id
	reaction = reaction_request.reaction

	try:
		add_reaction(session_id, transaction_id, reaction)
	except Exception as e:
		raise HTTPException(status_code=404, detail=str(e))

	return {"message": "Update successful"}

@app.get("/close")
async def close():
	await chatter.close() 
	return {"detail": "SQL DB Close Successful"}

@app.post("/get-recommendations")
def get_recommendations(recommendation_request: RecommendationRequest):
	logger.info(f'Generating recommendation for user: {recommendation_request.user_id}')
	data = generate_recommendations()
	response = {"data": data}
	return response


