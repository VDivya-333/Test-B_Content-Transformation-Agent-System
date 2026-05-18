import json
import re
import time
from app.services.llm_service import ask_llm
from app.utils.logger import get_logger

logger = get_logger()

class RAGService:
    def get_style_guidelines(self, style_name: str, target_format: str = "general"):
        knowledge_base = {
            "academic": ["Use passive voice", "Avoid contractions", "Include citations"],
            "blog": ["Use engaging headers", "Maintain conversational tone", "Short paragraphs"],
            "professional": ["Maintain authority", "Be concise", "Focus on value"],
            "casual": ["Use emojis sparingly", "Direct address", "Friendly sign-offs"],
            "kid_friendly": ["Use analogies", "Avoid jargon", "Simple sentence structures"]
        }
        
        format_templates = {
            "linkedin_post": "🔗 Hook + simple explanation + takeaway",
            "slack_message": "💬 Direct and actionable",
            "executive_summary": "Bullet points with key metrics",
            "markdown": "Structured Markdown with appropriate headers (##, ###), bold text for emphasis, and bulleted lists for clarity.",
            "tweet": "🐦 Short, punchy statement (max 280 chars) with 1-2 relevant hashtags.",
            "pdf": "Formal Document Layout: Include a clear Title, followed by Section Headers (# and ##) for organization, and 7-9 lines professional paragraph spacing.",
            "report": "Structured Professional Report: Executive Summary, Detailed Analysis with headers, and a Recommendations section.",
            "email": "Professional Email Format: Subject Line, formal Salutation, structured Body, and a professional Sign-off."
        }

        # Mock few-shot examples for better transformation context
        example_cases = {
            "academic": [
                {"input": "I think this is a big problem.", "output": "This issue constitutes a significant challenge within the field."}
            ],
            "blog": [
                {"input": "The data shows growth.", "output": "🚀 Great news! We're seeing some amazing growth in the numbers."}
            ]
        }

        guidelines = knowledge_base.get(style_name.lower(), ["Standard clarity guidelines"])
        template = format_templates.get(target_format.lower(), "Standard prose")
        examples = example_cases.get(style_name.lower(), [{"input": "Original text", "output": f"Transformed {style_name} text"}])

        return {
            "guidelines": guidelines,
            "template": template,
            "examples": examples,
            "source_metadata": f"Retrieved from {style_name} style guide and {target_format} format library."
        }

    async def verify_factual_consistency(self, source, transformed):
        """
        Provides a detailed factual integrity score.
        """
        start_time = time.perf_counter()
        prompt = f"""
        Identify any factual discrepancies between the Source and Transformed text.
        Check for: 
        1. Omissions (Facts in source missing in transformed)
        2. Additions (Facts in transformed not found in source)
        3. Distortions (Facts changed or misinterpreted)

        Source: {source}
        Transformed: {transformed}

        Return a JSON object: {{"score": 0-100, "reasoning": "explanation", "issues": []}}
        """
        try:
            logger.info(f"[RAG] Verifying factual consistency for content...")
            response = await ask_llm(
                prompt,
                config={"tags": ["service:rag"], "run_name": "FactCheck"}
            )
            duration = time.perf_counter() - start_time
            logger.info(f"SERVICE_TIME | RAG Fact Check | {duration:.4f} seconds")

            if not response:
                raise ValueError("Empty response from LLM for factual consistency check.")

            res_clean = response.strip()
            # More robust JSON extraction
            json_match = re.search(r'\{.*\}', res_clean, re.DOTALL)
            json_str = json_match.group(0) if json_match else res_clean

            data = json.loads(json_str)
            return data.get("score", 100), data.get("reasoning", "No issues found.")
        except Exception as e:
            logger.error(f"Fact check error: {e}", exc_info=True)
            return 70, "Verification service unavailable; defaulting to neutral score."