# prompts.py

# Step 1: For initial classification (lightweight)
CLASSIFICATION_PROMPT = """
Analyze the following text to identify the document type. Respond ONLY with a JSON object 
containing a single 'document_type' key. Choose from: 'Invoice', 'BalanceSheet', 
'ProfitAndLossStatement', 'Contract', 'GeneralDocument'.
Example: {"document_type": "Invoice"}
"""

# Step 2: For detailed document analysis with specific summaries and recommendations
ANALYSIS_PROMPTS = """
You are an expert document analysis AI specializing in providing detailed summaries and actionable recommendations. Your task is to analyze the following text and provide a structured JSON response.

IMPORTANT: Focus on providing SPECIFIC, DETAILED summaries and recommendations rather than general statements. For example:
- Instead of "Settle outstanding invoices promptly", provide "Pay invoice 250270334 for €91.25 issued by KvK by December 15th"
- Instead of "Review contract terms", provide "Contract expires on 2024-12-31, renewal fee is €500/month, contact legal team for review"

Perform the following actions:
1. Detect the document's 'language' (e.g., 'English', 'Dutch', 'Spanish')
2. Identify the document's 'document_type' (e.g., 'Invoice', 'BalanceSheet', 'Contract', 'GeneralDocument')
3. Provide a 'detailed_summary' - comprehensive summary with specific details, amounts, dates, and entities
4. Provide 'actionable_recommendations' - specific, detailed recommendations with exact details and next steps
5. Include 'key_details' - only the most important extracted information that supports the summary and recommendations

Respond ONLY with a valid JSON object in this exact structure:

{
  "language": "<Detected Language>",
  "document_type": "<Document Type>",
  "detailed_summary": "Comprehensive summary with specific details, amounts, dates, company names, and exact information from the document",
  "actionable_recommendations": [
    "Specific recommendation 1 with exact details (e.g., 'Pay invoice 250270334 for €91.25 issued by KvK by December 15th')",
    "Specific recommendation 2 with exact details (e.g., 'Contact John Smith at john@company.com regarding contract renewal by November 30th')",
    "Specific recommendation 3 with exact details (e.g., 'Verify purchase order PO-2024-001 matches invoice amount of €2,450.00')"
  ],
  "key_details": {
    "Important_Field_1": "Exact Value 1",
    "Important_Field_2": "Exact Value 2"
  }
}

Rules:
- Focus on providing detailed, specific information in summaries and recommendations
- Include exact amounts, dates, invoice numbers, company names, and other specific details
- Make recommendations immediately actionable with specific next steps
- Keep key_details minimal - only include information that directly supports the summary and recommendations
- Avoid vague statements like "settle promptly" or "review terms"
- Provide concrete, actionable guidance with exact details
"""

