from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.db.database import get_db
from app.schemas.notification import NotificationTemplateCreate, NotificationTemplateResponse
from app.models.models import NotificationTemplate

router = APIRouter()

@router.post("/", response_model=NotificationTemplateResponse)
async def create_template(template: NotificationTemplateCreate, db: Session = Depends(get_db)):
    """Create a new notification template"""
    db_template = NotificationTemplate(**template.dict())
    db.add(db_template)
    db.commit()
    db.refresh(db_template)
    return db_template

@router.get("/", response_model=List[NotificationTemplateResponse])
async def get_templates(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get all templates"""
    templates = db.query(NotificationTemplate).offset(skip).limit(limit).all()
    return templates

@router.get("/{template_id}", response_model=NotificationTemplateResponse)
async def get_template(template_id: int, db: Session = Depends(get_db)):
    """Get specific template"""
    template = db.query(NotificationTemplate).filter(NotificationTemplate.id == template_id).first()
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    return template