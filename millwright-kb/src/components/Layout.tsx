import { useEffect, useState } from 'react'
import { Link, NavLink, Outlet, useLocation, useNavigate } from 'react-router-dom'
import { useAuth } from '../lib/auth'
import { SearchBox } from './SearchBox'
import { Logo } from './Logo'
import { Icon } from '../lib/icons'
import { BUILD_ID, COMPANY, COPYRIGHT_YEAR, DONATE_URL, donateHref } from '../lib/site'
import { resolvedTheme, toggleTheme } from '../lib/theme'

export function Layout() {
  const { user, profile, signOut } = useAuth()
  const location = useLocation()
  const navigate = useNavigate()
  const onHome = location.pathname === '/'
  const [online, setOnline] = useState(() => typeof navigator === 'undefined' ? true : navigator.onLine)
  const [dark, setDark] = useState(() => resolvedTheme() === 'dark')
  useEffect(() => {
    const up = () => setOnline(true), down = () => setOnline(false)
    window.addEventListener('online', up); window.addEventListener('offline', down)
    return () => { window.removeEventListener('online', up); window.removeEventListener('offline', down) }
  }, [])

  const support = DONATE_URL
    ? <a className="btn primary small" href={DONATE_URL} target="_blank" rel="noopener noreferrer"><Icon name="heart" size={18} />Support the creator</a>
    : <Link className="btn primary small" to={donateHref}><Icon name="heart" size={18} />Support the creator</Link>

  return (
    <>
      <header className="site-header">
        <div className="inner">
          <Link to="/" className="brand" aria-label="Millwright KB home"><Logo size={34} /><span className="wordmark">Millwright <b>KB</b></span></Link>
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
            <button type="button" className="iconbtn" onClick={() => setDark(toggleTheme() === 'dark')} aria-label={dark ? 'Switch to light theme' : 'Switch to dark theme'} title={dark ? 'Light theme' : 'Dark theme'}>
              <Icon name={dark ? 'sun' : 'moon'} size={20} />
            </button>
          </nav>
        </div>
      </header>
      {!online && <div className="offline-bar">You are offline. Articles and diagrams you have opened still work; search and sign-in need a connection.</div>}
      <main>
        <Outlet />
      </main>
      <footer className="site-footer">
        <div className="inner">
          <div className="footer-links"><Link to="/install">Install on your phone</Link><Link to="/article/set-me-up-for-a-task">Task index</Link><Link to="/terms">Terms and legal</Link><Link to="/privacy">Privacy</Link><Link to="/credits">Photo credits</Link><Link to="/support">Support the creator</Link></div>
          <div className="footer-row">
            <span>Free to use, no ads, built by one person. Reference values are starting points: the equipment manual and your instructor always win. Community contributions are not reviewed before they appear; verify before you rely on them.</span>
            {support}
          </div>
          <div className="footer-amp">
            <img src="/brand/amp-logo.png" alt="Addictive Media Productions" width="640" height="289" />
            <div>Millwright KB is a product of <b>{COMPANY}</b><br /><span className="footer-copy">© {COPYRIGHT_YEAR} {COMPANY}, Blanchard, Idaho. All rights reserved. <span className="footer-build">build {BUILD_ID}</span></span></div>
          </div>
        </div>
      </footer>
    </>
  )
}
