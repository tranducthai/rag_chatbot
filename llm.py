import google.generativeai as genai
import os
import streamlit as st
from rag import get_retriever,rerank
from dotenv import load_dotenv
load_dotenv()

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel(model_name="gemini-1.5-flash")

def get_ans(question):
    
    history = st.session_state.chat_history

    
    docs = get_retriever(question)
    if not docs:
        return "Không tìm thấy tài liệu liên quan để trả lời câu hỏi."
    top_docs = rerank(question, docs)
    context = "\n".join(top_docs)

    # Kết hợp lịch sử hội thoại vào truy vấn
    history_context = "\n".join(history[-5:])  # Lấy 5 câu hỏi gần nhất để duy trì ngữ cảnh
    input_prompt = f"""
    LỊCH SỬ HỘI THOẠI:
    {history_context}

    CONTEXT: {context}

    QUESTION: {question}

    Hãy trả lời câu hỏi bằng tiếng Việt một cách chi tiết.
    """

    # Gửi yêu cầu đến mô hình Gemini
    response = model.generate_content(input_prompt).text

    # Lưu câu hỏi và câu trả lời vào lịch sử hội thoại
    history.append(f"Người dùng: {question}")
    history.append(f"Chatbot: {response}")

    # Giới hạn lịch sử tối đa 10 lượt trao đổi
    if len(history) > 10:
        history = history[-10:]

    # Cập nhật lại lịch sử trong session_state
    st.session_state.chat_history = history
    return response
