import React, { useEffect, useState } from 'react';
import { createRoot } from 'react-dom/client';
import { ArrowUpRight, CalendarDays, MapPin, Search, Ticket, Users, Sparkles, RefreshCw } from 'lucide-react';
import './style.css';

const API = (import.meta.env.VITE_API_URL || 'https://aiworkshop-prnv.onrender.com').replace(/\/$/, '');
function App() {
  const [events, setEvents] = useState([]), [loading, setLoading] = useState(true), [error, setError] = useState(''), [query, setQuery] = useState('');
  async function loadEvents() {
    setLoading(true); setError('');
    try { const res = await fetch(`${API}/api/events`); const data = await res.json(); if (!res.ok) throw new Error(data.error || `Request failed (${res.status})`); setEvents(Array.isArray(data) ? data : data.events || []); }
    catch (e) { setError(`${e.message}. Check that the backend is awake and Supabase allows public reads on events.`); }
    finally { setLoading(false); }
  }
  useEffect(() => { loadEvents(); }, []);
  const shown = events.filter(e => `${e.title || ''} ${e.description || ''} ${e.location || ''}`.toLowerCase().includes(query.toLowerCase()));
  return <><header className="nav"><a className="brand" href="#top"><span className="brand-icon"><Sparkles size={18}/></span> gather<span className="period">.</span></a><nav><a href="#discover">Discover</a><a href="#about">About</a></nav><a className="nav-cta" href="#discover">Explore events <ArrowUpRight size={16}/></a></header>
  <main id="top"><section className="hero"><div className="hero-copy"><div className="eyebrow"><span className="pulse"/> YOUR CITY, YOUR PEOPLE</div><h1>Make room for<br/><em>something real.</em></h1><p>Find the gatherings, ideas, and people that make your city feel a little smaller.</p><a href="#discover" className="button">Find your next thing <ArrowUpRight size={17}/></a><div className="social-proof"><div className="faces"><b>J</b><b>M</b><b>A</b><b>+</b></div><span>Good people. Great plans.</span></div></div><div className="hero-art"><div className="sun"/><div className="art-label"><span>UP NEXT</span><strong>Make it a moment.</strong></div><div className="art-stamp">GO<br/>OUT<br/>THERE</div><div className="art-line"/></div></section>
  <section className="discover" id="discover"><div className="section-head"><div><div className="eyebrow">THE GOOD STUFF</div><h2>Find your <em>people.</em></h2></div><label className="search"><Search size={17}/><input placeholder="Search events..." value={query} onChange={e=>setQuery(e.target.value)}/></label></div>
  {loading ? <div className="state"><span className="spinner"/> Finding something good…</div> : error ? <div className="error"><div><strong>Events aren’t loading yet</strong><p>{error}</p></div><button className="retry" onClick={loadEvents}><RefreshCw size={15}/> Try again</button></div> : shown.length === 0 ? <div className="state">{events.length ? 'No events match that search.' : 'No events to show right now. Check back soon.'}</div> : <div className="grid">{shown.map((event,i)=><article className="card" key={event.id || i}><div className={`card-art art-${i%4}`}><span className="category">{event.status || 'COMMUNITY'}</span><span className="card-number">0{i+1}</span><div className="orb"/></div><div className="card-body"><h3>{event.title || 'Untitled event'}</h3><div className="meta"><span><CalendarDays size={15}/>{event.date || event.starts_at || 'Date to be announced'}</span><span><MapPin size={15}/>{event.location || 'Location to be announced'}</span></div><div className="card-bottom"><span className="capacity"><Users size={15}/>{event.capacity ? `${event.capacity} spots` : 'Come as you are'}</span><a aria-label={`View ${event.title}`} href={`${API}/api/events/${event.id}`} target="_blank" rel="noreferrer"><ArrowUpRight size={18}/></a></div></div></article>)}</div>}</section>
  <section className="bottom-cta" id="about"><div className="eyebrow">LIFE HAPPENS OUT THERE</div><h2>Go on. Say <em>yes.</em></h2><p>Small plans. New faces. Stories for later.</p><a href="#discover" className="button light">Browse the events <Ticket size={17}/></a></section></main><footer><a className="brand" href="#top">gather<span className="period">.</span></a><span>Made for getting together.</span><span>© 2025 Gather</span></footer></>;
}

createRoot(document.getElementById('root')).render(<App/>);
