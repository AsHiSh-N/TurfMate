'use client';

import { useEffect, useState } from 'react';
import PortalNav from '@/components/PortalNav';
import { apiErrorMessage, apiRequest } from '@/lib/api';

type Venue = { id: number; name: string; city: string; owner_id: number; status: string };
type Booking = { id: number; booking_reference: string; venue_id: number; status: string; total_amount: number };
type Payment = { id: number; booking_id: number; transaction_id: string; amount: number; status: string };

export default function AdminPage() {
  const [venues, setVenues] = useState<Venue[]>([]);
  const [bookings, setBookings] = useState<Booking[]>([]);
  const [payments, setPayments] = useState<Payment[]>([]);
  const [notice, setNotice] = useState('');
  const token = () => window.localStorage.getItem('turfmate_token') ?? '';

  async function load() {
    const headers = { Authorization: `Bearer ${token()}` };
    try {
      const [venuePayload, bookingPayload, paymentPayload] = await Promise.all([
        apiRequest<{ data: Venue[] }>('/admin/venues', { headers }),
        apiRequest<{ data: Booking[] }>('/admin/bookings', { headers }),
        apiRequest<{ data: Payment[] }>('/admin/payments', { headers }),
      ]);
      setVenues(venuePayload.data);
      setBookings(bookingPayload.data);
      setPayments(paymentPayload.data);
      setNotice('');
    } catch (error) {
      setVenues([]);
      setBookings([]);
      setPayments([]);
      setNotice(apiErrorMessage(error, 'Unable to load admin data.'));
    }
  }

  useEffect(() => { void load(); }, []);

  async function approve(venueId: number) {
    try {
      await apiRequest(`/admin/venues/${venueId}/approve`, { method: 'POST', headers: { Authorization: `Bearer ${token()}` } });
      setNotice('Venue approved and visible to customers.');
      await load();
    } catch (error) {
      setNotice(apiErrorMessage(error, 'Unable to approve venue.'));
    }
  }

  const pending = venues.filter((venue) => venue.status === 'PENDING');
  return <main className="min-h-screen bg-[var(--canvas)]"><PortalNav role="admin" /><section className="mx-auto max-w-7xl px-5 py-12 lg:px-8">
    <p className="eyebrow">Platform operations</p><h1 className="font-display mt-2 text-5xl font-black">Keep play moving.</h1>
    {notice && <p className="mt-6 border-l-4 border-[var(--orange)] bg-white p-4 text-sm font-bold" role="alert">{notice}</p>}
    <div className="mt-8 grid gap-4 sm:grid-cols-3"><div className="metric"><strong>{pending.length}</strong><span>Pending venues</span></div><div className="metric"><strong>{bookings.length}</strong><span>Total bookings</span></div><div className="metric"><strong>{payments.length}</strong><span>Payments</span></div></div>
    <section className="mt-10"><div className="flex items-end justify-between"><div><p className="eyebrow">Review queue</p><h2 className="font-display mt-1 text-3xl font-bold">Venue approvals</h2></div></div>
      <div className="mt-4 space-y-3">{venues.length === 0 ? <div className="bg-white p-6 text-[var(--muted)]">No venues found.</div> : venues.map((venue) => <article className="flex flex-col justify-between gap-4 bg-white p-5 sm:flex-row sm:items-center" key={venue.id}>
        <div><h3 className="font-display text-2xl font-bold">{venue.name}</h3><p className="text-sm text-[var(--muted)]">{venue.city} · owner #{venue.owner_id}</p></div>
        <div className="flex items-center gap-4"><strong className="text-sm">{venue.status}</strong>{venue.status === 'PENDING' && <button className="button button-primary" onClick={() => void approve(venue.id)}>Approve venue</button>}</div>
      </article>)}</div>
    </section>
    <section className="mt-10 grid gap-6 lg:grid-cols-2"><div><h2 className="font-display text-2xl font-bold">Bookings</h2><div className="mt-3 space-y-2">{bookings.map((booking) => <div className="bg-white p-4" key={booking.id}><strong>{booking.booking_reference}</strong><p className="text-sm text-[var(--muted)]">Venue #{booking.venue_id} · ₹{booking.total_amount} · {booking.status}</p></div>)}</div></div>
      <div><h2 className="font-display text-2xl font-bold">Payments</h2><div className="mt-3 space-y-2">{payments.map((payment) => <div className="bg-white p-4" key={payment.id}><strong>{payment.transaction_id}</strong><p className="text-sm text-[var(--muted)]">Booking #{payment.booking_id} · ₹{payment.amount} · {payment.status}</p></div>)}</div></div>
    </section>
  </section></main>;
}
