from contextlib import asynccontextmanager
from fastapi import FastAPI
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from slowapi.middleware import SlowAPIMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from app.utils.limiter import limiter
from prometheus_fastapi_instrumentator import Instrumentator

from app.api.routes.transform import router as transform_router
from app.api.routes.feedback import router as feedback_router
from app.api.routes.health import router as health_router
from app.api.routes.auth import router as auth_router
from app.api.routes.analytics import router as analytics_router
from app.services.queue_service import transformation_queue

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Start the queue worker
    transformation_queue.start()
    yield
    # Shutdown: Stop the queue worker
    transformation_queue.stop()

app = FastAPI(
    title="Content Transformation Agent System",
    lifespan=lifespan
)

# Set up rate limiting
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

app.include_router(auth_router)
app.include_router(transform_router)
app.include_router(feedback_router)
app.include_router(health_router)
app.include_router(analytics_router)

# Enable monitoring metrics
Instrumentator().instrument(app).expose(app)

# Enable tracing
FastAPIInstrumentor.instrument_app(app)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)