# -------------------------------
# Import Required Libraries
# -------------------------------

import os                     # For interacting with the operating system and file paths (not directly used in this script)
import json                   # For parsing JSON content
import PyPDF2                 # Library to read and extract text from PDF files
import pandas as pd           # For reading and manipulating CSV and tabular data
import re                     # For regex operations like cleaning text
import logging                # For logging information, warnings, or errors
import nltk                   # Natural Language Toolkit, used for tokenizing text
from bs4 import BeautifulSoup # For parsing HTML and cleaning it from tags like <script>, <style>
from nltk.tokenize import sent_tokenize  # NLTK's sentence-level tokenizer
from io import StringIO       # Allows treating a string as a file (used for reading CSV from a string)

# -------------------------------
# Logging Setup
# -------------------------------

# Set up logging configuration
# - Shows logs with level INFO or above
# - Custom format for clarity
logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')

# -------------------------------
# NLTK Punkt Tokenizer Setup
# -------------------------------

# Make sure the sentence tokenizer is downloaded before using it
# It’s needed for splitting text into sentences (tokenizing)
try:
    nltk.data.find('tokenizers/punkt')  # Check if tokenizer is available
except LookupError:
    logging.info("Downloading NLTK punkt tokenizer...")
    nltk.download('punkt')  # Download if not found

# -------------------------------
# Function: Extract Text from PDF
# -------------------------------

def extract_text_from_pdf(file) -> str:
    """
    Extract text from a PDF file or file-like object.
    Iterates through all pages and extracts the visible text.
    """
    text = ""
    try:
        pdf_reader = PyPDF2.PdfReader(file)  # Load the PDF file
        for page in pdf_reader.pages:
            # Extract text from each page (or empty string if None)
            page_text = page.extract_text() or ''
            text += page_text  # Append to overall text
    except Exception as e:
        logging.error(f"PDF extraction failed: {e}")  # Log errors
    return text  # Return the full extracted text

# -------------------------------
# Function: Extract Text from HTML
# -------------------------------

def extract_text_from_html(html_content: str) -> str:
    """
    Extract readable and visible text from raw HTML content.
    Strips out scripts, styles, and unnecessary tags.
    """
    try:
        soup = BeautifulSoup(html_content, 'html.parser')  # Parse HTML

        # Remove script, style, and noscript tags to avoid clutter
        for tag in soup(['script', 'style', 'noscript']):
            tag.decompose()  # Remove the tag from the DOM

        # Extract text from HTML, separating blocks with spaces
        text = soup.get_text(separator=' ')
        return ' '.join(text.split())  # Normalize whitespace
    except Exception as e:
        logging.error(f"HTML extraction failed: {e}")
        return ""

# -------------------------------
# Function: Extract Text from CSV
# -------------------------------

def extract_text_from_csv(csv_content: str, delimiter=',', include_headers=True) -> str:
    """
    Extracts text from a CSV string.
    Optionally includes column headers. Each row becomes a sentence-like string.
    """
    try:
        df = pd.read_csv(StringIO(csv_content), delimiter=delimiter)  # Read CSV from string

        rows = []
        if include_headers:
            rows.append(', '.join(df.columns))  # Add column names

        # Convert each row to a comma-separated string
        rows += df.astype(str).apply(lambda row: ', '.join(row), axis=1).tolist()

        return ' '.join(rows)  # Join all rows into one text blob
    except Exception as e:
        logging.error(f"CSV extraction failed: {e}")
        return ""

# -------------------------------
# Function: Extract Text from JSON
# -------------------------------

def extract_text_from_json(json_content: str) -> str:
    """
    Flatten and extract text from a JSON string.
    Handles nested dictionaries and lists using recursion.
    """
    try:
        data = json.loads(json_content)  # Parse JSON string into Python dict/list

        # Recursive function to flatten nested JSON structure
        def flatten_json(obj, parent_key=''):
            items = []

            if isinstance(obj, dict):
                for k, v in obj.items():
                    new_key = f"{parent_key}.{k}" if parent_key else k  # Build key path
                    items.extend(flatten_json(v, new_key))  # Recurse
            elif isinstance(obj, list):
                for i, v in enumerate(obj):
                    items.extend(flatten_json(v, f"{parent_key}[{i}]"))  # Recurse with index
            else:
                # Base case: non-list, non-dict (e.g., string, int, float)
                items.append(f"{parent_key}: {str(obj)}")
            return items

        flat_text = '\n'.join(flatten_json(data))  # Combine flattened entries into text
        return flat_text
    except Exception as e:
        logging.error(f"JSON extraction failed: {e}")
        return ""

# -------------------------------
# Function: Extract Text from TXT
# -------------------------------

def extract_text_from_txt(file_path: str) -> str:
    """
    Read and return plain text from a .txt file.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()  # Return entire file content
    except Exception as e:
        logging.error(f"TXT extraction failed: {e}")
        return ""

# -------------------------------
# Function: Clean Raw Text
# -------------------------------

def clean_text(text: str) -> str:
    """
    Clean and normalize text.
    Removes extra whitespace, line breaks, and tabs.
    """
    try:
        text = re.sub(r'\s+', ' ', text)  # Replace all whitespace with a single space
        return text.strip()  # Remove leading/trailing spaces
    except Exception as e:
        logging.error(f"Text cleaning failed: {e}")
        return text  # Return original text on failure

# -------------------------------
# Function: Tokenize Text into Sentences
# -------------------------------

def tokenize_sentences(text: str) -> list:
    """
    Split a large text block into individual sentences using NLTK.
    """
    try:
        return sent_tokenize(text)  # Return list of sentences
    except Exception as e:
        logging.error(f"Sentence tokenization failed: {e}")
        return [text]  # If tokenization fails, return whole text as one item
