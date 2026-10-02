from datetime import date, datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.booking_rules import SLOT_PRICE, slots_for_day
from app.db.session import get_db
from app.models import Activity, BlockedSlot, Booking, BookingState, Court, Venue, VenueState

router = APIRouter()


@router.get('/activities')
def activities(db: Session = Depends(get_db)):
    return {'success': True, 'data': [{'id': item.id, 'name': item.name, 'slug': item.slug} for item in db.query(Activity).all()]}


@router.get('/venues')
def venues(city: str | None = None, activity: str | None = None, db: Session = Depends(get_db)):
    query = db.query(Venue).filter(Venue.status == VenueState.ACTIVE)
    if city:
        query = query.filter(func.lower(Venue.city) == city.lower())
    venue_rows = query.all()
    venue_ids = [venue.id for venue in venue_rows]
    courts = db.query(Court).filter(Court.venue_id.in_(venue_ids)).order_by(Court.id).all() if venue_ids else []
    activity_ids = {court.activity_id for court in courts}
    activity_rows = db.query(Activity).filter(Activity.id.in_(activity_ids)).all() if activity_ids else []
    activities_by_id = {item.id: item for item in activity_rows}
    first_court_by_venue = {}
    for court in courts:
        first_court_by_venue.setdefault(court.venue_id, court)

    rows = []
    for venue in venue_rows:
        court = first_court_by_venue.get(venue.id)
        activity_row = activities_by_id.get(court.activity_id) if court else None
        if activity and (not activity_row or activity_row.slug.lower() != activity.lower()):
            continue
        rows.append({
            'id': venue.id,
            'name': venue.name,
            'city': venue.city,
            'activity_id': activity_row.id if activity_row else None,
            'activity': activity_row.name if activity_row else 'Sports',
            'rating': venue.rating,
            'starting_price': SLOT_PRICE,
            'distance_km': 2.4,
        })
    return {'success': True, 'data': rows}


@router.get('/venues/{venue_id}/availability')
def availability(venue_id: int, date: date, db: Session = Depends(get_db)):
    venue = db.query(Venue).filter(Venue.id == venue_id, Venue.status == VenueState.ACTIVE).first()
    if not venue:
        raise HTTPException(404, 'Active venue not found')

    courts = db.query(Court).filter(Court.venue_id == venue_id).all()
    court_ids = [court.id for court in courts]
    bookings = db.query(Booking).filter(
        Booking.court_id.in_(court_ids),
        Booking.booking_date == date,
        Booking.status == BookingState.CONFIRMED,
    ).all() if court_ids else []
    blocked_slots = db.query(BlockedSlot).filter(
        BlockedSlot.court_id.in_(court_ids),
        BlockedSlot.date == date,
        BlockedSlot.status == 'ACTIVE',
    ).all() if court_ids else []

    now = datetime.now()
    available_courts = []
    for court in courts:
        court_bookings = [booking for booking in bookings if booking.court_id == court.id]
        court_blocks = [blocked for blocked in blocked_slots if blocked.court_id == court.id]
        slots = []
        for start_time, end_time in slots_for_day(date):
            has_booking = any(booking.start_time < end_time and booking.end_time > start_time for booking in court_bookings)
            has_block = any(blocked.start_time < end_time and blocked.end_time > start_time for blocked in court_blocks)
            future = datetime.combine(date, start_time) > now
            slots.append({
                'start': start_time.strftime('%H:%M'),
                'end': end_time.strftime('%H:%M'),
                'price': SLOT_PRICE,
                'available': future and not has_booking and not has_block,
            })
        available_courts.append({'court_id': court.id, 'court_name': court.name, 'slots': slots})

    return {'success': True, 'data': {'date': date.isoformat(), 'courts': available_courts}}
