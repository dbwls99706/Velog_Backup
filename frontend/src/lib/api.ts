import axios from 'axios';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export const api = axios.create({
  baseURL: `${API_URL}/api/v1`,
  headers: {'Content-Type': 'application/json'},
});

// 토큰 인터셉터
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// 에러 인터셉터
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('access_token');
      window.location.href = '/';
    }
    return Promise.reject(error);
  }
);

export const authAPI = {
  getGitHubUrl: () => api.get('/auth/github/url'),
  gitHubCallback: (code: string, state?: string) => api.post('/auth/github/callback', { code, state }),
  getCurrentUser: () => api.get('/user/me'),
  verifyVelog: (username: string) => api.post('/user/velog/verify', { username }),
};

export const backupAPI = {
  trigger: (force: boolean = false) => api.post('/backup/trigger', { force }),
  getStats: () => api.get('/backup/stats'),
  getLogs: (limit: number = 20) => api.get(`/backup/logs?limit=${limit}`),
  downloadZip: () => api.get('/backup/download-zip', { responseType: 'blob' }),
};

export const postsAPI = {
  getAll: (page: number = 1, limit: number = 20) =>
    api.get(`/backup/posts?page=${page}&limit=${limit}`),
  getOne: (postId: number) => api.get(`/backup/posts/${postId}`),
  delete: (postId: number) => api.delete(`/backup/posts/${postId}`),
};

export const settingsAPI = {
  get: () => api.get('/user/settings'),
  update: (data: {
    github_repo?: string;
    github_sync_enabled?: boolean;
    email_notification_enabled?: boolean;
  }) => api.put('/user/settings', data),
  checkGitHubRepo: (name: string) => api.get(`/user/github/repo/check?name=${encodeURIComponent(name)}`),
};
