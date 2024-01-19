import google.generativeai as genai
import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_google_genai import GoogleGenerativeAIEmbeddings


from typing import Dict, List, Union
import csv
import time

from google.cloud import aiplatform
from google.protobuf import json_format
from google.protobuf.struct_pb2 import Value

RESPONSE_THRESHOLD = 0.4

def predict_custom_trained_model_sample(
    project: str,
    endpoint_id: str,
    instances: Union[Dict, List[Dict]],
    location: str = "us-central1",
    api_endpoint: str = "us-central1-aiplatform.googleapis.com",):
    """
    `instances` can be either single instance of type dict or a list
    of instances.
    """
    # The AI Platform services require regional API endpoints.
    client_options = {"api_endpoint": api_endpoint}
    # Initialize client that will be used to create and send requests.
    # This client only needs to be created once, and can be reused for multiple requests.
    client = aiplatform.gapic.PredictionServiceClient(client_options=client_options)

    instances = instances if isinstance(instances, list) else [instances]
    instances = [
        json_format.ParseDict(instance_dict, Value()) for instance_dict in instances
    ]
    parameters_dict = {}
    parameters = json_format.ParseDict(parameters_dict, Value())
    endpoint = client.endpoint_path(
        project=project, location=location, endpoint=endpoint_id
    )
    response = client.predict(
        endpoint=endpoint, instances=instances, parameters=parameters
    )
    print("response")
    print(" deployed_model_id:", response.deployed_model_id)

    predictions = response.predictions
    print(predictions)
    responses = predictions[0]

    return responses

def get_keywords(query: str) -> list[str]:
	instance = [{"data": query}]
	predictions = predict_custom_trained_model_sample(
	    project="81825140663",
	    endpoint_id="5419158561773060096",
	    location="asia-east1",
	    instances=instance,
	    api_endpoint="asia-east1-aiplatform.googleapis.com"
		)
	keywords = [instance_response[0] for instance_response in predictions if instance_response[1] > RESPONSE_THRESHOLD]
	return keywords

def get_dynamic_theme(query: str) -> str:
	genai.configure(api_key=GOOGLE_API_KEY)
	model = genai.GenerativeModel(model_name="gemini-pro")

	keywords = get_keywords(query)

	prompt = """I have the following chat from one of my users: 
				{question} 

				The important words in the above chat are: {joined_keywords}. 

				Please generate a summary with less than 7 words keeping the important words in mind?""".format(question=query,
																												joined_keywords=", ".join(keywords))

	response = model.generate_content(prompt)

	return response.text

def get_segment(query: str):
	genai.configure(api_key=GOOGLE_API_KEY)
	model = genai.GenerativeModel(model_name="gemini-pro")

	prompt = """
		The following classes are provided with respect to Google Ads Products.
		Educational Question,Product Bug,Feature Request,Spam,Greeting Chat.
	    
	    Here is the brief description of each Class for your understanding :
	    Educational Question: A question that is being asked for more information about a specific topic related to Google Ads products for more understanding.
	    Product Bug: A complaint about a problem with a product or service related to Google Ads Products.
	    Feature Request: A request for a new feature or improvement to a product or service pertaining to Google Ads.
	    Spam: A message that is not relevant to the topic of Google Ads Products. 
	    Greeting Chat: A message that is simply saying hello or goodbye.

	    Please classify a query according to the following rules:
	    1. The query must be relevant to Google Ads Products, else it is considered as a Spam
	    2. The query can belong to multiple classes
	    3. Please use the sample cases to get an understanding about classification.


	    Some sample cases for you to understand the classification:
	    Question: What will be tomorrows weather?
	    Class: Spam
	    Question: What is the impact of Pmax in a Search campaign?
	    Class: Educational Question
	    Question: What is python?
	    Class: Spam
	    Question: How does Google calculate monthly budget when you only run ads M-F? - Google Ads Community, I am setting up my ads to only run Monday-Friday. We are trying to avoid spend on days that are not vauable to our business. Will Google still calculate our ""monthly cap"" by taking the daily budget x 30? Or is there a way to lessen the ""monthly cap"" by daily budget x number of days ads are turned on per month or will Google spend more on M-F to makeup for not spending on weekend?For example: daily spend ($10) x days per month (30) = Google wont spend more than 300 per month, OR: daily spend ($10) x days per month Monday - Friday (20) = Google wont spend more than 200 per month?
	    Class: Educational Question, Feature Request
	    Question: Got Disapproved: Malicious or unwanted software - Google Ads Community,  Hello,I got my ads disapproved because of malware I have checked my website and I can't find any Unwanted Software. In the search console, I have no errors or warnings. Please help me my site lepiercenter.comThanks
	    Class: Product Bug, Educational Question
	    Question: Is there an agency aggregate score target? How are dismissals weighted against implemented recommendations? What can we do at the manager level to ensure we are not hurting our agency score while also being mindful to our client's needs v. Google's assumptions of those needs?
	    Class: Educational Question, Feature Request
	    Question: Recommendation for Device level bid adjustments
	    Class: Feature Request


	    Please classify the query given below, following the above instructions :
	    Question: {query}
	    Class: """.format(query=query)

	response = model.generate_content(prompt)

	return response.text




def main():
	test_data = ["hi! I would like to know if you have any benchmark or data of how a pmax campaign improves 2hen", 
               "Will it increase 18% conversion rate on one campaign or multiple?",
              "What about cannibalization between pmax and search campaigns?",
              "Please explain Keyword optimization in Performance Max. Do we have to have a search campaign besides PM to manage keywords?"]

	# for instance in test_data:
	# 	theme = get_dynamic_theme(instance)
	# 	print(f'Query: {instance}, Dynamic theme: {theme}')

	segment_test_data = ["IF a recommendation is dismissed, the optiscore goes up. Will it have any impact on incremental conversions?",
					"Here's a more specific example. Let's say a client doesn't have reliable conversion value data due to their own systems limitations. That may tells us that anything related to ROAS is never going to improve performance. So the data may suggest tROAS opportunities, but we have to dismiss. Now our team has to constantly dismiss all of these recommendations and it potentially negatively impacts the Agency level optiscore or dismiss rate. How can we improve that process?",
					"Q1: Could you tell us the maximum, minimum, and recommended file sizes that can be submitted on the masthead?, Q2: Regarding the audio regulations for mastheads, are there any audio codecs such as stereo, stereo + 5.1, etc., as in the case of operational types?",
					"My advertiser will be launching a new promo that requires them to show 2 different creatives depending on the state, along with another national promo. This means they would have to create 3 PMax campaigns optimizing to Store Visits running in the same account at the same time. Will that lead to cannibalization or will the system choose one to serve based on ad rank/creative strength, etc.?"]

	# for instance in segment_test_data:
	# 	segment = get_segment(instance)
	# 	print(segment)

	with open('data/segmentation_test.csv', mode ='r') as file:
		csvFile = csv.reader(file)
		header = next(csvFile)
		print(header)
		for lines in csvFile:
			print(f'{lines[0]}, Actual: {lines[1]}, predicted: {get_segment(lines[0])}')
			time.sleep(2)

if __name__ == '__main__':
	main()
