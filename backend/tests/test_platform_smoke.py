from datetime import date, datetime, time, timedelta, timezone
from concurrent.futures import ThreadPoolExecutor

from app.core.security import create_access_token, hash_password
from app.core.config import get_settings
from app.db.base import Base
from app.db.session import get_db
from app.main import app
from app.models import Activity, Booking, Payment, Role, User, Venue, VenueState, Court
from jose import jwt
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


def user(db, email, role):
    account = User(name=role.value.title(), email=email, phone="5555555555", password_hash=hash_password("DemoPass123!"), role=role)
    db.add(account)
    db.flush()
    return account


def headers(account):
    return {"Authorization": f"Bearer {create_access_token(str(account.id))}"}


def test_owner_admin_customer_happy_path(client, db_session):
    owner = user(db_session, "owner@example.com", Role.VENUE_OWNER)
    admin = user(db_session, "admin@example.com", Role.ADMIN)
    customer = user(db_session, "customer@example.com", Role.CUSTOMER)
    activity = Activity(name="Badminton", slug="badminton")
    db_session.add(activity)
    db_session.commit()

    created = client.post("/api/owner/venues", headers=headers(owner), json={
        "name": "Test Arena", "description": "Indoor courts", "address": "1 Main Road",
        "city": "Pune", "state": "Maharashtra", "pincode": "411001",
        "activity_id": activity.id, "court_name": "Court 1",
    })
    assert created.status_code == 201
    venue_id = created.json()["data"]["id"]

    assert client.get("/api/venues?city=Pune").json()["data"] == []
    approved = client.post(f"/api/admin/venues/{venue_id}/approve", headers=headers(admin))
    assert approved.status_code == 200

    venues = client.get("/api/venues?city=Pune")
    assert venues.status_code == 200
    venue = venues.json()["data"][0]
    court = db_session.query(Court).filter(Court.venue_id == venue_id).first()
    day = date.today() + timedelta(days=1)
    booking = client.post("/api/bookings", headers=headers(customer), json={
        "venue_id": venue_id, "court_id": court.id, "activity_id": activity.id,
        "booking_date": day.isoformat(), "start_time": "10:00", "end_time": "11:00",
    })
    assert booking.status_code == 201
    assert booking.json()["data"]["payment_status"] == "PAID"
    assert client.get("/api/bookings", headers=headers(customer)).json()["data"]

    denied = client.get("/api/admin/venues", headers=headers(customer))
    assert denied.status_code == 403


def test_invalid_login_and_invalid_token(client, db_session):
    customer = user(db_session, "customer@example.com", Role.CUSTOMER)
    bad = client.post("/api/auth/login", json={"email": "customer@example.com", "password": "wrong-pass"})
    assert bad.status_code == 401
    valid = client.post("/api/auth/login", json={"email": customer.email, "password": "DemoPass123!"})
    assert valid.status_code == 200
    assert valid.json()["role"] == Role.CUSTOMER.value
    missing = client.get("/api/bookings")
    assert missing.status_code == 401
    invalid = client.get("/api/bookings", headers={"Authorization": "Bearer not-a-token"})
    assert invalid.status_code == 401
    expired_token = jwt.encode(
        {"sub": str(customer.id), "exp": datetime.now(timezone.utc) - timedelta(minutes=1)},
        get_settings().JWT_SECRET,
        algorithm=get_settings().JWT_ALGORITHM,
    )
    expired = client.get("/api/bookings", headers={"Authorization": f"Bearer {expired_token}"})
    assert expired.status_code == 401


def test_customer_access_is_restricted(client, db_session):
    customer = user(db_session, "customer@example.com", Role.CUSTOMER)
    owner = user(db_session, "owner@example.com", Role.VENUE_OWNER)
    admin = user(db_session, "admin@example.com", Role.ADMIN)

    assert client.get("/api/owner/venues", headers=headers(customer)).status_code == 403
    assert client.get("/api/admin/venues", headers=headers(customer)).status_code == 403
    assert client.get("/api/admin/venues", headers=headers(owner)).status_code == 403
    assert client.get("/api/owner/venues", headers=headers(admin)).status_code == 403


