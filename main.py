# main.py
import logging
from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy import Column, Integer, String, DateTime, func, event, select
from pydantic import BaseModel, conint, EmailStr
from dotenv import load_dotenv
from typing import Optional, Any, List
import os

# Load environment variables from .env file
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
CORS_ORIGINS = os.getenv("CORS_ORIGINS").split(',')

Base = declarative_base()
engine = create_async_engine(DATABASE_URL, echo=True)

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

async_session = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def get_db_session() -> AsyncSession:
    async with async_session() as session:
        yield session

class Feedback(Base):
    __tablename__ = "feedback"
    id = Column(Integer, primary_key=True, index=True)
    score = Column(Integer, nullable=False)
    full_name = Column(String, nullable=False)
    email = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

# Listen to before_update events to automatically update updated_at field
@event.listens_for(Feedback, 'before_update')
def receive_before_update(mapper, connection, target):
    target.updated_at = func.now()

class FeedbackCreate(BaseModel):
    score: conint(ge=1, le=5)
    full_name: str
    email: EmailStr

class FeedbackUpdate(BaseModel):
    score: Optional[conint(ge=1, le=5)] = None
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None

class FeedbackResponseData(BaseModel):
    id: int
    score: int
    full_name: str
    email: str
    created_at: str
    updated_at: str

class ResponseModel(BaseModel):
    code: int
    message: str
    data: Optional[Any] = None

@app.exception_handler(HTTPException)
async def custom_http_exception_handler(request: Request, exc: HTTPException):
    logger.error(f"HTTPException: {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "code": exc.status_code,
            "message": exc.detail,
            "data": None
        }
    )

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled Exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "code": 500,
            "message": "Internal Server Error",
            "data": None
        }
    )

@app.post("/feedback/", response_model=ResponseModel, tags=["Feedback"])
async def create_feedback(feedback: FeedbackCreate, db: AsyncSession = Depends(get_db_session)):
    """
    Create a new feedback entry.
    """
    try:
        db_feedback = Feedback(**feedback.dict())
        db.add(db_feedback)
        await db.commit()
        await db.refresh(db_feedback)
        response_data = FeedbackResponseData(
            id=db_feedback.id,
            score=db_feedback.score,
            full_name=db_feedback.full_name,
            email=db_feedback.email,
            created_at=db_feedback.created_at.isoformat(),
            updated_at=db_feedback.updated_at.isoformat()
        )
        return ResponseModel(
            code=200,
            message="Feedback submitted successfully",
            data=response_data
        )
    except Exception as e:
        await db.rollback()
        logger.error(f"Error creating feedback: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/feedback/{feedback_id}", response_model=ResponseModel, tags=["Feedback"])
async def get_feedback(feedback_id: int, db: AsyncSession = Depends(get_db_session)):
    """
    Get a feedback entry by ID.
    """
    try:
        db_feedback = await db.get(Feedback, feedback_id)
        if not db_feedback:
            raise HTTPException(status_code=404, detail="Feedback not found")
        response_data = FeedbackResponseData(
            id=db_feedback.id,
            score=db_feedback.score,
            full_name=db_feedback.full_name,
            email=db_feedback.email,
            created_at=db_feedback.created_at.isoformat(),
            updated_at=db_feedback.updated_at.isoformat()
        )
        return ResponseModel(
            code=200,
            message="Feedback retrieved successfully",
            data=response_data
        )
    except Exception as e:
        logger.error(f"Error getting feedback: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/feedback/", response_model=ResponseModel, tags=["Feedback"])
async def get_all_feedback(db: AsyncSession = Depends(get_db_session)):
    """
    Get all feedback entries.
    """
    try:
        result = await db.execute(select(Feedback))
        feedback_list = result.scalars().all()
        response_data = [FeedbackResponseData(
            id=feedback.id,
            score=feedback.score,
            full_name=feedback.full_name,
            email=feedback.email,
            created_at=feedback.created_at.isoformat(),
            updated_at=feedback.updated_at.isoformat()
        ) for feedback in feedback_list]
        return ResponseModel(
            code=200,
            message="All feedback retrieved successfully",
            data=response_data
        )
    except Exception as e:
        logger.error(f"Error getting all feedback: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/feedback/{feedback_id}", response_model=ResponseModel, tags=["Feedback"])
async def delete_feedback(feedback_id: int, db: AsyncSession = Depends(get_db_session)):
    """
    Delete a feedback entry by ID.
    """
    try:
        db_feedback = await db.get(Feedback, feedback_id)
        if not db_feedback:
            raise HTTPException(status_code=404, detail="Feedback not found")
        await db.delete(db_feedback)
        await db.commit()
        return ResponseModel(
            code=200,
            message="Feedback deleted successfully",
            data=None
        )
    except Exception as e:
        logger.error(f"Error deleting feedback: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/feedback/{feedback_id}", response_model=ResponseModel, tags=["Feedback"])
async def edit_feedback(feedback_id: int, feedback: FeedbackUpdate, db: AsyncSession = Depends(get_db_session)):
    """
    Edit a feedback entry by ID.
    """
    try:
        db_feedback = await db.get(Feedback, feedback_id)
        if not db_feedback:
            raise HTTPException(status_code=404, detail="Feedback not found")

        update_data = feedback.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_feedback, key, value)

        await db.commit()
        await db.refresh(db_feedback)
        response_data = FeedbackResponseData(
            id=db_feedback.id,
            score=db_feedback.score,
            full_name=db_feedback.full_name,
            email=db_feedback.email,
            created_at=db_feedback.created_at.isoformat(),
            updated_at=db_feedback.updated_at.isoformat()
        )
        return ResponseModel(
            code=200,
            message="Feedback updated successfully",
            data=response_data
        )
    except Exception as e:
        logger.error(f"Error updating feedback: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
