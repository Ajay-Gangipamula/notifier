from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List
from app.db.database import get_db
from app.schemas.notification import EventCreate, EventResponse
from app.models.models import Event
from app.workers.event_tasks import process_event

router = APIRouter()

@router.post("/", response_model=EventResponse)
async def create_event(
    event: EventCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Create and process a new event"""
    try:
        # Create event
        db_event = Event(
            event_type=event.event_type,
            user_id=event.user_id,
            event_data=event.event_data
        )
        db.add(db_event)
        db.commit()
        db.refresh(db_event)
        
        # Process event asynchronously
        background_tasks.add_task(process_event.delay, db_event.id)
        
        return db_event
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/", response_model=List[EventResponse])
async def get_events(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get all events"""
    events = db.query(Event).offset(skip).limit(limit).all()
    return events

@router.get("/{event_id}", response_model=EventResponse)
async def get_event(event_id: int, db: Session = Depends(get_db)):
    """Get specific event"""
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    return event