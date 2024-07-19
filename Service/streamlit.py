import streamlit as st
import re
import sqlite3
from embedding import call_model

# Main title
st.title("숙박추천 서비스")

with st.container():
    prompt = st.text_input("GPT에게 요청하세요~", key='prompt')

# Define the layout
col1, col2 = st.columns([2, 5])

def load_data():
    db = sqlite3.connect('')
    c = db.cursor()
    c.execute("SELECT name FROM items")
    rows = c.fetchall()
    db.close()
    return [row[0] for row in rows]

def list_load(data):
    with col2:
        
        st.markdown(f"{data}")

def reset_state():
    st.session_state['selected_regions'] = []
    st.session_state['selected_roomOption'] = []
    st.session_state['selected_amenities'] = []
    st.session_state['price'] = '5만원 이하'
    st.session_state['MaxNum'] = '1명'
    st.session_state['checkin_times'] = []
    st.session_state['pickup_service'] = '상관없음'
    st.session_state['prompt'] = ''

@st.experimental_fragment
def search():
    if st.button("검색"):
        print("1")
        list_load()

@st.experimental_fragment
def reSet():
    if st.button("초기화"):
        reset_state()
        st.rerun()

with col2:
    st.markdown("## 검색결과")
    if prompt:
        response = call_model(prompt)
        list_load(response)