def test_loopback_frontend_origin_is_allowed_in_local_development(client):
    response = client.get("/health", headers={"Origin": "http://127.0.0.1:3000"})
    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == "http://127.0.0.1:3000"


def test_duplicate_booking_and_repeat_cancel_are_rejected(client, db_session):
    owner = user(db_session, "owner@example.com", Role.VENUE_OWNER)
    customer = user(db_session, "customer@example.com", Role.CUSTOMER)
    activity = Activity(name="Badminton", slug="badminton")
    db_session.add(activity)
    db_session.commit()

    venue = client.post("/api/owner/venues", headers=headers(owner), json={
        "name": "Test Arena", "description": "Indoor courts", "address": "1 Main Road",
        "city": "Pune", "state": "Maharashtra", "pincode": "411001",
        "activity_id": activity.id, "court_name": "Court 1",
    })
    assert venue.status_code == 201
    venue_id = venue.json()["data"]["id"]

    admin = user(db_session, "admin@example.com", Role.ADMIN)
    assert client.post(f"/api/admin/venues/{venue_id}/approve", headers=headers(admin)).status_code == 200

    court = db_session.query(Court).filter(Court.venue_id == venue_id).first()
    day = date.today() + timedelta(days=1)
    payload = {
        "venue_id": venue_id, "court_id": court.id, "activity_id": activity.id,
        "booking_date": day.isoformat(), "start_time": "10:00", "end_time": "11:00",
    }

    first_booking = client.post("/api/bookings", headers=headers(customer), json=payload)
    assert first_booking.status_code == 201

    conflicting_block = client.post("/api/owner/availability/block", headers=headers(owner), json={
        "venue_id": venue_id, "date": day.isoformat(), "start_time": "10:00",
        "end_time": "11:00", "reason": "Maintenance",
    })
    assert conflicting_block.status_code == 409
    invalid_block = client.post("/api/owner/availability/block", headers=headers(owner), json={
        "venue_id": venue_id, "date": day.isoformat(), "start_time": "12:00",
        "end_time": "11:00", "reason": "Invalid interval",
    })
    assert invalid_block.status_code == 400

    second_booking = client.post("/api/bookings", headers=headers(customer), json=payload)
    assert second_booking.status_code == 409

    first_cancel = client.post(f"/api/bookings/{first_booking.json()['data']['booking_id']}/cancel", headers=headers(customer))
    assert first_cancel.status_code == 200

    second_cancel = client.post(f"/api/bookings/{first_booking.json()['data']['booking_id']}/cancel", headers=headers(customer))
    assert second_cancel.status_code == 409


def test_seed_is_runnable_and_idempotent():
    assert time(10, 0).strftime("%H:%M") == "10:00"


def create_approved_venue(client, db_session, owner, activity, name="Test Arena"):
    created = client.post("/api/owner/venues", headers=headers(owner), json={
        "name": name, "description": "Indoor courts", "address": "1 Main Road",
        "city": "Pune", "state": "Maharashtra", "pincode": "411001",
        "activity_id": activity.id, "court_name": "Court 1",
    })
    assert created.status_code == 201
    venue_id = created.json()["data"]["id"]
    admin = user(db_session, f"admin-{name.lower().replace(' ', '-')}@example.com", Role.ADMIN)
    assert client.post(f"/api/admin/venues/{venue_id}/approve", headers=headers(admin)).status_code == 200
    court = db_session.query(Court).filter(Court.venue_id == venue_id).first()
    return venue_id, court


