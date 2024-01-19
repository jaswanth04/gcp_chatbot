from langchain.document_loaders import TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import GooglePalmEmbeddings
from langchain.llms import GooglePalm
from langchain.vectorstores import Pinecone
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate

import pinecone
import os
import sys
from config import Settings


class Chatter:
	def __init__(self, faq_doc_name: str = "") -> None:
		# loader = TextLoader(faq_doc_name)
		# data = loader.load()

		# text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=20)

		# text_chunks = text_splitter.split_documents(data)
		settings = Settings(_env_file='.env.development', _env_file_encoding='utf-8')
		os.environ['GOOGLE_API_KEY'] = settings.GOOGLE_API_KEY
		embeddings = GooglePalmEmbeddings()


		# PINECONE_API_KEY = os.getenv('PINECONE_API_KEY')
		# PINECONE_API_ENV = os.getenv('PINECONE_API_ENV')
		# os.setenv('GOOGLE_API_KEY') = Settings.GOOGLE_API_KEY

		pinecone.init(api_key=settings.PINECONE_API_KEY, environment=settings.PINECONE_API_ENV)
		index_name = "pmax"

		docsearch = Pinecone.from_existing_index(index_name=index_name, embedding=embeddings)

		llm = GooglePalm(temparature=0.0)

		self.qa = RetrievalQA.from_chain_type(llm, chain_type="stuff", retriever=docsearch.as_retriever())

		prompt_template = """
		Please use the persona given below:
		Persona: You are Performance Max Chatbot. Your responses are professional. If you dont know about an answer, say that you dont know.
		
		To respond to the questions use the following piece of context to answer the question. 
		{context}

		Also, Please provide a response in less than 100 words.

		Question: {query}
		"""

		prompt = PromptTemplate(
		    input_variables=["context", "query"],
		    template=prompt_template,
		)

	def get_response(self, query: str) -> str:
		# query = "When do I analyze my asset performance?"
		return self.qa.run(query)

# Some code for testing
def main() -> None:
	filename = "PMAX_FAQ.txt"
	chatter = Chatter(filename)

	query_list = ["When do I analyze my asset performance?", 
					"Are youtube shorts supported ?",
					"How does Pmax favour in Search campaign ?",
					"Can you please provide me some details on the integrations supported by Pmax ?",
					"Can you please tell me about the best brand suitable?",
					"What about shared budgets? Are they on the roadmap?",
					"What support is provided, if my company has separate budgets?",
					"How many performance max campaigns should I setup?",
					"What is the process of Demographic Control in Pmax?",
					"I want to optimize the campaign, but I dont want to look at the insights. How do I do it ?"]

	for query in query_list:
		print(f'Query: {query}')
		print(f'Response: {chatter.get_response(query)}\n\n')


if __name__ == '__main__':
	main()
