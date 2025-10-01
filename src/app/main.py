from fastapi import FastAPI

from src.app.api.v1.endpoints.jobs import router as jobs_router
from src.app.api.v1.endpoints.process import router as process_router
from src.app.db.session import Base, engine  


Base.metadata.create_all(bind=engine)


def create_app():
    app = FastAPI()
    app.include_router(jobs_router, prefix="/v1")
    app.include_router(process_router, prefix="/v1")
    return app


app = create_app()
