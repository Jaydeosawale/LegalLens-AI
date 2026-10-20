from datetime import datetime, timedelta
from uuid import uuid4
from typing import Literal
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, Session
from api.database.database import Base, get_db
from api.dependencies import get_current_user, get_current_admin
from api.models.user import User

class ContentReport(Base):
    __tablename__ = "content_reports"
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"), index=True)
    reason: Mapped[str] = mapped_column(String(40))
    content: Mapped[str] = mapped_column(Text)
    details: Mapped[str] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(20), default="pending")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

class ReportCreate(BaseModel):
    reason: Literal["Harmful or unsafe", "Incorrect or misleading", "Privacy concern", "Other"]
    content: str = Field(min_length=1, max_length=8000)
    details: str = Field(default="", max_length=1000)

router = APIRouter(prefix="/content-reports", tags=["AI content reports"])

@router.post("", status_code=201)
def create_report(payload: ReportCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    count = db.query(ContentReport).filter(ContentReport.user_id == user.id, ContentReport.created_at >= datetime.utcnow() - timedelta(days=1)).count()
    if count >= 20:
        raise HTTPException(429, "Report limit reached. Please contact support.")
    if not payload.content.strip():
        raise HTTPException(422, "Select an AI answer to report.")
    report = ContentReport(id=str(uuid4()), user_id=user.id, reason=payload.reason, content=payload.content.strip(), details=payload.details.strip())
    db.add(report)
    db.commit()
    return {"id": report.id, "status": report.status}

@router.get("")
def review_reports(db: Session = Depends(get_db), user: User = Depends(get_current_admin)):
    return [{"id": r.id, "user_id": r.user_id, "reason": r.reason, "content": r.content, "details": r.details, "status": r.status, "created_at": r.created_at} for r in db.query(ContentReport).order_by(ContentReport.created_at.desc()).limit(100).all()]

class ReportReview(BaseModel):
    status: Literal["reviewed", "resolved", "dismissed"]

@router.patch("/{report_id}")
def update_report(report_id: str, payload: ReportReview, db: Session = Depends(get_db), user: User = Depends(get_current_admin)):
    report = db.get(ContentReport, report_id)
    if report is None:
        raise HTTPException(404, "Report not found.")
    report.status = payload.status
    db.commit()
    return {"id": report.id, "status": report.status}
