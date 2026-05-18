from app.config.prompts import TRANSFORMATION_PROMPT
from app.services.llm_service import ask_llm
from app.utils.logger import get_logger
import time
from typing import Optional

logger = get_logger()

class ConversionAgent:
    async def transform(self, content: str, plan: dict, feedback: Optional[str] = None) -> str:
        start_time = time.perf_counter()
        transformation_steps = "\n".join([f"- {step}" for step in plan.get("steps", [])])
        transformation_guidelines = "\n".join([f"- {guideline}" for guideline in plan.get("guidelines", [])])
        
        feedback_instruction = ""
        if feedback:
            feedback_instruction = f"""
IMPORTANT FEEDBACK FOR REFINEMENT:
The previous attempt had issues. Please address the following feedback:
{feedback}
"""
        
        #few shot example
        examples_text = ""
        if plan.get("examples"):
            examples_text = "\nFollowing these similar transformation patterns:\n"
            for ex in plan["examples"]:
                examples_text += f"Input: {ex['input']}\nOutput: {ex['output']}\n---\n"

        full_prompt = f"""
{TRANSFORMATION_PROMPT}

Here are the specific instructions for transformation:
Steps:
{transformation_steps}

Guidelines:
{transformation_guidelines}

{feedback_instruction}

{examples_text}

Content to Rewrite:
{content}

IMPORTANT: Return ONLY the transformed content itself. Do NOT include any introductory or concluding meta-commentary, preamble, or debug information. Structural formatting (like Markdown headers and lists) is required if it fits the requested format.
"""
        try:
            response = await ask_llm(
                full_prompt, 
                config={"tags": ["agent:converter"], "run_name": "ConversionTransformation"}
            )
            transformed_content = response.strip() # Modified
            logger.info("Conversion Agent Completed") # Added
            duration = time.perf_counter() - start_time # Added
            logger.info(f"AGENT_TIME | Conversion Agent | {duration:.4f} seconds") # Added
            return transformed_content # Modified
        except Exception as e:
            logger.error(f"Error during content transformation: {e}", exc_info=True)
            # Fallback to original content to keep the workflow moving
            logger.error("Conversion Agent Failed") # Added
            duration = time.perf_counter() - start_time # Added
            logger.info(f"AGENT_TIME | Conversion Agent | {duration:.4f} seconds (Failed)") # Added
            return content.strip() # Modified