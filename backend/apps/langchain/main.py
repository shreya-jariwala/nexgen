import streamlit as st

from langchain_google_vertexai import VertexAI
import vertexai
from langchain_google_vertexai import VertexAIEmbeddings
from google.oauth2 import service_account

from langchain.prompts import ChatPromptTemplate
from concurrent.futures import ThreadPoolExecutor

from langchain.evaluation import load_evaluator
from langchain_core.prompts import PromptTemplate


# Initialize the client
VERTEXAI_PROJECT = st.secrets.vertexai.project
VERTEXAI_LOCATION = st.secrets.vertexai.location
GOOGLE_CREDENTIALS = service_account.Credentials.from_service_account_info(st.secrets["gcs_connections"])

vertexai.init(project=VERTEXAI_PROJECT, location=VERTEXAI_LOCATION, credentials=GOOGLE_CREDENTIALS)

#Config
model = VertexAI(model_name="gemini-1.5-pro-preview-0409")
llm = VertexAI(model_name="gemini-1.0-pro-vision-001")
embeddings = VertexAIEmbeddings(model_name="textembedding-gecko@003")

def get_response(prompt_list):
    with ThreadPoolExecutor(max_workers=30) as executor:
        results = executor.map(get_response_worker, prompt_list)
    return list(results)

def get_response_worker(item):
    prompt = ChatPromptTemplate.from_messages(
        [("{context}\n\n{question}")]
    )
    chain = prompt | model
    response = chain.invoke(item)
    return response

def get_eval(eval_prompt_list):
    with ThreadPoolExecutor(max_workers=30) as executor:
        results = executor.map(get_eval_worker, eval_prompt_list)
    return list(results)

def get_eval_worker(eval_item):
    evaluator = load_evaluator("labeled_criteria", llm=model, criteria="correctness")
    eval_result = evaluator.evaluate_strings(
        input=eval_item['input'],
        prediction=eval_item['prediction'],
        reference=eval_item['reference']
    )
        
    return eval_result["score"]
