'use client';

import { useEffect, useState } from 'react';
import DashboardLayout from '@/components/DashboardLayout';
import { integrationAPI, authAPI } from '@/lib/api';
import toast from 'react-hot-toast';
import { Cloud, Github, Check, X } from 'lucide-react';

export default function SettingsPage() {
  const [integrations, setIntegrations] = useState<any>(null);
  const [velogUsername, setVelogUsername] = useState('');
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    loadIntegrations();
  }, []);

  const loadIntegrations = async () => {
    try {
      const response = await integrationAPI.getIntegrations();
      setIntegrations(response.data);
    } catch (error) {
      toast.error('연동 정보를 불러오는데 실패했습니다');
    } finally {
      setIsLoading(false);
    }
  };

  const connectGoogleDrive = async () => {
    try {
      const response = await integrationAPI.getGoogleDriveAuthUrl();
      window.location.href = response.data.auth_url;
    } catch (error) {
      toast.error('Google Drive 연동 URL을 가져오는데 실패했습니다');
    }
  };

  const disconnectGoogleDrive = async () => {
    if (!confirm('Google Drive 연동을 해제하시겠습니까?')) return;

    try {
      await integrationAPI.disconnectGoogleDrive();
      toast.success('Google Drive 연동이 해제되었습니다');
      loadIntegrations();
    } catch (error) {
      toast.error('연동 해제에 실패했습니다');
    }
  };

  const connectGitHub = async () => {
    try {
      const response = await integrationAPI.getGitHubAuthUrl();
      window.location.href = response.data.auth_url;
    } catch (error) {
      toast.error('GitHub 연동 URL을 가져오는데 실패했습니다');
    }
  };

  const disconnectGitHub = async () => {
    if (!confirm('GitHub 연동을 해제하시겠습니까?')) return;

    try {
      await integrationAPI.disconnectGitHub();
      toast.success('GitHub 연동이 해제되었습니다');
      loadIntegrations();
    } catch (error) {
      toast.error('연동 해제에 실패했습니다');
    }
  };

  const verifyVelogUsername = async () => {
    if (!velogUsername.trim()) {
      toast.error('Velog 사용자명을 입력해주세요');
      return;
    }

    try {
      await authAPI.verifyVelogUsername(velogUsername);
      toast.success('Velog 사용자명이 확인되었습니다!');
    } catch (error) {
      toast.error('Velog 사용자를 찾을 수 없습니다');
    }
  };

  if (isLoading) {
    return (
      <DashboardLayout>
        <div className="text-center py-12">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto"></div>
        </div>
      </DashboardLayout>
    );
  }

  return (
    <DashboardLayout>
      <div className="space-y-6">
        <div>
          <h1 className="text-3xl font-bold">설정</h1>
          <p className="text-gray-600 dark:text-gray-400 mt-1">
            백업 연동 및 계정 설정을 관리하세요
          </p>
        </div>

        {/* Velog Username */}
        <div className="card">
          <h2 className="text-xl font-bold mb-4">Velog 계정</h2>
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium mb-2">
                Velog 사용자명
              </label>
              <div className="flex gap-2">
                <input
                  type="text"
                  className="input flex-1"
                  placeholder="@username"
                  value={velogUsername}
                  onChange={(e) => setVelogUsername(e.target.value)}
                />
                <button
                  onClick={verifyVelogUsername}
                  className="btn btn-primary"
                >
                  확인
                </button>
              </div>
              <p className="text-sm text-gray-500 mt-1">
                백업할 Velog 계정의 사용자명을 입력하세요
              </p>
            </div>
          </div>
        </div>

        {/* Google Drive Integration */}
        <div className="card">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center space-x-3">
              <Cloud className="text-primary-600" size={32} />
              <div>
                <h2 className="text-xl font-bold">Google Drive</h2>
                <p className="text-sm text-gray-600 dark:text-gray-400">
                  포스트를 Google Drive에 백업
                </p>
              </div>
            </div>
            {integrations?.google_drive_enabled ? (
              <span className="flex items-center space-x-1 text-green-600">
                <Check size={20} />
                <span className="font-semibold">연결됨</span>
              </span>
            ) : (
              <span className="flex items-center space-x-1 text-gray-400">
                <X size={20} />
                <span className="font-semibold">미연결</span>
              </span>
            )}
          </div>

          {integrations?.google_drive_enabled ? (
            <div className="bg-green-50 dark:bg-green-900/20 p-4 rounded-lg">
              <p className="text-sm text-green-800 dark:text-green-200 mb-3">
                Google Drive가 연결되어 있습니다. 백업 폴더 ID: {integrations.google_folder_id}
              </p>
              <button
                onClick={disconnectGoogleDrive}
                className="btn btn-secondary"
              >
                연동 해제
              </button>
            </div>
          ) : (
            <button
              onClick={connectGoogleDrive}
              className="btn btn-primary"
            >
              Google Drive 연결하기
            </button>
          )}
        </div>

        {/* GitHub Integration */}
        <div className="card">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center space-x-3">
              <Github className="text-primary-600" size={32} />
              <div>
                <h2 className="text-xl font-bold">GitHub</h2>
                <p className="text-sm text-gray-600 dark:text-gray-400">
                  포스트를 GitHub 저장소에 백업
                </p>
              </div>
            </div>
            {integrations?.github_enabled ? (
              <span className="flex items-center space-x-1 text-green-600">
                <Check size={20} />
                <span className="font-semibold">연결됨</span>
              </span>
            ) : (
              <span className="flex items-center space-x-1 text-gray-400">
                <X size={20} />
                <span className="font-semibold">미연결</span>
              </span>
            )}
          </div>

          {integrations?.github_enabled ? (
            <div className="bg-green-50 dark:bg-green-900/20 p-4 rounded-lg">
              <p className="text-sm text-green-800 dark:text-green-200 mb-1">
                GitHub 저장소가 연결되어 있습니다.
              </p>
              <a
                href={integrations.github_repo_url}
                target="_blank"
                rel="noopener noreferrer"
                className="text-primary-600 hover:underline text-sm"
              >
                {integrations.github_repo_url}
              </a>
              <div className="mt-3">
                <button
                  onClick={disconnectGitHub}
                  className="btn btn-secondary"
                >
                  연동 해제
                </button>
              </div>
            </div>
          ) : (
            <button
              onClick={connectGitHub}
              className="btn btn-primary"
            >
              GitHub 연결하기
            </button>
          )}
        </div>

        {/* Backup Settings */}
        <div className="card">
          <h2 className="text-xl font-bold mb-4">백업 설정</h2>
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="font-medium">자동 백업</p>
                <p className="text-sm text-gray-600 dark:text-gray-400">
                  매일 자동으로 백업을 수행합니다
                </p>
              </div>
              <label className="relative inline-flex items-center cursor-pointer">
                <input
                  type="checkbox"
                  className="sr-only peer"
                  checked={integrations?.auto_backup_enabled}
                  onChange={async (e) => {
                    try {
                      await integrationAPI.updateIntegrations({
                        auto_backup_enabled: e.target.checked
                      });
                      toast.success('설정이 저장되었습니다');
                      loadIntegrations();
                    } catch (error) {
                      toast.error('설정 저장에 실패했습니다');
                    }
                  }}
                />
                <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-primary-300 dark:peer-focus:ring-primary-800 rounded-full peer dark:bg-gray-700 peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all dark:border-gray-600 peer-checked:bg-primary-600"></div>
              </label>
            </div>
          </div>
        </div>
      </div>
    </DashboardLayout>
  );
}
