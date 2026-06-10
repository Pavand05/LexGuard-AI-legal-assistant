# Legal AI Assistant

A powerful AI-powered legal document analysis tool that uses LangChain and local LLMs to summarize documents, extract clauses, and provide legal Q&A capabilities.

## Features

- 📄 **Document Upload**: Support for PDF, DOCX, and TXT files
- 🤖 **AI-Powered Analysis**: Uses LangChain and local LLMs for processing
- 📊 **Document Summarization**: Generate comprehensive summaries of legal documents
- 🔍 **Clause Extraction**: Automatically identify and categorize legal clauses
- ⚠️ **Risk Assessment**: Analyze and categorize risks (high, medium, low)
- 💬 **Legal Q&A**: Ask questions about your uploaded documents
- 📈 **Interactive Dashboard**: Beautiful UI with real-time analysis
- 📤 **Export Reports**: Download analysis results in JSON format

## Tech Stack

- **Backend**: Python, Flask, LangChain
- **Frontend**: React, Tailwind CSS, Vite
- **AI**: Local LLMs (Llama-2, Mistral), Sentence Transformers
- **Document Processing**: PyMuPDF, python-docx2txt

## Quick Start

### Prerequisites

- Python 3.8 or higher
- Node.js 16 or higher
- At least 8GB RAM (for local LLM processing)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd legal-ai-assistant
   ```

2. **Setup Backend**
   ```bash
   cd backend
   python setup.py
   ```
   
   This will:
   - Install all Python dependencies
   - Download a local LLM model (optional)
   - Create configuration files

3. **Setup Frontend**
   ```bash
   cd ../frontend
   npm install
   ```

4. **Start the Application**
   
   In one terminal (backend):
   ```bash
   cd backend
   python app.py
   ```
   
   In another terminal (frontend):
   ```bash
   cd frontend
   npm run dev
   ```

5. **Open the Application**
   - Frontend: http://localhost:5173
   - Backend API: http://localhost:5000

## Local LLM Setup

The application can work with or without a local LLM model:

### With Local LLM (Recommended)

1. **Download a Model**
   - Visit [HuggingFace GGUF Models](https://huggingface.co/TheBloke)
   - Download a GGUF format model (e.g., Llama-2-7B-Chat-GGUF)
   - Place it in the `backend/models/` directory

2. **Configure the Model**
   Edit `backend/config.py`:
   ```python
   MODEL_PATH = "models/llama-2-7b-chat.gguf"
   ```

3. **Restart the Backend**
   ```bash
   python app.py
   ```

### Without Local LLM

The application will use fallback methods (regex-based extraction) when no LLM is available. This provides basic functionality but with limited AI capabilities.

## Usage

### 1. Upload Document
- Navigate to the "Upload Document" tab
- Click to upload or drag and drop your legal document
- Supported formats: PDF, DOCX, TXT (up to 10MB)

### 2. View Analysis
- The system will automatically process your document
- View the document summary and extracted clauses
- Check the risk assessment dashboard

### 3. Ask Questions
- Go to the "Legal Q&A" tab
- Ask specific questions about your document
- Use the quick questions sidebar for common queries

### 4. Export Results
- Click "Export Report" to download analysis results
- Results are saved in JSON format

## Configuration

Edit `backend/config.py` to customize:

- **Model Path**: Path to your local LLM model
- **Processing Settings**: Chunk size and overlap for text processing
- **Risk Keywords**: Customize risk assessment criteria

## API Endpoints

- `POST /upload` - Upload and process documents
- `POST /chat` - Ask questions about documents
- `GET /health` - Health check endpoint

## Troubleshooting

### Common Issues

1. **Model Download Fails**
   - Download manually from HuggingFace
   - Ensure you have sufficient disk space (~4GB per model)

2. **Memory Issues**
   - Reduce chunk size in config.py
   - Use a smaller model
   - Close other applications

3. **Processing Errors**
   - Check file format compatibility
   - Ensure file size is under 10MB
   - Verify backend is running

4. **Frontend Connection Issues**
   - Ensure backend is running on port 5000
   - Check CORS settings
   - Verify network connectivity

### Performance Tips

- Use SSD storage for faster model loading
- Allocate at least 8GB RAM for optimal performance
- Consider using a smaller model for faster processing

## Development

### Project Structure
```
legal-ai-assistant/
├── backend/
│   ├── app.py              # Main Flask application
│   ├── ai_processor.py     # AI processing logic
│   ├── setup.py           # Setup script
│   ├── config.py          # Configuration
│   ├── requirements.txt   # Python dependencies
│   └── uploads/           # Uploaded files
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   └── LegalAIAssistant.jsx
│   │   └── App.jsx
│   ├── package.json
│   └── vite.config.js
└── README.md
```

### Adding New Features

1. **Backend Extensions**
   - Add new routes in `app.py`
   - Extend `ai_processor.py` for new AI capabilities
   - Update requirements.txt for new dependencies

2. **Frontend Extensions**
   - Add new components in `src/components/`
   - Update the main `LegalAIAssistant.jsx`
   - Add new API calls as needed

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For issues and questions:
- Check the troubleshooting section
- Review the configuration options
- Open an issue on GitHub

## Acknowledgments

- [LangChain](https://langchain.com/) for AI processing framework
- [HuggingFace](https://huggingface.co/) for model hosting
- [TheBloke](https://huggingface.co/TheBloke) for GGUF model conversions 