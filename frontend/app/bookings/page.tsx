'use client';

import { useEffect, useState } from 'react';
import PortalNav from '@/components/PortalNav';
import { apiErrorMessage, apiRequest } from '@/lib/api';

type Booking = { id: number; booking_reference: string; venue_id: number; booking_date: string; start_time: string; end_time: string; status: string; total_amount: number };

export default function Bookings() {
  const [rows, setRows] = useState<Booking[]>([]);
  const [notice, setNotice] = useState('');
  const token = () => window.localStorage.getItem('turfmate_token') ?? '';

  async function load() {
    try {
      const payload = await apiRequest<{ data: Booking[] }>('/bookings', { headers: { Authorization: `Bearer ${token()}` } });
      setRows(payload.data);
      setNotice('');
    } catch (error) {
      setRows([]);
      setNotice(apiErrorMessage(error, 'Unable to load bookings.'));
    }
  }

  useEffect(() => { void load(); }, []);

  async function cancel(bookingId: number) {
    try {
      await apiRequest(`/bookings/${bookingId}/cancel`, { method: 'POST', headers: { Authorization: `Bearer ${token()}` } });
      await load();
    } catch (error) {
      setNotice(apiErrorMessage(error, 'Unable to cancel this booking.'));
    }
  }

  return <><PortalNav /><main className="shell"><p className="eyebrow">Your activity</p><h1 className="font-display">Bookings</h1>
    {notice && <p className="card" role="alert">{notice}</p>}
    <div className="grid">{rows.map((booking) => <article className="card" key={booking.id}>
      <p className="eyebrow">{booking.status}</p><h3>{booking.booking_reference}</h3>
      <p className="muted">Venue #{booking.venue_id} · {booking.booking_date}<br />{booking.start_time}–{booking.end_time}</p>
      <div className="row"><strong>₹{booking.total_amount}</strong>{booking.status === 'CONFIRMED' && <button className="button" onClick={() => void cancel(booking.id)}>Cancel</button>}</div>
    </article>)}</div>
  </main></>;
}
