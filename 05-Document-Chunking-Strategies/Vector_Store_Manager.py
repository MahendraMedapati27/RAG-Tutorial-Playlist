# -------------------------------
# Imports
# -------------------------------

import os  # For handling file paths (not directly used but useful for dir checks)

# Import Chroma vector store and embedding model from LangChain's community package
from langchain_community.vectorstores import Chroma                       # Chroma = persistent vector DB
from langchain_community.embeddings import HuggingFaceEmbeddings         # For generating vector embeddings
from langchain.schema import Document                                    # LangChain's Document object for storing text and metadata


# -------------------------------
# Function: Save Chunks to Vector Store
# -------------------------------

def save_chunks_to_vectorstore(chunks, persist_dir="./chroma_groq_db"):
    """
    Embeds document chunks and saves them into a Chroma vector store.
    
    Parameters:
    - chunks (list): List of dictionaries, each containing chunked text and metadata.
    - persist_dir (str): Directory where the vector store should be saved.

    Returns:
    - vectorstore: The Chroma vector store object containing all embedded documents.
    """

    # Initialize HuggingFace embeddings (MiniLM is small and fast, ideal for many RAG apps)
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

    # Convert text chunks to LangChain Document objects
    documents = []
    for chunk in chunks:
        doc = Document(
            page_content=chunk['text'],  # The actual text content
            metadata=chunk               # All metadata (like position, method, etc.)
        )
        documents.append(doc)

    # Create and persist the Chroma vector store using the embedded documents
    vectorstore = Chroma.from_documents(
        documents=documents,            # List of Document objects to store
        embedding=embeddings,           # Embedding model used to encode text
        persist_directory=persist_dir   # Where to store the database files
    )

    # Feedback in console
    print(f"✅ Saved {len(chunks)} chunks to vector store at {persist_dir}")

    return vectorstore
