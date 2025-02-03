from langchain_community.embeddings import GPT4AllEmbeddings
from qdrant_client import QdrantClient
from langchain_community.vectorstores import Qdrant
from sentence_transformers import CrossEncoder
import streamlit as st
import os
from dotenv import load_dotenv
load_dotenv()

rerank_model_name='itdainb/PhoRanker'
embed_model_name= "sentence-transformers/paraphrase-multilingual-mpnet-base-v2"

cross_encoder = CrossEncoder(rerank_model_name)
embeddings = GPT4AllEmbeddings(model_file = embed_model_name)
QDRANT_COLLECTION_NAME = "stsv_vector_db_v1"
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")
QDRANT_URL = os.getenv("QDRANT_URL")

def get_retriever(query):
 client = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY, prefer_grpc=False)
 db = Qdrant(client=client, embeddings=embeddings, collection_name=QDRANT_COLLECTION_NAME)
 vectorstore = db.as_retriever(search_kwargs={"k":15})
 docs = vectorstore.invoke(query)
 return docs

def rerank(query,docs):
 documents = [doc.page_content for doc in docs]
 query_doc_pairs = [(query, doc) for doc in documents]
 scores = cross_encoder.predict(query_doc_pairs)
 reranked_results = sorted(zip(documents, scores), key=lambda x: x[1], reverse=True)
 top_doc, top_score = reranked_results[0]
 top_doc_2,top_score_2=reranked_results[1]
 return top_doc,top_doc_2
