from app.services.rag_service import RAGService
from app.services.llm_service import ask_llm

class PlanningAgent:
    def __init__(self):
        self.rag = RAGService()

    async def create_plan(self, analysis: dict, target_style: str, target_complexity: str, target_format: str) -> dict:
        # Retrieve similar transformation patterns from the RAG knowledge base
        rag_data = self.rag.get_style_guidelines(target_style, target_format)
        
        structure_instruction = f"Format strictly as {target_format} using the structure: {rag_data['template']}."
        if target_complexity.lower() == "expert":
            structure_instruction += " Use advanced domain-specific terminology and expand on the technical implications of the source text."

        return {
            "steps": [
                f"Rewrite content from {analysis.get('source_style')} to {target_style}",
                f"Adjust vocabulary to meet {target_complexity} level",
                f"{structure_instruction} NOTE: Structural layout MUST be maintained regardless of content length."
            ],
            "guidelines": rag_data["guidelines"],
            "examples": rag_data.get("examples", [])
        }