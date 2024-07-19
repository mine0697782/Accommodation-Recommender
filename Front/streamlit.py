import streamlit as st
import re
import sqlite3

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

def list_load():
    accommodations = [
        ["웰리힐리파크", "강원특별자치도 횡성군 둔내면 고원로 451", "", "", "15:00", "익일 11:00"],
        ["코레스코치악산콘도미니엄", "강원특별자치도 횡성군 우천면 전재로 254", "033-342-7880", "", "15:00", "익일 11:00"],
        ["호텔 느낌", "강원특별자치도 속초시 온천로 313", "033-635-2580", "", "15:00", "14:00"],
        ["관광펜션 시실리(평창시실리펜션)", "강원특별자치도 평창군 진부면 탑동길 195-8", "010-4364-2655", "", "15:00", "11:00"],
        ["연어의 고향 펜션", "강원특별자치도 양양군 양양읍 동해신묘길 8-3", "033-672-6809", "", "15:00", "익일 11:00"],
        ["키스멧코티지", "강원특별자치도 평창군 용평면 금당길 213-20", "", "", "15:00", "11:00"]
    ]
    
    with col2:
        for accommodation in accommodations:
            st.markdown(
                f"""
                <div style="border: 1px solid black; padding: 10px; margin-top: 20px;  border-radius: 5px;">
                    <strong>이름</strong>: {accommodation[0]}<br>
                    <strong>주소</strong>: {accommodation[1]}<br>
                    <strong>전화번호</strong>: {accommodation[2]}<br>
                    <strong>체크인 시간</strong>: {accommodation[4]}<br>
                    <strong>체크아웃 시간</strong>: {accommodation[5]}
                </div>
                """,
                unsafe_allow_html=True
             )

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
        list_load()

@st.experimental_fragment
def reSet():
    if st.button("초기화"):
        reset_state()
        st.rerun()

with col1:
    reSet()
    st.subheader("선호 Tag")

    st.markdown("#### 광역시/도")
    regions = ["전국", "서울", "인천", "대전", "대구", "광주", "부산", "강원특별자치도", "충청북도",
               "충청남도", "경상북도", "경상남도", "전라남도", "전북특별자치도", "세종특별자치시", "제주도", "경기도", "울산"]
    selected_regions = st.multiselect(
        "지역을 선택하시오", regions, key='selected_regions')

    st.markdown("#### 객실시설")
    roomOption = ["TV",  "냉장고", "에어컨", "드라이기", "소파"]
    selected_roomOption = st.multiselect(
        "부대시설을 선택하시오", roomOption, key='selected_roomOption')

    st.markdown("#### 부대시설")
    amenities = ["휘트니스센터", "식음료장", "바베큐장", "주차장", "수영장", "사우나", "스파",
                 "세미나실", "PC", "족구장", "연회장", "매점/편의점", "보관함", "골프장", "노래방"]
    selected_amenities = st.multiselect(
        "부대시설을 선택하시오", amenities, key='selected_amenities')

    st.markdown('#### 가격')
    price = st.select_slider(
        "원하는 가격을 설정하세요",
        options=["5만원 이하", "10만원", "15만원", "20만원", "25만원", "30만원 이상",], key='price')

    price = re.sub(r'[^0-9]', '', price)

    st.markdown('#### 숙박 인원수')
    MaxNum = st.select_slider(
        "최대인원 수를 고르세요",
        options=["1명", "2명", "3명", "4명", "5명", "6명", "7명", "8명", "9명", "10명", "11명 이상"], key='MaxNum')

    st.markdown('#### 체크인 시간')
    checkin_times = ["14시 이전", "14시", "15시", "16시", "17시", "18시", "18시 이후"]
    selected_checkin_times = st.multiselect(
        "체크인 시간 선택", checkin_times, key='checkin_times')

    st.markdown('#### 픽업서비스')
    pickup_service = st.radio(
        "픽업 서비스 여부", ["상관없음", "유", "무"], key='pickup_service')

    search()

with col2:
    st.markdown("## 검색결과")
    if prompt:
        st.markdown(
            f"""
            <div style="background-color: #ADD8E6; padding: 20px; border-radius: 5px;">
                {prompt}
            </div>
            """,
            unsafe_allow_html=True
        )
        list_load()
