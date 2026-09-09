import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { BrowserRouter, Navigate, Route, Routes, useLocation } from 'react-router-dom'
import './fonts.css'
import './index.css'
import { initTheme } from './lib/theme'
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
import { Terms } from './pages/Terms'
import { SupportPage } from './pages/Support'
import { CreditsPage } from './pages/Credits'
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
        <Route path="/terms" element={<Terms />} />
        <Route path="/support" element={<SupportPage />} />
        <Route path="/credits" element={<CreditsPage />} />
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

// Service worker: precached shell, cached diagrams and articles. A new build installs and reloads
// on its own (autoUpdate); long-lived tabs check for one every hour.
registerSW({
  onRegisteredSW(_url, registration) {
    if (registration) setInterval(() => registration.update(), 60 * 60 * 1000)
  },
})

initTheme()

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <BrowserRouter basename={import.meta.env.BASE_URL.replace(/\/$/, '')}>
      <AuthProvider>
        <App />
      </AuthProvider>
    </BrowserRouter>
  </StrictMode>,
)
