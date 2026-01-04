from fastapi import FastAPI

from backend.api.routes.health import router as health_router
from backend.api.routes.run import router as run_router
from backend.api.routes.workflow import router as workflow_router


def create_app() -> FastAPI:
    app = FastAPI(title="Visual Agent IDE API")

    app.include_router(health_router)
    app.include_router(run_router)
    app.include_router(workflow_router)

    return app


app = create_app()
