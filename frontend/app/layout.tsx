import './globals.css';
import type { Metadata } from 'next';
export const metadata: Metadata={title:'TurfMate | Book your game',description:'Discover and book sports venues.'};
export default function Layout({children}:{children:React.ReactNode}){return <html lang="en"><body>{children}</body></html>}
