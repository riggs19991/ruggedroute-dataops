import { Link, NavLink, Outlet, useLocation, useNavigate } from 'react-router-dom'
import { useAuth } from '../lib/auth'
import { SearchBox } from './SearchBox'

export function Layout() {
  const { user, profile, isTeacher, signOut } = useAuth()
  const location = useLocation()
  const navigate = useNavigate()
  const onHome = location.pathname === '/'

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
            {isTeacher && <NavLink to="/review">Review</NavLink>}
            <NavLink to="/contribute" className="pill">+ Contribute</NavLink>
            {user ? (
              <>
                <NavLink to="/profile">{profile?.display_name || 'Profile'}{isTeacher ? ' (teacher)' : ''}</NavLink>
                <button type="button" onClick={async () => { await signOut(); navigate('/') }}>Sign out</button>
              </>
            ) : (
              <NavLink to="/signin">Sign in</NavLink>
            )}
          </nav>
        </div>
      </header>
      <main>
        <Outlet />
      </main>
      <footer className="site-footer">
        Millwright Knowledge Base. Reference values are starting points: the equipment manual and your instructor always win.
        Content is contributed by students and teachers and reviewed before publishing.
      </footer>
    </>
  )
}
