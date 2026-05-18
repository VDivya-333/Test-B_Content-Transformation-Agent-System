from app.services.llm_service import ask_llm
from app.utils.logger import get_logger

logger = get_logger()

class FeedbackAgent:
    async def apply_feedback(self, content: str, feedback: str) -> str:
        """
        Uses the LLM to refine the transformed content based on specific user feedback.
        """
        prompt = f"""
        You are a content editor. A user has provided feedback on a transformed piece of text.
        Please update the content to incorporate the feedback while maintaining the overall style.
        
        Original Transformed Content:
        {content}
        
        User Feedback:
        {feedback}

        Return ONLY the revised content.
        """
        try:
            response = await ask_llm(
                prompt,
                config={"tags": ["agent:feedback"], "run_name": "FeedbackApplication"}
            )
            return response.strip() if response else content
        except Exception as e:
            logger.error(f"Error applying feedback: {e}", exc_info=True)
            return content