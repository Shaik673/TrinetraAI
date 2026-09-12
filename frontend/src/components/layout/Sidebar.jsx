import { NavLink, useLocation } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'
import {
  LayoutDashboard, Shield, Bell, Search, Brain,
  Zap, CheckCircle, Clock, BarChart3, Settings,
  ChevronLeft, ChevronRight, Eye, Target, FileSearch
} from 'lucide-react'
import { useUIStore } from '../../store/uiStore'
import clsx from 'clsx'

const NAV_ITEMS = [
  { path: '/dashboard', label: 'Dashboard', icon: LayoutDashboard, group: 'main' },
  { path: '/investigations', label: 'Investigations', icon: FileSearch, group: 'main' },
  { path: '/alerts', label: 'Alert Center', icon: Bell, group: 'main' },
  { path: '/evidence', label: 'Evidence Explorer', icon: Search, group: 'intelligence' },
  { path: '/threat-intel', label: 'Threat Intel', icon: Eye, group: 'intelligence' },
  { path: '/agents', label: 'Agent Operations', icon: Brain, group: 'operations' },
  { path: '/response', label: 'Response Center', icon: Zap, group: 'operations' },
  { path: '/verification', label: 'Verification', icon: CheckCircle, group: 'operations' },
  { path: '/timeline', label: 'Incident Timeline', icon: Clock, group: 'reporting' },
  { path: '/analytics', label: 'Analytics', icon: BarChart3, group: 'reporting' },
  { path: '/settings', label: 'Settings', icon: Settings, group: 'system' },
]

const GROUPS = ['main', 'intelligence', 'operations', 'reporting', 'system']
const GROUP_LABELS = {
  main: 'OPERATIONS',
  intelligence: 'INTELLIGENCE',
  operations: 'RESPONSE',
  reporting: 'REPORTING',
  system: 'SYSTEM',
}

export default function Sidebar() {
  const { sidebarCollapsed, toggleSidebar } = useUIStore()

  return (
    <motion.aside
      initial={false}
      animate={{ width: sidebarCollapsed ? 64 : 240 }}
      transition={{ duration: 0.3, ease: 'easeInOut' }}
      className="fixed left-0 top-0 h-screen z-50 flex flex-col glass-strong border-r border-cyber-border overflow-hidden"
    >
      {/* Logo */}
      <div className="flex items-center gap-3 px-4 py-5 border-b border-cyber-border/50">
        <div className="w-8 h-8 flex-shrink-0 relative">
          <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-neon-blue/30 to-neon-purple/30 border border-neon-blue/40 flex items-center justify-center">
            <Shield className="w-4 h-4 text-neon-blue" />
          </div>
          <div className="absolute inset-0 rounded-lg animate-pulse-slow border border-neon-blue/20" />
        </div>
        <AnimatePresence>
          {!sidebarCollapsed && (
            <motion.div
              initial={{ opacity: 0, x: -10 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -10 }}
              transition={{ duration: 0.2 }}
              className="overflow-hidden"
            >
              <span className="font-bold text-white text-sm tracking-wider gradient-text">TrinetraAI</span>
              <p className="text-[10px] text-slate-500 tracking-widest uppercase">SOC Platform</p>
            </motion.div>
          )}
        </AnimatePresence>
      </div>

      {/* Navigation */}
      <nav className="flex-1 overflow-y-auto overflow-x-hidden py-4 px-2 space-y-1">
        {GROUPS.map((group) => {
          const items = NAV_ITEMS.filter((i) => i.group === group)
          if (!items.length) return null
          return (
            <div key={group}>
              <AnimatePresence>
                {!sidebarCollapsed && (
                  <motion.p
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    exit={{ opacity: 0 }}
                    className="text-[10px] font-semibold text-slate-600 tracking-widest px-3 py-2 uppercase"
                  >
                    {GROUP_LABELS[group]}
                  </motion.p>
                )}
              </AnimatePresence>
              {items.map((item) => (
                <SidebarItem key={item.path} item={item} collapsed={sidebarCollapsed} />
              ))}
            </div>
          )
        })}
      </nav>

      {/* Collapse toggle */}
      <button
        onClick={toggleSidebar}
        className="flex items-center justify-center h-12 border-t border-cyber-border/50 text-slate-500 hover:text-neon-blue transition-colors"
      >
        {sidebarCollapsed ? <ChevronRight className="w-4 h-4" /> : <ChevronLeft className="w-4 h-4" />}
      </button>
    </motion.aside>
  )
}

function SidebarItem({ item, collapsed }) {
  const { icon: Icon, path, label } = item
  return (
    <NavLink
      to={path}
      title={collapsed ? label : undefined}
      className={({ isActive }) =>
        clsx(
          'flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-all duration-200 group relative',
          isActive
            ? 'bg-neon-blue/10 text-neon-blue border border-neon-blue/20'
            : 'text-slate-400 hover:text-white hover:bg-white/5'
        )
      }
    >
      {({ isActive }) => (
        <>
          {isActive && (
            <motion.div
              layoutId="sidebar-active"
              className="absolute inset-0 rounded-lg bg-neon-blue/10 border border-neon-blue/20"
              transition={{ type: 'spring', bounce: 0.2, duration: 0.4 }}
            />
          )}
          <Icon className={clsx('w-4 h-4 flex-shrink-0 relative z-10', isActive && 'text-neon-blue')} />
          <AnimatePresence>
            {!collapsed && (
              <motion.span
                initial={{ opacity: 0, width: 0 }}
                animate={{ opacity: 1, width: 'auto' }}
                exit={{ opacity: 0, width: 0 }}
                transition={{ duration: 0.2 }}
                className="relative z-10 whitespace-nowrap overflow-hidden"
              >
                {label}
              </motion.span>
            )}
          </AnimatePresence>
        </>
      )}
    </NavLink>
  )
}
