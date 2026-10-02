from datetime import date, time
from pydantic import BaseModel

class BookingCreate(BaseModel):
    venue_id: int; court_id: int; activity_id: int; booking_date: date; start_time: time; end_time: time; payment_method: str = "mock"
class VenueCreate(BaseModel):
    name: str; description: str | None = None; address: str; city: str; state: str; pincode: str; activity_id: int; court_name: str = "Court 1"
class BlockCreate(BaseModel):
    venue_id: int; date: date; start_time: time; end_time: time; reason: str
