import pandas as pd
import openai
import chromadb
from chromadb.utils import embedding_functions
from langchain_chroma import Chroma

from dotenv import load_dotenv
import os

load_dotenv()

# CSV 파일 읽기
file_path = 'Data/combined_dataset.csv'
df = pd.read_csv(file_path)

# 필요한 컬럼들
columns_to_embed = [
    '명칭', '전화번호', '주소', '개요', '상세정보'
]

df = df[columns_to_embed]
df = df.head(100)

output_file_path = 'Data/preprocessed_dataset.csv'
df.to_csv(output_file_path, index=False)
print(df)
