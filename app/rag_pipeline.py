from langchain_openai import ChatOpenAI
from langchain_qdrant import Qdrant
from langchain_huggingface import HuggingFaceEmbeddings
from qdrant_client import QdrantClient
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

client = QdrantClient(host='host.docker.internal', port=6333)
embedding_model = HuggingFaceEmbeddings(model_name = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")

# Загрузка VectoreStore в LangChain
vector_store = Qdrant(
    client=client,
    collection_name="tsu_programs",
    embeddings=embedding_model
)

# Query prompt
query_prompt = ChatPromptTemplate.from_template(
    """Rephrase the following question so that it is as short, unambiguous, and suitable for searching the university's program database.
Use russian language.
Question: {original_question}
Rephrased:"""
)

# Augmented Prompt
prompt = ChatPromptTemplate.from_template(
    """You are helpful assistant that can answer questions about bachelors educational programs in the university.
Use the following pieces of retrieved context to hel you to answer the question. If you don't know information about program, just say "I don't know".
Give me the answer in Russian."
Question: {question}
Context: {context}
Answer:""")

query_llm = ChatOpenAI(
    model = "qwen/qwen3-8b:free",
    openai_api_key = "YOUR_API",
    openai_api_base = "YOUR_API",
    temperature=0.3,
    max_tokens = 512,
)

# Model
llm = ChatOpenAI(
    model = "qwen/qwen3-8b:free",
    openai_api_key = "YOUR_API",
    openai_api_base = "YOUR_API",
    temperature=0.3,
)

query_chain = query_prompt | query_llm | StrOutputParser()

def generate_answer(question: str) -> dict:
    # Query transformation
    transformed_question = query_chain.invoke({"original_question": original_question})
    # Retrieve
    retrieved_docs = vector_store.similarity_search(transformed_question, k=3)
    docs_content = "\n".join([doc.page_content for doc in retrieved_docs])
    # Augmented Prompt
    message = prompt.invoke({"question": original_question, "context": docs_content})
    # Generation
    answer = llm.invoke(message)
    return {
        'answer': answer.content,
        'sources': [doc.metadata.get('source', '') for doc in retrieved_docs]
    }