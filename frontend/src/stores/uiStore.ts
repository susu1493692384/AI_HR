import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { Notification } from '@/types';

interface UIState {
  theme: 'light' | 'dark';
  sidebarCollapsed: boolean;
  loading: Record<string, boolean>;
  notifications: Notification[];
  setTheme: (theme: 'light' | 'dark') => void;
  toggleSidebar: () => void;
  setSidebarCollapsed: (collapsed: boolean) => void;
  setGlobalLoading: (key: string, value: boolean) => void;
  addNotification: (notification: Omit<Notification, 'id'>) => void;
  removeNotification: (id: string) => void;
  clearNotifications: () => void;
}

export const useUIStore = create<UIState>()(
  persist(
    (set, get) => ({
      theme: 'light',
      sidebarCollapsed: false,
      loading: {},
      notifications: [],

      setTheme: (theme: 'light' | 'dark') => {
        set({ theme });
        // TODO: Apply theme to document
        document.documentElement.classList.toggle('dark', theme === 'dark');
      },

      toggleSidebar: () => {
        set((state) => ({ sidebarCollapsed: !state.sidebarCollapsed }));
      },

      setSidebarCollapsed: (collapsed: boolean) => {
        set({ sidebarCollapsed: collapsed });
      },

      setGlobalLoading: (key: string, value: boolean) => {
        set((state) => ({
          loading: {
            ...state.loading,
            [key]: value,
          },
        }));
      },

      addNotification: (notification: Omit<Notification, 'id'>) => {
        const id = Date.now().toString();
        const newNotification = { ...notification, id };

        set((state) => ({
          notifications: [...state.notifications, newNotification],
        }));

        // Auto remove notification after duration
        if (notification.duration && notification.duration > 0) {
          setTimeout(() => {
            get().removeNotification(id);
          }, notification.duration);
        }
      },

      removeNotification: (id: string) => {
        set((state) => ({
          notifications: state.notifications.filter((n) => n.id !== id),
        }));
      },

      clearNotifications: () => {
        set({ notifications: [] });
      },
    }),
    {
      name: 'ui-storage',
      partialize: (state) => ({
        theme: state.theme,
        sidebarCollapsed: state.sidebarCollapsed,
      }),
    }
  )
);