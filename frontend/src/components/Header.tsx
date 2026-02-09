'use client'

import Link from 'next/link'
import { usePathname, useRouter } from 'next/navigation'
import { BookOpen, LogOut, LayoutDashboard, FileText, Settings } from 'lucide-react'

interface HeaderProps {
  user?: { email?: string; name?: string } | null
}

const navItems = [
  { href: '/dashboard', label: '대시보드', icon: LayoutDashboard },
  { href: '/posts', label: '포스트', icon: FileText },
  { href: '/settings', label: '설정', icon: Settings },
]

export default function Header({ user }: HeaderProps) {
  const pathname = usePathname()
  const router = useRouter()

  const handleLogout = () => {
    localStorage.removeItem('access_token')
    sessionStorage.removeItem('setup_dismissed')
    router.push('/')
  }

  return (
    <header className="bg-white shadow-sm dark:bg-gray-800 dark:shadow-gray-900/20">
      <div className="container mx-auto px-4 py-4">
        <div className="flex justify-between items-center">
          <div className="flex items-center space-x-8">
            <Link
              href="/dashboard"
              className="flex items-center space-x-2 hover:opacity-80 transition-opacity"
            >
              <BookOpen className="text-primary-600" size={32} />
              <span className="text-xl font-bold">Velog Backup</span>
            </Link>

            <nav className="hidden md:flex items-center space-x-1">
              {navItems.map((item) => {
                const isActive = pathname === item.href || pathname.startsWith(item.href + '/')
                return (
                  <Link
                    key={item.href}
                    href={item.href}
                    className={`flex items-center space-x-1 px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
                      isActive
                        ? 'bg-primary-100 text-primary-800 dark:bg-primary-900 dark:text-primary-200'
                        : 'text-gray-600 hover:bg-gray-100 hover:text-gray-900 dark:text-gray-400 dark:hover:bg-gray-700 dark:hover:text-gray-100'
                    }`}
                  >
                    <item.icon size={16} />
                    <span>{item.label}</span>
                  </Link>
                )
              })}
            </nav>
          </div>

          <div className="flex items-center space-x-4 min-h-[36px]">
            {user && (
              <>
                <span className="hidden sm:inline text-sm text-gray-600 dark:text-gray-400">{user.email}</span>
                <button onClick={handleLogout} className="btn btn-secondary text-sm">
                  <LogOut size={16} className="inline mr-1" />
                  로그아웃
                </button>
              </>
            )}
          </div>
        </div>

        {/* Mobile navigation */}
        <nav className="flex md:hidden items-center space-x-1 mt-3 pt-3 border-t border-gray-100 dark:border-gray-700">
          {navItems.map((item) => {
            const isActive = pathname === item.href || pathname.startsWith(item.href + '/')
            return (
              <Link
                key={item.href}
                href={item.href}
                className={`flex items-center space-x-1 px-3 py-2 rounded-lg text-sm font-medium transition-colors flex-1 justify-center ${
                  isActive
                    ? 'bg-primary-100 text-primary-800 dark:bg-primary-900 dark:text-primary-200'
                    : 'text-gray-600 hover:bg-gray-100 dark:text-gray-400 dark:hover:bg-gray-700'
                }`}
              >
                <item.icon size={16} />
                <span>{item.label}</span>
              </Link>
            )
          })}
        </nav>
      </div>
    </header>
  )
}
