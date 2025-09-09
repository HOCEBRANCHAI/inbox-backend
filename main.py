import os
import tempfile
import logging
import asyncio
from pathlib import Path
from typing import List
from dotenv import load_dotenv
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import textract_service
import openai_service

# Load environment variables from .env file
load_dotenv()

app = FastAPI(title="Document Analysis API")
logging.basicConfig(level=logging.INFO)

# Configure CORS for development (restrict in production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Use ["https://yourfrontend.com"] in production
    allow_credentials=True,
    allow_methods=["POST", "GET"],
    allow_headers=["*"],
)

# Allowed file extensions
ALLOWED_EXTENSIONS = [".pdf", ".docx", ".csv", ".xlsx", ".png", ".jpg", ".jpeg"]

def validate_file(file: UploadFile):
    ext = Path(file.filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type: {ext}. Allowed types: {', '.join(ALLOWED_EXTENSIONS)}"
        )

async def process_single_file(file: UploadFile) -> dict:
    """Process a single file and return analysis results."""
    tmp_path = None
    try:
        validate_file(file)

        # Save file temporarily to disk
        with tempfile.NamedTemporaryFile(delete=False, suffix=Path(file.filename).suffix) as tmp:
            file_bytes = await file.read()
            tmp.write(file_bytes)
            tmp_path = tmp.name

        # 1. Extract text using the hybrid service
        extracted_text = textract_service.extract_text_from_upload(tmp_path, file_bytes)
        if not extracted_text or not extracted_text.strip():
            return {
                "filename": file.filename,
                "error": "Failed to extract text from document.",
                "status": "failed"
            }

        # 2. Classify the document type
        classification_result = await openai_service.classify_document(extracted_text)
        logging.info(f"classification_result type: {type(classification_result)}, value: {classification_result}")
        if not isinstance(classification_result, dict):
            classification_result = {"document_type": str(classification_result)}
        doc_type = classification_result.get("document_type", "GeneralDocument")

        # 3. Perform specialized analysis
        analysis_result = await openai_service.analyze_document_by_type(extracted_text, doc_type)
        
        # ✅ Ensure analysis_result is a dictionary
        if not isinstance(analysis_result, dict):
            logging.warning("OpenAI returned non-dict analysis result. Wrapping it.")
            analysis_result = {"analysis_output": str(analysis_result)}

        # ✅ Optional debug logging
        logging.info(f"analysis_result type: {type(analysis_result)}, value: {analysis_result}")

        return {
            "filename": file.filename,
            "document_type": doc_type,
            "analysis": analysis_result,
            "status": "success",
            "extracted_text": extracted_text[:1000]  # Keep first 1000 chars for reference
        }

    except Exception as e:
        logging.error(f"Error processing file {file.filename}: {e}")
        return {
            "filename": file.filename,
            "error": str(e),
            "status": "failed"
        }
    finally:
        # Clean up the temporary file
        if tmp_path and os.path.exists(tmp_path):
            os.remove(tmp_path)

async def analyze_multiple_files_consolidated(files: List[UploadFile]) -> dict:
    """Analyze multiple files together and provide a single consolidated analysis."""
    if not files:
        raise HTTPException(status_code=400, detail="No files provided")
    
    if len(files) > 10:  # Limit to prevent abuse
        raise HTTPException(status_code=400, detail="Maximum 10 files allowed per request")
    
    # Process all files to extract text and basic info
    file_results = []
    all_texts = []
    file_info = []
    
    for file in files:
        result = await process_single_file(file)
        if result['status'] == 'success':
            file_results.append(result)
            all_texts.append(result['extracted_text'])
            file_info.append({
                "filename": result['filename'],
                "document_type": result['document_type'],
                "text_length": len(result['extracted_text'])
            })
        else:
            logging.warning(f"File {file.filename} failed processing: {result.get('error')}")
    
    if not file_results:
        raise HTTPException(status_code=422, detail="No files could be processed successfully")
    
    # Combine all extracted texts for consolidated analysis
    combined_text = "\n\n--- DOCUMENT SEPARATOR ---\n\n".join(all_texts)
    
    # Perform consolidated analysis using OpenAI
    try:
        consolidated_analysis = await openai_service.analyze_multiple_documents_consolidated(
            combined_text, 
            file_info
        )
        
        return {
            "total_files": len(files),
            "successful_files": len(file_results),
            "failed_files": len(files) - len(file_results),
            "file_info": file_info,
            "consolidated_analysis": consolidated_analysis,
            "status": "success"
        }
        
    except Exception as e:
        logging.error(f"Error in consolidated analysis: {e}")
        raise HTTPException(status_code=500, detail=f"Consolidated analysis failed: {str(e)}")

@app.get("/health", status_code=200)
async def health_check():
    return {"status": "ok"}

@app.post("/analyze")
async def analyze_single(file: UploadFile = File(...)):
    """Analyze a single document (backward compatibility)."""
    result = await process_single_file(file)
    if result.get("status") == "failed":
        raise HTTPException(status_code=500, detail=result.get("error", "Unknown error"))
    return result

@app.post("/analyze-multiple")
async def analyze_multiple(files: List[UploadFile] = File(...)):
    """Analyze multiple documents individually (separate analysis for each)."""
    if not files:
        raise HTTPException(status_code=400, detail="No files provided")
    
    if len(files) > 10:  # Limit to prevent abuse
        raise HTTPException(status_code=400, detail="Maximum 10 files allowed per request")
    
    # Process all files in parallel
    tasks = [process_single_file(file) for file in files]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    # Handle any exceptions that occurred during processing
    processed_results = []
    for i, result in enumerate(results):
        if isinstance(result, Exception):
            processed_results.append({
                "filename": files[i].filename,
                "error": str(result),
                "status": "failed"
            })
        else:
            processed_results.append(result)
    
    # Count successes and failures
    successful = sum(1 for r in processed_results if r.get("status") == "success")
    failed = len(processed_results) - successful
    
    return {
        "total_files": len(processed_results),
        "successful": successful,
        "failed": failed,
        "results": processed_results
    }

@app.post("/analyze-consolidated")
async def analyze_consolidated(files: List[UploadFile] = File(...)):
    """Analyze multiple documents together and provide a single consolidated analysis."""
    return await analyze_multiple_files_consolidated(files)
