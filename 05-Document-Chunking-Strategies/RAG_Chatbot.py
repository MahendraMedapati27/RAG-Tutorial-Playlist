# -------------------------------
# Imports
# -------------------------------

import os                              # To work with environment variables
from dotenv import load_dotenv         # Load variables from a .env file (e.g., API keys)

# Chroma vector DB and embeddings
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings

# RAG chain wrapper
from langchain.chains import RetrievalQA

# Groq integration (uses LLaMA3)
from langchain_groq import ChatGroq

# Optional: for OpenAI backend
# from langchain_openai import ChatOpenAI

# -------------------------------
# Load environment variables
# -------------------------------

load_dotenv()  # Loads API keys or config from .env file

# -------------------------------
# Load Vector Database
# -------------------------------

def load_vector_db(persist_dir="./chroma_groq_db"):
    """
    Load a persisted Chroma vector database with embedded documents.

    Parameters:
    - persist_dir: path where Chroma vector DB is stored.

    Returns:
    - Retriever object to fetch relevant documents using vector similarity.
    """
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")  # Load embedding model

    # Load the existing Chroma DB and associate it with embedding function
    vectorstore = Chroma(persist_directory=persist_dir, embedding_function=embeddings)

    # Return a retriever that will return top 3 similar chunks
    return vectorstore.as_retriever(search_kwargs={"k": 3})

# -------------------------------
# Set Up RetrievalQA Chain
# -------------------------------

def get_qa_chain(use_groq=True):
    """
    Initialize a RetrievalQA chain using Groq (LLaMA3) or OpenAI (GPT-3.5).
    
    Parameters:
    - use_groq: Boolean, whether to use Groq LLaMA3 or OpenAI's GPT.

    Returns:
    - RetrievalQA chain that uses the retriever and LLM to answer questions.
    """
    retriever = load_vector_db()  # Load retriever (vector search)

    # Choose which LLM to use
    if use_groq:
        llm = ChatGroq(
            model_name="llama3-8b-8192",  # Groq supports LLaMA3 model
            temperature=0.7               # Creativity level
        )
    else:
        from langchain_openai import ChatOpenAI  # Lazy import to avoid import error
        llm = ChatOpenAI(
            model_name="gpt-3.5-turbo",
            temperature=0.7
        )

    # Build the QA chain using "stuff" strategy (concatenate documents)
    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        retriever=retriever,
        return_source_documents=True,  # Include source chunks in the response
        chain_type="stuff"             # "stuff" = concatenate retrieved docs into a prompt
    )

    return qa_chain

# -------------------------------
# Main Query Handler
# -------------------------------

def answer_question(query: str, use_groq=True):
    """
    Answers a question by retrieving relevant chunks and generating an answer.

    Parameters:
    - query: user's natural language question
    - use_groq: whether to use Groq or OpenAI as the backend LLM

    Returns:
    - Dictionary with:
        - 'answer': LLM's answer
        - 'sources': list of source Document objects used to answer
    """
    chain = get_qa_chain(use_groq=use_groq)  # Set up RAG chain
    result = chain.invoke({"query": query})  # Send the query to the chain

    # Parse response
    answer = result["result"]
    sources = result["source_documents"]

    return {
        "answer": answer,
        "sources": sources
    }
