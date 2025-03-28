# RAG Chatbot - Retrieval-Augmented Generation System

## Installation

- `git clone https://github.com/tranducthai/rag_chatbot.git`
- `cd rag_chatbot`
- `python -m venv venv`
- Activate the virtual environment:
  - On Linux/macOS: `source venv/bin/activate`
  - On Windows: `venv\Scripts\activate`

## Configure Environment Variables

- Create a `.env` file in the root directory and add:
  ```
  GEMINI_API_KEY=your_api_key_here
  QDRANT_API_KEY=your_api_key_here
  QDRANT_URL=your_qdrant_url_here
  ```

## Add Documents for Retrieval

- Place the documents in the `docs` folder.

## Run the Application

- `streamlit run app.py`

