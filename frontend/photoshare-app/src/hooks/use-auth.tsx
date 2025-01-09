"use client"

import { createContext, useContext, useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import { BACKEND_API_BASE_URL } from '@/app/constants'

interface User {
  id: number
  username: string
  email: string
  first_name: string
  last_name: string
  bio: string
  avatar: string
  role: 'admin' | 'moderator' | 'user'
}

interface AuthContextType {
  user: User | null
  token: string | null
  login: (email: string, password: string) => Promise<void>
  register: (username: string, email: string, password: string) => Promise<void>
  logout: () => void
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [token, setToken] = useState<string | null>(null);
  const router = useRouter()
  useEffect(() => {
    const savedToken = localStorage.getItem('token');
    setToken(savedToken);
    // Fetch user data if token exists
  }, []);

  const login = async (email: string, password: string) => {
    const res = await fetch(`${BACKEND_API_BASE_URL}/api/auth/token`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded'
      },
      body: new URLSearchParams({
        username: email,
        password: password
      })
    })

    const data = await res.json()
    if (data.access_token) {
      localStorage.setItem('token', data.access_token)
      const userRes = await fetch(`${BACKEND_API_BASE_URL}/api/auth/me`, {
        headers: {
          'Authorization': `Bearer ${data.access_token}`
        }
      })
      const userData = await userRes.json()
      setToken(data.access_token);
      setUser(userData)
      router.push('/')
    } else {
      throw new Error(data.detail)
    }
  }


  const register = async (username: string, email: string, password: string) => {
    const res = await fetch(`${BACKEND_API_BASE_URL}/api/auth/register/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        username,
        email,
        password
      })
    })

    const data = await res.json()
    if (data.id) {
      await login(email, password)
    } else {
      throw new Error(data.detail)
    }
  }

  const logout = () => {
    localStorage.removeItem('token')
    setUser(null)
    setToken(null)
    router.push('/login')
  }

  return (
    <AuthContext.Provider value={{ user, token, login, register, logout }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}