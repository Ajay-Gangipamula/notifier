from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from app.db.database import get_db
from app.schemas.notification import NotificationResponse
from app.models.models import Notification, NotificationStatus

router = APIRouter()

@router.get("/", response_model=List[NotificationResponse])
async def get_notifications(
    skip: int = 0, 
    limit: int = 100, 
    status: Optional[NotificationStatus] = None,
    db: Session = Depends(get_db)
):
    """Get all notifications with optional status filter"""
    query = db.query(Notification)
    if status:
        query = query.filter(Notification.status == status)
    
    notifications = query.offset(skip).limit(limit).all()
    return notifications

@router.get("/{notification_id}", response_model=NotificationResponse)
async def get_notification(notification_id: int, db: Session = Depends(get_db)):
    """Get specific notification"""
    notification = db.query(Notification).filter(Notification.id == notification_id).first()
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")
    return notification