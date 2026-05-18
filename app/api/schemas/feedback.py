from pydantic import BaseModel

class FeedbackRequest(BaseModel):
    transformation_id: str
    rating: int
    comments: str