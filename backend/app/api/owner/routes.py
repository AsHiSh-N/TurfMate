import re
from datetime import time

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.db.session import get_db
from app.models import Activity, BlockedSlot, Booking, BookingState, Court, Role, User, Venue, VenueState
from app.schemas.common import BlockCreate, VenueCreate

router = APIRouter()


def owner_id(user: dict, db: Session) -> int:
    try:
        user_id = int(user['sub'])
    except (KeyError, TypeError, ValueError) as exc:
        raise HTTPException(401, 'Invalid token') from exc
    account = db.query(User).filter(User.id == user_id).first()
    if not account or account.role != Role.VENUE_OWNER:
        raise HTTPException(403, 'Venue owner access required')
    return user_id


def slugify(value: str) -> str:
    return re.sub(r'[^a-z0-9]+', '-', value.lower()).strip('-')


@router.get('/venues')
def owner_venues(db: Session = Depends(get_db), user: dict = Depends(get_current_user)):
    venues = db.query(Venue).filter(Venue.owner_id == owner_id(user, db)).all()
    return {'success': True, 'data': [{'id': venue.id, 'name': venue.name, 'city': venue.city, 'status': venue.status.value} for venue in venues]}


@router.post('/venues', status_code=201)
def create_venue(payload: VenueCreate, db: Session = Depends(get_db), user: dict = Depends(get_current_user)):
    activity = db.query(Activity).filter(Activity.id == payload.activity_id).first()
    if not activity:
        raise HTTPException(404, 'Activity not found')
    venue = Venue(
        owner_id=owner_id(user, db),
        name=payload.name,
        slug=slugify(payload.name),
        description=payload.description,
        address=payload.address,
        city=payload.city,
        state=payload.state,
        pincode=payload.pincode,
        status=VenueState.PENDING,
    )
    db.add(venue)
    db.flush()
    db.add(Court(venue_id=venue.id, activity_id=activity.id, name=payload.court_name))
    db.commit()
    return {'success': True, 'data': {'id': venue.id, 'name': venue.name, 'status': VenueState.PENDING.value}}


@router.post('/availability/block', status_code=201)
def block(payload: BlockCreate, db: Session = Depends(get_db), user: dict = Depends(get_current_user)):
    venue = db.query(Venue).filter(
        Venue.id == payload.venue_id,
        Venue.owner_id == owner_id(user, db),
    ).first()
    court = db.query(Court).filter(Court.venue_id == payload.venue_id).first()
    if not venue or not court:
        raise HTTPException(404, 'Venue or court not found')
    if payload.start_time >= payload.end_time or payload.start_time < time(6) or payload.end_time > time(23):
        raise HTTPException(400, 'Blocked interval must be within 06:00 to 23:00 and end after it starts')

    booking = db.query(Booking).filter(
        Booking.court_id == court.id,
        Booking.booking_date == payload.date,
        Booking.status == BookingState.CONFIRMED,
        Booking.start_time < payload.end_time,
        Booking.end_time > payload.start_time,
    ).first()
    if booking:
        raise HTTPException(409, 'Cannot block a slot with a confirmed booking')

    db.add(BlockedSlot(
        court_id=court.id,
        date=payload.date,
        start_time=payload.start_time,
        end_time=payload.end_time,
        reason=payload.reason,
    ))
    db.commit()
    return {'success': True, 'data': {'blocked': True}}
