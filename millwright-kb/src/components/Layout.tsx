import { useEffect, useState } from 'react'
import { Link, NavLink, Outlet, useLocation, useNavigate } from 'react-router-dom'
import { useAuth } from '../lib/auth'
import { SearchBox } from './SearchBox'
import { SupportAsk } from './SupportAsk'
import { COMPANY, COPYRIGHT_YEAR } from '../lib/site'

export function Layout() {
  const { user, profile, signOut } = useAuth()
  const location = useLocation()
  const navigate = useNavigate()
  const onHome = location.pathname === '/'
  const [online, setOnline] = useState(() => typeof navigator === 'undefined' ? true : navigator.onLine)
  useEffect(() => {
    const up = () => setOnline(true), down = () => setOnline(false)
    window.addEventListener('online', up); window.addEventListener('offline', down)
    return () => { window.removeEventListener('online', up); window.removeEventListener('offline', down) }
  }, [])

  return (
    <>
      <header className="site-header">
        <div className="inner">
          <Link to="/" className="brand"><span className="gear">⚙️</span> Millwright KB</Link>
          {!onHome && <div className="header-search"><SearchBox /></div>}
          <nav className="site-nav">
            <NavLink to="/" end>Browse</NavLink>
            <NavLink to="/a-z">A-Z</NavLink>
            {user && <NavLink to="/groups">Groups</NavLink>}
            <NavLink to="/contribute" className="pill">+ Contribute</NavLink>
            {user ? (
              <>
                <NavLink to="/profile">{profile?.display_name || 'Profile'}</NavLink>
                <button type="button" onClick={async () => { await signOut(); navigate('/') }}>Sign out</button>
              </>
            ) : (
              <NavLink to="/signin">Sign in</NavLink>
            )}
          </nav>
        </div>
      </header>
      {!online && <div className="offline-bar">You are offline. Articles and diagrams you have opened still work; search and sign-in need a connection.</div>}
      <main>
        <Outlet />
      </main>
      <footer className="site-footer">
        Millwright Knowledge Base. Reference values are starting points: the equipment manual and your instructor always win.
        Content is contributed by the millwright community and is not reviewed before it appears: verify before you rely on it.
        <div className="footer-links"><Link to="/install">Install on your phone</Link> · <Link to="/article/set-me-up-for-a-task">Task index</Link> · <Link to="/terms">Terms and legal</Link> · <Link to="/privacy">Privacy</Link> · <Link to="/support">Support the creator</Link></div>
        <div className="footer-legal">© {COPYRIGHT_YEAR} {COMPANY}, Blanchard, Idaho. Free to use, no ads, built by one person.</div>
        <div className="footer-legal"><SupportAsk compact /></div>
      </footer>
    </>
  )
}
