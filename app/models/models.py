from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, JSON, ForeignKey, Enum, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from datetime import datetime

Base = declarative_base()

class NotificationStatus(enum.Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    SENT = "sent"
    FAILED = "failed"
    RETRYING = "retrying"

class NotificationType(enum.Enum):
    EMAIL = "email"
    SMS = "sms"
    PUSH = "push"
    WEBHOOK = "webhook"

class EventType(enum.Enum):
    USER_SIGNUP = "user_signup"
    ORDER_PLACED = "order_placed"
    PAYMENT_SUCCESS = "payment_success"
    PAYMENT_FAILED = "payment_failed"
    USER_LOGIN = "user_login"
    PASSWORD_RESET = "password_reset"
    CUSTOM = "custom"

class NotificationRule(Base):
    __tablename__ = "notification_rules"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    event_type = Column(Enum(EventType), nullable=False)
    notification_type = Column(Enum(NotificationType), nullable=False)
    template_id = Column(Integer, ForeignKey("notification_templates.id"))
    conditions = Column(JSON, default={})
    is_active = Column(Boolean, default=True)
    priority = Column(Integer, default=1)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    template = relationship("NotificationTemplate", back_populates="rules")
    notifications = relationship("Notification", back_populates="rule")

class NotificationTemplate(Base):
    __tablename__ = "notification_templates"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    notification_type = Column(Enum(NotificationType), nullable=False)
    subject = Column(String(500))
    body = Column(Text, nullable=False)
    variables = Column(JSON, default={})
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    rules = relationship("NotificationRule", back_populates="template")

class Notification(Base):
    __tablename__ = "notifications"
    
    id = Column(Integer, primary_key=True, index=True)
    rule_id = Column(Integer, ForeignKey("notification_rules.id"))
    recipient = Column(String(255), nullable=False)
    notification_type = Column(Enum(NotificationType), nullable=False)
    subject = Column(String(500))
    body = Column(Text, nullable=False)
    status = Column(Enum(NotificationStatus), default=NotificationStatus.PENDING)
    retry_count = Column(Integer, default=0)
    max_retries = Column(Integer, default=3)
    scheduled_at = Column(DateTime(timezone=True))
    sent_at = Column(DateTime(timezone=True))
    error_message = Column(Text)
    metadata = Column(JSON, default={})
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    rule = relationship("NotificationRule", back_populates="notifications")

class Event(Base):
    __tablename__ = "events"
    
    id = Column(Integer, primary_key=True, index=True)
    event_type = Column(Enum(EventType), nullable=False)
    user_id = Column(String(255))
    event_data = Column(JSON, nullable=False)
    processed = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class NotificationStats(Base):
    __tablename__ = "notification_stats"
    
    id = Column(Integer, primary_key=True, index=True)
    date = Column(DateTime(timezone=True), nullable=False)
    notification_type = Column(Enum(NotificationType), nullable=False)
    total_sent = Column(Integer, default=0)
    total_failed = Column(Integer, default=0)
    total_retries = Column(Integer, default=0)
    avg_delivery_time = Column(Float, default=0.0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())