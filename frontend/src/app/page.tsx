'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import { GoogleLogin, CredentialResponse } from '@react-oauth/google'
import { BookOpen, Cloud, Shield, Zap } from 'lucide-react'
import toast from 'react-hot-toast'
import { authAPI } from '@/lib/api'

export default function HomePage() {
  const router = useRouter()
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    const token = localStorage.getItem('access_token')
    if (token) {
      router.push('/dashboard')
    } else {
      setIsLoading(false)
    }
  }, [router])

  const handleGoogleLogin = async (response: CredentialResponse) => {
    try {
      if (!response.credential) {
        toast.error('로그인에 실패했습니다')
        return
      }

      const result = await authAPI.googleLogin(response.credential)
      localStorage.setItem('access_token', result.data.access_token)
      toast.success('로그인 성공!')
      router.push('/dashboard')
    } catch (error: any) {
      toast.error(error.response?.data?.detail || '로그인에 실패했습니다')
    }
  }

  if (isLoading) {
    return <div className="min-h-screen flex items-center justify-center">
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
              <GoogleLogin
                onSuccess={handleGoogleLogin}
                onError={() => toast.error('로그인에 실패했습니다')}
                useOneTap
                theme="filled_blue"
                size="large"
                text="continue_with"
                locale="ko"
              />
            </div>
          </div>
        </div>
      </header>

      {/* Features */}
      <section className="container mx-auto px-4 py-20">
        <h2 className="text-3xl font-bold text-center mb-12">주요 기능</h2>
        <div className="grid md:grid-cols-3 gap-8 max-w-5xl mx-auto">
          <div className="card text-center">
            <Cloud className="mx-auto mb-4 text-primary-600" size={48} />
            <h3 className="text-xl font-bold mb-2">자동 백업</h3>
            <p className="text-gray-600">
              Velog 포스트를 Markdown 형식으로 자동 백업합니다
            </p>
          </div>

          <div className="card text-center">
            <Shield className="mx-auto mb-4 text-primary-600" size={48} />
            <h3 className="text-xl font-bold mb-2">안전한 보관</h3>
            <p className="text-gray-600">
              서버에 안전하게 저장됩니다
            </p>
          </div>

          <div className="card text-center">
            <Zap className="mx-auto mb-4 text-primary-600" size={48} />
            <h3 className="text-xl font-bold mb-2">완전 무료</h3>
            <p className="text-gray-600">
              모든 기능을 무료로 사용할 수 있습니다
            </p>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-gray-800 text-white py-8">
        <div className="container mx-auto px-4 text-center">
          <p>&copy; 2024 Velog Backup. All rights reserved.</p>
        </div>
      </footer>
    </div>
  )
}
