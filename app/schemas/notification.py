from pydantic import BaseModel, EmailStr, validator
from typing import Optional, Dict, Any, List
from datetime import datetime
from app.models.models import NotificationStatus, NotificationType, EventType

# Event Schemas
class EventCreate(BaseModel):
    event_type: EventType
    user_id: Optional[str] = None
    event_data: Dict[str, Any]

class EventResponse(BaseModel):
    id: int
    event_type: EventType
    user_id: Optional[str]
    event_data: Dict[str, Any]
    processed: bool
    created_at: datetime

    class Config:
        from_attributes = True

# Template Schemas
class NotificationTemplateCreate(BaseModel):
    name: str
    notification_type: NotificationType
    subject: Optional[str] = None
    body: str
    variables: Dict[str, Any] = {}

class NotificationTemplateResponse(BaseModel):
    id: int
    name: str
    notification_type: NotificationType
    subject: Optional[str]
    body: str
    variables: Dict[str, Any]
    created_at: datetime

    class Config:
        from_attributes = True

# Rule Schemas
class NotificationRuleCreate(BaseModel):
    name: str
    event_type: EventType
    notification_type: NotificationType
    template_id: int
    conditions: Dict[str, Any] = {}
    priority: int = 1

class NotificationRuleResponse(BaseModel):
    id: int
    name: str
    event_type: EventType
    notification_type: NotificationType
    template_id: int
    conditions: Dict[str, Any]
    is_active: bool
    priority: int
    created_at: datetime

    class Config:
        from_attributes = True

# Notification Schemas
class NotificationResponse(BaseModel):
    id: int
    recipient: str
    notification_type: NotificationType
    subject: Optional[str]
    body: str
    status: NotificationStatus
    retry_count: int
    sent_at: Optional[datetime]
    error_message: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True

# Analytics Schemas
class NotificationStatsResponse(BaseModel):
    date: datetime
    notification_type: NotificationType
    total_sent: int
    total_failed: int
    total_retries: int
    avg_delivery_time: float

    class Config:
        from_attributes = True

class DashboardStats(BaseModel):
    total_notifications_today: int
    total_sent_today: int
    total_failed_today: int
    success_rate: float
    avg_delivery_time: float
    notifications_by_type: Dict[str, int]
    hourly_stats: List[Dict[str, Any]]
