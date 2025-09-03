# openai_service.py
import os
import json
import logging
from openai import AsyncOpenAI
from prompts import CLASSIFICATION_PROMPT, ANALYSIS_PROMPTS

# Load OpenAI credentials
client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o")
MAX_RETRIES = 3

async def classify_document(text: str) -> dict:
    """Step 1: Classify the document type with retries."""
    logging.info("Classifying document type...")
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            logging.info(f"Attempt {attempt}: Sending classification request to OpenAI...")
            response = await client.chat.completions.create(
                model=OPENAI_MODEL,
                response_format={"type": "json_object"},
                messages=[
                    {"role": "system", "content": CLASSIFICATION_PROMPT},
                    {"role": "user", "content": text[:4000]}
                ],
                temperature=0.2
            )
            result = json.loads(response.choices[0].message.content)

            if isinstance(result, dict) and 'document_type' in result:
                return {"document_type": result['document_type']}
            else:
                logging.warning("Unexpected classification format.")
                return {"document_type": str(result)}

        except Exception as e:
            logging.warning(f"Attempt {attempt} failed: {e}")
    logging.error("All classification attempts failed.")
    return {"document_type": "GeneralDocument"}

async def analyze_document_by_type(text: str, doc_type: str) -> dict:
    """Step 2: Analyze the document using a universal analysis prompt with retries."""
    logging.info(f"Analyzing document. Type: {doc_type}")
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            logging.info(f"Attempt {attempt}: Sending analysis request to OpenAI...")
            response = await client.chat.completions.create(
                model=OPENAI_MODEL,
                response_format={"type": "json_object"},
                messages=[
                    {"role": "system", "content": ANALYSIS_PROMPTS},
                    {"role": "user", "content": text}
                ],
                temperature=0.2
            )
            content = response.choices[0].message.content.strip()
            logging.debug(f"OpenAI response: {content}")
            result = json.loads(content)

            if isinstance(result, dict):
                return result
            else:
                logging.warning("Unexpected analysis format.")
                return {"result": str(result)}

        except Exception as e:
            logging.warning(f"Attempt {attempt} failed: {e}")
    logging.error("All analysis attempts failed.")
    return {"error": "Failed to analyze document."}

async def analyze_multiple_documents_consolidated(combined_text: str, file_info: list) -> dict:
    """Analyze multiple documents together and provide a single consolidated analysis."""
    logging.info(f"Performing consolidated analysis of {len(file_info)} documents")
    
    # Create a detailed prompt for consolidated analysis focusing on summaries and recommendations
    consolidated_prompt = f"""
You are an expert document analyst specializing in providing detailed summaries and actionable recommendations. You have been given {len(file_info)} documents to analyze together.

Your task is to provide a comprehensive analysis with detailed summaries and specific, actionable recommendations:

1. **Comprehensive Summary**: Detailed summary of all documents combined with specific details, amounts, dates, and entities
2. **Key Findings**: Specific, actionable findings from the document collection
3. **Detailed Recommendations**: Specific, actionable recommendations with exact details and next steps
4. **Priority Actions**: Most urgent or important actions that need immediate attention with specific details

Document Information:
{json.dumps(file_info, indent=2)}

Please provide a clean JSON response with these fields:
{{
    "comprehensive_summary": "Detailed summary of all documents combined with specific details, amounts, dates, company names, and exact information",
    "key_findings": [
        "Specific finding 1 with exact details",
        "Specific finding 2 with exact details"
    ],
    "detailed_recommendations": [
        "Specific recommendation 1 with exact details (e.g., 'Pay invoice 250270334 for €91.25 issued by KvK by December 15th')",
        "Specific recommendation 2 with exact details (e.g., 'Contact legal team regarding contract ABC-2024-001 renewal by November 30th')",
        "Specific recommendation 3 with exact details (e.g., 'Verify purchase order PO-2024-001 matches invoice amount of €2,450.00')"
    ],
    "priority_actions": [
        "Most urgent action 1 with exact details and deadlines",
        "Most urgent action 2 with exact details and deadlines"
    ]
}}

Analyze the following combined text from all documents:
{combined_text[:8000]}  # Limit to prevent token overflow

IMPORTANT: Focus on providing SPECIFIC, DETAILED summaries and recommendations rather than general statements. Include exact invoice numbers, amounts, company names, dates, and other specific details that make the recommendations immediately actionable.
"""

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            logging.info(f"Attempt {attempt}: Sending consolidated analysis request to OpenAI...")
            response = await client.chat.completions.create(
                model=OPENAI_MODEL,
                response_format={"type": "json_object"},
                messages=[
                    {"role": "system", "content": "You are an expert document analyst specializing in multi-document analysis and providing detailed summaries with actionable recommendations. Focus on specific details and concrete guidance."},
                    {"role": "user", "content": consolidated_prompt}
                ],
                temperature=0.3,
                max_tokens=3000
            )
            content = response.choices[0].message.content.strip()
            logging.debug(f"OpenAI consolidated analysis response: {content}")
            result = json.loads(content)

            if isinstance(result, dict):
                return result
            else:
                logging.warning("Unexpected consolidated analysis format.")
                return {"comprehensive_summary": "Analysis completed but format was unexpected", "detailed_recommendations": ["Please check document format"]}

        except Exception as e:
            logging.warning(f"Attempt {attempt} failed: {e}")
    
    logging.error("All consolidated analysis attempts failed.")
    return {"comprehensive_summary": "Failed to analyze documents", "detailed_recommendations": ["Please try again or check document format"]}
