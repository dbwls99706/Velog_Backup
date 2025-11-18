'use client';

import Link from 'next/link';
import { BookOpen, Cloud, Github, Zap, Shield, Clock } from 'lucide-react';

export default function HomePage() {
  return (
    <div className="min-h-screen">
      {/* Hero Section */}
      <header className="bg-gradient-to-r from-primary-600 to-primary-800 text-white">
        <nav className="container mx-auto px-4 py-6 flex justify-between items-center">
          <div className="flex items-center space-x-2">
            <BookOpen size={32} />
            <span className="text-2xl font-bold">Velog Backup</span>
          </div>
          <div className="space-x-4">
            <Link href="/login" className="btn btn-secondary">
              로그인
            </Link>
            <Link href="/register" className="btn bg-white text-primary-600 hover:bg-gray-100">
              회원가입
            </Link>
          </div>
        </nav>

        <div className="container mx-auto px-4 py-20 text-center">
          <h1 className="text-5xl md:text-6xl font-bold mb-6">
            Velog 포스트를<br />안전하게 백업하세요
          </h1>
          <p className="text-xl md:text-2xl mb-8 text-primary-100">
            Google Drive와 GitHub에 자동으로 백업되는 블로그 관리 서비스
          </p>
          <Link href="/register" className="btn bg-white text-primary-600 hover:bg-gray-100 text-lg px-8 py-3">
            무료로 시작하기
          </Link>
        </div>
      </header>

      {/* Features Section */}
      <section className="container mx-auto px-4 py-20">
        <h2 className="text-4xl font-bold text-center mb-16">주요 기능</h2>
        <div className="grid md:grid-cols-3 gap-8">
          <div className="card text-center">
            <div className="flex justify-center mb-4">
              <Zap className="text-primary-600" size={48} />
            </div>
            <h3 className="text-2xl font-bold mb-4">자동 백업</h3>
            <p className="text-gray-600 dark:text-gray-300">
              하루 1회 자동으로 Velog 포스트를 백업합니다. 새 글과 수정된 글을 자동 감지합니다.
            </p>
          </div>

          <div className="card text-center">
            <div className="flex justify-center mb-4">
              <Cloud className="text-primary-600" size={48} />
            </div>
            <h3 className="text-2xl font-bold mb-4">Google Drive 연동</h3>
            <p className="text-gray-600 dark:text-gray-300">
              모든 포스트를 Markdown 형식으로 Google Drive에 안전하게 저장합니다.
            </p>
          </div>

          <div className="card text-center">
            <div className="flex justify-center mb-4">
              <Github className="text-primary-600" size={48} />
            </div>
            <h3 className="text-2xl font-bold mb-4">GitHub 저장소</h3>
            <p className="text-gray-600 dark:text-gray-300">
              GitHub 저장소에 자동으로 커밋하여 버전 관리와 백업을 동시에 수행합니다.
            </p>
          </div>

          <div className="card text-center">
            <div className="flex justify-center mb-4">
              <Shield className="text-primary-600" size={48} />
            </div>
            <h3 className="text-2xl font-bold mb-4">안전한 보안</h3>
            <p className="text-gray-600 dark:text-gray-300">
              OAuth 2.0 기반의 안전한 인증으로 개인정보를 보호합니다.
            </p>
          </div>

          <div className="card text-center">
            <div className="flex justify-center mb-4">
              <Clock className="text-primary-600" size={48} />
            </div>
            <h3 className="text-2xl font-bold mb-4">실시간 모니터링</h3>
            <p className="text-gray-600 dark:text-gray-300">
              대시보드에서 백업 현황과 로그를 실시간으로 확인할 수 있습니다.
            </p>
          </div>

          <div className="card text-center">
            <div className="flex justify-center mb-4">
              <BookOpen className="text-primary-600" size={48} />
            </div>
            <h3 className="text-2xl font-bold mb-4">Markdown 변환</h3>
            <p className="text-gray-600 dark:text-gray-300">
              Velog 포스트를 표준 Markdown 형식으로 변환하여 어디서든 사용 가능합니다.
            </p>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="bg-primary-600 text-white py-20">
        <div className="container mx-auto px-4 text-center">
          <h2 className="text-4xl font-bold mb-6">
            지금 바로 시작하세요
          </h2>
          <p className="text-xl mb-8 text-primary-100">
            무료로 가입하고 소중한 블로그 포스트를 안전하게 보호하세요
          </p>
          <Link href="/register" className="btn bg-white text-primary-600 hover:bg-gray-100 text-lg px-8 py-3">
            무료 회원가입
          </Link>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-gray-800 text-white py-8">
        <div className="container mx-auto px-4 text-center">
          <p>&copy; 2024 Velog Backup. All rights reserved.</p>
        </div>
      </footer>
    </div>
  );
}
