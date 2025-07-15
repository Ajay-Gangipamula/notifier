import requests
import json

BASE_URL = "http://localhost:8000/api/v1"

def test_notification_system():
    print("🧪 Testing Notification Orchestrator...")
    
    # Test 1: Create a user signup event
    print("\n1. Creating user signup event...")
    event_data = {
        "event_type": "user_signup",
        "user_id": "user123",
        "event_data": {
            "user_name": "John Doe",
            "email": "john@example.com",
            "phone": "+1234567890",
            "send_sms": True
        }
    }
    
    response = requests.post(f"{BASE_URL}/events/", json=event_data)
    if response.status_code == 200:
        print("✅ Event created successfully!")
        event_id = response.json()["id"]
        print(f"Event ID: {event_id}")
    else:
        print(f"❌ Failed to create event: {response.text}")
        return
    
    # Test 2: Create an order event
    print("\n2. Creating order event...")
    order_data = {
        "event_type": "order_placed",
        "user_id": "user123",
        "event_data": {
            "user_name": "John Doe",
            "email": "john@example.com",
            "phone": "+1234567890",
            "order_id": "ORD-001",
            "amount": 150.00
        }
    }
    
    response = requests.post(f"{BASE_URL}/events/", json=order_data)
    if response.status_code == 200:
        print("✅ Order event created successfully!")
    else:
        print(f"❌ Failed to create order event: {response.text}")
    
    # Test 3: Check notifications
    print("\n3. Checking notifications...")
    import time
    time.sleep(2)  # Wait for processing
    
    response = requests.get(f"{BASE_URL}/notifications/")
    if response.status_code == 200:
        notifications = response.json()
        print(f"✅ Found {len(notifications)} notifications")
        for notif in notifications:
            print(f"  - {notif['notification_type']} to {notif['recipient']}: {notif['status']}")
    else:
        print(f"❌ Failed to get notifications: {response.text}")
    
    # Test 4: Check dashboard stats
    print("\n4. Checking dashboard stats...")
    response = requests.get(f"{BASE_URL}/analytics/dashboard")
    if response.status_code == 200:
        stats = response.json()
        print("✅ Dashboard stats:")
        print(f"  - Total today: {stats['total_notifications_today']}")
        print(f"  - Sent today: {stats['total_sent_today']}")
        print(f"  - Success rate: {stats['success_rate']}%")
    else:
        print(f"❌ Failed to get stats: {response.text}")

if __name__ == "__main__":
    test_notification_system()