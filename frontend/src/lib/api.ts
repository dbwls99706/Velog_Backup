import axios from 'axios';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
const API_V1 = `${API_URL}/api/v1`;

export const api = axios.create({
  baseURL: API_V1,
  headers: {
    'Content-Type': 'application/json',
  },
});

// 요청 인터셉터 - 토큰 자동 추가
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// 응답 인터셉터 - 에러 처리
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // 토큰 만료 시 로그아웃
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// Auth API
export const authAPI = {
  register: (data: { email: string; password: string; full_name?: string; velog_username?: string }) =>
    api.post('/auth/register', data),

  login: (data: { email: string; password: string }) =>
    api.post('/auth/login', data),

  getCurrentUser: () => api.get('/auth/me'),

  verifyVelogUsername: (username: string) =>
    api.post('/auth/verify-velog', null, { params: { velog_username: username } }),
};

// Integration API
export const integrationAPI = {
  getIntegrations: () => api.get('/integrations/'),

  updateIntegrations: (data: any) => api.patch('/integrations/', data),

  getGoogleDriveAuthUrl: () => api.get('/integrations/google-drive/auth-url'),

  connectGoogleDrive: (code: string) =>
    api.post('/integrations/google-drive/connect', { code }),

  disconnectGoogleDrive: () => api.delete('/integrations/google-drive/disconnect'),

  getGitHubAuthUrl: () => api.get('/integrations/github/auth-url'),

  connectGitHub: (code: string, repo_name?: string) =>
    api.post('/integrations/github/connect', { code, repo_name }),

  disconnectGitHub: () => api.delete('/integrations/github/disconnect'),
};

// Backup API
export const backupAPI = {
  triggerBackup: (destination: string, force: boolean = false) =>
    api.post('/backup/trigger', { destination, force }),

  getBackupLogs: (limit: number = 20) =>
    api.get('/backup/logs', { params: { limit } }),

  getBackupStats: () => api.get('/backup/stats'),
};
