from app.workers.celery_app import celery_app
from app.db.database import SessionLocal
from app.models.models import Event, Notification, NotificationStatus
from app.services.rules_engine import RulesEngine
from app.services.template_service import TemplateService
from sqlalchemy.orm import Session
from datetime import datetime
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

def get_db() -> Session:
    return SessionLocal()

def extract_recipient(event_data: Dict[str, Any], notification_type: str) -> str:
    """Extract recipient based on notification type"""
    if notification_type == "email":
        return event_data.get("email") or event_data.get("user_email")
    elif notification_type == "sms":
        return event_data.get("phone") or event_data.get("mobile")
    elif notification_type == "push":
        return event_data.get("device_token") or event_data.get("fcm_token")
    elif notification_type == "webhook":
        return event_data.get("webhook_url") or event_data.get("callback_url")
    return None

@celery_app.task
def process_event(event_id: int):
    """Process a single event and trigger notifications"""
    db = get_db()
    try:
        event = db.query(Event).filter(Event.id == event_id).first()
        
        if not event:
            logger.error(f"Event {event_id} not found")
            return False
        
        if event.processed:
            logger.warning(f"Event {event_id} already processed")
            return True
        
        # Initialize services
        rules_engine = RulesEngine(db)
        template_service = TemplateService(db)
        
        # Get matching rules
        matching_rules = rules_engine.get_matching_rules(
            event.event_type, 
            event.event_data
        )
        
        notifications_created = 0
        
        for rule in matching_rules:
            try:
                # Extract recipient from event data
                recipient = extract_recipient(event.event_data, rule.notification_type.value)
                
                if not recipient:
                    logger.warning(f"No recipient found for rule {rule.id}")
                    continue
                
                # Render template
                subject, body = template_service.render_template(
                    rule.template_id, 
                    event.event_data
                )
                
                # Create notification
                notification = Notification(
                    rule_id=rule.id,
                    recipient=recipient,
                    notification_type=rule.notification_type,
                    subject=subject,
                    body=body,
                    status=NotificationStatus.PENDING,
                    scheduled_at=datetime.utcnow(),
                    metadata={
                        'event_id': event.id,
                        'rule_id': rule.id,
                        'event_type': event.event_type.value
                    }
                )
                
                db.add(notification)
                notifications_created += 1
                
            except Exception as e:
                logger.error(f"Error creating notification for rule {rule.id}: {e}")
                continue
        
        # Mark event as processed
        event.processed = True
        db.commit()
        
        logger.info(f"Event {event_id} processed, created {notifications_created} notifications")
        return True
        
    except Exception as e:
        logger.error(f"Error processing event {event_id}: {e}")
        return False
    finally:
        db.close()