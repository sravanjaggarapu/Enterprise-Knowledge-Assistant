from fastapi import FastAPI
from pydantic import BaseModel
from dotenv import load_dotenv
from typing import List

from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores import Chroma
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

load_dotenv()

DB_PATH = "/app/db"

app = FastAPI()

class Query(BaseModel):
    question: str
    chat_history: List[dict] = []

embeddings = OpenAIEmbeddings()
db = Chroma(persist_directory=DB_PATH, embedding_function=embeddings)
retriever = db.as_retriever()

llm = ChatOpenAI()

prompt = ChatPromptTemplate.from_template(
    """Answer the question based ONLY on the context below:

{context}

Question: {question}
"""
)

chain = (
    {"context": retriever, "question": lambda x: x}
    | prompt
    | llm
    | StrOutputParser()
)

@app.post("/ask")
def ask(query: Query):
    # Retrieve documents with metadata
    docs = db.similarity_search(query.question, k=3)
    answer = chain.invoke(query.question)
    
    # Extract source documents (PDFs)
    sources = []
    for doc in docs:
        if doc.metadata and "source" in doc.metadata:
            sources.append(doc.metadata["source"])
    
    return {
        "answer": answer,
        "sources": list(set(sources))
    }
