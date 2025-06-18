# Standard libraries
import os  # For interacting with the file system
from dotenv import load_dotenv  # For loading environment variables from a .env file

# LangChain community modules
from langchain_community.document_loaders import TextLoader  # Loads text documents
from langchain.text_splitter import RecursiveCharacterTextSplitter  # Splits text into smaller chunks
from langchain_community.embeddings import HuggingFaceEmbeddings  # Embedding model from HuggingFace
from langchain_community.vectorstores import Chroma  # Chroma vector database for storing document embeddings

# LLM and chain
from langchain_groq import ChatGroq  # ChatGroq connects to Groq’s LLMs (e.g., LLaMA3)
from langchain.chains import RetrievalQA  # Retrieval-based QA chain

# Load environment variables (e.g., GROQ_API_KEY from .env file)
load_dotenv()


# Function to load all `.txt` files from the given directory
def load_documents(directory_path):
    documents = []
    for filename in os.listdir(directory_path):
        if filename.endswith('.txt'):  # Only consider text files
            loader = TextLoader(os.path.join(directory_path, filename))  # Load text file
            documents.extend(loader.load())  # Append loaded document(s) to list
    print(f"Loaded {len(documents)} documents")
    return documents


# Function to split large documents into manageable chunks
def chunk_documents(documents):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,     # Max characters per chunk
        chunk_overlap=200    # Overlap between chunks for better context
    )
    chunks = splitter.split_documents(documents)  # Perform splitting
    print(f"Split into {len(chunks)} chunks")
    return chunks


# Function to create vector store using HuggingFace embeddings + Chroma DB
def create_vector_store(chunks):
    # Load a small, fast sentence transformer model
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    
    # Store chunks + their embeddings in Chroma DB
    vectorstore = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory="./chroma_groq_db"  # Location to store the vector DB on disk
    )
    
    print("Vector store created and persisted.")
    return vectorstore


# Function to set up the retrieval-based question-answering chain using Groq LLaMA3
def setup_qa_chain(vectorstore):
    llm = ChatGroq(
        model_name="llama3-8b-8192",  # Use Groq's LLaMA3 model
        temperature=0.1               # Low temperature = more deterministic responses
    )
    
    # Create a RetrievalQA chain with source document return
    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",  # Stuff = combine all retrieved docs as input to LLM
        retriever=vectorstore.as_retriever(search_kwargs={"k": 3}),  # Use top 3 relevant chunks
        return_source_documents=True  # Return sources for transparency
    )
    
    return qa_chain


# Main logic
def main():
    print("Loading documents...")
    documents = load_documents("./documents")  # Step 1: Load from ./documents directory

    print("Chunking documents...")
    chunks = chunk_documents(documents)  # Step 2: Split into chunks

    print("Creating vectorstore...")
    vectorstore = create_vector_store(chunks)  # Step 3: Convert chunks to vector DB

    print("Setting up QA chain...")
    qa_chain = setup_qa_chain(vectorstore)  # Step 4: Connect Groq LLM to Chroma retriever

    # Step 5: Ask questions in a loop
    print("\nRAG System (Groq + HuggingFace) Ready! Ask me anything.")
    print("Type 'quit' to exit.\n")
    
    while True:
        query = input("Your question: ")  # Take user input
        if query.lower() == 'quit':       # Stop if user types 'quit'
            break

        # Use `invoke` instead of deprecated __call__
        result = qa_chain.invoke({"query": query})

        # Print the final answer
        print("\nAnswer:", result["result"])
        
        # Show source document snippets
        print("\nSources:")
        for i, doc in enumerate(result["source_documents"]):
            print(f"{i+1}. {doc.page_content[:150]}...")  # Preview first 150 characters
        print("-" * 50)


# Run the script if it’s the main file
if __name__ == "__main__":
    main()
