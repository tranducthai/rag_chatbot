from langchain_community.vectorstores import Qdrant
from langchain.text_splitter import RecursiveCharacterTextSplitter, CharacterTextSplitter
from langchain_community.embeddings import HuggingFaceBgeEmbeddings
from langchain_community.document_loaders import PyPDFDirectoryLoader, TextLoader
from langchain_community.embeddings import GPT4AllEmbeddings
import os
from docx import Document
from dotenv import load_dotenv
from langchain_community.document_loaders import DirectoryLoader,PyPDFLoader,TextLoader,CSVLoader,Docx2txtLoader

load_dotenv()

def clean_text(text):
    """
    Hàm tiền xử lý văn bản:
    - Loại bỏ tab, khoảng trắng dư thừa.
    - Giữ lại dấu câu để tránh làm đoạn văn bản quá ngắn.
    - Chuyển xuống dòng "\n" thành dấu chấm "." để tránh mất nghĩa.
    """
    text = text.replace("\n", ". ")  # Giữ lại cấu trúc câu bằng dấu chấm
    text = text.replace("\t", " ")  # Loại bỏ tab
    text = " ".join(text.split())  # Xóa khoảng trắng dư thừa
    return text 

def document_loader(file_path="docs/"):
    documents = []

    txt_loader = DirectoryLoader(file_path, glob="**/*.txt", loader_cls=TextLoader, show_progress=True)
    pdf_loader = DirectoryLoader(file_path, glob="**/*.pdf", loader_cls=PyPDFLoader, show_progress=True)
    csv_loader = DirectoryLoader(file_path, glob="**/*.csv", loader_cls=CSVLoader, show_progress=True, loader_kwargs={"encoding": "utf8"})
    doc_loader = DirectoryLoader(file_path, glob="**/*.docx", loader_cls=Docx2txtLoader, show_progress=True)

    # Tải dữ liệu từ các loader
    for loader in [txt_loader, pdf_loader, csv_loader, doc_loader]:
        try:
            docs = loader.load()
            # Tiền xử lý từng tài liệu
            for doc in docs:
                doc.page_content = clean_text(doc.page_content)  # Áp dụng tiền xử lý văn bản
            documents.extend(docs)
        except Exception as e:
            print(f"Lỗi khi tải dữ liệu từ {loader}: {e}")
    
    return documents

def chunking(documents):
    text_splitter=RecursiveCharacterTextSplitter(chunk_size=2000,chunk_overlap=800)
    texts=text_splitter.split_documents(documents)
    print(len(texts))
    return texts

def load_to_qrant(texts):
    embedding_model = GPT4AllEmbeddings(model_file = "sentence-transformers/paraphrase-multilingual-mpnet-base-v2")
    qdrant = Qdrant.from_documents(
    texts,
    embedding_model,
    url=os.getenv("QDRANT_URL"),
    prefer_grpc=False,
    collection_name="stsv_vector_db_v1",
    api_key=os.getenv("QDRANT_API_KEY"),
    )
    print("Tạo vector database thành công!")

documents=document_loader()
texts=chunking(documents)
load_to_qrant(texts)
        