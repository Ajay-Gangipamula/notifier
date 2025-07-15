from celery import current_task
from app.workers.celery_app import celery_app
from app.db.database import SessionLocal
from app.models.models import Notification, NotificationStatus
from app.services.notification_providers import NotificationServiceFactory
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import logging
import asyncio
from typing import Dict, Any

logger = logging.getLogger(__name__)

def get_db() -> Session:
    return SessionLocal()

@celery_app.task(bind=True, max_retries=3)
def send_notification(self, notification_id: int):
    """Send a single notification"""
    db = get_db()
    try:
        notification = db.query(Notification).filter(
            Notification.id == notification_id
        ).first()
        
        if not notification:
            logger.error(f"Notification {notification_id} not found")
            return False
        
        # Update status to processing
        notification.status = NotificationStatus.PROCESSING
        db.commit()
        
        # Get notification provider
        provider = NotificationServiceFactory.get_provider(
            notification.notification_type.value
        )
        
        if not provider:
            raise ValueError(f"No provider for {notification.notification_type}")
        
        # Send notification
        success = asyncio.run(provider.send(
            recipient=notification.recipient,
            subject=notification.subject or "",
            body=notification.body,
            metadata=notification.metadata
        ))
        
        if success:
            notification.status = NotificationStatus.SENT
            notification.sent_at = datetime.utcnow()
            notification.error_message = None
            logger.info(f"Notification {notification_id} sent successfully")
        else:
            raise Exception("Provider returned failure")
        
        db.commit()
        return True
        
    except Exception as e:
        logger.error(f"Failed to send notification {notification_id}: {e}")
        
        # Update notification with error
        notification = db.query(Notification).filter(
            Notification.id == notification_id
        ).first()
        
        if notification:
            notification.retry_count += 1
            notification.error_message = str(e)
            
            if notification.retry_count >= notification.max_retries:
                notification.status = NotificationStatus.FAILED
                logger.error(f"Notification {notification_id} failed permanently")
            else:
                notification.status = NotificationStatus.RETRYING
                # Calculate backoff delay
                delay = (2 ** notification.retry_count) * 60  # Exponential backoff
                logger.info(f"Retrying notification {notification_id} in {delay} seconds")
                
                # Retry with delay
                self.retry(countdown=delay, exc=e)
            
            db.commit()
        
        db.close()
        return False
    
    finally:
        db.close()

@celery_app.task
def process_pending_notifications():
    """Process all pending notifications"""
    db = get_db()
    try:
        pending_notifications = db.query(Notification).filter(
            Notification.status == NotificationStatus.PENDING,
            Notification.scheduled_at <= datetime.utcnow()
        ).limit(100).all()
        
        for notification in pending_notifications:
            send_notification.delay(notification.id)
        
        logger.info(f"Queued {len(pending_notifications)} pending notifications")
        
    except Exception as e:
        logger.error(f"Error processing pending notifications: {e}")
    finally:
        db.close()

@celery_app.task
def retry_failed_notifications():
    """Retry failed notifications that haven't exceeded max retries"""
    db = get_db()
    try:
        retry_notifications = db.query(Notification).filter(
            Notification.status == NotificationStatus.RETRYING,
            Notification.retry_count < Notification.max_retries
        ).limit(50).all()
        
        for notification in retry_notifications:
            send_notification.delay(notification.id)
        
        logger.info(f"Queued {len(retry_notifications)} notifications for retry")
        
    except Exception as e:
        logger.error(f"Error retrying failed notifications: {e}")
    finally:
        db.close()

@celery_app.task
def send_bulk_notifications(notification_ids: list):
    """Send multiple notifications in bulk"""
    for notification_id in notification_ids:
        send_notification.delay(notification_id)
    
    logger.info(f"Queued {len(notification_ids)} bulk notifications")