from app.db.database import SessionLocal
from app.models.models import NotificationTemplate, NotificationRule, NotificationType, EventType
import sys
import os

# Add the app directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def create_initial_data():
    db = SessionLocal()
    try:
        # Create email templates
        email_templates = [
            {
                "name": "Welcome Email",
                "notification_type": NotificationType.EMAIL,
                "subject": "Welcome to our platform, {{user_name}}!",
                "body": """
                <h1>Welcome {{user_name}}!</h1>
                <p>Thank you for signing up. Your email is: {{email}}</p>
                <p>We're excited to have you on board!</p>
                """,
                "variables": {"user_name": "string", "email": "string"}
            },
            {
                "name": "Order Confirmation",
                "notification_type": NotificationType.EMAIL,
                "subject": "Order Confirmed - #{{order_id}}",
                "body": """
                <h1>Order Confirmation</h1>
                <p>Hi {{user_name}},</p>
                <p>Your order #{{order_id}} for ${{amount}} has been confirmed!</p>
                <p>Thank you for your purchase.</p>
                """,
                "variables": {"user_name": "string", "order_id": "string", "amount": "number"}
            }
        ]
        
        # Create SMS templates
        sms_templates = [
            {
                "name": "Welcome SMS",
                "notification_type": NotificationType.SMS,
                "subject": None,
                "body": "Welcome {{user_name}}! Thanks for joining us. Your account is now active.",
                "variables": {"user_name": "string"}
            },
            {
                "name": "Order SMS",
                "notification_type": NotificationType.SMS,
                "subject": None,
                "body": "Order #{{order_id}} confirmed! Amount: ${{amount}}. Thank you!",
                "variables": {"order_id": "string", "amount": "number"}
            }
        ]
        
        # Create templates
        all_templates = email_templates + sms_templates
        created_templates = {}
        
        for template_data in all_templates:
            template = NotificationTemplate(**template_data)
            db.add(template)
            db.flush()  # Get the ID
            created_templates[template_data["name"]] = template.id
        
        # Create notification rules
        rules = [
            {
                "name": "Welcome Email Rule",
                "event_type": EventType.USER_SIGNUP,
                "notification_type": NotificationType.EMAIL,
                "template_id": created_templates["Welcome Email"],
                "conditions": {},
                "priority": 1
            },
            {
                "name": "Welcome SMS Rule",
                "event_type": EventType.USER_SIGNUP,
                "notification_type": NotificationType.SMS,
                "template_id": created_templates["Welcome SMS"],
                "conditions": {"send_sms": {"operator": "equals", "value": True}},
                "priority": 2
            },
            {
                "name": "Order Email Rule",
                "event_type": EventType.ORDER_PLACED,
                "notification_type": NotificationType.EMAIL,
                "template_id": created_templates["Order Confirmation"],
                "conditions": {},
                "priority": 1
            },
            {
                "name": "Order SMS Rule",
                "event_type": EventType.ORDER_PLACED,
                "notification_type": NotificationType.SMS,
                "template_id": created_templates["Order SMS"],
                "conditions": {"amount": {"operator": "greater_than", "value": 100}},
                "priority": 2
            }
        ]
        
        for rule_data in rules:
            rule = NotificationRule(**rule_data)
            db.add(rule)
        
        db.commit()
        print("✅ Initial data created successfully!")
        print(f"Created {len(all_templates)} templates and {len(rules)} rules")
        
    except Exception as e:
        print(f"❌ Error creating initial data: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_initial_data()