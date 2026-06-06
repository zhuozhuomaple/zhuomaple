from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import RedirectResponse

from app.database import init_db
from app.routers import tasks


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(
    title="Task Management API",
    description="校招 AI Coding 培训课题 SD-01：RESTful 任务管理 API",
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(tasks.router)


@app.get("/", include_in_schema=False)
def root():
    return RedirectResponse(url="/docs")
