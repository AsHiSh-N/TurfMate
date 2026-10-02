'use client';

import { useEffect, useState } from 'react';
import PortalNav from '@/components/PortalNav';
import { apiErrorMessage, apiRequest } from '@/lib/api';

type Venue = { id: number; name: string; city: string; activity: string; activity_id: number | null; rating: number; starting_price: number };
type Slot = { start: string; end: string; price: number; available: boolean };
type CourtAvailability = { court_id: number; court_name: string; slots: Slot[] };

function todayLocal(): string {
  const date = new Date();
  const month = String(date.getMonth() + 1).padStart(2, '0');
  const day = String(date.getDate()).padStart(2, '0');
  return `${date.getFullYear()}-${month}-${day}`;
}

export default function Home() {
  const [venues, setVenues] = useState<Venue[]>([]);
  const [selected, setSelected] = useState<Venue | null>(null);
  const [courts, setCourts] = useState<CourtAvailability[]>([]);
  const [slot, setSlot] = useState<{ court: number; slot: Slot } | null>(null);
  const [date, setDate] = useState(todayLocal());
  const [city, setCity] = useState('Pune');
  const [activity, setActivity] = useState('');
  const [notice, setNotice] = useState('');

  async function load() {
    const query = new URLSearchParams({ city });
    if (activity) query.set('activity', activity);
    try {
      const payload = await apiRequest<{ data: Venue[] }>(`/venues?${query}`);
      setVenues(payload.data ?? []);
      setNotice('');
    } catch (error) {
      setVenues([]);
      setNotice(apiErrorMessage(error, 'Unable to load venues.'));
    }
  }

  useEffect(() => { void load(); }, []);

  async function open(venue: Venue, targetDate = date) {
    setSelected(venue);
    setSlot(null);
    setNotice('');
    try {
      const payload = await apiRequest<{ data: { courts: CourtAvailability[] } }>(`/venues/${venue.id}/availability?date=${targetDate}`);
      setCourts(payload.data?.courts ?? []);
    } catch (error) {
      setCourts([]);
      setNotice(apiErrorMessage(error, 'Unable to load availability.'));
    }
  }

  async function book() {
    const token = window.localStorage.getItem('turfmate_token');
    if (!token || !selected || !slot) {
      setNotice('Sign in and select an available slot first.');
      return;
    }
    try {
      const payload = await apiRequest<{ data: { booking_reference: string } }>('/bookings', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
        body: JSON.stringify({
          venue_id: selected.id,
          court_id: slot.court,
          activity_id: selected.activity_id,
          booking_date: date,
          start_time: slot.slot.start,
          end_time: slot.slot.end,
        }),
      });
      setNotice(`Confirmed: ${payload.data.booking_reference}`);
    } catch (error) {
      setNotice(apiErrorMessage(error, 'Booking failed. Please try again.'));
    }
  }

  return <>
    <PortalNav />
    <main>
      <section className="shell hero">
        <div>
          <p className="eyebrow">Your court, your hour</p>
          <h1 className="font-display">Make time for the game.</h1>
          <p className="muted">Find trusted courts, compare live slots, and book your next match.</p>
          <form className="search" onSubmit={(event) => { event.preventDefault(); void load(); }}>
            <input className="field" value={city} onChange={(event) => setCity(event.target.value)} placeholder="City" />
            <select className="field" value={activity} onChange={(event) => setActivity(event.target.value)}>
              <option value="">All sports</option><option value="badminton">Badminton</option><option value="cricket">Cricket</option>
            </select>
            <button className="button primary">Find a court</button>
          </form>
        </div>
        <div className="hero-art">The best games are already on the calendar.</div>
      </section>
      <section className="shell">
        <p className="eyebrow">Near you</p><h2 className="font-display">Available venues</h2>
        {notice && !selected && <p className="card" role="alert">{notice}</p>}
        <div className="grid">{venues.map((venue) => <article className="card" key={venue.id}>
          <div className="venue-art">{venue.activity[0]}</div><h3>{venue.name}</h3><p className="muted">{venue.city} · ★ {venue.rating}</p>
          <div className="row"><b>From ₹{venue.starting_price}/hr</b><button className="button" onClick={() => void open(venue)}>View slots</button></div>
        </article>)}</div>
      </section>
    </main>
    {selected && <div className="overlay" onClick={() => setSelected(null)}>
      <section className="modal" onClick={(event) => event.stopPropagation()}>
        <div className="row"><div><p className="eyebrow">Book a slot</p><h2>{selected.name}</h2></div><button className="button" onClick={() => setSelected(null)}>Close</button></div>
        <input className="field" type="date" value={date} min={todayLocal()} onChange={(event) => {
          const nextDate = event.target.value;
          setDate(nextDate);
          void open(selected, nextDate);
        }} />
        {notice && <p className="card" role="alert">{notice}</p>}
        {courts.map((court) => <div key={court.court_id}><h3>{court.court_name}</h3><div className="grid" style={{ gridTemplateColumns: 'repeat(3,1fr)' }}>
          {court.slots.map((availableSlot) => <button disabled={!availableSlot.available} className={`slot ${slot?.slot.start === availableSlot.start && slot.court === court.court_id ? 'selected' : ''}`} key={availableSlot.start} onClick={() => setSlot({ court: court.court_id, slot: availableSlot })}>
            {availableSlot.start}<small>₹{availableSlot.price}</small>
          </button>)}
        </div></div>)}
        <button className="button primary" onClick={() => void book()}>Confirm booking</button>
      </section>
    </div>}
  </>;
}
