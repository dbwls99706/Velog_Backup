'use client'

import { useEffect, useState } from 'react'
import { useRouter, useSearchParams } from 'next/navigation'
import { BookOpen } from 'lucide-react'
import toast from 'react-hot-toast'
import { authAPI } from '@/lib/api'

export default function AuthCallbackPage() {
  const router = useRouter()
  const searchParams = useSearchParams()
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const code = searchParams.get('code')
    const errorParam = searchParams.get('error')

    if (errorParam) {
      setError('GitHub 인증이 취소되었습니다')
      return
    }

    if (!code) {
      setError('인증 코드가 없습니다')
      return
    }

    handleCallback(code)
  }, [searchParams])

  const handleCallback = async (code: string) => {
    try {
      const response = await authAPI.gitHubCallback(code)
      localStorage.setItem('access_token', response.data.access_token)
      toast.success('로그인 성공!')
      router.push('/dashboard')
    } catch (error: any) {
      console.error('GitHub callback error:', error)
      setError(error.response?.data?.detail || 'GitHub 인증에 실패했습니다')
    }
  }

  if (error) {
    return (
      <div className="min-h-screen flex flex-col items-center justify-center bg-gray-50">
        <BookOpen className="text-primary-600 mb-4" size={48} />
        <h1 className="text-2xl font-bold mb-2">인증 실패</h1>
        <p className="text-gray-600 mb-4">{error}</p>
        <button
          onClick={() => router.push('/')}
          className="btn btn-primary"
        >
          홈으로 돌아가기
        </button>
      </div>
    )
  }

  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-gray-50">
      <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mb-4"></div>
      <p className="text-gray-600">GitHub 로그인 처리 중...</p>
    </div>
  )
}
