# RAG System with Advanced Document Chunking Strategies

[![Medium](https://img.shields.io/badge/Medium-12100E?style=for-the-badge&logo=medium&logoColor=white)](https://medium.com/@mahendramedapati)
[![YouTube](https://img.shields.io/badge/YouTube-FF0000?style=for-the-badge&logo=youtube&logoColor=white)](https://www.youtube.com/@tech_with_mahendra)
[![GitHub](https://img.shields.io/badge/GitHub-100000?style=for-the-badge&logo=github&logoColor=white)](https://github.com/MahendraMedapati27)

A comprehensive Retrieval-Augmented Generation (RAG) system that demonstrates different document chunking strategies for optimal information retrieval. This project implements multiple chunking techniques including fixed-size, semantic, and structure-aware chunking methods.

> 🎥 **Watch the full tutorial**: [Document Chunking Strategies - Getting It Right](https://www.youtube.com/@tech_with_mahendra)  
> 📖 **Read the detailed guide**: [Mastering Document Chunking for RAG Systems](https://medium.com/@mahendramedapati)

## 🎯 Project Overview

This RAG system showcases the critical importance of document chunking in building effective question-answering systems. By implementing various chunking strategies, users can compare performance and choose the optimal approach for their specific use case.

## ✨ Features

- **Multiple Chunking Strategies**: Fixed-size, sentence-based, paragraph-based chunking
- **Overlapping Windows**: Smart context preservation across chunk boundaries
- **Document Type Support**: PDF, HTML, plain text with format-specific processing
- **Interactive Streamlit Interface**: User-friendly web interface for testing
- **Vector Database Integration**: ChromaDB for efficient similarity search
- **Metadata Preservation**: Complete tracking of chunk origins and properties
- **Real-time Comparison**: Side-by-side comparison of different chunking approaches

## 🏗️ Architecture

```
RAG System Architecture
├── Document Processing Layer
│   ├── PDF, HTML, Text parsing
│   └── Content cleaning and normalization
├── Chunking Strategy Layer
│   ├── Fixed-size chunking
│   ├── Semantic chunking
│   └── Structure-aware chunking
├── Vector Store Layer
│   ├── Text embedding generation
│   ├── ChromaDB vector storage
│   └── Similarity search
└── RAG Interface Layer
    ├── Query processing
    ├── Context retrieval
    └── Response generation
```

## 🚀 Quick Start

### Prerequisites

```bash
python >= 3.8
pip
```

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/rag-document-chunking.git
   cd rag-document-chunking
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the Streamlit application**
   ```bash
   streamlit run app.py
   ```

4. **Access the interface**
   Open your browser and navigate to `http://localhost:8501`

## 📁 Project Structure

```
rag-document-chunking/
├── app.py                      # Main Streamlit application
├── document_processor.py       # Document parsing and processing
├── chunking_strategies.py      # Implementation of chunking methods
├── vector_store_manager.py     # ChromaDB vector store management
├── .env.example                 # Environment variables template
├── rag_chatbot.py              # RAG query processing and response generation
├── requirements.txt            # Python dependencies
├── README.md                   # Project documentation
├── chromadb/                   # Vector database storage (auto-generated)
└── assets/                     # Screenshots and documentation images
    └── streamlit_interface.png
```

## 🔧 Component Details

### Document Processor (`document_processor.py`)
- Handles multiple document formats (PDF, HTML, TXT)
- Implements content cleaning and normalization
- Preserves document structure and metadata

### Chunking Strategies (`chunking_strategies.py`)
- **Fixed-Size Chunking**: Equal-sized chunks with configurable overlap
- **Sentence-Based Chunking**: Respects sentence boundaries
- **Paragraph-Based Chunking**: Maintains paragraph structure

### Vector Store Manager (`vector_store_manager.py`)
- ChromaDB integration for vector storage
- Embedding generation and similarity search
- Metadata indexing and filtering

### RAG Chatbot (`rag_chatbot.py`)
- Query processing and context retrieval
- Response generation with source attribution
- Conversation history management

## 📊 Chunking Strategies Comparison

| Strategy | Best For | Pros | Cons |
|----------|---------|------|------|
| **Fixed-Size** | Consistent documents, speed | Fast, simple, predictable | May break context |
| **Sentence-Based** | General content | Preserves thoughts | Variable chunk sizes |
| **Paragraph-Based** | Articles, reports | Natural boundaries | Large size variation |
| **Structure-Aware** | Technical docs | Preserves formatting | Complex implementation |

## 🎮 Using the Interface

![Streamlit Interface](assets/Screenshot (272).png)
![Streamlit Interface](assets/Screenshot (273).png)

### 1. Document Upload
- Upload your documents (PDF, TXT, HTML)
- Preview document content and metadata

### 2. Chunking Strategy Selection
- Choose from available chunking methods
- Configure chunk size and overlap parameters
- Preview chunking results

### 3. Vector Store Creation
- Generate embeddings for document chunks
- Store vectors in ChromaDB
- View database statistics

### 4. Query Testing
- Ask questions about your documents
- Compare results across different chunking strategies
- View retrieved chunks and confidence scores

## ⚙️ Configuration Options

### Chunking Parameters
```python
# Fixed-size chunking
CHUNK_SIZE = 500          # Characters per chunk
OVERLAP_SIZE = 50         # Character overlap between chunks

# Semantic chunking
MAX_CHUNK_SIZE = 600      # Maximum chunk size
MIN_CHUNK_SIZE = 100      # Minimum chunk size

# Structure-aware chunking
PRESERVE_TABLES = True    # Keep tables intact
RESPECT_HEADERS = True    # Use headers as boundaries
```

### Vector Store Settings
```python
# Embedding configuration
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
VECTOR_DIMENSION = 384

# ChromaDB settings
COLLECTION_NAME = "document_chunks"
DISTANCE_METRIC = "cosine"
```

## 📈 Performance Optimization

### Chunking Best Practices
1. **Start with paragraph-based chunking** for most use cases
2. **Use 10-20% overlap** for general content
3. **Increase overlap to 25-30%** for technical documents
4. **Test with real queries** from your domain
5. **Monitor chunk size distribution** for consistency

### Vector Store Optimization
- Use appropriate embedding models for your content type
- Consider batch processing for large document sets
- Implement metadata filtering for faster retrieval
- Regular database maintenance and optimization

## 🧪 Testing and Evaluation

### Built-in Evaluation Tools
```python
# Compare chunking strategies
def evaluate_chunking_strategy(chunks, test_queries):
    """Evaluate chunking performance with test queries"""
    # Implementation in chunking_strategies.py

# Measure retrieval accuracy
def measure_retrieval_accuracy(query, relevant_chunks):
    """Calculate precision and recall metrics"""
    # Implementation in rag_chatbot.py
```

### Sample Test Queries
The system includes sample queries for different document types:
- Technical documentation
- Legal documents
- Academic papers
- Business reports

## 🔍 Troubleshooting

### Common Issues

**ChromaDB Connection Error**
```bash
# Delete existing database and restart
rm -rf chromadb/
streamlit run app.py
```

**Memory Issues with Large Documents**
```python
# Adjust chunk size in chunking_strategies.py
MAX_CHUNK_SIZE = 400  # Reduce from default 600
```

**Poor Retrieval Quality**
- Try different chunking strategies
- Adjust overlap parameters
- Check document preprocessing quality
- Experiment with embedding models

## 🤝 Contributing

We welcome contributions! Please see our contribution guidelines:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Setup
```bash
# Clone your fork
git clone https://github.com/MahendraMedapati27/rag-document-chunking.git

# Install development dependencies
pip install -r requirements-dev.txt

# Run tests
pytest tests/

# Format code
black .
flake8 .
```

## 📋 Requirements

```txt
streamlit>=1.28.0
chromadb>=0.4.15
sentence-transformers>=2.2.2
pypdf2>=3.0.1
beautifulsoup4>=4.12.2
pandas>=2.0.3
numpy>=1.24.3
plotly>=5.15.0
python-dotenv>=1.0.0
```

## 🎓 Learning Resources

This project is part of the **RAG Mastery Series**. Check out related videos:
- Video 4: Vector Databases and Embeddings
- Video 5: Document Chunking Strategies (this project)

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- ChromaDB team for the excellent vector database
- Sentence Transformers for embedding models
- Streamlit for the amazing web framework
- The open-source community for inspiration and tools

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/MahendraMedapati27/05-Document-Chunking-Strategies/issues)
- **Discussions**: [GitHub Discussions](https://github.com/MahendraMedapati27/05-Document-Chunking-Strategies/discussions)
- **Email**: techwithmahendra27@gmail.com

---

⭐ **Star this repository** if you found it helpful!

🔔 **Watch** for updates and new features

🍴 **Fork** to customize for your use case