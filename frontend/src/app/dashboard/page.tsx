'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import { Database, FileText, Calendar, Play, FolderOpen, Download, Loader2, Settings } from 'lucide-react'
import toast from 'react-hot-toast'
import { authAPI, backupAPI } from '@/lib/api'
import { format } from 'date-fns'
import { ko } from 'date-fns/locale'
import Header from '@/components/Header'
import LoadingSpinner from '@/components/LoadingSpinner'

export default function DashboardPage() {
  const router = useRouter()
  const [user, setUser] = useState<any>(null)
  const [stats, setStats] = useState<any>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [isBackingUp, setIsBackingUp] = useState(false)

  useEffect(() => {
    loadData()
  }, [])

  useEffect(() => {
    const hasInProgressBackup = stats?.recent_logs?.some(
      (log: any) => log.status === 'in_progress'
    )

    if (!hasInProgressBackup) return

    const interval = setInterval(() => {
      loadData()
    }, 3000)

    return () => clearInterval(interval)
  }, [stats])

  const loadData = async () => {
    try {
      const [userRes, statsRes] = await Promise.all([
        authAPI.getCurrentUser(),
        backupAPI.getStats()
      ])
      setUser(userRes.data)
      setStats(statsRes.data)
    } catch (error) {
      toast.error('데이터를 불러오는데 실패했습니다')
      router.push('/')
    } finally {
      setIsLoading(false)
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

      const blob = new Blob([response.data], { type: 'application/zip' })
      const url = window.URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = url

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

  if (isLoading) return <LoadingSpinner />

  return (
    <div className="min-h-screen bg-gray-50">
      <Header user={user} />

      <main className="container mx-auto px-4 py-8 max-w-5xl">
        <div className="mb-8">
          <h1 className="text-3xl font-bold mb-2">대시보드</h1>
          <p className="text-gray-600">백업 현황을 확인하고 관리하세요</p>
        </div>

        {/* Velog 미연동 안내 */}
        {!stats?.velog_connected && (
          <div className="card mb-6 border-yellow-200 bg-yellow-50">
            <div className="flex items-center justify-between">
              <div>
                <h2 className="text-lg font-bold text-yellow-800">Velog 계정 연동 필요</h2>
                <p className="text-sm text-yellow-700 mt-1">
                  백업을 시작하려면 먼저 설정에서 Velog 계정을 연동해주세요
                </p>
              </div>
              <Link href="/settings" className="btn btn-primary flex items-center space-x-2">
                <Settings size={16} />
                <span>설정으로 이동</span>
              </Link>
            </div>
          </div>
        )}

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

        {/* Backup Action */}
        <div className="card mb-6">
          <div className="flex justify-between items-center">
            <div>
              <h2 className="text-xl font-bold">백업 실행</h2>
              <p className="text-sm text-gray-600 mt-1">
                Velog 포스트를 이미지 포함하여 서버에 백업합니다
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
                  <div className="flex items-center space-x-2">
                    {log.status === 'in_progress' && (
                      <Loader2 className="animate-spin text-blue-600" size={16} />
                    )}
                    <div>
                      <span className={`px-2 py-1 rounded text-xs font-semibold ${
                        log.status === 'success'
                          ? 'bg-gray-200 text-gray-800'
                          : log.status === 'in_progress'
                          ? 'bg-blue-100 text-blue-800'
                          : 'bg-red-100 text-red-800'
                      }`}>
                        {log.status === 'in_progress' ? '진행 중' : log.status}
                      </span>
                      <p className="text-sm mt-1">{log.message || '백업 진행 중...'}</p>
                    </div>
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
