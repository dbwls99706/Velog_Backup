'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import { Edit, X, Github, Mail, Bell, BellOff } from 'lucide-react'
import toast from 'react-hot-toast'
import { authAPI, settingsAPI } from '@/lib/api'
import Header from '@/components/Header'
import LoadingSpinner from '@/components/LoadingSpinner'
import { useUser } from '@/contexts/UserContext'

export default function SettingsPage() {
  const router = useRouter()
  const { user, isLoading: userLoading, refreshUser } = useUser()
  const [settingsLoading, setSettingsLoading] = useState(true)

  // Velog
  const [velogUsername, setVelogUsername] = useState('')
  const [isEditingVelog, setIsEditingVelog] = useState(false)

  // GitHub Sync
  const [githubRepo, setGithubRepo] = useState('')
  const [githubSyncEnabled, setGithubSyncEnabled] = useState(false)

  // Email Notification
  const [emailNotificationEnabled, setEmailNotificationEnabled] = useState(false)

  useEffect(() => {
    if (!userLoading && !user) {
      router.push('/')
      return
    }
    if (user) {
      setVelogUsername(user.velog_username || '')
      loadSettings()
    }
  }, [user, userLoading])

  const loadSettings = async () => {
    try {
      const settingsRes = await settingsAPI.get()
      setGithubRepo(settingsRes.data.github_repo || '')
      setGithubSyncEnabled(settingsRes.data.github_sync_enabled || false)
      setEmailNotificationEnabled(settingsRes.data.email_notification_enabled || false)
    } catch (error) {
      toast.error('설정을 불러오는데 실패했습니다')
    } finally {
      setSettingsLoading(false)
    }
  }

  const handleVerifyVelog = async () => {
    try {
      const response = await authAPI.verifyVelog(velogUsername)
      toast.success(response.data.message)
      setIsEditingVelog(false)
      await refreshUser()
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Velog 계정을 찾을 수 없습니다')
    }
  }

  const handleEditVelog = () => setIsEditingVelog(true)

  const handleCancelEditVelog = () => {
    setVelogUsername(user?.velog_username || '')
    setIsEditingVelog(false)
  }

  const handleSaveGithubSync = async () => {
    try {
      await settingsAPI.update({
        github_repo: githubRepo,
        github_sync_enabled: githubSyncEnabled,
      })
      toast.success('GitHub 동기화 설정이 저장되었습니다')
    } catch (error: any) {
      toast.error(error.response?.data?.detail || '설정 저장에 실패했습니다')
    }
  }

  const handleToggleEmailNotification = async () => {
    const newValue = !emailNotificationEnabled
    try {
      await settingsAPI.update({ email_notification_enabled: newValue })
      setEmailNotificationEnabled(newValue)
      toast.success(newValue ? '이메일 알림이 활성화되었습니다' : '이메일 알림이 비활성화되었습니다')
    } catch (error: any) {
      toast.error('설정 변경에 실패했습니다')
    }
  }

  if (userLoading || settingsLoading) return <LoadingSpinner />

  return (
    <div className="min-h-screen bg-gray-50">
      <Header user={user} />

      <main className="container mx-auto px-4 py-8 max-w-3xl">
        <div className="mb-8">
          <h1 className="text-3xl font-bold mb-2">설정</h1>
          <p className="text-gray-600">백업 서비스 설정을 관리하세요</p>
        </div>

        {/* Velog 계정 연동 */}
        <div className="card mb-6">
          <h2 className="text-xl font-bold mb-4">Velog 계정 연동</h2>
          <div className="flex gap-2">
            <input
              type="text"
              className="input flex-1"
              placeholder="@username"
              value={velogUsername}
              onChange={(e) => setVelogUsername(e.target.value)}
              disabled={!!user?.velog_username && !isEditingVelog}
            />
            {!user?.velog_username || isEditingVelog ? (
              <>
                <button
                  onClick={handleVerifyVelog}
                  className="btn btn-primary"
                  disabled={!velogUsername.trim()}
                >
                  {user?.velog_username ? '저장' : '확인'}
                </button>
                {isEditingVelog && (
                  <button onClick={handleCancelEditVelog} className="btn btn-secondary">
                    <X size={16} />
                  </button>
                )}
              </>
            ) : (
              <button
                onClick={handleEditVelog}
                className="btn btn-secondary flex items-center space-x-1"
              >
                <Edit size={16} />
                <span>수정</span>
              </button>
            )}
          </div>
          {user?.velog_username && !isEditingVelog && (
            <p className="text-sm text-primary-600 mt-2">
              @{user.velog_username} 계정이 연동되었습니다
            </p>
          )}
          {isEditingVelog && (
            <p className="text-sm text-red-600 font-semibold mt-2">
              주의: 계정을 변경하면 기존에 백업된 모든 포스트가 삭제됩니다!
              변경 후 다시 백업을 실행해주세요.
            </p>
          )}
        </div>

        {/* GitHub 동기화 */}
        <div className="card mb-6">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center space-x-2">
              <Github size={20} />
              <h2 className="text-xl font-bold">GitHub Repository 동기화</h2>
            </div>
          </div>
          <p className="text-sm text-gray-600 mb-4">
            백업된 포스트를 GitHub Repository에 자동으로 커밋합니다.
            각 글은 제목별 폴더로 정리되며, 이미지도 함께 저장됩니다.
          </p>

          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Repository 이름
              </label>
              <div className="flex gap-2">
                <input
                  type="text"
                  className="input flex-1"
                  placeholder="예: my-velog-backup"
                  value={githubRepo}
                  onChange={(e) => setGithubRepo(e.target.value)}
                />
              </div>
              <p className="text-xs text-gray-500 mt-1">
                존재하지 않으면 자동으로 생성됩니다
              </p>
            </div>

            <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
              <div>
                <p className="font-medium">자동 동기화</p>
                <p className="text-sm text-gray-600">백업 완료 시 자동으로 GitHub에 커밋</p>
              </div>
              <button
                onClick={() => setGithubSyncEnabled(!githubSyncEnabled)}
                className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
                  githubSyncEnabled ? 'bg-primary-600' : 'bg-gray-300'
                }`}
              >
                <span
                  className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                    githubSyncEnabled ? 'translate-x-6' : 'translate-x-1'
                  }`}
                />
              </button>
            </div>

            <button onClick={handleSaveGithubSync} className="btn btn-primary">
              설정 저장
            </button>
          </div>
        </div>

        {/* 이메일 알림 */}
        <div className="card mb-6">
          <div className="flex items-center space-x-2 mb-4">
            <Mail size={20} />
            <h2 className="text-xl font-bold">이메일 알림</h2>
          </div>
          <p className="text-sm text-gray-600 mb-4">
            백업 완료 또는 실패 시 등록된 이메일({user?.email})로 알림을 받습니다.
          </p>

          <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
            <div className="flex items-center space-x-3">
              {emailNotificationEnabled ? (
                <Bell size={20} className="text-primary-600" />
              ) : (
                <BellOff size={20} className="text-gray-400" />
              )}
              <div>
                <p className="font-medium">백업 알림</p>
                <p className="text-sm text-gray-600">
                  {emailNotificationEnabled ? '알림 활성화됨' : '알림 비활성화됨'}
                </p>
              </div>
            </div>
            <button
              onClick={handleToggleEmailNotification}
              className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
                emailNotificationEnabled ? 'bg-primary-600' : 'bg-gray-300'
              }`}
            >
              <span
                className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                  emailNotificationEnabled ? 'translate-x-6' : 'translate-x-1'
                }`}
              />
            </button>
          </div>
        </div>
      </main>
    </div>
  )
}
