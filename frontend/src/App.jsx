import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { AnimatePresence } from 'framer-motion'
import { useAuthStore } from './store/authStore'
import AppLayout from './components/layout/AppLayout'
import LandingPage from './pages/landing/LandingPage'
import LoginPage from './pages/auth/LoginPage'
import SignupPage from './pages/auth/SignupPage'
import ForgotPasswordPage from './pages/auth/ForgotPasswordPage'
import DashboardPage from './pages/dashboard/DashboardPage'
import InvestigationsPage from './pages/investigations/InvestigationsPage'
import InvestigationDetailPage from './pages/investigations/InvestigationDetailPage'
import AlertsPage from './pages/alerts/AlertsPage'
import AlertDetailPage from './pages/alerts/AlertDetailPage'
import EvidenceExplorerPage from './pages/evidence/EvidenceExplorerPage'
import ThreatIntelPage from './pages/threat-intel/ThreatIntelPage'
import AgentOperationsPage from './pages/agents/AgentOperationsPage'
import ResponseCenterPage from './pages/response/ResponseCenterPage'
import VerificationCenterPage from './pages/verification/VerificationCenterPage'
import IncidentTimelinePage from './pages/timeline/IncidentTimelinePage'
import AnalyticsPage from './pages/analytics/AnalyticsPage'
import SettingsPage from './pages/settings/SettingsPage'

function ProtectedRoute({ children }) {
  const { isAuthenticated } = useAuthStore()
  return isAuthenticated ? children : <Navigate to="/login" replace />
}

function PublicRoute({ children }) {
  const { isAuthenticated } = useAuthStore()
  return !isAuthenticated ? children : <Navigate to="/dashboard" replace />
}

export default function App() {
  return (
    <BrowserRouter>
      <AnimatePresence mode="wait">
        <Routes>
          {/* Public routes */}
          <Route path="/" element={<LandingPage />} />
          <Route path="/login" element={<PublicRoute><LoginPage /></PublicRoute>} />
          <Route path="/signup" element={<PublicRoute><SignupPage /></PublicRoute>} />
          <Route path="/forgot-password" element={<PublicRoute><ForgotPasswordPage /></PublicRoute>} />

          {/* Protected app routes */}
          <Route path="/" element={<ProtectedRoute><AppLayout /></ProtectedRoute>}>
            <Route path="dashboard" element={<DashboardPage />} />
            <Route path="investigations" element={<InvestigationsPage />} />
            <Route path="investigations/:id" element={<InvestigationDetailPage />} />
            <Route path="alerts" element={<AlertsPage />} />
            <Route path="alerts/:id" element={<AlertDetailPage />} />
            <Route path="evidence" element={<EvidenceExplorerPage />} />
            <Route path="threat-intel" element={<ThreatIntelPage />} />
            <Route path="agents" element={<AgentOperationsPage />} />
            <Route path="response" element={<ResponseCenterPage />} />
            <Route path="verification" element={<VerificationCenterPage />} />
            <Route path="timeline" element={<IncidentTimelinePage />} />
            <Route path="analytics" element={<AnalyticsPage />} />
            <Route path="settings" element={<SettingsPage />} />
          </Route>
        </Routes>
      </AnimatePresence>
    </BrowserRouter>
  )
}
