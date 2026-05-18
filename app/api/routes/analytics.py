from fastapi import APIRouter
from app.services.job_store import job_results

router = APIRouter(prefix="/analytics", tags=["Monitoring"])

@router.get("/summary")
async def get_performance_summary():
    """
    Aggregates performance metrics from the in-memory job store.
    Provides insights into agent success rates and quality scores.
    """
    all_jobs = list(job_results.values())
    total = len(all_jobs)
    
    if total == 0:
        return {
            "total_jobs": 0,
            "success_rate": "0%",
            "average_quality_score": 0,
            "status_counts": {}
        }

    completed = [j for j in all_jobs if j.get("status") == "completed"]
    failed = [j for j in all_jobs if j.get("status") == "failed"]
    
    # Calculate average quality score from successful transformations
    scores = [
        j.get("result", {}).get("quality_score", 0) 
        for j in completed 
        if "result" in j
    ]
    
    avg_quality = sum(scores) / len(scores) if scores else 0
    
    return {
        "total_jobs": total,
        "success_rate": f"{(len(completed) / total * 100):.1f}%",
        "average_quality_score": round(avg_quality, 2),
        "status_counts": {
            "completed": len(completed),
            "failed": len(failed),
            "processing": total - len(completed) - len(failed)
        }
    }