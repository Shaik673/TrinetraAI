import axios from 'axios'
import { useAuthStore } from '../store/authStore'

const BASE_URL = import.meta.env.VITE_API_URL || '/api/v1'

export const apiClient = axios.create({
  baseURL: BASE_URL,
  headers: { 'Content-Type': 'application/json' },
  timeout: 30000,
})

// Attach auth token
apiClient.interceptors.request.use((config) => {
  const token = useAuthStore.getState().getToken()
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

// Handle 401 globally
apiClient.interceptors.response.use(
  (res) => res,
  async (error) => {
    if (error.response?.status === 401) {
      useAuthStore.getState().logout()
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

// API methods
export const api = {
  // Auth
  login: (data) => apiClient.post('/auth/login', data),
  register: (data) => apiClient.post('/auth/register', data),
  getMe: () => apiClient.get('/auth/me'),
  updateMe: (data) => apiClient.put('/auth/me', data),
  requestPasswordReset: (data) => apiClient.post('/auth/request-password-reset', data),

  // Alerts
  getAlerts: (params) => apiClient.get('/alerts', { params }),
  getAlert: (id) => apiClient.get(`/alerts/${id}`),
  getAlertStats: () => apiClient.get('/alerts/stats'),
  createAlert: (data) => apiClient.post('/alerts', data),
  triggerInvestigation: (id) => apiClient.post(`/alerts/${id}/investigate`),
  seedDemoAlerts: () => apiClient.post('/alerts/demo/seed'),

  // Investigations
  getInvestigations: (params) => apiClient.get('/investigations', { params }),
  getInvestigation: (id) => apiClient.get(`/investigations/${id}`),
  getInvestigationEvidence: (id) => apiClient.get(`/investigations/${id}/evidence`),
  getInvestigationAssessments: (id) => apiClient.get(`/investigations/${id}/assessments`),
  getInvestigationResponses: (id) => apiClient.get(`/investigations/${id}/responses`),
  getInvestigationVerifications: (id) => apiClient.get(`/investigations/${id}/verifications`),
  getInvestigationReflections: (id) => apiClient.get(`/investigations/${id}/reflections`),
  getInvestigationAgents: (id) => apiClient.get(`/investigations/${id}/agents`),

  // Analytics
  getDashboardStats: () => apiClient.get('/analytics/dashboard'),
  getSeverityDistribution: () => apiClient.get('/analytics/severity-distribution'),
  getInvestigationTrend: (days) => apiClient.get('/analytics/investigation-trend', { params: { days } }),

  // Threat Intel
  getMitreTechniques: (params) => apiClient.get('/threat-intel/mitre/techniques', { params }),
  getCVEs: (params) => apiClient.get('/threat-intel/cves', { params }),
  getCVE: (id) => apiClient.get(`/threat-intel/cves/${id}`),
  getThreatFeeds: () => apiClient.get('/threat-intel/threat-feeds'),
}
