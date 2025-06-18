# Core imports
import os
from dotenv import load_dotenv  # Load environment variables from .env file

# Updated LangChain imports (v0.2+)
from langchain_community.document_loaders import TextLoader  # Loads plain text files
from langchain.text_splitter import RecursiveCharacterTextSplitter  # Splits documents into chunks
from langchain_community.embeddings import OpenAIEmbeddings  # OpenAI embedding model
from langchain_community.vectorstores import Chroma  # Vector store to persist embeddings
from langchain_openai import ChatOpenAI  # OpenAI LLM wrapper for LangChain
from langchain.chains import RetrievalQA  # Retrieval-augmented QA chain

# Load environment variables like OPENAI_API_KEY
load_dotenv()


# Function to load all .txt files from a directory as LangChain documents
def load_documents(directory_path):
    documents = []
    for filename in os.listdir(directory_path):
        if filename.endswith('.txt'):  # Only pick .txt files
            loader = TextLoader(os.path.join(directory_path, filename))
            documents.extend(loader.load())  # Load and extend the document list
    print(f"Loaded {len(documents)} documents")
    return documents


# Function to split large documents into manageable overlapping chunks
def chunk_documents(documents):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,     # Max tokens per chunk
        chunk_overlap=200    # Overlap for context continuity
    )
    chunks = splitter.split_documents(documents)
    print(f"Split into {len(chunks)} chunks")
    return chunks


# Create Chroma vector store using OpenAI embeddings
def create_vector_store(chunks):
    embeddings = OpenAIEmbeddings()  # Use default embedding model from OpenAI
    vectorstore = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory="./chroma_openai_db"  # Store vector DB locally
    )
    print("Vector store created and persisted.")
    return vectorstore


# Build a retrieval-based QA chain using OpenAI's GPT model
def setup_qa_chain(vectorstore):
    llm = ChatOpenAI(
        model_name="gpt-3.5-turbo",  # You can change this to "gpt-4" if needed
        temperature=0.1              # Lower temperature for more accurate results
    )
    
    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",  # Combines all retrieved chunks into one prompt
        retriever=vectorstore.as_retriever(search_kwargs={"k": 3}),  # Retrieve top 3 relevant docs
        return_source_documents=True  # Return source docs for traceability
    )
    
    return qa_chain


# Main application loop
def main():
    print("Loading documents...")
    documents = load_documents("./documents")  # Load all documents in ./documents

    print("Chunking documents...")
    chunks = chunk_documents(documents)  # Split into manageable chunks

    print("Creating vectorstore...")
    vectorstore = create_vector_store(chunks)  # Generate and persist vector database

    print("Setting up QA chain...")
    qa_chain = setup_qa_chain(vectorstore)  # Create the RAG pipeline

    print("\nRAG System (OpenAI) Ready! Ask me anything.")
    print("Type 'quit' to exit.\n")
    
    while True:
        query = input("Your question: ")
        if query.lower() == 'quit':
            break

        result = qa_chain.invoke({"query": query})  # Use `invoke()` as recommended
        print("\nAnswer:", result["result"])
        
        print("\nSources:")
        for i, doc in enumerate(result["source_documents"]):
            print(f"{i+1}. {doc.page_content[:150]}...")  # Show a snippet of source
        print("-" * 50)


# Run the script only if this is the entry point
if __name__ == "__main__":
    main()
