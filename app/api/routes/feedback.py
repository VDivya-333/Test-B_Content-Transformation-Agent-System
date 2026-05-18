from fastapi import APIRouter, Request
from app.api.schemas.feedback import FeedbackRequest
from app.services.feedback_service import process_feedback
from app.utils.limiter import limiter

router = APIRouter(prefix="/feedback", tags=["Feedback"])

@router.post("/")
@limiter.limit("20/minute")
async def submit_feedback(request: Request, feedback_request: FeedbackRequest):
    # Pass the validated request data to the feedback service for storage
    process_feedback(feedback_request.model_dump())
    
    return {
        "status": "Feedback received",
        "transformation_id": feedback_request.transformation_id
    }