from pydantic import BaseModel
from typing import Optional

class TransformRequest(BaseModel):
    source_text: str
    target_format: str
    target_style: str
    target_complexity: str
    preserve_facts: bool = True