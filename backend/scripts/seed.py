from app.core.security import hash_password
from app.db.base import Base
from app.db.session import SessionLocal, engine
from app.models import Activity, Court, Role, User, Venue, VenueState


def get_or_create_user(db, email: str, name: str, role: Role, phone: str) -> User:
    user = db.query(User).filter(User.email == email).first()
    if user is None:
        user = User(name=name, email=email, phone=phone, password_hash=hash_password("DemoPass123!"), role=role)
        db.add(user)
        db.flush()
    return user


def seed() -> None:
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        owner = get_or_create_user(db, "owner@example.com", "Demo Venue Owner", Role.VENUE_OWNER, "9999999999")
        get_or_create_user(db, "customer@example.com", "Demo Customer", Role.CUSTOMER, "8888888888")
        get_or_create_user(db, "admin@example.com", "Demo Admin", Role.ADMIN, "7777777777")

        activity = db.query(Activity).filter(Activity.slug == "badminton").first()
        if activity is None:
            activity = Activity(name="Badminton", slug="badminton")
            db.add(activity)
            db.flush()

        venue = db.query(Venue).filter(Venue.slug == "pune-sports-arena").first()
        if venue is None:
            venue = Venue(
                owner_id=owner.id,
                name="Pune Sports Arena",
                slug="pune-sports-arena",
                description="Indoor courts for friendly matches and league nights.",
                address="MG Road",
                city="Pune",
                state="Maharashtra",
                pincode="411001",
                status=VenueState.ACTIVE,
                rating=4.7,
            )
            db.add(venue)
            db.flush()

        if db.query(Court).filter(Court.venue_id == venue.id).first() is None:
            db.add(Court(venue_id=venue.id, activity_id=activity.id, name="Court 1"))
        db.commit()
        print("Seeded demo users and Pune Sports Arena.")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
