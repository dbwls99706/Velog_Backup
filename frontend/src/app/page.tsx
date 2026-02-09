'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import { BookOpen, Cloud, Shield, Zap, Github } from 'lucide-react'
import toast from 'react-hot-toast'
import { authAPI } from '@/lib/api'

export default function HomePage() {
  const router = useRouter()
  const [isLoading, setIsLoading] = useState(true)
  const [isLoggingIn, setIsLoggingIn] = useState(false)

  useEffect(() => {
    const token = localStorage.getItem('access_token')
    if (token) {
      router.push('/dashboard')
    } else {
      setIsLoading(false)
    }
  }, [router])

  const handleGitHubLogin = async () => {
    setIsLoggingIn(true)
    try {
      const response = await authAPI.getGitHubUrl()
      window.location.href = response.data.auth_url
    } catch (error) {
      toast.error('로그인에 실패했습니다')
      setIsLoggingIn(false)
    }
  }

  if (isLoading) {
    return <div className="min-h-screen flex items-center justify-center bg-gray-50 dark:bg-gray-900">
      <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
    </div>
  }

  return (
    <div className="min-h-screen">
      {/* Hero */}
      <header className="bg-gradient-to-r from-primary-600 to-primary-800 text-white">
        <div className="container mx-auto px-4 py-20">
          <div className="max-w-3xl mx-auto text-center">
            <div className="flex justify-center mb-6">
              <BookOpen size={64} />
            </div>
            <h1 className="text-5xl font-bold mb-6">Velog Backup</h1>
            <p className="text-xl mb-8 text-primary-100">
              Velog 블로그 포스트를 서버에 무료로 백업하세요
            </p>
            <div className="flex justify-center">
              <button
                onClick={handleGitHubLogin}
                disabled={isLoggingIn}
                className="flex items-center gap-3 bg-gray-900 hover:bg-gray-800 text-white px-6 py-3 rounded-lg font-medium transition-colors disabled:opacity-50"
              >
                <Github size={24} />
                {isLoggingIn ? '로그인 중...' : 'GitHub로 시작하기'}
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Features */}
      <section className="container mx-auto px-4 py-20 dark:bg-gray-900">
        <h2 className="text-3xl font-bold text-center mb-12">주요 기능</h2>
        <div className="grid md:grid-cols-3 gap-8 max-w-5xl mx-auto">
          <div className="card text-center">
            <Cloud className="mx-auto mb-4 text-primary-600" size={48} />
            <h3 className="text-xl font-bold mb-2">자동 백업</h3>
            <p className="text-gray-600 dark:text-gray-400">
              Velog 포스트를 Markdown 형식으로 자동 백업합니다
            </p>
          </div>

          <div className="card text-center">
            <Shield className="mx-auto mb-4 text-primary-600" size={48} />
            <h3 className="text-xl font-bold mb-2">안전한 보관</h3>
            <p className="text-gray-600 dark:text-gray-400">
              서버에 안전하게 저장됩니다
            </p>
          </div>

          <div className="card text-center">
            <Zap className="mx-auto mb-4 text-primary-600" size={48} />
            <h3 className="text-xl font-bold mb-2">완전 무료</h3>
            <p className="text-gray-600 dark:text-gray-400">
              모든 기능을 무료로 사용할 수 있습니다
            </p>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-gray-800 dark:bg-gray-950 text-white py-8">
        <div className="container mx-auto px-4 text-center">
          <p>&copy; 2024 Velog Backup. All rights reserved.</p>
        </div>
      </footer>
    </div>
  )
}
