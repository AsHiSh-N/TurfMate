from datetime import date, datetime, time, timedelta

OPENING_HOUR = 6
CLOSING_HOUR = 23
SLOT_PRICE = 400


def is_supported_slot(start_time: time, end_time: time) -> bool:
    if start_time.tzinfo is not None or end_time.tzinfo is not None:
        return False
    if start_time.minute or start_time.second or start_time.microsecond:
        return False
    if end_time.minute or end_time.second or end_time.microsecond:
        return False
    return OPENING_HOUR <= start_time.hour < CLOSING_HOUR and end_time.hour == start_time.hour + 1


def is_slot_in_future(target_date: date, start_time: time) -> bool:
    if target_date > date.today():
        return True
    return target_date == date.today() and datetime.combine(target_date, start_time) > datetime.now()


def slots_for_day(target_date: date) -> list[tuple[time, time]]:
    start = datetime.combine(target_date, time(OPENING_HOUR))
    closing = datetime.combine(target_date, time(CLOSING_HOUR))
    slots = []
    while start + timedelta(hours=1) <= closing:
        end = start + timedelta(hours=1)
        slots.append((start.time(), end.time()))
        start = end
    return slots