'use client';
import Link from 'next/link';
export default function PortalNav({role}:{role?:string}){return <header className="nav"><Link href="/" className="brand"><b>T</b><span>TurfMate<small>PLAY STARTS HERE</small></span></Link><nav><Link href="/">Discover</Link><Link href="/bookings">Bookings</Link>{role==='owner'&&<Link href="/owner">Owner studio</Link>}{role==='admin'&&<Link href="/admin">Admin console</Link>}<Link href="/login" className="nav-cta">Sign in</Link></nav></header>}
