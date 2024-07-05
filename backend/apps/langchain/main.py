import streamlit as st
import time
from concurrent.futures import ThreadPoolExecutor

import litellm
from langchain_google_vertexai import VertexAI
import vertexai
from google.oauth2 import service_account

from langchain.evaluation import load_evaluator


GEMINI_API_KEY = st.secrets.gemini.api_key

# Initialize the client
VERTEXAI_PROJECT = st.secrets.vertexai.project
VERTEXAI_LOCATION = st.secrets.vertexai.location
GOOGLE_CREDENTIALS = service_account.Credentials.from_service_account_info(st.secrets["gcs_connections"])

vertexai.init(project=VERTEXAI_PROJECT, location=VERTEXAI_LOCATION, credentials=GOOGLE_CREDENTIALS)

#Config
llm = VertexAI(model_name="gemini-1.0-pro")

# Your API request limit per minute
API_LIMIT_PER_MINUTE = 1000
EVAL_API_LIMIT_PER_MINUTE = 300

# Function to get responses from the language model
def get_response(prompt_list):
    # Keep track of the number of requests made in the current minute
    requests_this_minute = 0
    start_time = time.time()

    with ThreadPoolExecutor() as executor:
        results = []
        for prompt in prompt_list:
            # Wait if the API limit is reached
            while requests_this_minute >= API_LIMIT_PER_MINUTE:
                time.sleep(60 - (time.time() - start_time))
                requests_this_minute = 0
                start_time = time.time()

            # Submit the task to the executor
            future = executor.submit(get_response_worker, prompt)
            results.append(future)

            # Increment the request counter
            requests_this_minute += 1

        # Retrieve the results from the futures
        return [future.result() for future in results]

def get_response_worker(item):
    """
    Retrieves a response from the language model with automatic retries.
    """
    try:
        response = litellm.completion(
            model="gemini/gemini-1.5-flash",
            api_key=GEMINI_API_KEY,
            messages=[{"role": "user", "content": f"{item}"}],
            safety_settings=[
        {
            "category": "HARM_CATEGORY_HARASSMENT",
            "threshold": "BLOCK_NONE",
        },
        {
            "category": "HARM_CATEGORY_HATE_SPEECH",
            "threshold": "BLOCK_NONE",
        },
        {
            "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
            "threshold": "BLOCK_NONE",
        },
        {
            "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
            "threshold": "BLOCK_NONE",
        }],
        )
        message_content = response.choices[0].message.content
        return message_content
    except Exception as e:
        raise  # This ensures the retry mechanism is triggered

# Function to get evaluations
def get_eval(eval_prompt_list):
    # Keep track of the number of requests made in the current minute
    requests_this_minute = 0
    start_time = time.time()

    with ThreadPoolExecutor() as executor:
        results = []
        for eval_item in eval_prompt_list:
            # Wait if the API limit is reached
            while requests_this_minute >= EVAL_API_LIMIT_PER_MINUTE:
                time.sleep(60 - (time.time() - start_time))
                requests_this_minute = 0
                start_time = time.time()

            # Submit the task to the executor
            future = executor.submit(get_eval_worker, eval_item)
            results.append(future)

            # Increment the request counter
            requests_this_minute += 1

        # Retrieve the results from the futures
        return [future.result() for future in results]

def get_eval_worker(eval_item):
    
    try:
        evaluator = load_evaluator("labeled_criteria", llm=llm, criteria="correctness")
        eval_result = evaluator.evaluate_strings(
            input=eval_item['input'],
            prediction=eval_item['prediction'],
            reference=eval_item['reference']
        )   
        return eval_result["score"]
    except Exception as e:
        raise  # This ensures the retry mechanism is triggered