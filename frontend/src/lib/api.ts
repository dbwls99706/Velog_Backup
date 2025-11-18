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
  googleLogin: (token: string) => api.post('/auth/google', { token }),
  getCurrentUser: () => api.get('/user/me'),
  verifyVelog: (username: string) => api.post('/user/velog/verify', { username }),
};

export const googleAPI = {
  getAuthUrl: () => api.get('/google/auth-url'),
  connect: (code: string) => api.post('/google/connect', { code }),
  disconnect: () => api.delete('/google/disconnect'),
};

export const backupAPI = {
  trigger: (force: boolean = false) => api.post('/backup/trigger', { force }),
  getStats: () => api.get('/backup/stats'),
  getLogs: (limit: number = 20) => api.get(`/backup/logs?limit=${limit}`),
};
