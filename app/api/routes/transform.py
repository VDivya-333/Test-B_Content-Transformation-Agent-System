from fastapi import APIRouter, Depends, Request
from app.api.schemas.request import TransformRequest
from app.api.routes.auth import require_role
from app.utils.limiter import limiter
from app.services.job_store import job_results
from app.services.queue_service import transformation_queue
import uuid

router = APIRouter(prefix="/transform", tags=["Transformation"])

@router.post("/")
@limiter.limit("10/minute")
async def transform_content_api(
    request: Request,
    transform_request: TransformRequest,
    current_user: dict = Depends(require_role(["editor", "admin"]))
):
    job_id = str(uuid.uuid4())[:8]  # Shortened for cleaner terminal logs
    job_results[job_id] = {"status": "accepted"}
    # Enqueue the job instead of running in a simple background task
    await transformation_queue.add_job(job_id, transform_request)
    return {"job_id": job_id, "status": "accepted", "message": "Transformation started in background"}

@router.get("/result/{job_id}")
async def get_result(job_id: str):
    if job_id not in job_results:
        return {"status": "not_found"}
    return job_results[job_id]