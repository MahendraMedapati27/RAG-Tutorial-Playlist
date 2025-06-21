# -------------------------------
# Imports
# -------------------------------

import streamlit as st                           # Streamlit for interactive UI
import os                                        # OS module (not used directly here, might be used by other modules)

# Import custom modules for document processing and RAG pipeline
from Document_Processor import (
    extract_text_from_pdf, extract_text_from_html,
    extract_text_from_csv, extract_text_from_json,
    clean_text
)
from Chunking_Strategies import (
    fixed_size_chunking, sentence_based_chunking, paragraph_based_chunking
)
from Vector_Store_Manager import save_chunks_to_vectorstore  # To store processed chunks into a vector DB
from RAG_Chatbot import answer_question                      # To query the documents using a chatbot interface

# -------------------------------
# UI Setup (Streamlit)
# -------------------------------

# Configure Streamlit page title and layout
st.set_page_config(page_title="📚 Chunk & Chat with Your Docs", layout="wide")

# Main title at the top
st.title("📚 RAG-powered Document Playground")

# Create two tabs: one for chunking/uploading, another for chatting
tab1, tab2 = st.tabs(["📄 Chunk & Save", "🤖 Chatbot"])

# -------------------------------
# Tab 1: Chunk & Save
# -------------------------------

with tab1:
    st.header("📄 Upload & Chunk Your Document")

    # File upload widget - allows specific types
    uploaded_file = st.file_uploader(
        "Choose a file (txt, pdf, html, csv, json)",
        type=["txt", "pdf", "html", "csv", "json"]
    )

    # Dropdown to choose the chunking method
    strategy = st.selectbox("Choose Chunking Strategy", [
        "Fixed Size", "Sentence Based", "Paragraph Based"
    ])

    # Show parameter sliders based on selected strategy
    if strategy == "Fixed Size":
        chunk_size = st.slider("Chunk Size", 100, 2000, 500)           # Number of characters per chunk
        overlap = st.slider("Chunk Overlap", 0, 500, 50)               # Overlap between chunks
    elif strategy == "Sentence Based":
        max_sentences = st.slider("Max Sentences per Chunk", 1, 10, 5) # Number of sentences in each chunk
        overlap_sentences = st.slider("Overlap Sentences", 0, 3, 1)    # Number of repeated sentences between chunks
    else:
        overlap_paragraphs = st.slider("Overlap Paragraphs", 0, 2, 0)  # Paragraph-level overlap

    # ------------------- File Processing & Chunking ------------------- #

    if uploaded_file:
        file_type = uploaded_file.type  # Get MIME type of file

        try:
            # Based on MIME type, apply appropriate extraction method
            if file_type == "application/pdf":
                raw_text = extract_text_from_pdf(uploaded_file)
            elif file_type == "text/html":
                file_content = uploaded_file.read()
                raw_text = extract_text_from_html(file_content.decode('utf-8'))
            elif file_type == "text/csv":
                file_content = uploaded_file.read()
                raw_text = extract_text_from_csv(file_content.decode('utf-8'))
            elif file_type == "application/json":
                file_content = uploaded_file.read()
                raw_text = extract_text_from_json(file_content.decode('utf-8'))
            else:  # For .txt files
                file_content = uploaded_file.read()
                raw_text = file_content.decode('utf-8')

            # Clean the extracted raw text
            cleaned = clean_text(raw_text)

            # Apply the selected chunking strategy
            if strategy == "Fixed Size":
                chunks = fixed_size_chunking(cleaned, chunk_size, overlap)
            elif strategy == "Sentence Based":
                chunks = sentence_based_chunking(cleaned, max_sentences, overlap_sentences)
            else:
                chunks = paragraph_based_chunking(cleaned, overlap_paragraphs)

            # Display how many chunks were created
            st.success(f"✅ {len(chunks)} chunks created.")

            # Preview first 5 chunks using expanders
            for i, chunk in enumerate(chunks[:5]):
                with st.expander(f"Chunk {i+1}"):
                    st.write(chunk['text'])

            # Button to save chunks to a persistent Chroma Vector DB
            if st.button("📥 Save to Vector DB"):
                save_chunks_to_vectorstore(chunks, persist_dir="./chroma_groq_db")
                st.success("Chunks embedded and stored in Chroma Vector DB!")

        except Exception as e:
            st.error(f"❌ Failed to process file: {e}")

# -------------------------------
# Tab 2: Chatbot
# -------------------------------

with tab2:
    st.header("🤖 Chat with Your Vector DB")

    # Optional settings section to choose LLM backend
    with st.expander("⚙️ Settings"):
        use_groq = st.radio(
            "Choose LLM Backend", 
            ["Groq (LLaMA3)", "OpenAI (GPT-3.5)"]
        ) == "Groq (LLaMA3)"  # Returns True if Groq is selected

    # User prompt for a natural language question
    user_query = st.text_input("💬 Enter your question about the documents:")

    if user_query:
        with st.spinner("Thinking..."):
            try:
                # Call the RAG pipeline to get an answer
                result = answer_question(user_query, use_groq=use_groq)

                # Display the main answer
                st.success(result['answer'])

                # Show the chunks (documents) used to answer
                with st.expander("📚 Source Chunks"):
                    for i, doc in enumerate(result['sources']):
                        st.markdown(f"**Chunk {i+1}**")
                        st.write(str(doc)[:500])  # Truncate long texts

            except Exception as e:
                st.error(f"❌ Error answering question: {e}")
