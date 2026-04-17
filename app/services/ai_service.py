import logging
import json
from groq import Groq
from app.config import settings

logger = logging.getLogger(__name__)


class AIService:
    def __init__(self):
        """Initialize Groq client"""
        if not settings.GROQ_API_KEY:
            raise ValueError("GROQ_API_KEY not found in environment variables")

        self.client = Groq(api_key=settings.GROQ_API_KEY)
        self.model = settings.GROQ_MODEL
        logger.info("✅ Groq AI service initialized")

    def analyze_document(self, extracted_text: str) -> dict:
        """Analyze document text using Groq AI"""
        try:
            logger.info("🤖 Sending text to Groq AI for analysis...")

            # Create the prompt
            prompt = f"""You are an expert academic document analyzer for the Indian education system.

A document has been scanned and its text is provided below. Read it CAREFULLY and extract all information from it.

=== DOCUMENT TEXT START ===
{extracted_text}
=== DOCUMENT TEXT END ===

Your job is to analyze this document and return a JSON response with the following fields:

1. "document_type": What type of document is this? (e.g., "10th Marksheet", "12th Marksheet", "Degree Certificate", "Transfer Certificate", "ID Card", "Resume", etc.). Be specific based on the actual document content.

2. "student_name": Extract the student's full name from the document. If not found, return an empty string.

3. "key_fields": Summarize the most important data found in the document. Include:
   - Roll number / Seat number (if present)
   - School/College name (if present)
   - Board/University name (if present)
   - Year of passing (if present)
   - Total marks / Percentage / CGPA (if present)
   - Stream or subjects (if present, e.g., Science, Commerce, Arts, PCM, PCB, etc.)
   - Any grades or division (First, Second, etc.)
   - Any other key academic fields visible in the document
   Write this as a readable paragraph summarizing all key data found.

4. "analysis_note": A short 1-2 sentence note about what this document is and its academic significance.

5. "analysis_summary": Write a 3-4 sentence professional summary:
   - What the document represents
   - What academic level/qualification it confirms
   - How it can be used for college admissions
   - Any important context (stream, performance level, etc.)

6. "eligible_courses": Based STRICTLY on the information in the document (qualification level, stream, subjects, marks/percentage), list the courses this student would likely be eligible for in India. Be SPECIFIC and DYNAMIC:
   - If it is a 10th marksheet: suggest 11th/12th stream options (Science, Commerce, Arts) and relevant diploma/ITI courses
   - If it is a 12th Science (PCM) marksheet: suggest B.Tech, B.Sc (Physics/Maths/CS), B.Arch, BCA, etc.
   - If it is a 12th Science (PCB) marksheet: suggest MBBS, BDS, BAMS, BHMS, B.Sc (Biology/Nursing/Biotech), etc.
   - If it is a 12th Commerce marksheet: suggest B.Com, BBA, CA, CS, BMS, etc.
   - If it is a 12th Arts marksheet: suggest B.A, BA-LLB, BFA, B.Journalism, B.Social Work, etc.
   - If it is a graduation certificate: suggest PG courses like M.A, M.Com, M.Sc, MBA, MCA, LLM, etc.
   - If stream is unclear, suggest general undergraduate courses
   - Always list at least 4-6 specific, realistic course options
   - Include the full course name (e.g., "B.Tech (Computer Science & Engineering)")

STRICT RULES:
- Return ONLY valid JSON — no markdown, no code fences, no extra text
- All fields must be present in the JSON
- Base your answer on the ACTUAL document content above, not on assumptions
- Do NOT copy from any template — analyze the real document
- If a field truly cannot be determined, use a sensible default or empty string

Return your response in this EXACT JSON structure:
{{
  "analysis_summary": "<your dynamic summary based on document>",
  "extracted_data": {{
    "document_type": "<specific document type>",
    "student_name": "<student name or empty string>",
    "analysis_note": "<short note about this document>",
    "key_fields": "<paragraph summarizing all key extracted data>"
  }},
  "eligible_courses": [
    "<course 1>",
    "<course 2>",
    "<course 3>",
    "<course 4>",
    "<course 5>"
  ]
}}"""

            # Call Groq API
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a professional document analyzer. Always return valid JSON only."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.3,
                max_tokens=2000,
                response_format={"type": "json_object"}
            )

            # Extract response
            ai_response = response.choices[0].message.content

            logger.info("✅ Received response from Groq AI")

            # Parse JSON
            try:
                result = json.loads(ai_response)
                return result
            except json.JSONDecodeError as e:
                logger.error(f"❌ Invalid JSON from AI: {ai_response}")
                raise Exception("Failed to parse AI response")

        except Exception as e:
            logger.error(f"❌ AI analysis failed: {str(e)}")
            raise Exception(f"Failed to analyze document: {str(e)}")


# Initialize AI service
ai_service = AIService()