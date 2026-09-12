import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'
import { Bell, Search, User, LogOut, Settings, ChevronDown, Wifi, WifiOff } from 'lucide-react'
import { useAuthStore } from '../../store/authStore'
import { useUIStore } from '../../store/uiStore'
import { formatRelative } from '../../utils/helpers'
import clsx from 'clsx'

export default function TopNav() {
  const { user, logout } = useAuthStore()
  const { notifications, clearNotifications } = useUIStore()
  const navigate = useNavigate()
  const [showNotifs, setShowNotifs] = useState(false)
  const [showUser, setShowUser] = useState(false)
  const [searchOpen, setSearchOpen] = useState(false)
  const [connected] = useState(true)

  const unreadCount = notifications.filter((n) => !n.read).length

  return (
    <header className="h-14 flex items-center justify-between px-6 border-b border-cyber-border/50 glass-strong relative z-40">
      {/* Left: Page context */}
      <div className="flex items-center gap-3">
        <div className="flex items-center gap-2 text-xs text-slate-500">
          <span className={clsx('w-2 h-2 rounded-full', connected ? 'bg-neon-green animate-pulse' : 'bg-threat-critical')}>
          </span>
          <span className="font-mono">{connected ? 'SYSTEMS NOMINAL' : 'DISCONNECTED'}</span>
        </div>
      </div>

      {/* Right: Actions */}
      <div className="flex items-center gap-3">
        {/* Search */}
        <button
          onClick={() => setSearchOpen(true)}
          className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-cyber-card/50 border border-cyber-border text-slate-400 hover:text-white hover:border-neon-blue/30 transition-all text-sm"
        >
          <Search className="w-3.5 h-3.5" />
          <span className="hidden md:block font-mono text-xs">Search...</span>
          <kbd className="hidden md:block text-[10px] px-1.5 py-0.5 rounded bg-cyber-border text-slate-500">⌘K</kbd>
        </button>

        {/* Agent status indicator */}
        <div className="hidden md:flex items-center gap-2 px-3 py-1.5 rounded-lg bg-neon-blue/5 border border-neon-blue/20 text-xs">
          <span className="w-1.5 h-1.5 rounded-full bg-neon-blue animate-pulse" />
          <span className="text-neon-blue font-mono">AI ACTIVE</span>
        </div>

        {/* Notifications */}
        <div className="relative">
          <button
            onClick={() => { setShowNotifs(!showNotifs); setShowUser(false) }}
            className="relative p-2 rounded-lg text-slate-400 hover:text-white hover:bg-white/5 transition-all"
          >
            <Bell className="w-4 h-4" />
            {unreadCount > 0 && (
              <span className="absolute -top-0.5 -right-0.5 w-4 h-4 rounded-full bg-threat-critical text-[9px] font-bold flex items-center justify-center text-white">
                {unreadCount > 9 ? '9+' : unreadCount}
              </span>
            )}
          </button>

          <AnimatePresence>
            {showNotifs && (
              <motion.div
                initial={{ opacity: 0, y: -10, scale: 0.95 }}
                animate={{ opacity: 1, y: 0, scale: 1 }}
                exit={{ opacity: 0, y: -10, scale: 0.95 }}
                transition={{ duration: 0.15 }}
                className="absolute right-0 top-10 w-80 glass-strong border border-cyber-border rounded-xl shadow-glass overflow-hidden z-50"
              >
                <div className="flex items-center justify-between p-4 border-b border-cyber-border/50">
                  <span className="text-sm font-semibold text-white">Notifications</span>
                  <button onClick={clearNotifications} className="text-xs text-neon-blue hover:text-neon-cyan">
                    Clear all
                  </button>
                </div>
                <div className="max-h-64 overflow-y-auto">
                  {notifications.length === 0 ? (
                    <p className="text-slate-500 text-sm text-center py-6">No notifications</p>
                  ) : (
                    notifications.slice(0, 10).map((n) => (
                      <div key={n.id} className="p-3 border-b border-cyber-border/30 hover:bg-white/3">
                        <p className="text-sm text-slate-300">{n.message}</p>
                        <p className="text-xs text-slate-600 mt-1">{formatRelative(n.timestamp)}</p>
                      </div>
                    ))
                  )}
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </div>

        {/* User menu */}
        <div className="relative">
          <button
            onClick={() => { setShowUser(!showUser); setShowNotifs(false) }}
            className="flex items-center gap-2 px-2 py-1.5 rounded-lg hover:bg-white/5 transition-all"
          >
            <div className="w-7 h-7 rounded-lg bg-gradient-to-br from-neon-blue/30 to-neon-purple/30 border border-neon-blue/30 flex items-center justify-center">
              <User className="w-3.5 h-3.5 text-neon-blue" />
            </div>
            <div className="hidden md:block text-left">
              <p className="text-xs font-medium text-white leading-none">{user?.full_name || user?.username || 'Analyst'}</p>
              <p className="text-[10px] text-slate-500 capitalize mt-0.5">{user?.role || 'analyst'}</p>
            </div>
            <ChevronDown className="w-3 h-3 text-slate-500 hidden md:block" />
          </button>

          <AnimatePresence>
            {showUser && (
              <motion.div
                initial={{ opacity: 0, y: -10, scale: 0.95 }}
                animate={{ opacity: 1, y: 0, scale: 1 }}
                exit={{ opacity: 0, y: -10, scale: 0.95 }}
                transition={{ duration: 0.15 }}
                className="absolute right-0 top-10 w-48 glass-strong border border-cyber-border rounded-xl shadow-glass overflow-hidden z-50"
              >
                <div className="p-3 border-b border-cyber-border/50">
                  <p className="text-sm font-medium text-white">{user?.full_name || user?.username}</p>
                  <p className="text-xs text-slate-500">{user?.email}</p>
                </div>
                <button
                  onClick={() => { navigate('/settings'); setShowUser(false) }}
                  className="w-full flex items-center gap-2 px-3 py-2.5 text-sm text-slate-400 hover:text-white hover:bg-white/5 transition-all"
                >
                  <Settings className="w-4 h-4" />
                  Settings
                </button>
                <button
                  onClick={() => { logout(); navigate('/login') }}
                  className="w-full flex items-center gap-2 px-3 py-2.5 text-sm text-threat-critical hover:bg-threat-critical/10 transition-all"
                >
                  <LogOut className="w-4 h-4" />
                  Sign Out
                </button>
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </div>

      {/* Click outside handler */}
      {(showNotifs || showUser) && (
        <div
          className="fixed inset-0 z-30"
          onClick={() => { setShowNotifs(false); setShowUser(false) }}
        />
      )}
    </header>
  )
}
