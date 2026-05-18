from pydantic import BaseModel

class TransformResponse(BaseModel):
    transformed_content: str
    quality_score: float