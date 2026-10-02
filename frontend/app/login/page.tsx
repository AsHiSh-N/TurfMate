'use client';

import { FormEvent, useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import PortalNav from '@/components/PortalNav';
import { apiErrorMessage, apiRequest } from '@/lib/api';

type LoginResponse = { access_token: string; role: string };

export default function Login() {
  const [email, setEmail] = useState('customer@example.com');
  const [password, setPassword] = useState('DemoPass123!');
  const [error, setError] = useState('');
  const router = useRouter();

  async function submit(event: FormEvent) {
    event.preventDefault();
    setError('');
    try {
      const payload = await apiRequest<LoginResponse>('/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password }),
      });
      window.localStorage.setItem('turfmate_token', payload.access_token);
      window.localStorage.setItem('turfmate_role', payload.role);
      router.push(payload.role === 'ADMIN' ? '/admin' : payload.role === 'VENUE_OWNER' ? '/owner' : '/bookings');
    } catch (requestError) {
      setError(apiErrorMessage(requestError, 'Unable to sign in. Please try again.'));
    }
  }

  return <><PortalNav /><main className="shell"><div className="card" style={{ maxWidth: 480, margin: '40px auto' }}>
    <p className="eyebrow">Welcome back</p><h1 className="font-display">Sign in</h1>
    <p className="muted">Use a demo account or your TurfMate account.</p>
    {error && <p className="card" role="alert">{error}</p>}
    <form className="form-grid" onSubmit={submit}>
      <input className="field" value={email} onChange={(event) => setEmail(event.target.value)} type="email" placeholder="Email" />
      <input className="field" value={password} onChange={(event) => setPassword(event.target.value)} type="password" placeholder="Password" />
      <button className="button primary">Sign in</button>
    </form>
    <p className="muted">Customer: customer@example.com / DemoPass123!</p><Link href="/">Back to discovery</Link>
  </div></main></>;
}
