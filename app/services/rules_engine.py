from typing import Dict, Any, List
from sqlalchemy.orm import Session
from app.models.models import NotificationRule, EventType
import logging

logger = logging.getLogger(__name__)

class RulesEngine:
    def __init__(self, db: Session):
        self.db = db
    
    def evaluate_conditions(self, conditions: Dict[str, Any], event_data: Dict[str, Any]) -> bool:
        """
        Evaluate rule conditions against event data
        Supports: equals, not_equals, greater_than, less_than, contains, in_list, exists
        """
        if not conditions:
            return True
            
        try:
            for field, condition in conditions.items():
                if not isinstance(condition, dict):
                    continue
                    
                operator = condition.get("operator")
                value = condition.get("value")
                
                # Check if field exists in event data
                if field not in event_data:
                    if operator == "exists":
                        return False
                    continue
                
                event_value = event_data[field]
                
                # Evaluate conditions
                if operator == "equals" and event_value != value:
                    return False
                elif operator == "not_equals" and event_value == value:
                    return False
                elif operator == "greater_than" and float(event_value) <= float(value):
                    return False
                elif operator == "less_than" and float(event_value) >= float(value):
                    return False
                elif operator == "contains" and value not in str(event_value):
                    return False
                elif operator == "in_list" and event_value not in value:
                    return False
                elif operator == "exists" and field not in event_data:
                    return False
            
            return True
        except Exception as e:
            logger.error(f"Error evaluating conditions: {e}")
            return False
    
    def get_matching_rules(self, event_type: EventType, event_data: Dict[str, Any]) -> List[NotificationRule]:
        """Get all active rules that match the event"""
        try:
            rules = self.db.query(NotificationRule).filter(
                NotificationRule.event_type == event_type,
                NotificationRule.is_active == True
            ).order_by(NotificationRule.priority.desc()).all()
            
            matching_rules = []
            for rule in rules:
                if self.evaluate_conditions(rule.conditions, event_data):
                    matching_rules.append(rule)
            
            logger.info(f"Found {len(matching_rules)} matching rules for event {event_type}")
            return matching_rules
            
        except Exception as e:
            logger.error(f"Error getting matching rules: {e}")
            return []