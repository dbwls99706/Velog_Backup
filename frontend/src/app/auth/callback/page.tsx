'use client'

import { useEffect, useState, useRef, Suspense } from 'react'
import { useSearchParams } from 'next/navigation'
import { BookOpen } from 'lucide-react'
import toast from 'react-hot-toast'
import { authAPI } from '@/lib/api'

function AuthCallbackContent() {
  const searchParams = useSearchParams()
  const [error, setError] = useState<string | null>(null)
  const hasRun = useRef(false)

  useEffect(() => {
    if (hasRun.current) return
    hasRun.current = true

    const code = searchParams.get('code')
    const state = searchParams.get('state')
    const errorParam = searchParams.get('error')

    if (errorParam) {
      setError('GitHub 인증이 취소되었습니다')
      return
    }

    if (!code) {
      setError('인증 코드가 없습니다')
      return
    }

    handleCallback(code, state || undefined)
  }, [searchParams])

  const handleCallback = async (code: string, state?: string) => {
    try {
      const response = await authAPI.gitHubCallback(code, state)
      localStorage.setItem('access_token', response.data.access_token)
      toast.success('로그인 성공!')
      window.location.href = '/dashboard'
    } catch (error: any) {
      console.error('GitHub callback error:', error)
      setError(error.response?.data?.detail || 'GitHub 인증에 실패했습니다')
    }
  }

  if (error) {
    return (
      <div className="min-h-screen flex flex-col items-center justify-center bg-gray-50 dark:bg-gray-900">
        <BookOpen className="text-primary-600 mb-4" size={48} />
        <h1 className="text-2xl font-bold mb-2">인증 실패</h1>
        <p className="text-gray-600 dark:text-gray-400 mb-4">{error}</p>
        <button
          onClick={() => window.location.href = '/'}
          className="btn btn-primary"
        >
          홈으로 돌아가기
        </button>
      </div>
    )
  }

  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-gray-50 dark:bg-gray-900">
      <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mb-4"></div>
      <p className="text-gray-600 dark:text-gray-400">GitHub 로그인 처리 중...</p>
    </div>
  )
}

export default function AuthCallbackPage() {
  return (
    <Suspense fallback={
      <div className="min-h-screen flex flex-col items-center justify-center bg-gray-50 dark:bg-gray-900">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mb-4"></div>
        <p className="text-gray-600 dark:text-gray-400">로딩 중...</p>
      </div>
    }>
      <AuthCallbackContent />
    </Suspense>
  )
}
