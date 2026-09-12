import { create } from 'zustand'

export const useUIStore = create((set) => ({
  sidebarCollapsed: false,
  activeInvestigation: null,
  notifications: [],

  toggleSidebar: () => set((state) => ({ sidebarCollapsed: !state.sidebarCollapsed })),
  setSidebarCollapsed: (v) => set({ sidebarCollapsed: v }),
  setActiveInvestigation: (id) => set({ activeInvestigation: id }),

  addNotification: (n) =>
    set((state) => ({
      notifications: [{ id: Date.now(), ...n }, ...state.notifications].slice(0, 50),
    })),
  clearNotifications: () => set({ notifications: [] }),
  markRead: (id) =>
    set((state) => ({
      notifications: state.notifications.map((n) => (n.id === id ? { ...n, read: true } : n)),
    })),
}))
