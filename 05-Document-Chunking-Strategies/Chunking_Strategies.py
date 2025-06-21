# -------------------------------
# Imports
# -------------------------------

import nltk                          # Natural Language Toolkit for tokenization
from nltk.tokenize import sent_tokenize  # Function to split text into sentences
import logging                       # For logging information and warnings
import re                            # For cleaning and normalizing text using regex

# -------------------------------
# Logging Configuration
# -------------------------------

# Set up logging to print INFO level messages with a clean format
logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')

# -------------------------------
# Ensure Tokenizer Availability
# -------------------------------

# Check if 'punkt' sentence tokenizer is downloaded; download if missing
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    logging.info("Downloading NLTK punkt tokenizer...")
    nltk.download('punkt')


# -------------------------------
# Text Cleaning Utility
# -------------------------------

def clean_and_normalize_text(text):
    """
    Cleans and normalizes text by:
    - Removing extra whitespaces (spaces, tabs, newlines)
    - Trimming leading and trailing spaces
    """
    text = re.sub(r'\s+', ' ', text)  # Replace multiple whitespace characters with a single space
    return text.strip()               # Remove leading/trailing spaces


# -------------------------------
# Fixed-Size Chunking
# -------------------------------

def fixed_size_chunking(text, chunk_size=500, overlap=50, min_length=100):
    """
    Breaks text into fixed-length overlapping chunks.
    
    Parameters:
    - chunk_size: number of characters in each chunk
    - overlap: number of characters repeated from the end of the last chunk
    - min_length: minimum chunk length to be considered valid
    
    Returns:
    - List of chunk dictionaries with metadata
    """
    text = clean_and_normalize_text(text)
    
    if not text:
        logging.warning("Input text is empty.")
        return []

    chunks = []
    start = 0
    
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]

        # Only add the chunk if it meets the minimum length requirement
        if chunk.strip() and len(chunk.strip()) >= min_length:
            chunks.append({
                'text': chunk,
                'start_pos': start,
                'end_pos': min(end, len(text)),
                'method': 'fixed_size'  # Metadata tag to identify chunking strategy
            })

        # Move start forward by chunk_size minus overlap for sliding effect
        start = end - overlap

        # Safety break if we’ve reached the end
        if start >= len(text):
            break

    logging.info(f"Created {len(chunks)} fixed-size chunks.")
    return chunks


# -------------------------------
# Sentence-Based Chunking
# -------------------------------

def sentence_based_chunking(text, max_sentences=5, overlap_sentences=1, min_length=100):
    """
    Breaks text into chunks of sentences (instead of characters).
    
    Parameters:
    - max_sentences: number of sentences per chunk
    - overlap_sentences: number of overlapping sentences between chunks
    - min_length: minimum character length for each chunk
    
    Returns:
    - List of chunk dictionaries with metadata
    """
    text = clean_and_normalize_text(text)
    
    if not text:
        logging.warning("Input text is empty.")
        return []

    sentences = sent_tokenize(text)  # Tokenize entire text into individual sentences
    chunks = []

    i = 0
    while i < len(sentences):
        chunk_sentences = sentences[i:i + max_sentences]  # Select a group of sentences
        chunk_text = ' '.join(chunk_sentences)  # Combine them into a single string

        if chunk_text and len(chunk_text.strip()) >= min_length:
            chunks.append({
                'text': chunk_text,
                'sentence_count': len(chunk_sentences),
                'method': 'sentence_based'  # Metadata tag for tracking method
            })

        # Advance pointer, allowing for overlap
        i += max_sentences - overlap_sentences

        # Stop if we're at the end of the sentence list
        if i >= len(sentences):
            break

    logging.info(f"Created {len(chunks)} sentence-based chunks.")
    return chunks


# -------------------------------
# Paragraph-Based Chunking
# -------------------------------

def paragraph_based_chunking(text, overlap_paragraphs=0, min_length=100):
    """
    Splits text into chunks based on paragraphs (separated by double newlines).
    
    Parameters:
    - overlap_paragraphs: number of previous paragraphs to include in the current chunk (for context)
    - min_length: minimum character length for a chunk to be included
    
    Returns:
    - List of paragraph-based chunks with indexing info
    """
    text = clean_and_normalize_text(text)
    
    if not text:
        logging.warning("Input text is empty.")
        return []

    # Split based on double newlines, which typically separate paragraphs
    paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
    chunks = []

    for i, paragraph in enumerate(paragraphs):
        chunk_text = paragraph  # Start with the current paragraph

        # If overlap is enabled, prepend previous paragraphs for context
        if overlap_paragraphs > 0 and i > 0:
            prev_paragraphs = paragraphs[max(0, i - overlap_paragraphs):i]
            chunk_text = ' '.join(prev_paragraphs) + ' ' + paragraph

        if chunk_text and len(chunk_text.strip()) >= min_length:
            chunks.append({
                'text': chunk_text,
                'paragraph_index': i,  # To track which paragraph this chunk starts at
                'method': 'paragraph_based'
            })

    logging.info(f"Created {len(chunks)} paragraph-based chunks.")
    return chunks
