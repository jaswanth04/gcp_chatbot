
# Not using chat message hisotry to store the history

from pgvector.asyncpg import register_vector
import asyncio
import asyncpg
from google.cloud.sql.connector import Connector
import os
from langchain.embeddings import GooglePalmEmbeddings
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain.llms import GooglePalm
from google.cloud import bigtable
from langchain.memory import ChatMessageHistory
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationChain
import datetime
# from logger import logger

import logging
from fastapi.logger import logger
import uuid
from config import Settings

gunicorn_logger = logging.getLogger('gunicorn.error')

logger.handlers = gunicorn_logger.handlers
# logger.setLevel(gunicorn_logger.level)
logger.setLevel(logging.DEBUG)

settings = Settings(_env_file='.env.development', _env_file_encoding='utf-8')

class Chatter:
	def __init__(self):
		print("Initiated")
		os.environ["GOOGLE_API_KEY"] = settings.GOOGLE_API

		self._llm = GooglePalm(temparature=0.25)

		self._embeddings = GooglePalmEmbeddings()

		prompt_template = """Please embody the persona of a knowledgeable expert in the Products domain. Respond professionally to user questions, utilizing relevant quotations from the context.
            To respond to the questions use the following piece of context to answer the question. 
            Context:
            {context}


            Given below is the history of the conversation which is to be kept in mind before answering any history related or context related question.
            History:
            {history}

            Please follow the steps(1, 2, 3, 4, 5, 6, 7, 8 and 9) given below:
            1. Retrieve answer from your context explicitly.
            2. Clearly state if information is unavailable in the context. Please be very strict in your answering. 
            3. when asked a question about the conversation going on or previous conversation then please use relevant pieces of previous conversation: History
            4. Use previous conversation to answer upcoming conversations which are related to earlier asked queries. Be consistent with answers on the products asked by user in the query, don't mix the products and answer according to the query only.
            5. The recently asked question is the top question which is retrieved from the History and keeping that context if it is the chain of related questions take into consideration the recently asked question and flush out the earlier conversations just keep the most recent conversation in the memory strictly.
            6. Please do not answer anything which is not their in your context just say "<p>Sorry, I am Google Ads chatbot and, I wont be able to do anything apart from answering your questions related to Google Ads Products.</p>", regardless of the conversation history.
            7. For any question that has nothing related to Google Ads, regardless of the history, please say <p>Sorry, I am Google Ads chatbot and, I wont be able to do anything apart from answering your questions related to Google Ads Products.</p>"
            8. Please provide the response in a html format
            9. In the response, the anchor tag should have an additional attribute <a target="_blank" href="REDIRECT_URL"></a>, where REDIRECT_URL is the url to be redirected to.

            
            Some sample conversations for you to understand:
            Human: What will be tomorrows weather?
            AI: <p>Sorry, I am Google Ads chatbot and, I wont be able to do anything apart from answering your questions related to Google Ads Products.</p>
            Human: What is the impact of Pmax in a Search campaign?
            AI: <p>Performance Max prioritizes serving on Search inventory based on the campaign with the highest probability of winning the auction (ad rank). Exceptions exist for identical keyword matches favoring Search campaigns over Performance Max.</p>
            Human: What is python?
            AI: <p>Sorry, I am Google Ads chatbot and, I wont be able to do anything apart from answering your questions related to Google Ads Products.</p>
            Human: What is tailwind CSS?
            AI: <p>Sorry, I am Google Ads chatbot and, I wont be able to do anything apart from answering your questions related to Google Ads Products.</p>
            Human: Any question other than the one present in context
            AI: <p>Sorry, I am Google Ads chatbot and, I wont be able to do anything apart from answering your questions related to Google Ads Products.</p>
            

            Current Conversation:
            Human: {query}
            AI: 
            Keep responses concise within 120 words. Keep the reference of examples in mind"""

		self._prompt = PromptTemplate(
			input_variables=["history", "context", "query"],
			template=prompt_template,
		)

		# self._llm_chain = LLMChain(prompt=prompt, llm=llm)

		project_name = settings.PROJECT_NAME
		instance_name = settings.BIGTABLE_INSTANCE_NAME
		table_name = settings.BIGTABLE_TABLE_NAME


		client = bigtable.Client(project=project_name, admin=True)
		instance = client.instance(instance_name)
		self._big_table = instance.table(table_name)
		self._conn = None


	async def connect(self):
		loop = asyncio.get_running_loop()
		connector = Connector(loop=loop)
		project_id = settings.PROJECT_NAME
		region = settings.GCP_REGION_NAME
		instance_name = settings.POSTGRES_INSTANCE_NAME
		database_user = settings.POSTGRES_DB_USERNAME
		database_password = settings.POSTGRES_DB_PASSWORD
		database_name = settings.POSTGRES_DB_NAME

		logger.info("Postgres SQL Connection commencing")
		self._conn = await connector.connect_async(
			f"{project_id}:{region}:{instance_name}",  # Cloud SQL instance connection name
			"asyncpg",
			user=f"{database_user}",
			password=f"{database_password}",
			db=f"{database_name}",
			)
		await register_vector(self._conn)
		logger.info("Postgres SQL connection registered")

	def get_history(self, session_id):
		logger.info(f"Retreiving history for {session_id}")
		history = ChatMessageHistory()
		row = self._big_table.row(session_id)
		read_rows = self._big_table.read_row(session_id)
		col_family_name = 'transaction'
		questions = []
		if read_rows is not None:
			q_read = read_rows.cells[col_family_name]['question'.encode()]
			a_read = read_rows.cells[col_family_name]['answer'.encode()]
			for q in reversed(q_read):
				ques = q.value.decode()
				questions.append(ques)
				history.add_user_message(ques)
				logger.debug(f"History for {session_id}, Q: {ques}")
			for a in reversed(a_read):
				history.add_ai_message(a.value.decode())
				logger.debug(f"History for {session_id}, A: {a.value.decode()}")

		logger.info(f"Successfully retreived history for {session_id}")

		return history, questions

	def save_response(self, session_id, transaction_id, query, response):

		logger.info(f"Saving the response for {session_id} ")
		row = self._big_table.row(session_id)
		col_family_name = 'transaction'
		timestamp = datetime.datetime.utcnow()
		
		row.set_cell(col_family_name, 'transaction_id', transaction_id.encode('utf-8'), timestamp)
		row.set_cell(col_family_name, 'question', query.encode('utf-8'), timestamp)
		row.set_cell(col_family_name, 'answer', response.encode('utf-8'), timestamp)

		row.commit()
		logger.info(f"Successfully Saved the response for {session_id} ")


	async def get_answer(self, session_id, query):

		history, questions = self.get_history(session_id)

		memory = ConversationBufferMemory(memory_key="history", chat_memory=history, input_key="query")

		conversation = LLMChain(
			llm=self._llm,
			prompt=self._prompt,
			verbose=False,
			memory=memory)

		query_with_questions = "\n".join([query, *questions])
		logger.debug(f"query with questions: {query_with_questions}")
		query_embeddings = self._embeddings.embed_query(query_with_questions)

		matches = await self.get_matches(query_embeddings)
		context = "\n".join(matches)

		response = conversation.predict(query=query, context=context)
		transaction_id = str(uuid.uuid4())


		# Save response to bigtable
		
		self.save_response(session_id, transaction_id, query, response)

		result = {'answer': response, 'transaction_id': transaction_id, 'session_id': session_id}

		return result

	async def get_matches(self, qe):
		logger.info("Extracting nearest vectors from Post gres")

		if (not self._conn) or self._conn.is_closed():
			logger.info("No connection to cloud sql found, trying to create a connection !!")
			await self.connect()
			logger.info("Connection established !!!")
		matches = []
		similarity_threshold = 0.7
		num_matches = 5

		# Find similar products to the query using cosine similarity search
		# over all vector embeddings. This new feature is provided by `pgvector`.
		# async with self._pool.acquire() as connection:
            # return await connection.execute(query, *args)
		results = await self._conn.fetch(
			"""
				SELECT content, 1 - (embedding <=> $1) AS similarity
				FROM product_embeddings
				WHERE 1 - (embedding <=> $1) > $2
				ORDER BY similarity DESC
				LIMIT $3
			""",
			qe,
			similarity_threshold,
			num_matches,
		)

		if len(results) == 0:
			logger.info("No Matches found")
			return matches

		for r in results:
			# Collect the description for all the matched similar toy products.
			matches.append(r["content"])

		logger.info("Matches extracted successfully !!!")
		logger.debug(matches)

		return matches

	async def close(self):
		await self._conn.close()
		logger.info("Connection closed.")
		# self._conn = None


