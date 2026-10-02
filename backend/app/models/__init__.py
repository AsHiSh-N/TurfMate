from datetime import date, time
from enum import Enum
from sqlalchemy import Date, Enum as SAEnum, Float, ForeignKey, String, Time
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base

class Role(str, Enum): CUSTOMER = "CUSTOMER"; VENUE_OWNER = "VENUE_OWNER"; ADMIN = "ADMIN"
class VenueState(str, Enum): PENDING = "PENDING"; ACTIVE = "ACTIVE"; REJECTED = "REJECTED"
class BookingState(str, Enum): CONFIRMED = "CONFIRMED"; CANCELLED = "CANCELLED"

class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120))
    email: Mapped[str] = mapped_column(String(150), unique=True)
    phone: Mapped[str] = mapped_column(String(30))
    password_hash: Mapped[str] = mapped_column(String(255))
    role: Mapped[Role] = mapped_column(SAEnum(Role), default=Role.CUSTOMER)

class Activity(Base):
    __tablename__ = "activities"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(80))
    slug: Mapped[str] = mapped_column(String(80), unique=True)

class Venue(Base):
    __tablename__ = "venues"
    id: Mapped[int] = mapped_column(primary_key=True)
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    name: Mapped[str] = mapped_column(String(150))
    slug: Mapped[str] = mapped_column(String(150), unique=True)
    description: Mapped[str | None] = mapped_column(String(1000))
    address: Mapped[str] = mapped_column(String(250))
    city: Mapped[str] = mapped_column(String(80))
    state: Mapped[str] = mapped_column(String(80))
    pincode: Mapped[str] = mapped_column(String(20))
    status: Mapped[VenueState] = mapped_column(SAEnum(VenueState), default=VenueState.PENDING)
    rating: Mapped[float] = mapped_column(Float, default=4.5)

class Court(Base):
    __tablename__ = "courts"
    id: Mapped[int] = mapped_column(primary_key=True)
    venue_id: Mapped[int] = mapped_column(ForeignKey("venues.id"))
    activity_id: Mapped[int] = mapped_column(ForeignKey("activities.id"))
    name: Mapped[str] = mapped_column(String(100))

class Booking(Base):
    __tablename__ = "bookings"
    id: Mapped[int] = mapped_column(primary_key=True)
    booking_reference: Mapped[str] = mapped_column(String(50), unique=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    venue_id: Mapped[int] = mapped_column(ForeignKey("venues.id"))
    court_id: Mapped[int] = mapped_column(ForeignKey("courts.id"))
    activity_id: Mapped[int] = mapped_column(ForeignKey("activities.id"))
    booking_date: Mapped[date] = mapped_column(Date)
    start_time: Mapped[time] = mapped_column(Time)
    end_time: Mapped[time] = mapped_column(Time)
    total_amount: Mapped[float] = mapped_column(Float, default=400)
    status: Mapped[BookingState] = mapped_column(SAEnum(BookingState), default=BookingState.CONFIRMED)

class Payment(Base):
    __tablename__ = "payments"
    id: Mapped[int] = mapped_column(primary_key=True)
    booking_id: Mapped[int] = mapped_column(ForeignKey("bookings.id"))
    transaction_id: Mapped[str] = mapped_column(String(100), unique=True)
    amount: Mapped[float] = mapped_column(Float)
    status: Mapped[str] = mapped_column(String(20), default="PAID")

class BlockedSlot(Base):
    __tablename__ = "blocked_slots"
    id: Mapped[int] = mapped_column(primary_key=True)
    court_id: Mapped[int] = mapped_column(ForeignKey("courts.id"))
    date: Mapped[date] = mapped_column(Date)
    start_time: Mapped[time] = mapped_column(Time)
    end_time: Mapped[time] = mapped_column(Time)
    reason: Mapped[str] = mapped_column(String(200))
    status: Mapped[str] = mapped_column(String(20), default="ACTIVE")
