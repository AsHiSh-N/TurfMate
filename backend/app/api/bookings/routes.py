from datetime import date
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.booking_rules import SLOT_PRICE, is_slot_in_future, is_supported_slot
from app.core.security import get_current_user
from app.db.session import get_db
from app.models import Booking, BookingState, BlockedSlot, Court, Payment, Role, User, Venue, VenueState
from app.schemas.common import BookingCreate

router = APIRouter()


def user_id_from_token(user: dict) -> int:
    try:
        return int(user['sub'])
    except (KeyError, TypeError, ValueError) as exc:
        raise HTTPException(401, 'Invalid token') from exc


def require_customer(user: dict, db: Session) -> int:
    user_id = user_id_from_token(user)
    account = db.query(User).filter(User.id == user_id).first()
    if not account or account.role != Role.CUSTOMER:
        raise HTTPException(403, 'Customer access required')
    return user_id


@router.post('/bookings', status_code=201)
def create(payload: BookingCreate, db: Session = Depends(get_db), user: dict = Depends(get_current_user)):
    customer_id = require_customer(user, db)
    if not is_supported_slot(payload.start_time, payload.end_time):
        raise HTTPException(400, 'Bookings must be one-hour slots between 06:00 and 23:00')
    if payload.booking_date < date.today() or not is_slot_in_future(payload.booking_date, payload.start_time):
        raise HTTPException(400, 'Booking date and time must be in the future')

    try:
        if db.get_bind().dialect.name == 'sqlite':
            db.execute(text('BEGIN IMMEDIATE'))

        venue = db.query(Venue).filter(
            Venue.id == payload.venue_id,
            Venue.status == VenueState.ACTIVE,
        ).first()
        court = db.query(Court).filter(
            Court.id == payload.court_id,
            Court.venue_id == payload.venue_id,
            Court.activity_id == payload.activity_id,
        ).first()
        if not venue or not court:
            raise HTTPException(404, 'Active venue or matching court not found')

        blocked = db.query(BlockedSlot).filter(
            BlockedSlot.court_id == court.id,
            BlockedSlot.date == payload.booking_date,
            BlockedSlot.status == 'ACTIVE',
            BlockedSlot.start_time < payload.end_time,
            BlockedSlot.end_time > payload.start_time,
        ).first()
        if blocked:
            raise HTTPException(409, 'The selected slot is blocked')

        overlap = db.query(Booking).filter(
            Booking.court_id == court.id,
            Booking.booking_date == payload.booking_date,
            Booking.status == BookingState.CONFIRMED,
            Booking.start_time < payload.end_time,
            Booking.end_time > payload.start_time,
        ).first()
        if overlap:
            raise HTTPException(409, 'The selected slot is no longer available')

        booking = Booking(
            booking_reference=f'SPT-{payload.booking_date:%Y%m%d}-{uuid4().hex[:6].upper()}',
            user_id=customer_id,
            venue_id=venue.id,
            court_id=court.id,
            activity_id=court.activity_id,
            booking_date=payload.booking_date,
            start_time=payload.start_time,
            end_time=payload.end_time,
            total_amount=SLOT_PRICE,
            status=BookingState.CONFIRMED,
        )
        db.add(booking)
        db.flush()
        db.add(Payment(
            booking_id=booking.id,
            transaction_id=f'MOCK-{uuid4().hex}',
            amount=SLOT_PRICE,
            status='PAID',
        ))
        db.commit()
        return {
            'success': True,
            'data': {
                'booking_id': booking.id,
                'booking_reference': booking.booking_reference,
                'status': BookingState.CONFIRMED.value,
                'payment_status': 'PAID',
                'total_amount': SLOT_PRICE,
            },
        }
    except Exception:
        db.rollback()
        raise


@router.get('/bookings')
def list_bookings(db: Session = Depends(get_db), user: dict = Depends(get_current_user)):
    customer_id = require_customer(user, db)
    rows = db.query(Booking).filter(Booking.user_id == customer_id).all()
    return {
        'success': True,
        'data': [
            {
                'id': booking.id,
                'booking_reference': booking.booking_reference,
                'venue_id': booking.venue_id,
                'booking_date': booking.booking_date.isoformat(),
                'start_time': booking.start_time.strftime('%H:%M'),
                'end_time': booking.end_time.strftime('%H:%M'),
                'status': booking.status.value,
                'total_amount': booking.total_amount,
            }
            for booking in rows
        ],
    }


@router.post('/bookings/{booking_id}/cancel')
def cancel(booking_id: int, db: Session = Depends(get_db), user: dict = Depends(get_current_user)):
    customer_id = require_customer(user, db)
    booking = db.query(Booking).filter(
        Booking.id == booking_id,
        Booking.user_id == customer_id,
    ).first()
    if not booking:
        raise HTTPException(404, 'Booking not found')
    if booking.status == BookingState.CANCELLED:
        raise HTTPException(409, 'Booking is already cancelled')

    booking.status = BookingState.CANCELLED
    db.commit()
    return {'success': True, 'data': {'id': booking.id, 'status': BookingState.CANCELLED.value}}
