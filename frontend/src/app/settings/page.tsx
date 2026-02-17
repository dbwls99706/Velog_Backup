'use client'

import { useEffect, useState, useCallback } from 'react'
import { useRouter } from 'next/navigation'
import { Edit, X, Github, Mail, Bell, BellOff, AlertTriangle, Sun, Moon, CheckCircle, ExternalLink, Unlink } from 'lucide-react'
import toast from 'react-hot-toast'
import { authAPI, settingsAPI, githubAppAPI } from '@/lib/api'
import Header from '@/components/Header'
import { useUser } from '@/contexts/UserContext'
import { useTheme } from '@/contexts/ThemeContext'

interface GitHubRepo {
  name: string
  full_name: string
  private: boolean
  description: string
}

export default function SettingsPage() {
  const router = useRouter()
  const { user, isLoading: userLoading, refreshUser } = useUser()
  const { theme, toggleTheme } = useTheme()
  const [settingsLoading, setSettingsLoading] = useState(true)

  // Velog
  const [velogUsername, setVelogUsername] = useState('')
  const [isEditingVelog, setIsEditingVelog] = useState(false)

  // GitHub Sync
  const [githubRepo, setGithubRepo] = useState('')
  const [githubSyncEnabled, setGithubSyncEnabled] = useState(false)
  const [githubInstalled, setGithubInstalled] = useState(false)
  const [savedGithubRepo, setSavedGithubRepo] = useState('')
  const [repoWarning, setRepoWarning] = useState<{ exists: boolean; description?: string } | null>(null)
  const [savingGithub, setSavingGithub] = useState(false)

  // GitHub App
  const [appRepos, setAppRepos] = useState<GitHubRepo[]>([])
  const [loadingRepos, setLoadingRepos] = useState(false)
  const [connecting, setConnecting] = useState(false)

  // Email Notification
  const [emailNotificationEnabled, setEmailNotificationEnabled] = useState(false)

  const loadSettings = useCallback(async () => {
    try {
      const settingsRes = await settingsAPI.get()
      const repo = settingsRes.data.github_repo || ''
      setGithubRepo(repo)
      setSavedGithubRepo(repo)
      setGithubSyncEnabled(settingsRes.data.github_sync_enabled || false)
      setGithubInstalled(settingsRes.data.github_installed || false)
      setEmailNotificationEnabled(settingsRes.data.email_notification_enabled || false)
    } catch (error) {
      toast.error('설정을 불러오는데 실패했습니다')
    } finally {
      setSettingsLoading(false)
    }
  }, [])

  const loadAppRepos = useCallback(async () => {
    setLoadingRepos(true)
    try {
      const res = await githubAppAPI.listRepos()
      setAppRepos(res.data.repos || [])
    } catch {
      // GitHub App 미설정 시 무시
    } finally {
      setLoadingRepos(false)
    }
  }, [])

  useEffect(() => {
    if (!userLoading && !user) {
      router.push('/')
      return
    }
    if (user) {
      setVelogUsername(user.velog_username || '')
      loadSettings()
    }
  }, [user, userLoading, router, loadSettings])

  // GitHub App 연결 상태면 레포 목록 로드
  useEffect(() => {
    if (githubInstalled) {
      loadAppRepos()
    }
  }, [githubInstalled, loadAppRepos])

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

  // GitHub App 설치 페이지로 이동
  const handleInstallApp = async () => {
    try {
      const res = await githubAppAPI.getInstallUrl()
      window.open(res.data.install_url, '_blank')
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'GitHub App URL을 가져올 수 없습니다')
    }
  }

  // GitHub App 연결 감지
  const handleConnectApp = async () => {
    setConnecting(true)
    try {
      await githubAppAPI.connect()
      setGithubInstalled(true)
      toast.success('GitHub App이 연결되었습니다')
      await loadAppRepos()
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'GitHub App 연결에 실패했습니다')
    } finally {
      setConnecting(false)
    }
  }

  // GitHub App 연결 해제
  const handleDisconnectApp = async () => {
    try {
      await githubAppAPI.disconnect()
      setGithubInstalled(false)
      setAppRepos([])
      setGithubSyncEnabled(false)
      toast.success('GitHub App 연결이 해제되었습니다')
    } catch (error: any) {
      toast.error('연결 해제에 실패했습니다')
    }
  }

  const saveGithubSettings = async () => {
    setSavingGithub(true)
    try {
      await settingsAPI.update({
        github_repo: githubRepo,
        github_sync_enabled: githubSyncEnabled,
      })
      setSavedGithubRepo(githubRepo)
      setRepoWarning(null)
      toast.success('GitHub 동기화 설정이 저장되었습니다')
    } catch (error: any) {
      toast.error(error.response?.data?.detail || '설정 저장에 실패했습니다')
    } finally {
      setSavingGithub(false)
    }
  }

  const handleSaveGithubSync = async () => {
    // GitHub App 모드에서는 레포 존재 확인 불필요 (목록에서 선택하므로)
    if (githubInstalled) {
      await saveGithubSettings()
      return
    }

    const repoChanged = githubRepo.trim() && githubRepo.trim() !== savedGithubRepo
    if (!repoChanged) {
      await saveGithubSettings()
      return
    }

    // 새 레포 이름이면 존재 여부 확인
    setSavingGithub(true)
    try {
      const res = await settingsAPI.checkGitHubRepo(githubRepo.trim())
      if (res.data.exists) {
        setRepoWarning({ exists: true, description: res.data.description })
        setSavingGithub(false)
        return
      }
    } catch {
      // 확인 실패 시 그냥 저장 진행
    }
    await saveGithubSettings()
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

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      <Header user={user} />

      <main className="container mx-auto px-4 py-8 max-w-3xl">
        {(userLoading || settingsLoading) ? (
          <div className="flex justify-center py-16">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
          </div>
        ) : (<>
        <div className="mb-8">
          <h1 className="text-3xl font-bold mb-2">설정</h1>
          <p className="text-gray-600 dark:text-gray-400">백업 서비스 설정을 관리하세요</p>
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
            <p className="text-sm text-red-600 dark:text-red-400 font-semibold mt-2">
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
          <p className="text-sm text-gray-600 dark:text-gray-400 mb-4">
            백업된 포스트를 GitHub Repository에 자동으로 커밋합니다.
            각 글은 제목별 폴더로 정리되며, 이미지도 함께 저장됩니다.
          </p>

          {/* GitHub App 연결 상태 */}
          <div className="mb-4 p-3 rounded-lg border border-gray-200 dark:border-gray-600">
            {githubInstalled ? (
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-2">
                  <CheckCircle size={16} className="text-green-500" />
                  <span className="text-sm font-medium text-green-700 dark:text-green-400">
                    GitHub App 연결됨
                  </span>
                  <span className="text-xs text-gray-500 dark:text-gray-400">
                    (선택한 Repository만 접근)
                  </span>
                </div>
                <button
                  onClick={handleDisconnectApp}
                  className="text-xs text-red-500 hover:text-red-700 flex items-center space-x-1"
                >
                  <Unlink size={12} />
                  <span>연결 해제</span>
                </button>
              </div>
            ) : (
              <div className="space-y-2">
                <p className="text-sm text-gray-600 dark:text-gray-400">
                  GitHub App을 설치하면 선택한 Repository에만 접근 권한을 부여합니다.
                  설치하지 않아도 아래에서 Repository 이름을 직접 입력하여 동기화할 수 있습니다.
                </p>
                <details className="text-xs text-gray-500 dark:text-gray-400">
                  <summary className="cursor-pointer text-primary-600 dark:text-primary-400 font-medium">
                    GitHub App으로 보안 강화하기 (선택)
                  </summary>
                  <ol className="list-decimal list-inside space-y-0.5 mt-2">
                    <li>GitHub에서 백업용 Repository를 먼저 생성하세요</li>
                    <li>아래 버튼으로 App을 설치하고, 해당 Repository를 선택하세요</li>
                    <li>&ldquo;설치 완료 후 연결&rdquo;을 눌러 연동을 완료하세요</li>
                  </ol>
                  <div className="flex gap-2 mt-2">
                    <button
                      onClick={handleInstallApp}
                      className="btn btn-primary text-sm flex items-center space-x-1"
                    >
                      <ExternalLink size={14} />
                      <span>GitHub App 설치</span>
                    </button>
                    <button
                      onClick={handleConnectApp}
                      disabled={connecting}
                      className="btn btn-secondary text-sm"
                    >
                      {connecting ? '확인 중...' : '설치 완료 후 연결'}
                    </button>
                  </div>
                </details>
              </div>
            )}
          </div>

          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Repository {githubInstalled ? '선택' : '이름'}
              </label>
              {githubInstalled && appRepos.length > 0 ? (
                <select
                  className="input w-full"
                  value={githubRepo}
                  onChange={(e) => setGithubRepo(e.target.value)}
                >
                  <option value="">Repository를 선택하세요</option>
                  {appRepos.map((repo) => (
                    <option key={repo.full_name} value={repo.name}>
                      {repo.name} {repo.private ? '(비공개)' : '(공개)'}{repo.description ? ` - ${repo.description}` : ''}
                    </option>
                  ))}
                </select>
              ) : (
                <>
                  <div className="flex gap-2">
                    <input
                      type="text"
                      className="input flex-1"
                      placeholder="예: my-velog-backup"
                      value={githubRepo}
                      onChange={(e) => setGithubRepo(e.target.value)}
                    />
                  </div>
                  {githubInstalled && loadingRepos ? (
                    <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                      레포지토리 목록을 불러오는 중...
                    </p>
                  ) : githubInstalled ? (
                    <p className="text-xs text-yellow-600 dark:text-yellow-400 mt-1">
                      접근 가능한 레포지토리가 없습니다. GitHub App 설정에서 레포지토리를 추가해주세요.
                    </p>
                  ) : (
                    <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                      존재하지 않으면 자동으로 생성됩니다
                    </p>
                  )}
                </>
              )}
              {repoWarning?.exists && (
                <div className="mt-3 p-3 bg-yellow-50 border border-yellow-200 rounded-lg dark:bg-yellow-900/20 dark:border-yellow-800">
                  <div className="flex items-start space-x-2">
                    <AlertTriangle size={16} className="text-yellow-600 dark:text-yellow-400 mt-0.5 flex-shrink-0" />
                    <div className="flex-1">
                      <p className="text-sm font-medium text-yellow-800 dark:text-yellow-400">
                        이미 존재하는 Repository입니다
                      </p>
                      {repoWarning.description && (
                        <p className="text-xs text-yellow-700 dark:text-yellow-500 mt-1">{repoWarning.description}</p>
                      )}
                      <p className="text-xs text-yellow-700 dark:text-yellow-500 mt-1">
                        동기화 시 README.md가 덮어씌워지고, posts/ 폴더에 백업 파일이 추가됩니다.
                      </p>
                      <div className="flex gap-2 mt-2">
                        <button
                          onClick={saveGithubSettings}
                          disabled={savingGithub}
                          className="text-xs px-3 py-1 bg-yellow-600 text-white rounded hover:bg-yellow-700 transition-colors disabled:opacity-50"
                        >
                          그래도 사용
                        </button>
                        <button
                          onClick={() => setRepoWarning(null)}
                          className="text-xs px-3 py-1 bg-gray-200 text-gray-700 rounded hover:bg-gray-300 transition-colors dark:bg-gray-600 dark:text-gray-200 dark:hover:bg-gray-500"
                        >
                          취소
                        </button>
                      </div>
                    </div>
                  </div>
                </div>
              )}
            </div>

            <div className="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-700 rounded-lg">
              <div>
                <p className="font-medium">자동 동기화</p>
                <p className="text-sm text-gray-600 dark:text-gray-400">백업 완료 시 자동으로 GitHub에 커밋</p>
              </div>
              <button
                role="switch"
                aria-checked={githubSyncEnabled}
                aria-label="자동 동기화"
                onClick={() => setGithubSyncEnabled(!githubSyncEnabled)}
                className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
                  githubSyncEnabled ? 'bg-primary-600' : 'bg-gray-300 dark:bg-gray-500'
                }`}
              >
                <span
                  className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                    githubSyncEnabled ? 'translate-x-6' : 'translate-x-1'
                  }`}
                />
              </button>
            </div>

            <button onClick={handleSaveGithubSync} className="btn btn-primary" disabled={savingGithub}>
              {savingGithub ? '확인 중...' : '설정 저장'}
            </button>
          </div>
        </div>

        {/* 이메일 알림 */}
        <div className="card mb-6">
          <div className="flex items-center space-x-2 mb-4">
            <Mail size={20} />
            <h2 className="text-xl font-bold">이메일 알림</h2>
          </div>
          <p className="text-sm text-gray-600 dark:text-gray-400 mb-4">
            백업 완료 또는 실패 시 등록된 이메일({user?.email})로 알림을 받습니다.
          </p>

          <div className="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-700 rounded-lg">
            <div className="flex items-center space-x-3">
              {emailNotificationEnabled ? (
                <Bell size={20} className="text-primary-600" />
              ) : (
                <BellOff size={20} className="text-gray-400" />
              )}
              <div>
                <p className="font-medium">백업 알림</p>
                <p className="text-sm text-gray-600 dark:text-gray-400">
                  {emailNotificationEnabled ? '알림 활성화됨' : '알림 비활성화됨'}
                </p>
              </div>
            </div>
            <button
              role="switch"
              aria-checked={emailNotificationEnabled}
              aria-label="백업 알림"
              onClick={handleToggleEmailNotification}
              className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
                emailNotificationEnabled ? 'bg-primary-600' : 'bg-gray-300 dark:bg-gray-500'
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

        {/* 테마 설정 */}
        <div className="card mb-6">
          <div className="flex items-center space-x-2 mb-4">
            {theme === 'dark' ? <Moon size={20} /> : <Sun size={20} />}
            <h2 className="text-xl font-bold">테마</h2>
          </div>
          <p className="text-sm text-gray-600 dark:text-gray-400 mb-4">
            화면 테마를 설정합니다.
          </p>

          <div className="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-700 rounded-lg">
            <div className="flex items-center space-x-3">
              {theme === 'dark' ? (
                <Moon size={20} className="text-primary-600" />
              ) : (
                <Sun size={20} className="text-yellow-500" />
              )}
              <div>
                <p className="font-medium">다크 모드</p>
                <p className="text-sm text-gray-600 dark:text-gray-400">
                  {theme === 'dark' ? '다크 모드 사용 중' : '라이트 모드 사용 중'}
                </p>
              </div>
            </div>
            <button
              role="switch"
              aria-checked={theme === 'dark'}
              aria-label="다크 모드"
              onClick={toggleTheme}
              className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
                theme === 'dark' ? 'bg-primary-600' : 'bg-gray-300 dark:bg-gray-500'
              }`}
            >
              <span
                className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                  theme === 'dark' ? 'translate-x-6' : 'translate-x-1'
                }`}
              />
            </button>
          </div>
        </div>
        </>)}
      </main>
    </div>
  )
}
