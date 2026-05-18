import asyncio
from typing import Dict, Any
from app.utils.logger import get_logger
from app.graph.workflow import run_workflow
from app.services.job_store import job_results

logger = get_logger()

class TransformationQueue:
    def __init__(self):
        self.queue = asyncio.Queue()
        self.worker_task = None

    async def add_job(self, job_id: str, payload: Any):
        """Adds a new transformation job to the queue."""
        await self.queue.put((job_id, payload))
        logger.info(f"Queue | Job {job_id} enqueued.")

    async def _worker(self):
        """Background worker that processes jobs one by one."""
        logger.info("Queue | Worker process started.")
        while True:
            job_id, payload = await self.queue.get()
            try:
                job_results[job_id]["status"] = "processing"
                logger.info(f"Queue | >>> Starting Job {job_id} <<<")

                final_state = await run_workflow(
                    job_id=job_id,
                    source_text=payload.source_text,
                    target_format=payload.target_format,
                    target_style=payload.target_style,
                    target_complexity=payload.target_complexity,
                    preserve_facts=payload.preserve_facts
                )

                final_output = final_state.get("final_output") or {}
                job_results[job_id].update({
                    "status": "completed",
                    "result": {
                        "transformed_content": final_output.get("transformed_content", final_state.get("transformed_content")),
                        "quality_score": final_output.get("quality_score", 0.0)
                    }
                })
                logger.info(f"Queue | <<< Finished Job {job_id} (Success) >>>")
            except Exception as e:
                logger.error(f"Queue | Job {job_id} failed: {str(e)}")
                job_results[job_id].update({"status": "failed", "error": str(e)})
            finally:
                self.queue.task_done()

    def start(self):
        """Initializes the background worker task."""
        self.worker_task = asyncio.create_task(self._worker())

    def stop(self):
        """Gracefully cancels the worker task."""
        if self.worker_task:
            self.worker_task.cancel()

transformation_queue = TransformationQueue()