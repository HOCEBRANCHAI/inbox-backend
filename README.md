# Document Analyzer

A powerful document analysis tool that uses AI to classify and analyze various document types including PDFs, Word documents, Excel files, CSV files, and images.

## Features

- **Multiple Analysis Modes**: 
  - Single file analysis
  - Multiple files analysis (individual results for each)
  - **Multiple files consolidated analysis (single comprehensive output)**
- **AI-Powered Classification**: Automatically detects document types using OpenAI GPT-4
- **Intelligent Analysis**: Provides detailed analysis based on document content and type
- **Multiple Format Support**: Handles PDF, DOCX, CSV, XLSX, PNG, JPG, JPEG files
- **Hybrid Text Extraction**: Uses specialized libraries for digital documents and AWS Textract for OCR
- **User-Friendly UI**: Beautiful Streamlit interface for easy document upload and analysis

## Prerequisites

- Python 3.8+
- OpenAI API key
- AWS credentials (optional, for OCR functionality)

## Installation

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd oDoc_analyser-main
   ```

2. **Create a virtual environment:**
   ```bash
   python -m venv venv
   
   # On Windows
   venv\Scripts\activate
   
   # On macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables:**
   
   Create a `.env` file in the project root with your API keys:
   ```bash
   # Required
   OPENAI_API_KEY=your_openai_api_key_here
   OPENAI_MODEL=gpt-4o
   
   # Optional (for OCR functionality)
   AWS_ACCESS_KEY_ID=your_aws_access_key_here
   AWS_SECRET_ACCESS_KEY=your_aws_secret_access_key_here
   AWS_REGION=us-east-1
   ```

## Usage

### 1. Start the FastAPI Backend

```bash
# Start the API server
uvicorn main:app --reload
```

The API will be available at `http://localhost:8000`

### 2. Start the Streamlit UI

In a new terminal:

```bash
# Start the Streamlit interface
streamlit run app.py
```

The UI will open in your browser at `http://localhost:8501`

### 3. Analyze Documents

#### Single File Analysis
1. Select "Single File" mode
2. Upload a document
3. Click "Analyze Document"
4. View results including document type and analysis

#### Multiple Files Analysis (Individual)
1. Select "Multiple Files (Individual)" mode
2. Upload up to 10 documents
3. Click "Analyze All Documents Individually"
4. View individual results for each file with success/failure counts

#### **Multiple Files Analysis (Consolidated) - NEW!**
1. Select "Multiple Files (Consolidated)" mode
2. Upload up to 10 documents
3. Click "Analyze Documents Together"
4. **Get a single comprehensive analysis that includes:**
   - **Summary**: Comprehensive summary of all documents combined
   - **Recommendations**: Actionable insights and next steps
   - Clean JSON format for easy integration

## API Endpoints

- `GET /health` - Health check
- `POST /analyze` - Analyze single document
- `POST /analyze-multiple` - Analyze multiple documents individually
- `POST /analyze-consolidated` - **NEW!** Analyze multiple documents together for consolidated analysis

## Supported File Types

- **PDF**: Digital PDFs with text extraction, scanned PDFs with OCR
- **DOCX**: Microsoft Word documents
- **CSV**: Comma-separated values
- **XLSX**: Microsoft Excel files
- **PNG/JPG/JPEG**: Images with OCR processing

## Configuration

### Environment Variables

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `OPENAI_API_KEY` | Your OpenAI API key | Yes | - |
| `OPENAI_MODEL` | OpenAI model to use | No | `gpt-4o` |
| `AWS_ACCESS_KEY_ID` | AWS access key for OCR | No | - |
| `AWS_SECRET_ACCESS_KEY` | AWS secret key for OCR | No | - |
| `AWS_REGION` | AWS region for OCR | No | - |

### AWS Configuration (Optional)

AWS credentials are only required if you need OCR functionality for:
- Scanned documents
- Images
- Poor quality PDFs

Without AWS credentials, the application will still work for digital documents (PDF, DOCX, CSV, XLSX) but won't be able to process scanned content.

## Architecture

- **Frontend**: Streamlit web interface
- **Backend**: FastAPI REST API
- **AI Processing**: OpenAI GPT-4 for classification and analysis
- **Text Extraction**: Hybrid approach using specialized libraries + AWS Textract
- **File Processing**: Asynchronous processing for multiple files
- **Consolidated Analysis**: Multi-document corpus analysis with cross-document insights

## Error Handling

The application includes comprehensive error handling:
- File validation
- API health checks
- Graceful degradation when services are unavailable
- Detailed error messages for troubleshooting

## Development

### Running Tests
```bash
# Install test dependencies
pip install pytest pytest-asyncio

# Run tests
pytest
```

### Code Structure
```
oDoc_analyser-main/
├── main.py              # FastAPI application with consolidated analysis
├── app.py               # Streamlit UI with three analysis modes
├── openai_service.py    # OpenAI integration + consolidated analysis
├── textract_service.py  # Text extraction service
├── prompts.py           # AI prompts
├── requirements.txt     # Python dependencies
└── README.md           # This file
```

## Use Cases

### Single File Analysis
- Quick document review
- Individual document classification
- Single document insights

### Multiple Files (Individual)
- Batch processing of unrelated documents
- Individual analysis when documents are independent
- Quality control across multiple documents

### **Multiple Files (Consolidated) - Best for:**
- **Research projects** with multiple related documents
- **Legal cases** with multiple evidence files
- **Business analysis** across multiple reports
- **Academic papers** from the same field
- **Project documentation** review
- **Cross-reference analysis** between documents
- **Pattern identification** across a document corpus
- **Comprehensive insights** from multiple sources

## Troubleshooting

### Common Issues

1. **API not running**: Ensure you've started the FastAPI server with `uvicorn main:app --reload`
2. **OpenAI API errors**: Check your API key and billing status
3. **AWS errors**: Verify your credentials and region if using OCR features
4. **File upload issues**: Check file size and format restrictions
5. **Consolidated analysis timeout**: Large documents may take longer; increase timeout if needed

### Logs

Check the terminal output for detailed logging information about:
- File processing steps
- API responses
- Error details
- Performance metrics
- Consolidated analysis progress

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

[Add your license information here]

## Support

For issues and questions:
1. Check the troubleshooting section
2. Review the logs
3. Open an issue on GitHub
