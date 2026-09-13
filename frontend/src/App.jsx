import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom'
import { useAuthStore } from './store/authStore'
import AppLayout from './components/layout/AppLayout'
import LandingPage from './pages/landing/LandingPage'
import LoginPage from './pages/auth/LoginPage'
import SignupPage from './pages/auth/SignupPage'
import ForgotPasswordPage from './pages/auth/ForgotPasswordPage'
import ResetPasswordPage from './pages/auth/ResetPasswordPage'
import OAuthCallbackPage from './pages/auth/OAuthCallbackPage'
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
  return useAuthStore((state) => state.isAuthenticated) ? children : <Navigate to="/login" replace />
}

function PublicRoute({ children }) {
  return useAuthStore((state) => state.isAuthenticated) ? <Navigate to="/dashboard" replace /> : children
}

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        {/* Public marketing page */}
        <Route path="/" element={<LandingPage />} />

        {/* Auth pages — redirect to dashboard if already logged in */}
        <Route path="/login" element={<PublicRoute><LoginPage /></PublicRoute>} />
        <Route path="/signup" element={<PublicRoute><SignupPage /></PublicRoute>} />
        <Route path="/forgot-password" element={<PublicRoute><ForgotPasswordPage /></PublicRoute>} />
        <Route path="/reset-password" element={<PublicRoute><ResetPasswordPage /></PublicRoute>} />

        {/* OAuth callback — must be accessible without auth (tokens arrive here) */}
        <Route path="/auth/callback" element={<OAuthCallbackPage />} />

        {/* Protected app routes — wrapped in the sidebar layout */}
        <Route element={<ProtectedRoute><AppLayout /></ProtectedRoute>}>
          <Route path="/dashboard" element={<DashboardPage />} />
          <Route path="/investigations" element={<InvestigationsPage />} />
          <Route path="/investigations/:id" element={<InvestigationDetailPage />} />
          <Route path="/alerts" element={<AlertsPage />} />
          <Route path="/alerts/:id" element={<AlertDetailPage />} />
          <Route path="/evidence" element={<EvidenceExplorerPage />} />
          <Route path="/threat-intel" element={<ThreatIntelPage />} />
          <Route path="/agents" element={<AgentOperationsPage />} />
          <Route path="/response" element={<ResponseCenterPage />} />
          <Route path="/verification" element={<VerificationCenterPage />} />
          <Route path="/timeline" element={<IncidentTimelinePage />} />
          <Route path="/analytics" element={<AnalyticsPage />} />
          <Route path="/settings" element={<SettingsPage />} />
        </Route>

        {/* Fallback */}
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  )
}
