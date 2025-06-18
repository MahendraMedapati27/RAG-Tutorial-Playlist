# Building Your First RAG System - Step by Step

Welcome to the practical implementation of RAG (Retrieval-Augmented Generation) systems! This repository contains all the code and resources from the RAG Mastery Series Video 4, where we build a complete RAG system from scratch.

## 🎥 Video Resources

[![YouTube Tutorial](https://img.shields.io/badge/YouTube-Tutorial-FF0000?style=for-the-badge&logo=youtube&logoColor=white)](https://youtube.com/playlist?list=PL_YSOkuDdgvOp8s_MwfcU1QtYjW0oyKB9&si=y1jZsmX_9O33X04s)
[![Medium Article](https://img.shields.io/badge/Medium-Article-12100E?style=for-the-badge&logo=medium&logoColor=white)](https://medium.com/@mahendramedapati)
[![Video Series](https://img.shields.io/badge/Playlist-RAG%20Mastery-FF0000?style=for-the-badge&logo=youtube&logoColor=white)](https://youtube.com/playlist?list=PL_YSOkuDdgvOp8s_MwfcU1QtYjW0oyKB9&si=y1jZsmX_9O33X04s)

---

## 🚀 What You'll Build

A complete RAG system that can:
- Ingest and process your personal documents
- Create semantic embeddings for intelligent search
- Store data in a vector database
- Answer questions based on your document content
- Provide source citations for transparency

## 📁 Repository Structure

```
my-first-rag-system/
├── simple_rag_openai.py          # RAG system using OpenAI embeddings (requires API credits)
├── simple_rag_groq.py            # RAG system using Groq + Sentence Transformers (completely free)
├── requirements_openai.txt       # Dependencies for OpenAI version
├── requirements_groq.txt         # Dependencies for Groq version
├── .env.example                  # Environment variables template
├── documents/                    # Sample documents for testing
│   ├── Ancient_Eygpt.txt             # Ancient Eygpt related some matter
│   ├── Climate_Change.txt      # A Paragraph related to Climate Change
│   └── Machine_Learning.txt         # A Paragraph related to Climate Change
├── chroma_db_openai/            # Vector database (created by OpenAI version)
├── chroma_db_groq/              # Vector database (created by Groq version)
└── README.md                    # This file
```

## 🛠️ Two Implementation Options

### Option 1: OpenAI Version (Paid but Premium)
- Uses OpenAI's text-embedding-ada-002 for embeddings
- Requires OpenAI API credits (~$0.0001 per 1K tokens)
- Higher quality embeddings and responses
- File: `simple_rag_openai.py`

### Option 2: Groq + Sentence Transformers (Completely Free)
- Uses local Sentence Transformers for embeddings
- Groq API for LLM (free with generous limits)
- No costs involved, runs locally
- File: `simple_rag_groq.py`

## ⚡ Quick Start

### For the Free Version (Recommended for Beginners):

1. **Clone the repository**:
   ```bash
   git clone https://github.com/yourusername/my-first-rag-system.git
   cd my-first-rag-system
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements_groq.txt
   ```

3. **Set up environment variables**:
   ```bash
   cp .env.example .env
   # Edit .env and add your free Groq API key
   ```

4. **Get your free Groq API key**:
   - Visit [console.groq.com](https://console.groq.com)
   - Sign up for free (no credit card required)
   - Generate an API key
   - Add it to your `.env` file

5. **Run the system**:
   ```bash
   python simple_rag_groq.py
   ```

### For the OpenAI Version:

1. **Install OpenAI dependencies**:
   ```bash
   pip install -r requirements_openai.txt
   ```

2. **Set up OpenAI API key**:
   - Get your API key from [platform.openai.com](https://platform.openai.com)
   - Add it to your `.env` file

3. **Run the system**:
   ```bash
   python simple_rag_openai.py
   ```

## 🔧 Environment Setup

Create a `.env` file in the root directory:

```env
# For Groq version (free)
GROQ_API_KEY=your-groq-api-key-here

# For OpenAI version (paid)
OPENAI_API_KEY=your-openai-api-key-here
```

**Important**: Never commit your `.env` file to version control!

## 📚 Sample Documents

The repository includes three sample documents to test your RAG system:

1. **AI Facts** (`ai_facts.txt`) - Information about artificial intelligence
2. **Cooking Recipes** (`cooking_recipes.txt`) - Various recipes and cooking tips
3. **Travel Guide** (`travel_guide.txt`) - Travel tips and destination information

Feel free to replace these with your own documents!

## 💡 Example Queries to Try

Once your system is running, try these questions:

- "What are the main benefits of artificial intelligence?"
- "How do I make chocolate chip cookies?"
- "What should I pack for a beach vacation?"
- "Tell me about machine learning applications"
- "What ingredients do I need for pasta?"

## 🎯 System Architecture

```
Documents → Chunking → Embeddings → Vector DB → Retrieval → LLM → Answer
     ↓           ↓          ↓           ↓          ↓        ↓       ↓
  Load .txt   Split     Convert    Store in   Search    Generate  Display
   files      text     to vectors  Chroma   similar   response  with sources
```

## 🔧 Customization Options

### Adjusting Chunk Size
```python
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,        # Increase for more context
    chunk_overlap=200,      # Adjust overlap as needed
    length_function=len,
)
```

### Changing Retrieval Count
```python
retriever = vectorstore.as_retriever(
    search_kwargs={"k": 3}  # Retrieve more/fewer chunks
)
```

### Different LLM Models (Groq)
```python
# Available free models:
# - llama-3.1-70b-versatile (high quality)
# - llama-3.1-8b-instant (faster)
# - mixtral-8x7b-32768 (good balance)
```

## 🐛 Troubleshooting

### Common Issues:

**"Invalid API key"**
- Verify your API key in the `.env` file
- Ensure you're using the correct service (Groq vs OpenAI)

**"No relevant documents found"**
- Check if your documents contain information related to your question
- Try rephrasing your query
- Verify documents are in the `documents/` folder

**Slow first run (Groq version)**
- Sentence Transformers downloads models on first use
- Subsequent runs will be much faster

**Installation issues**
- Try upgrading pip: `pip install --upgrade pip`
- Use virtual environment: `python -m venv rag_env`

## 📈 Performance Tips

1. **Document Quality**: Use well-structured, clear text documents
2. **Chunk Size**: Experiment with different sizes based on your content
3. **Query Phrasing**: Be specific in your questions
4. **Model Selection**: Try different Groq models for your use case

## 🚀 Next Steps

Ready to enhance your RAG system? Check out these improvements:

- [ ] Add support for PDF and Word documents
- [ ] Implement metadata filtering
- [ ] Create a web interface with Streamlit
- [ ] Add conversation memory
- [ ] Implement advanced chunking strategies
- [ ] Add multi-language support

## 📝 Dependencies

### Groq Version (Free):
- `langchain` - RAG framework
- `groq` - Free LLM API
- `chromadb` - Vector database
- `sentence-transformers` - Local embeddings
- `python-dotenv` - Environment management

### OpenAI Version (Paid):
- `langchain` - RAG framework
- `openai` - OpenAI API
- `chromadb` - Vector database
- `python-dotenv` - Environment management

## 🤝 Contributing

Found an issue or have an improvement? Feel free to:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- LangChain team for the amazing framework
- Groq for providing free, fast LLM inference
- Chroma for the excellent vector database
- The open-source community for making this possible

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/MahendraMedapati27/my-first-rag-system/issues)
- **Discussions**: [GitHub Discussions](https://github.com/MahendraMedapati27/my-first-rag-system/discussions)
- **Video Comments**: Leave questions on the YouTube video
- **Article Comments**: Engage on the Medium article

---

⭐ **If this helped you build your first RAG system, please star the repository!**

Happy coding! 🎉