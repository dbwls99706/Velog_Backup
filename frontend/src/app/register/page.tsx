'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { useAuthStore } from '@/store/authStore';
import toast from 'react-hot-toast';
import { BookOpen } from 'lucide-react';

export default function RegisterPage() {
  const router = useRouter();
  const register = useAuthStore((state) => state.register);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [fullName, setFullName] = useState('');
  const [velogUsername, setVelogUsername] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);

    try {
      await register(email, password, fullName, velogUsername);
      toast.success('회원가입 성공! 대시보드로 이동합니다');
      router.push('/dashboard');
    } catch (error: any) {
      toast.error(error.response?.data?.detail || '회원가입에 실패했습니다');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 dark:bg-gray-900 px-4 py-12">
      <div className="max-w-md w-full">
        <div className="text-center mb-8">
          <Link href="/" className="inline-flex items-center space-x-2 text-primary-600">
            <BookOpen size={40} />
            <span className="text-3xl font-bold">Velog Backup</span>
          </Link>
          <h2 className="mt-6 text-3xl font-bold">회원가입</h2>
          <p className="mt-2 text-gray-600 dark:text-gray-400">
            무료로 가입하고 백업을 시작하세요
          </p>
        </div>

        <div className="card">
          <form onSubmit={handleSubmit} className="space-y-6">
            <div>
              <label htmlFor="email" className="block text-sm font-medium mb-2">
                이메일 *
              </label>
              <input
                id="email"
                type="email"
                required
                className="input"
                placeholder="your@email.com"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
              />
            </div>

            <div>
              <label htmlFor="password" className="block text-sm font-medium mb-2">
                비밀번호 * (최소 6자)
              </label>
              <input
                id="password"
                type="password"
                required
                minLength={6}
                className="input"
                placeholder="••••••••"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
              />
            </div>

            <div>
              <label htmlFor="fullName" className="block text-sm font-medium mb-2">
                이름 (선택)
              </label>
              <input
                id="fullName"
                type="text"
                className="input"
                placeholder="홍길동"
                value={fullName}
                onChange={(e) => setFullName(e.target.value)}
              />
            </div>

            <div>
              <label htmlFor="velogUsername" className="block text-sm font-medium mb-2">
                Velog 사용자명 (선택)
              </label>
              <input
                id="velogUsername"
                type="text"
                className="input"
                placeholder="@username"
                value={velogUsername}
                onChange={(e) => setVelogUsername(e.target.value)}
              />
              <p className="mt-1 text-sm text-gray-500">
                나중에 대시보드에서 설정할 수 있습니다
              </p>
            </div>

            <button
              type="submit"
              disabled={isLoading}
              className="w-full btn btn-primary"
            >
              {isLoading ? '가입 중...' : '회원가입'}
            </button>
          </form>

          <div className="mt-6 text-center">
            <p className="text-sm text-gray-600 dark:text-gray-400">
              이미 계정이 있으신가요?{' '}
              <Link href="/login" className="text-primary-600 hover:text-primary-700 font-medium">
                로그인
              </Link>
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
