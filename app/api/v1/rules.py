from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.db.database import get_db
from app.schemas.notification import NotificationRuleCreate, NotificationRuleResponse
from app.models.models import NotificationRule

router = APIRouter()

@router.post("/", response_model=NotificationRuleResponse)
async def create_rule(rule: NotificationRuleCreate, db: Session = Depends(get_db)):
    """Create a new notification rule"""
    db_rule = NotificationRule(**rule.dict())
    db.add(db_rule)
    db.commit()
    db.refresh(db_rule)
    return db_rule

@router.get("/", response_model=List[NotificationRuleResponse])
async def get_rules(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get all notification rules"""
    rules = db.query(NotificationRule).offset(skip).limit(limit).all()
    return rules

@router.get("/{rule_id}", response_model=NotificationRuleResponse)
async def get_rule(rule_id: int, db: Session = Depends(get_db)):
    """Get specific rule"""
    rule = db.query(NotificationRule).filter(NotificationRule.id == rule_id).first()
    if not rule:
        raise HTTPException(status_code=404, detail="Rule not found")
    return rule

@router.put("/{rule_id}", response_model=NotificationRuleResponse)
async def update_rule(rule_id: int, rule_update: NotificationRuleCreate, db: Session = Depends(get_db)):
    """Update a rule"""
    rule = db.query(NotificationRule).filter(NotificationRule.id == rule_id).first()
    if not rule:
        raise HTTPException(status_code=404, detail="Rule not found")
    
    for field, value in rule_update.dict().items():
        setattr(rule, field, value)
    
    db.commit()
    db.refresh(rule)
    return rule

@router.delete("/{rule_id}")
async def delete_rule(rule_id: int, db: Session = Depends(get_db)):
    """Delete a rule"""
    rule = db.query(NotificationRule).filter(NotificationRule.id == rule_id).first()
    if not rule:
        raise HTTPException(status_code=404, detail="Rule not found")
    
    db.delete(rule)
    db.commit()
    return {"message": "Rule deleted successfully"}
