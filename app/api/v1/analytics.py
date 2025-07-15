from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.db.database import get_db
from app.models.models import Notification, NotificationStatus, NotificationType
from app.schemas.notification import DashboardStats
from datetime import datetime, timedelta
from typing import Dict, Any

router = APIRouter()

@router.get("/dashboard", response_model=DashboardStats)
async def get_dashboard_stats(db: Session = Depends(get_db)):
    """Get dashboard statistics"""
    today = datetime.utcnow().date()
    
    # Total notifications today
    total_today = db.query(Notification).filter(
        func.date(Notification.created_at) == today
    ).count()
    
    # Sent today
    sent_today = db.query(Notification).filter(
        func.date(Notification.created_at) == today,
        Notification.status == NotificationStatus.SENT
    ).count()
    
    # Failed today
    failed_today = db.query(Notification).filter(
        func.date(Notification.created_at) == today,
        Notification.status == NotificationStatus.FAILED
    ).count()
    
    # Success rate
    success_rate = (sent_today / total_today * 100) if total_today > 0 else 0
    
    # Notifications by type
    type_stats = db.query(
        Notification.notification_type,
        func.count(Notification.id)
    ).filter(
        func.date(Notification.created_at) == today
    ).group_by(Notification.notification_type).all()
    
    notifications_by_type = {str(type_): count for type_, count in type_stats}
    
    return DashboardStats(
        total_notifications_today=total_today,
        total_sent_today=sent_today,
        total_failed_today=failed_today,
        success_rate=round(success_rate, 2),
        avg_delivery_time=0.0,  # Calculate if needed
        notifications_by_type=notifications_by_type,
        hourly_stats=[]  # Add hourly breakdown if needed
    )

@router.get("/stats/summary")
async def get_summary_stats(db: Session = Depends(get_db)):
    """Get summary statistics"""
    total_notifications = db.query(Notification).count()
    total_sent = db.query(Notification).filter(Notification.status == NotificationStatus.SENT).count()
    total_failed = db.query(Notification).filter(Notification.status == NotificationStatus.FAILED).count()
    
    return {
        "total_notifications": total_notifications,
        "total_sent": total_sent,
        "total_failed": total_failed,
        "success_rate": round((total_sent / total_notifications * 100) if total_notifications > 0 else 0, 2)
    }