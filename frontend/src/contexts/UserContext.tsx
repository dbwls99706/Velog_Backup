'use client'

import { createContext, useContext, useEffect, useState, useCallback, ReactNode } from 'react'
import { useRouter, usePathname } from 'next/navigation'
import { authAPI } from '@/lib/api'

interface UserContextType {
  user: any
  isLoading: boolean
  refreshUser: () => Promise<void>
}

const UserContext = createContext<UserContextType>({
  user: null,
  isLoading: true,
  refreshUser: async () => {},
})

export function useUser() {
  return useContext(UserContext)
}

const PUBLIC_PATHS = ['/', '/auth/callback']

export function UserProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<any>(null)
  const [isLoading, setIsLoading] = useState(true)
  const router = useRouter()
  const pathname = usePathname()

  const isPublicPath = PUBLIC_PATHS.some(
    (p) => pathname === p || pathname.startsWith(p + '/')
  )

  const refreshUser = useCallback(async () => {
    const token = localStorage.getItem('access_token')
    if (!token) {
      setUser(null)
      setIsLoading(false)
      return
    }
    try {
      const res = await authAPI.getCurrentUser()
      setUser(res.data)
    } catch {
      setUser(null)
      if (!isPublicPath) {
        localStorage.removeItem('access_token')
        router.push('/')
      }
    } finally {
      setIsLoading(false)
    }
  }, [isPublicPath, router])

  useEffect(() => {
    if (isPublicPath) {
      return
    }
    refreshUser()
  }, [isPublicPath, refreshUser])

  return (
    <UserContext.Provider value={{ user, isLoading, refreshUser }}>
      {children}
    </UserContext.Provider>
  )
}
