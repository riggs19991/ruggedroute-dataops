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
import { Review } from './pages/Review'

function RequireAuth({ children, teacher = false }: { children: React.ReactElement; teacher?: boolean }) {
  const { user, loading, isTeacher } = useAuth()
  const location = useLocation()
  if (loading) return <p className="loading">Loading…</p>
  if (!user) return <Navigate to="/signin" state={{ from: location.pathname + location.search }} replace />
  if (teacher && !isTeacher) return <div className="notice warn">This page is for teachers. Enter the teacher access code on your profile page to unlock it.</div>
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
        <Route path="/contribute" element={<RequireAuth><Contribute /></RequireAuth>} />
        <Route path="/contribute/:slug" element={<RequireAuth><Contribute /></RequireAuth>} />
        <Route path="/profile" element={<RequireAuth><ProfilePage /></RequireAuth>} />
        <Route path="/groups" element={<RequireAuth><Groups /></RequireAuth>} />
        <Route path="/groups/:id" element={<RequireAuth><GroupPage /></RequireAuth>} />
        <Route path="/review" element={<RequireAuth teacher><Review /></RequireAuth>} />
        <Route path="*" element={<div className="empty">Page not found.</div>} />
      </Route>
    </Routes>
  )
}

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <BrowserRouter basename={import.meta.env.BASE_URL.replace(/\/$/, '')}>
      <AuthProvider>
        <App />
      </AuthProvider>
    </BrowserRouter>
  </StrictMode>,
)
