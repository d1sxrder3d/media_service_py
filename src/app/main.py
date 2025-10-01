from fastapi import FastAPI

from src.app.api.main import main_router
from src.db.session import Base, engine  


Base.metadata.create_all(bind=engine)


def create_app():
    app = FastAPI()
    app.include_router(main_router)
    return app


app = create_app()
