from app.workers.celery_app import celery_app
from app.db.database import SessionLocal
from app.models.models import Notification, NotificationStats, NotificationStatus
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

def get_db() -> Session:
    return SessionLocal()

@celery_app.task
def update_daily_stats():
    """Update daily notification statistics"""
    db = get_db()
    try:
        today = datetime.utcnow().date()
        
        # Get stats for each notification type
        stats_query = db.query(
            Notification.notification_type,
            func.count(Notification.id).label('total'),
            func.sum(func.case([(Notification.status == NotificationStatus.SENT, 1)], else_=0)).label('sent'),
            func.sum(func.case([(Notification.status == NotificationStatus.FAILED, 1)], else_=0)).label('failed'),
            func.sum(Notification.retry_count).label('retries')
        ).filter(
            func.date(Notification.created_at) == today
        ).group_by(Notification.notification_type).all()
        
        for stat in stats_query:
            # Update or create daily stats
            existing_stat = db.query(NotificationStats).filter(
                func.date(NotificationStats.date) == today,
                NotificationStats.notification_type == stat.notification_type
            ).first()
            
            if existing_stat:
                existing_stat.total_sent = stat.sent or 0
                existing_stat.total_failed = stat.failed or 0
                existing_stat.total_retries = stat.retries or 0
            else:
                new_stat = NotificationStats(
                    date=datetime.combine(today, datetime.min.time()),
                    notification_type=stat.notification_type,
                    total_sent=stat.sent or 0,
                    total_failed=stat.failed or 0,
                    total_retries=stat.retries or 0
                )
                db.add(new_stat)
        
        db.commit()
        logger.info(f"Updated daily stats for {today}")
        
    except Exception as e:
        logger.error(f"Error updating daily stats: {e}")
    finally:
        db.close()