from langchain_community.vectorstores import Qdrant
from langchain.text_splitter import RecursiveCharacterTextSplitter, CharacterTextSplitter
from langchain_community.embeddings import HuggingFaceBgeEmbeddings
from langchain_community.document_loaders import PyPDFDirectoryLoader, TextLoader
from langchain_community.embeddings import GPT4AllEmbeddings
import os
from docx import Document
from dotenv import load_dotenv
from langchain_community.document_loaders import DirectoryLoader,PyPDFLoader,TextLoader,CSVLoader,Docx2txtLoader
import re

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

def count_words(text):
    # Sử dụng biểu thức chính quy để tìm tất cả các từ
    words = re.findall(r'\b\w+\b', text)
    return len(words)

# Biểu thức chính quy để tìm "Phần" và tiêu đề
part_pattern = re.compile(
    r'^(?:#{1,6}\s*)?(?i:PHẦN)\s+(?:THỨ\s+(\w+)|(\d+))\s*(?:[:\-]\s*)?(.*)$',
    re.MULTILINE
)

# Biểu thức chính quy để tìm các phần theo số La Mã và số Arab (I, II, III,... hoặc 1, 2, 3,...)
section_pattern = re.compile(r'(\b(?:I{1,3}|IV|V?I{0,3}|[1-9]|[1-9][0-9])[\).])')

def split_text_into_parts(text, max_len=512, overlap=50):
    """
    Hàm này chia văn bản thành các phần nhỏ dựa trên các tiêu đề "Phần", số La Mã và số Arab.
    Nếu một phần vượt quá độ dài max_len, chia nó thành nhiều khổ nhỏ với sự chồng lấn.
    """
    parts = []
    current_part = []
    part_title = None
    chunk_count = 0  # Đếm số phần (chunk) đã được chia

    # Duyệt qua các dòng và chia theo tiêu đề
    for line in text.split('\n'):
        # Tìm kiếm các phần tiêu đề "Phần"
        part_match = part_pattern.match(line.strip())
        if part_match:
            # Nếu tìm thấy tiêu đề phần
            if current_part:
                # Nếu phần hiện tại đã có văn bản, kiểm tra độ dài và chia nếu cần
                part_text = "\n".join(current_part)
                if count_words(part_text) > max_len:
                    chunks = chunking(part_text, max_len, overlap)
                    parts.extend(chunks)
                    chunk_count += len(chunks)  # Cập nhật số lượng chunk
                else:
                    parts.append(part_text)
                    chunk_count += 1  # Cập nhật số lượng chunk
                current_part = []
            part_title = part_match.group(3)  # Lấy tiêu đề phần (sau "Phần")

        # Kiểm tra phần với số La Mã hoặc số Arab
        section_match = section_pattern.match(line.strip())
        if section_match:
            # Nếu là một phần của văn bản có số La Mã hoặc số Arab
            if current_part:
                # Nếu phần hiện tại đã có văn bản, kiểm tra độ dài và chia nếu cần
                part_text = "\n".join(current_part)
                if count_words(part_text) > max_len:
                    chunks = chunking(part_text, max_len, overlap)
                    parts.extend(chunks)
                    chunk_count += len(chunks)  # Cập nhật số lượng chunk
                else:
                    parts.append(part_text)
                    chunk_count += 1  # Cập nhật số lượng chunk
                current_part = []
            current_part.append(line.strip())
        elif line.strip():  # Chỉ thêm dòng không trống vào phần hiện tại
            # Nếu không phải tiêu đề phần, thêm vào phần hiện tại
            current_part.append(line.strip())

    # Thêm phần còn lại vào kết quả
    if current_part:
        part_text = "\n".join(current_part)
        if count_words(part_text) > max_len:
            chunks = chunk_with_overlap(part_text, max_len, overlap)
            parts.extend(chunks)
            chunk_count += len(chunks)  # Cập nhật số lượng chunk
        else:
            parts.append(part_text)
            chunk_count += 1  # Cập nhật số lượng chunk

    print(f"Số lượng chunk đã được tạo: {chunk_count}")  # In số lượng chunk đã tạo
    return parts

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
texts=split_text_into_parts(documents)
load_to_qrant(texts)
        
