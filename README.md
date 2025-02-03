# RAG Chatbot - Hệ thống Truy Xuất và Tạo Văn Bản
## Cài đặt
- git clone https://github.com/tranducthai/rag_chatbot.git
- cd rag_chatbot

- python -m venv venv
- source venv/bin/activate  # trên Linux/macOS
- venv\Scripts\activate     # trên Windows

## Cấu hình tệp môi trường
Tạo tệp .env trong thư mục gốc của dự án và thêm các thông
- GEMINI_API_KEY
- QDRANT_API_KEY
- QRANT_URL
Thêm các tài liệu cần truy xuất vào folder docs

## Chạy ứng dụng
python m streamlit run app.py
