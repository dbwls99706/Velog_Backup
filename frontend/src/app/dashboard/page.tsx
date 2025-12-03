'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import { BookOpen, LogOut, Database, FileText, Calendar, Play, FolderOpen, Download } from 'lucide-react'
import toast from 'react-hot-toast'
import { authAPI, backupAPI } from '@/lib/api'
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

  const handleDownloadZip = async () => {
    try {
      toast.loading('ZIP 파일을 생성하는 중...')
      const response = await backupAPI.downloadZip()

      // Blob을 다운로드
      const blob = new Blob([response.data], { type: 'application/zip' })
      const url = window.URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = url

      // 파일명 추출 (Content-Disposition 헤더에서)
      const contentDisposition = response.headers['content-disposition']
      let filename = 'velog_backup.zip'
      if (contentDisposition) {
        const filenameMatch = contentDisposition.match(/filename=(.+)/)
        if (filenameMatch && filenameMatch[1]) {
          filename = filenameMatch[1]
        }
      }

      link.download = filename
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
      window.URL.revokeObjectURL(url)

      toast.dismiss()
      toast.success('ZIP 파일 다운로드가 완료되었습니다!')
    } catch (error: any) {
      toast.dismiss()
      toast.error(error.response?.data?.detail || 'ZIP 파일 다운로드에 실패했습니다')
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
                <p className="text-sm text-gray-600">총 백업 포스트</p>
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
                <p className="text-sm text-gray-600">저장소</p>
                <p className="text-lg font-semibold mt-1">
                  <span className="text-primary-600">서버 DB</span>
                </p>
              </div>
              <Database className="text-primary-600" size={40} />
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
            <p className="text-sm text-primary-600 mt-2">
              @{user.velog_username} 계정이 연동되었습니다
            </p>
          )}
        </div>

        {/* Backup Action */}
        <div className="card mb-6">
          <div className="flex justify-between items-center">
            <div>
              <h2 className="text-xl font-bold">백업 실행</h2>
              <p className="text-sm text-gray-600 mt-1">
                Velog 포스트를 서버에 백업합니다 (무료)
              </p>
            </div>
            <button
              onClick={handleBackup}
              disabled={isBackingUp || !stats?.velog_connected}
              className="btn btn-primary flex items-center space-x-2"
            >
              <Play size={18} />
              <span>{isBackingUp ? '백업 중...' : '지금 백업하기'}</span>
            </button>
          </div>
        </div>

        {/* View Posts */}
        {stats?.total_posts > 0 && (
          <div className="card mb-6">
            <div className="flex justify-between items-center">
              <div>
                <h2 className="text-xl font-bold">백업된 포스트</h2>
                <p className="text-sm text-gray-600 mt-1">
                  {stats?.total_posts}개의 포스트가 서버에 저장되어 있습니다
                </p>
              </div>
              <div className="flex space-x-2">
                <button
                  onClick={handleDownloadZip}
                  className="btn btn-primary flex items-center space-x-2"
                >
                  <Download size={18} />
                  <span>전체 다운로드 (ZIP)</span>
                </button>
                <Link href="/posts" className="btn btn-secondary flex items-center space-x-2">
                  <FolderOpen size={18} />
                  <span>포스트 보기</span>
                </Link>
              </div>
            </div>
          </div>
        )}

        {/* Recent Logs */}
        {stats?.recent_logs && stats.recent_logs.length > 0 && (
          <div className="card">
            <h2 className="text-xl font-bold mb-4">최근 백업 로그</h2>
            <div className="space-y-3">
              {stats.recent_logs.map((log: any) => (
                <div key={log.id} className="flex justify-between items-center p-3 bg-gray-50 rounded-lg">
                  <div>
                    <span className={`px-2 py-1 rounded text-xs font-semibold ${
                      log.status === 'success' ? 'bg-gray-200 text-gray-800' : 'bg-red-100 text-red-800'
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
