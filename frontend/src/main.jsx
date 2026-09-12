import React from 'react'
import ReactDOM from 'react-dom/client'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { Toaster } from 'react-hot-toast'
import App from './App.jsx'
import './index.css'

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 30 * 1000,
      retry: 2,
      refetchOnWindowFocus: false,
    },
  },
})

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <QueryClientProvider client={queryClient}>
      <App />
      <Toaster
        position="top-right"
        toastOptions={{
          style: {
            background: 'rgba(6, 14, 30, 0.95)',
            color: '#e2e8f0',
            border: '1px solid rgba(0, 212, 255, 0.2)',
            borderRadius: '8px',
            fontSize: '14px',
          },
          success: { iconTheme: { primary: '#00ff88', secondary: '#020812' } },
          error: { iconTheme: { primary: '#ff3366', secondary: '#020812' } },
        }}
      />
    </QueryClientProvider>
  </React.StrictMode>
)
