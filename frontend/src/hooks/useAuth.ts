import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import api from '../api/client'

interface User {
  id: number
  email: string
  username: string
  full_name?: string
  is_active: boolean
}

interface AuthState {
  user: User | null
  accessToken: string | null
  isAuthenticated: boolean
  isLoading: boolean
  login: (email: string, password: string) => Promise<void>
  register: (email: string, username: string, password: string) => Promise<void>
  logout: () => void
  checkAuth: () => Promise<void>
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      user: null,
      accessToken: null,
      isAuthenticated: false,
      isLoading: true,

      login: async (email: string, password: string) => {
        try {
          const response = await api.post('/auth/login', { email, password })
          const { access_token, refresh_token } = response.data
          
          // Store tokens
          localStorage.setItem('access_token', access_token)
          localStorage.setItem('refresh_token', refresh_token)
          api.defaults.headers.common['Authorization'] = `Bearer ${access_token}`
          
          // Fetch user profile
          const userResponse = await api.get('/auth/me')
          set({ user: userResponse.data, accessToken: access_token, isAuthenticated: true })
        } catch (error) {
          throw error
        }
      },

      register: async (email: string, username: string, password: string) => {
        try {
          await api.post('/auth/register', { email, username, password })
          // Auto login after registration
          await get().login(email, password)
        } catch (error) {
          throw error
        }
      },

      logout: () => {
        localStorage.removeItem('access_token')
        localStorage.removeItem('refresh_token')
        delete api.defaults.headers.common['Authorization']
        set({ user: null, accessToken: null, isAuthenticated: false })
      },

      checkAuth: async () => {
        const token = localStorage.getItem('access_token')
        if (!token) {
          set({ isLoading: false, isAuthenticated: false })
          return
        }
        
        try {
          api.defaults.headers.common['Authorization'] = `Bearer ${token}`
          const response = await api.get('/auth/me')
          set({ 
            user: response.data, 
            accessToken: token, 
            isAuthenticated: true,
            isLoading: false 
          })
        } catch {
          // Try refresh token
          const refreshToken = localStorage.getItem('refresh_token')
          if (refreshToken) {
            try {
              const response = await api.post('/auth/refresh', { refresh_token: refreshToken })
              const { access_token, refresh_token: newRefresh } = response.data
              localStorage.setItem('access_token', access_token)
              localStorage.setItem('refresh_token', newRefresh)
              api.defaults.headers.common['Authorization'] = `Bearer ${access_token}`
              
              const userResponse = await api.get('/auth/me')
              set({ 
                user: userResponse.data, 
                accessToken: access_token, 
                isAuthenticated: true,
                isLoading: false 
              })
            } catch {
              get().logout()
            }
          } else {
            get().logout()
          }
        }
      },
    }),
    {
      name: 'auth-storage',
      partialize: (state) => ({ 
        user: state.user,
        accessToken: state.accessToken,
        isAuthenticated: state.isAuthenticated 
      }),
    }
  )
)
