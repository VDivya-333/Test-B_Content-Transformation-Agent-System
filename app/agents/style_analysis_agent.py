import json
import re
from app.config.prompts import STYLE_ANALYSIS_PROMPT
from app.services.llm_service import ask_llm

class StyleAnalysisAgent:
    async def analyze(self, content: str) -> dict:
        prompt = f"{STYLE_ANALYSIS_PROMPT}\n\nContent: {content}\n\nReturn JSON with: content_type, domain, source_style, reading_level, technical_terms, estimated_complexity_score."

        try:
            response = await ask_llm(
                prompt,
                config={"tags": ["agent:style_analyst"], "run_name": "StyleAnalysis"}
            )
            
            # Robust JSON extraction
            res_clean = response.strip()
            json_match = re.search(r'\{.*\}', res_clean, re.DOTALL)
            json_string = json_match.group(0) if json_match else res_clean
            
            return json.loads(json_string)
        except (json.JSONDecodeError, Exception):
            return {
                "content_type": "text",
                "domain": "general",
                "source_style": "neutral",
                "reading_level": "standard",
                "technical_terms": [],
                "estimated_complexity_score": 5.0
            }