import streamlit as st
import requests
import os
from llm import get_ans
from dotenv import load_dotenv
load_dotenv()

import streamlit as st

st.set_page_config(page_title="Chatbot RAG", page_icon="🤖")

# Tiêu đề ứng dụng
st.title("🤖 Chatbot RAG - Trợ lý AI")
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Nút "Cuộc trò chuyện mới"
if st.button("🆕 Cuộc trò chuyện mới"):
    st.session_state.chat_history = []  
    st.rerun() 

for message in st.session_state.chat_history:
    st.write(message)
    

question = st.text_input("Nhập câu hỏi của bạn:")

if st.button("Gửi"):
    if question:
        answer = get_ans(question)  # Gọi hàm `get_ans` để trả lời câu hỏi
        st.write("### 🤖 Trả lời:")
        st.write(answer)
        st.text_input("Nhập câu hỏi của bạn:", key="new_question")  # Tạo ô nhập mới
    else:
        st.warning("Hãy nhập câu hỏi trước khi gửi!")       

