'use client';

import { FormEvent, useEffect, useState } from 'react';
import PortalNav from '@/components/PortalNav';
import { apiErrorMessage, apiRequest } from '@/lib/api';

type Venue = { id: number; name: string; city: string; status: string };
type VenueForm = { name: string; description: string; address: string; city: string; state: string; pincode: string; activity_id: string; court_name: string };

const emptyForm: VenueForm = { name: '', description: '', address: '', city: 'Pune', state: 'Maharashtra', pincode: '', activity_id: '1', court_name: 'Court 1' };

export default function Owner() {
  const [venues, setVenues] = useState<Venue[]>([]);
  const [notice, setNotice] = useState('');
  const [form, setForm] = useState(emptyForm);
  const token = () => window.localStorage.getItem('turfmate_token') ?? '';

  async function load() {
    try {
      const payload = await apiRequest<{ data: Venue[] }>('/owner/venues', { headers: { Authorization: `Bearer ${token()}` } });
      setVenues(payload.data);
      setNotice('');
    } catch (error) {
      setVenues([]);
      setNotice(apiErrorMessage(error, 'Owner sign-in required.'));
    }
  }

  useEffect(() => { void load(); }, []);

  async function submit(event: FormEvent) {
    event.preventDefault();
    try {
      await apiRequest('/owner/venues', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token()}` },
        body: JSON.stringify({ ...form, activity_id: Number(form.activity_id) }),
      });
      setNotice('Venue submitted for approval');
      setForm(emptyForm);
      await load();
    } catch (error) {
      setNotice(apiErrorMessage(error, 'Unable to submit venue.'));
    }
  }

  return <><PortalNav role="owner" /><main className="shell"><p className="eyebrow">Owner studio</p><h1 className="font-display">Bring your venue to life.</h1>
    {notice && <p className="card" role="alert">{notice}</p>}
    <div className="grid"><form className="card form-grid" onSubmit={submit}><h2>Submit a venue</h2>
      {Object.entries(form).map(([key, value]) => key !== 'activity_id' && <input className="field" key={key} placeholder={key.replace('_', ' ')} value={value} onChange={(event) => setForm({ ...form, [key]: event.target.value })} />)}
      <button className="button primary">Submit for review</button>
    </form><section className="card"><p className="eyebrow">Your venues</p>{venues.map((venue) => <div className="row card" key={venue.id}><span><b>{venue.name}</b><small className="muted">{venue.city}</small></span><strong>{venue.status}</strong></div>)}</section></div>
  </main></>;
}
