"""
FastAPI application entrypoint.

Phase 1 wires up: app instance, CORS, database table creation, and the
auth / users routers. Course, lesson, quiz, and agent routers are added
in later phases.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import auth, courses, users, assessment, lessons, quizzes, progress, analytics, roadmap
from app.core.config import settings
from app.database.base import Base
from app.database.session import engine

# Import models so they're registered on Base.metadata before create_all.
from app.models import (  # noqa: F401
    user,
    course,
    preference,
    module,
    lesson,
    quiz,
    quiz_question,
    quiz_attempt,
    progress as progress_model,
    analytics as analytics_model,
)

app = FastAPI(title=settings.APP_NAME)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_ORIGIN],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup() -> None:
    # Phase 1 uses create_all for simplicity. Swap to Alembic migrations
    # once the schema starts changing across phases (see README).
    Base.metadata.create_all(bind=engine)


@app.get("/health", tags=["health"])
def health_check() -> dict:
    return {"status": "ok", "app": settings.APP_NAME}


app.include_router(auth.router)
app.include_router(users.router)
app.include_router(courses.router)
app.include_router(assessment.router)
app.include_router(lessons.router)
app.include_router(quizzes.router)
app.include_router(progress.router)
app.include_router(analytics.router)
app.include_router(roadmap.router)
