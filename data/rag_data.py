import pandas as pd
from langchain_community.vectorstores import Qdrant
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.docstore.document import Document
from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams

df = pd.read_csv('programs.csv')

docs = []
# Итерируем по строкам df
for _, row in df.iterrows():
    text = f"{row['title']}. {row['description']}"
    docs.append(Document(page_content=text, metadata={'source': row['url']}))
    
# Эмбеддинг модель
embedding_model = HuggingFaceEmbeddings(model_name = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")

#Qdrant
client = QdrantClient(host='localhost', port=6333)
client.create_collection(
    collection_name="tsu_programs",
    vectors_config=VectorParams(
        size = 384, # Размерность эмбеддинга MiniLM-L12-v2
        distance = Distance.COSINE # Косинусное сходство
    )
)

# Загрузка в Qdrant
qdrant = Qdrant.from_documents(
    documents = docs,
    embedding = embedding_model,
    url="http://localhost:6333",  # URL Qdrant сервера
    prefer_grpc=False  # Использовать HTTP вместо gRPC
)