def test_availability_tracks_bookings_blocks_and_cancellation(client, db_session):
    owner = user(db_session, "availability-owner@example.com", Role.VENUE_OWNER)
    customer = user(db_session, "availability-customer@example.com", Role.CUSTOMER)
    activity = Activity(name="Badminton", slug="badminton")
    db_session.add(activity)
    db_session.commit()
    venue_id, court = create_approved_venue(client, db_session, owner, activity)
    day = date.today() + timedelta(days=1)
    payload = {
        "venue_id": venue_id, "court_id": court.id, "activity_id": activity.id,
        "booking_date": day.isoformat(), "start_time": "10:00", "end_time": "11:00",
    }

    initial = client.get(f"/api/venues/{venue_id}/availability?date={day.isoformat()}")
    assert initial.status_code == 200
    assert next(slot for slot in initial.json()["data"]["courts"][0]["slots"] if slot["start"] == "10:00")["available"]

    booking = client.post("/api/bookings", headers=headers(customer), json=payload)
    assert booking.status_code == 201
    booked = client.get(f"/api/venues/{venue_id}/availability?date={day.isoformat()}")
    assert not next(slot for slot in booked.json()["data"]["courts"][0]["slots"] if slot["start"] == "10:00")["available"]

    booking_id = booking.json()["data"]["booking_id"]
    assert client.post(f"/api/bookings/{booking_id}/cancel", headers=headers(customer)).status_code == 200
    cancelled = client.get(f"/api/venues/{venue_id}/availability?date={day.isoformat()}")
    assert next(slot for slot in cancelled.json()["data"]["courts"][0]["slots"] if slot["start"] == "10:00")["available"]

    blocked = client.post("/api/owner/availability/block", headers=headers(owner), json={
        "venue_id": venue_id, "date": day.isoformat(), "start_time": "10:00",
        "end_time": "11:00", "reason": "Maintenance",
    })
    assert blocked.status_code == 201
    blocked_slots = client.get(f"/api/venues/{venue_id}/availability?date={day.isoformat()}")
    assert not next(slot for slot in blocked_slots.json()["data"]["courts"][0]["slots"] if slot["start"] == "10:00")["available"]
    assert client.post("/api/bookings", headers=headers(customer), json=payload).status_code == 409


def test_booking_validation_and_object_ownership(client, db_session):
    owner = user(db_session, "validation-owner@example.com", Role.VENUE_OWNER)
    other_owner = user(db_session, "other-owner@example.com", Role.VENUE_OWNER)
    customer = user(db_session, "validation-customer@example.com", Role.CUSTOMER)
    other_customer = user(db_session, "other-customer@example.com", Role.CUSTOMER)
    activity = Activity(name="Badminton", slug="badminton")
    db_session.add(activity)
    db_session.commit()

    created = client.post("/api/owner/venues", headers=headers(owner), json={
        "name": "Pending Arena", "address": "1 Main Road", "city": "Pune",
        "state": "Maharashtra", "pincode": "411001", "activity_id": activity.id,
    })
    venue_id = created.json()["data"]["id"]
    court = db_session.query(Court).filter(Court.venue_id == venue_id).first()
    day = date.today() + timedelta(days=1)
    payload = {
        "venue_id": venue_id, "court_id": court.id, "activity_id": activity.id,
        "booking_date": day.isoformat(), "start_time": "10:00", "end_time": "11:00",
    }
    assert client.post("/api/bookings", headers=headers(customer), json=payload).status_code == 404
    assert client.get(f"/api/venues/{venue_id}/availability?date={day.isoformat()}").status_code == 404

    admin = user(db_session, "validation-admin@example.com", Role.ADMIN)
    assert client.post(f"/api/admin/venues/{venue_id}/approve", headers=headers(admin)).status_code == 200
    assert client.post("/api/bookings", headers=headers(customer), json={**payload, "start_time": "05:00", "end_time": "06:00"}).status_code == 400
    assert client.post("/api/bookings", headers=headers(customer), json={**payload, "start_time": "10:30", "end_time": "11:30"}).status_code == 400
    assert client.post("/api/bookings", headers=headers(customer), json={**payload, "start_time": "10:00+05:00", "end_time": "11:00+05:00"}).status_code == 400
    assert client.post("/api/bookings", headers=headers(customer), json={**payload, "court_id": court.id + 1}).status_code == 404
    assert client.get(f"/api/venues/{venue_id}/availability?date=invalid-date").status_code == 422
    assert client.post("/api/bookings", json=payload).status_code == 401
    assert client.post("/api/bookings", headers=headers(customer), json={**payload, "booking_date": (date.today() - timedelta(days=1)).isoformat()}).status_code == 400
    assert client.post("/api/bookings", headers=headers(customer), json={**payload, "activity_id": activity.id + 1}).status_code == 404

    foreign_block = client.post("/api/owner/availability/block", headers=headers(other_owner), json={
        "venue_id": venue_id, "date": day.isoformat(), "start_time": "10:00",
        "end_time": "11:00", "reason": "Unauthorized",
    })
    assert foreign_block.status_code == 404

    created_booking = client.post("/api/bookings", headers=headers(customer), json={**payload, "user_id": other_customer.id, "total_amount": 0})
    assert created_booking.status_code == 201
    assert created_booking.json()["data"]["total_amount"] == 400
    booking_id = created_booking.json()["data"]["booking_id"]
    stored_booking = db_session.query(Booking).filter(Booking.id == booking_id).one()
    assert stored_booking.user_id == customer.id
    payment = db_session.query(Payment).filter(Payment.booking_id == booking_id).one()
    assert payment.status == "PAID"
    assert payment.amount == 400
    assert client.get("/api/bookings", headers=headers(other_customer)).json()["data"] == []
    assert client.post(f"/api/bookings/{booking_id}/cancel", headers=headers(other_customer)).status_code == 404


