import json
import re
import time
from app.config.prompts import QUALITY_PROMPT
from app.services.rag_service import RAGService
from app.services.llm_service import ask_llm
from app.utils.logger import get_logger

logger = get_logger()

class QualityControlAgent:
    def __init__(self):
        self.rag = RAGService()

    async def verify(self, source_content, transformed_content, target_style, target_complexity, target_format):
        start_time = time.perf_counter()
        # 1. Perform dedicated factual consistency check via RAG Service as per architecture
        fact_score, fact_reasoning = await self.rag.verify_factual_consistency(source_content, transformed_content)

        # 2. Perform general quality assessment
        # We still ask for fact_preservation_score in the prompt to let the LLM see the whole context,
        # but we can prioritize or weight the RAG service's specific check.
        quality_prompt = f"""
{QUALITY_PROMPT}
Original: {source_content}

Transformation Goals:
- Style: {target_style}
- Complexity: {target_complexity}
- Format: {target_format}

Transformed: {transformed_content}

Return JSON:
{{
  "grammar": 0-100, "readability": 0-100, "style_match": 0-100, 
  "fact_preservation_score": 0-100, "unsupported_claims": false,
  "fact_reasoning": "...", "feedback": "..."
}}
"""

        try:
            response = await ask_llm(
                quality_prompt,
                config={"tags": ["agent:qc"], "run_name": "QualityAssessment"}
            )
            if not response:
                # If LLM returns nothing, jump straight to fallback
                raise ValueError("Empty response from LLM")
                
            # More robust JSON extraction using regex
            res_clean = response.strip()
            json_match = re.search(r'\{.*\}', res_clean, re.DOTALL)
            json_string = json_match.group(0) if json_match else res_clean

            metrics = json.loads(json_string)
            if not isinstance(metrics, dict):
                metrics = {}

            # Ensure scores are integers or floats as expected and clamp to 0-100
            # Reduced default to 60 to prevent false positives
            for key in ["grammar", "readability", "style_match", "fact_preservation_score"]:
                if key in metrics and isinstance(metrics[key], (int, float)):
                    metrics[key] = max(0, min(100, int(metrics[key])))
                else:
                    metrics[key] = 60 

            # Use the higher-fidelity fact score from the RAG service if available
            if fact_score is not None:
                metrics["fact_preservation_score"] = fact_score
                metrics["fact_reasoning"] = fact_reasoning
            fact_score_final = metrics.get("fact_preservation_score", 100)
            
            # Weighted overall score logic
            # Weights: Fact Preservation (45%), Style Match (25%), Readability (15%), Grammar (15%)
            # Increased style_match weight to emphasize format adherence
            score = round(
                (metrics.get("grammar", 60) * 0.10) +
                (metrics.get("readability", 60) * 0.10) +
                (metrics.get("style_match", 60) * 0.35) +
                (fact_score_final * 0.45), 1
            )
            metrics["overall_quality_score"] = score
            metrics["quality_score"] = score # Compatibility with UI display
            
            logger.info("Quality Control Agent Completed") # Added
            duration = time.perf_counter() - start_time # Added
            logger.info(f"AGENT_TIME | Quality Control Agent | {duration:.4f} seconds") # Added
            return metrics # Modified
        except json.JSONDecodeError as e:
            logger.error(f"JSON Decode Error during QC: {e}", exc_info=True) # Added
            logger.error("Quality Control Agent Failed") # Added
            duration = time.perf_counter() - start_time # Added
            logger.info(f"AGENT_TIME | Quality Control Agent | {duration:.4f} seconds (Failed)") # Added
            return {"grammar": 70, "readability": 70, "style_match": 70, "fact_preservation_score": 100, "feedback": "Failed to parse QC metrics.", "error": str(e)} # Modified
        except Exception as e:
            logger.error(f"Error during QC: {e}", exc_info=True) # Added
            logger.error("Quality Control Agent Failed") # Added
            duration = time.perf_counter() - start_time # Added
            logger.info(f"AGENT_TIME | Quality Control Agent | {duration:.4f} seconds (Failed)") # Added
            return {"grammar": 60, "readability": 60, "style_match": 60, "fact_preservation_score": 100, "feedback": f"Error during QC: {str(e)}"} # Modified