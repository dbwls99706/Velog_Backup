'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import { BookOpen, LogOut, Cloud, FileText, Calendar, Play } from 'lucide-react'
import toast from 'react-hot-toast'
import { authAPI, googleAPI, backupAPI } from '@/lib/api'
import { format } from 'date-fns'
import { ko } from 'date-fns/locale'

export default function DashboardPage() {
  const router = useRouter()
  const [user, setUser] = useState<any>(null)
  const [stats, setStats] = useState<any>(null)
  const [velogUsername, setVelogUsername] = useState('')
  const [isLoading, setIsLoading] = useState(true)
  const [isBackingUp, setIsBackingUp] = useState(false)

  useEffect(() => {
    loadData()
  }, [])

  const loadData = async () => {
    try {
      const [userRes, statsRes] = await Promise.all([
        authAPI.getCurrentUser(),
        backupAPI.getStats()
      ])
      setUser(userRes.data)
      setStats(statsRes.data)
      setVelogUsername(userRes.data.velog_username || '')
    } catch (error) {
      toast.error('데이터를 불러오는데 실패했습니다')
      router.push('/')
    } finally {
      setIsLoading(false)
    }
  }

  const handleLogout = () => {
    localStorage.removeItem('access_token')
    router.push('/')
  }

  const handleVerifyVelog = async () => {
    try {
      await authAPI.verifyVelog(velogUsername)
      toast.success('Velog 계정이 연동되었습니다!')
      loadData()
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Velog 계정을 찾을 수 없습니다')
    }
  }

  const handleConnectDrive = async () => {
    try {
      const response = await googleAPI.getAuthUrl()
      window.location.href = response.data.auth_url
    } catch (error) {
      toast.error('Google Drive 연동에 실패했습니다')
    }
  }

  const handleBackup = async () => {
    setIsBackingUp(true)
    try {
      await backupAPI.trigger(false)
      toast.success('백업이 시작되었습니다!')
      setTimeout(loadData, 2000)
    } catch (error: any) {
      toast.error(error.response?.data?.detail || '백업 시작에 실패했습니다')
    } finally {
      setIsBackingUp(false)
    }
  }

  if (isLoading) {
    return <div className="min-h-screen flex items-center justify-center">
      <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
    </div>
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm">
        <div className="container mx-auto px-4 py-4">
          <div className="flex justify-between items-center">
            <div className="flex items-center space-x-2">
              <BookOpen className="text-primary-600" size={32} />
              <span className="text-xl font-bold">Velog Backup</span>
            </div>
            <div className="flex items-center space-x-4">
              <span className="text-sm text-gray-600">{user?.email}</span>
              <button onClick={handleLogout} className="btn btn-secondary">
                <LogOut size={16} className="inline mr-1" />
                로그아웃
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-4 py-8 max-w-5xl">
        <div className="mb-8">
          <h1 className="text-3xl font-bold mb-2">대시보드</h1>
          <p className="text-gray-600">백업 현황을 확인하고 관리하세요</p>
        </div>

        {/* Stats Cards */}
        <div className="grid md:grid-cols-3 gap-6 mb-8">
          <div className="card">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">총 포스트</p>
                <p className="text-3xl font-bold mt-1">{stats?.total_posts || 0}</p>
              </div>
              <FileText className="text-primary-600" size={40} />
            </div>
          </div>

          <div className="card">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">마지막 백업</p>
                <p className="text-lg font-semibold mt-1">
                  {stats?.last_backup
                    ? format(new Date(stats.last_backup), 'MM/dd HH:mm', { locale: ko })
                    : '없음'}
                </p>
              </div>
              <Calendar className="text-primary-600" size={40} />
            </div>
          </div>

          <div className="card">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Google Drive</p>
                <p className="text-lg font-semibold mt-1">
                  {stats?.google_drive_connected ? (
                    <span className="text-green-600">연결됨</span>
                  ) : (
                    <span className="text-gray-400">미연결</span>
                  )}
                </p>
              </div>
              <Cloud className={stats?.google_drive_connected ? 'text-green-600' : 'text-gray-400'} size={40} />
            </div>
          </div>
        </div>

        {/* Velog Connection */}
        <div className="card mb-6">
          <h2 className="text-xl font-bold mb-4">Velog 계정 연동</h2>
          <div className="flex gap-2">
            <input
              type="text"
              className="input flex-1"
              placeholder="@username"
              value={velogUsername}
              onChange={(e) => setVelogUsername(e.target.value)}
              disabled={!!user?.velog_username}
            />
            <button
              onClick={handleVerifyVelog}
              className="btn btn-primary"
              disabled={!!user?.velog_username}
            >
              {user?.velog_username ? '연동됨' : '확인'}
            </button>
          </div>
          {user?.velog_username && (
            <p className="text-sm text-green-600 mt-2">
              ✓ @{user.velog_username} 계정이 연동되었습니다
            </p>
          )}
        </div>

        {/* Google Drive Connection */}
        <div className="card mb-6">
          <h2 className="text-xl font-bold mb-4">Google Drive 연동</h2>
          {stats?.google_drive_connected ? (
            <div className="bg-green-50 p-4 rounded-lg">
              <p className="text-green-800">✓ Google Drive가 연결되어 있습니다</p>
            </div>
          ) : (
            <button onClick={handleConnectDrive} className="btn btn-primary">
              <Cloud size={16} className="inline mr-1" />
              Google Drive 연결하기
            </button>
          )}
        </div>

        {/* Backup Action */}
        <div className="card mb-6">
          <div className="flex justify-between items-center">
            <div>
              <h2 className="text-xl font-bold">백업 실행</h2>
              <p className="text-sm text-gray-600 mt-1">
                Velog 포스트를 Google Drive에 백업합니다
              </p>
            </div>
            <button
              onClick={handleBackup}
              disabled={isBackingUp || !stats?.velog_connected || !stats?.google_drive_connected}
              className="btn btn-primary flex items-center space-x-2"
            >
              <Play size={18} />
              <span>{isBackingUp ? '백업 중...' : '지금 백업하기'}</span>
            </button>
          </div>
        </div>

        {/* Recent Logs */}
        {stats?.recent_logs && stats.recent_logs.length > 0 && (
          <div className="card">
            <h2 className="text-xl font-bold mb-4">최근 백업 로그</h2>
            <div className="space-y-3">
              {stats.recent_logs.map((log: any) => (
                <div key={log.id} className="flex justify-between items-center p-3 bg-gray-50 rounded-lg">
                  <div>
                    <span className={`px-2 py-1 rounded text-xs font-semibold ${
                      log.status === 'success' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                    }`}>
                      {log.status}
                    </span>
                    <p className="text-sm mt-1">{log.message}</p>
                  </div>
                  <span className="text-sm text-gray-600">
                    {format(new Date(log.started_at), 'MM/dd HH:mm')}
                  </span>
                </div>
              ))}
            </div>
          </div>
        )}
      </main>
    </div>
  )
}