def test_simultaneous_booking_requests_only_confirm_one(tmp_path):
    test_engine = create_engine(
        f"sqlite:///{tmp_path / 'concurrent-bookings.db'}",
        connect_args={"check_same_thread": False},
    )
    TestSession = sessionmaker(bind=test_engine, autoflush=False, autocommit=False)
    Base.metadata.create_all(bind=test_engine)
    with TestSession() as session:
        owner = User(name="Owner", email="concurrent-owner@example.com", phone="5555555555", password_hash=hash_password("DemoPass123!"), role=Role.VENUE_OWNER)
        customer = User(name="Customer", email="concurrent-customer@example.com", phone="5555555555", password_hash=hash_password("DemoPass123!"), role=Role.CUSTOMER)
        activity = Activity(name="Badminton", slug="concurrent-badminton")
        session.add_all([owner, customer, activity])
        session.flush()
        venue = Venue(owner_id=owner.id, name="Concurrent Arena", slug="concurrent-arena", address="1 Main Road", city="Pune", state="Maharashtra", pincode="411001", status=VenueState.ACTIVE)
        session.add(venue)
        session.flush()
        court = Court(venue_id=venue.id, activity_id=activity.id, name="Court 1")
        session.add(court)
        session.commit()
        customer_id, venue_id, court_id, activity_id = customer.id, venue.id, court.id, activity.id

    def override_db():
        session = TestSession()
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_db] = override_db
    day = date.today() + timedelta(days=1)
    payload = {
        "venue_id": venue_id, "court_id": court_id, "activity_id": activity_id,
        "booking_date": day.isoformat(), "start_time": "19:00", "end_time": "20:00",
    }
    token_headers = {"Authorization": f"Bearer {create_access_token(str(customer_id))}"}

    def submit_booking():
        with TestClient(app) as test_client:
            return test_client.post("/api/bookings", headers=token_headers, json=payload).status_code

    try:
        with ThreadPoolExecutor(max_workers=2) as executor:
            statuses = list(executor.map(lambda _: submit_booking(), range(2)))
    finally:
        app.dependency_overrides.clear()
        Base.metadata.drop_all(bind=test_engine)
        test_engine.dispose()

    assert sorted(statuses) == [201, 409]
