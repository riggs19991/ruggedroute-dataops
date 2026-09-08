import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { BrowserRouter, Navigate, Route, Routes, useLocation } from 'react-router-dom'
import './index.css'
import { AuthProvider, useAuth } from './lib/auth'
import { Layout } from './components/Layout'
import { Home } from './pages/Home'
import { IndexPage } from './pages/Index'
import { Search } from './pages/Search'
import { CategoryPage } from './pages/Category'
import { ArticlePage } from './pages/Article'
import { Contribute } from './pages/Contribute'
import { SignIn } from './pages/SignIn'
import { ProfilePage } from './pages/Profile'
import { Groups } from './pages/Groups'
import { GroupPage } from './pages/Group'
import { InstallPage } from './pages/Install'
import { AuthConfirmed } from './pages/AuthConfirmed'
import { AuthReset } from './pages/AuthReset'
import { Privacy } from './pages/Privacy'
import { registerSW } from 'virtual:pwa-register'

function RequireAuth({ children }: { children: React.ReactElement }) {
  const { user, loading } = useAuth()
  const location = useLocation()
  if (loading) return <p className="loading">Loading…</p>
  if (!user) return <Navigate to="/signin" state={{ from: location.pathname + location.search }} replace />
  return children
}

function App() {
  return (
    <Routes>
      <Route element={<Layout />}>
        <Route path="/" element={<Home />} />
        <Route path="/search" element={<Search />} />
        <Route path="/a-z" element={<IndexPage />} />
        <Route path="/category/:slug" element={<CategoryPage />} />
        <Route path="/article/:slug" element={<ArticlePage />} />
        <Route path="/signin" element={<SignIn />} />
        <Route path="/auth/confirmed" element={<AuthConfirmed />} />
        <Route path="/auth/reset" element={<AuthReset />} />
        <Route path="/install" element={<InstallPage />} />
        <Route path="/privacy" element={<Privacy />} />
        <Route path="/contribute" element={<RequireAuth><Contribute /></RequireAuth>} />
        <Route path="/contribute/:slug" element={<RequireAuth><Contribute /></RequireAuth>} />
        <Route path="/profile" element={<RequireAuth><ProfilePage /></RequireAuth>} />
        <Route path="/groups" element={<RequireAuth><Groups /></RequireAuth>} />
        <Route path="/groups/:id" element={<RequireAuth><GroupPage /></RequireAuth>} />
        <Route path="*" element={<div className="empty">Page not found.</div>} />
      </Route>
    </Routes>
  )
}

// Service worker: precached shell, cached diagrams and articles. When a new build is published,
// show a small bar offering to reload (content changes often).
const updateSW = registerSW({
  onNeedRefresh() {
    const bar = document.createElement('div')
    bar.className = 'update-bar'
    bar.innerHTML = '<span>A new version is ready.</span><button type="button">Reload</button>'
    bar.querySelector('button')!.onclick = () => updateSW(true)
    document.body.appendChild(bar)
  },
})

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <BrowserRouter basename={import.meta.env.BASE_URL.replace(/\/$/, '')}>
      <AuthProvider>
        <App />
      </AuthProvider>
    </BrowserRouter>
  </StrictMode>,
)
