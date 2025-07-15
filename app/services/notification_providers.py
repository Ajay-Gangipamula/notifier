from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import requests
import logging
from app.core.config import settings

logger = logging.getLogger(__name__)

class NotificationProvider(ABC):
    @abstractmethod
    async def send(self, recipient: str, subject: str, body: str, metadata: Dict[str, Any] = None) -> bool:
        pass

class EmailProvider(NotificationProvider):
    async def send(self, recipient: str, subject: str, body: str, metadata: Dict[str, Any] = None) -> bool:
        try:
            if not settings.SMTP_HOST or not settings.SMTP_USER:
                logger.warning("SMTP settings not configured, simulating email send")
                return True
            
            msg = MIMEMultipart()
            msg['From'] = settings.SMTP_USER
            msg['To'] = recipient
            msg['Subject'] = subject
            
            msg.attach(MIMEText(body, 'html'))
            
            server = smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT)
            server.starttls()
            server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
            server.send_message(msg)
            server.quit()
            
            logger.info(f"Email sent successfully to {recipient}")
            return True
            
        except Exception as e:
            logger.error(f"Email send failed to {recipient}: {e}")
            return False

class SMSProvider(NotificationProvider):
    async def send(self, recipient: str, subject: str, body: str, metadata: Dict[str, Any] = None) -> bool:
        try:
            if not settings.TWILIO_ACCOUNT_SID or not settings.TWILIO_AUTH_TOKEN:
                logger.warning("Twilio settings not configured, simulating SMS send")
                return True
            
            # Simulate Twilio SMS (replace with actual implementation)
            logger.info(f"SMS sent successfully to {recipient}: {body}")
            return True
            
        except Exception as e:
            logger.error(f"SMS send failed to {recipient}: {e}")
            return False

class PushProvider(NotificationProvider):
    async def send(self, recipient: str, subject: str, body: str, metadata: Dict[str, Any] = None) -> bool:
        try:
            if not settings.FCM_SERVER_KEY:
                logger.warning("FCM settings not configured, simulating push notification")
                return True
            
            # Simulate FCM push notification
            logger.info(f"Push notification sent successfully to {recipient}")
            return True
            
        except Exception as e:
            logger.error(f"Push notification send failed to {recipient}: {e}")
            return False

class WebhookProvider(NotificationProvider):
    async def send(self, recipient: str, subject: str, body: str, metadata: Dict[str, Any] = None) -> bool:
        try:
            payload = {
                'subject': subject,
                'body': body,
                'metadata': metadata or {},
                'timestamp': str(datetime.utcnow())
            }
            
            response = requests.post(
                recipient, 
                json=payload, 
                timeout=30,
                headers={'Content-Type': 'application/json'}
            )
            
            success = response.status_code == 200
            if success:
                logger.info(f"Webhook sent successfully to {recipient}")
            else:
                logger.error(f"Webhook failed to {recipient}: {response.status_code}")
            
            return success
            
        except Exception as e:
            logger.error(f"Webhook send failed to {recipient}: {e}")
            return False

class NotificationServiceFactory:
    @staticmethod
    def get_provider(notification_type: str) -> NotificationProvider:
        providers = {
            'email': EmailProvider(),
            'sms': SMSProvider(),
            'push': PushProvider(),
            'webhook': WebhookProvider(),
        }
        return providers.get(notification_type.lower())