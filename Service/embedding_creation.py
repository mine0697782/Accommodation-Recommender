import os
import pandas as pd
from dotenv import load_dotenv
from langchain_core.documents import Document
from langchain_openai import AzureOpenAIEmbeddings
from langchain_chroma import Chroma

VECTOR_STORE_PATH = "vector_store"

def load_csv(file_path):
    df = pd.read_csv(file_path)
    documents = []
    for _, row in df.iterrows():
        content = " ".join([str(value) for value in row])
        documents.append(Document(page_content=content, metadata={"source": "csv"}))
    return documents

def create_and_save_embeddings(file_path):
    documents = load_csv(file_path)
    
    embedding_model = AzureOpenAIEmbeddings(
        model="text-embedding-3-small"
    )

    chroma = Chroma(persist_directory=VECTOR_STORE_PATH)
    chroma.from_documents(
        documents=documents,
        embedding=embedding_model
    )
    chroma.persist()

if __name__ == "__main__":
    load_dotenv()
    csv_filepath = "/Users/jmj/Accommodation-Recommender/Data/preprocessed_dataset.csv"
    create_and_save_embeddings(csv_filepath)
