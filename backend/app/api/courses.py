"""
Course endpoints: create a course, list/read the current user's courses,
and read a course's generated roadmap (modules/lessons — populated once
the skill assessment has run; see api/assessment.py).
"""
import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload

from app.api.deps import get_current_user
from app.database.session import get_db
from app.models.course import Course
from app.models.module import Module
from app.models.user import User
from app.schemas.course import CourseCreate, CourseRead
from app.schemas.roadmap import RoadmapRead, ModuleSummary, LessonSummary

router = APIRouter(prefix="/courses", tags=["courses"])


@router.post("/create", response_model=CourseRead, status_code=status.HTTP_201_CREATED)
def create_course(
    payload: CourseCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Course:
    course = Course(user_id=current_user.id, **payload.model_dump())
    db.add(course)
    db.commit()
    db.refresh(course)
    return course


@router.get("", response_model=list[CourseRead])
def list_courses(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[Course]:
    return (
        db.query(Course)
        .filter(Course.user_id == current_user.id)
        .order_by(Course.created_at.desc())
        .all()
    )


@router.get("/{course_id}", response_model=CourseRead)
def get_course(
    course_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Course:
    course = (
        db.query(Course)
        .filter(Course.id == course_id, Course.user_id == current_user.id)
        .first()
    )
    if course is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found")
    return course


@router.get("/{course_id}/roadmap", response_model=RoadmapRead)
def get_roadmap(
    course_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> RoadmapRead:
    course = (
        db.query(Course)
        .options(joinedload(Course.modules).joinedload(Module.lessons), joinedload(Course.modules).joinedload(Module.quiz))
        .filter(Course.id == course_id, Course.user_id == current_user.id)
        .first()
    )
    if course is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found")

    modules = sorted(course.modules, key=lambda m: m.order_index)
    return RoadmapRead(
        modules=[
            ModuleSummary(
                id=m.id,
                title=m.title,
                order_index=m.order_index,
                estimated_minutes=m.estimated_minutes,
                status=m.status,
                quiz_id=m.quiz.id if m.quiz else None,
                lessons=[
                    LessonSummary.model_validate(l)
                    for l in sorted(m.lessons, key=lambda l: l.order_index)
                ],
            )
            for m in modules
        ]
    )
