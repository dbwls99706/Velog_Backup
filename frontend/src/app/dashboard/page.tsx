'use client';

import { useEffect, useState } from 'react';
import DashboardLayout from '@/components/DashboardLayout';
import { backupAPI, integrationAPI } from '@/lib/api';
import toast from 'react-hot-toast';
import { Cloud, Github, Play, TrendingUp, FileText, Calendar } from 'lucide-react';
import { format } from 'date-fns';
import { ko } from 'date-fns/locale';

export default function DashboardPage() {
  const [stats, setStats] = useState<any>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isTriggeringBackup, setIsTriggeringBackup] = useState(false);

  useEffect(() => {
    loadStats();
  }, []);

  const loadStats = async () => {
    try {
      const response = await backupAPI.getBackupStats();
      setStats(response.data);
    } catch (error) {
      toast.error('통계를 불러오는데 실패했습니다');
    } finally {
      setIsLoading(false);
    }
  };

  const triggerBackup = async () => {
    setIsTriggeringBackup(true);
    try {
      await backupAPI.triggerBackup('both');
      toast.success('백업이 시작되었습니다!');
      setTimeout(loadStats, 2000);
    } catch (error: any) {
      toast.error(error.response?.data?.detail || '백업 시작에 실패했습니다');
    } finally {
      setIsTriggeringBackup(false);
    }
  };

  if (isLoading) {
    return (
      <DashboardLayout>
        <div className="text-center py-12">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">로딩 중...</p>
        </div>
      </DashboardLayout>
    );
  }

  return (
    <DashboardLayout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-3xl font-bold">대시보드</h1>
            <p className="text-gray-600 dark:text-gray-400 mt-1">
              백업 현황을 한눈에 확인하세요
            </p>
          </div>
          <button
            onClick={triggerBackup}
            disabled={isTriggeringBackup || (!stats?.google_drive_connected && !stats?.github_connected)}
            className="btn btn-primary flex items-center space-x-2"
          >
            <Play size={18} />
            <span>{isTriggeringBackup ? '백업 중...' : '지금 백업하기'}</span>
          </button>
        </div>

        {/* Stats Cards */}
        <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
          <div className="card">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600 dark:text-gray-400">총 포스트</p>
                <p className="text-3xl font-bold mt-1">{stats?.total_posts || 0}</p>
              </div>
              <FileText className="text-primary-600" size={40} />
            </div>
          </div>

          <div className="card">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600 dark:text-gray-400">마지막 백업</p>
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
                <p className="text-sm text-gray-600 dark:text-gray-400">Google Drive</p>
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

          <div className="card">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600 dark:text-gray-400">GitHub</p>
                <p className="text-lg font-semibold mt-1">
                  {stats?.github_connected ? (
                    <span className="text-green-600">연결됨</span>
                  ) : (
                    <span className="text-gray-400">미연결</span>
                  )}
                </p>
              </div>
              <Github className={stats?.github_connected ? 'text-green-600' : 'text-gray-400'} size={40} />
            </div>
          </div>
        </div>

        {/* Connection Warning */}
        {!stats?.google_drive_connected && !stats?.github_connected && (
          <div className="card bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800">
            <div className="flex items-start space-x-3">
              <TrendingUp className="text-yellow-600 mt-1" size={24} />
              <div>
                <h3 className="font-semibold text-yellow-900 dark:text-yellow-100">
                  백업 연동이 필요합니다
                </h3>
                <p className="text-sm text-yellow-800 dark:text-yellow-200 mt-1">
                  Google Drive 또는 GitHub를 연동해야 백업을 시작할 수 있습니다.
                  설정 페이지에서 연동해주세요.
                </p>
                <a href="/dashboard/settings" className="btn btn-primary mt-3 inline-block">
                  설정으로 이동
                </a>
              </div>
            </div>
          </div>
        )}

        {/* Recent Backup Logs */}
        <div className="card">
          <h2 className="text-xl font-bold mb-4">최근 백업 로그</h2>
          {stats?.recent_logs && stats.recent_logs.length > 0 ? (
            <div className="space-y-3">
              {stats.recent_logs.map((log: any) => (
                <div
                  key={log.id}
                  className="flex items-center justify-between p-4 bg-gray-50 dark:bg-gray-700 rounded-lg"
                >
                  <div className="flex-1">
                    <div className="flex items-center space-x-2">
                      <span
                        className={`px-2 py-1 rounded text-xs font-semibold ${
                          log.status === 'success'
                            ? 'bg-green-100 text-green-800'
                            : log.status === 'failed'
                            ? 'bg-red-100 text-red-800'
                            : 'bg-yellow-100 text-yellow-800'
                        }`}
                      >
                        {log.status}
                      </span>
                      <span className="text-sm text-gray-600 dark:text-gray-300">
                        {format(new Date(log.started_at), 'yyyy-MM-dd HH:mm', { locale: ko })}
                      </span>
                    </div>
                    <p className="text-sm mt-1">
                      {log.message || `${log.posts_backed_up}/${log.posts_total} 포스트 백업 완료`}
                    </p>
                  </div>
                  <div className="text-right">
                    <p className="text-sm font-semibold">{log.destination}</p>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-center text-gray-500 py-8">백업 로그가 없습니다</p>
          )}
        </div>
      </div>
    </DashboardLayout>
  );
}
