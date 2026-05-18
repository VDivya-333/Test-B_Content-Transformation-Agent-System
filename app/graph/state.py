from typing import TypedDict, List, Dict, Optional

class GraphState(TypedDict):
    job_id: str
    source_text: str
    target_format: str
    target_style: str
    target_complexity: str
    preserve_facts: bool
    max_iterations: int
    iteration_count: int
    retry_reason: Optional[str]

    analysis: Optional[Dict]
    plan: Optional[Dict]
    transformed_content: Optional[str]
    quality_metrics: Optional[Dict]
    final_output: Optional[Dict]