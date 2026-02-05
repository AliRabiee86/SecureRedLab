import api, { handleApiError } from './api';
import type { Scan, Attack, Vulnerability, Report, User, ScanConfig, AttackConfig } from '../types';

// ============================================
// AUTHENTICATION ENDPOINTS
// ============================================
export const authApi = {
  login: async (email: string, password: string): Promise<{ token: string; user: User }> => {
    try {
      const response = await api.post('/auth/login', { email, password });
      return response.data;
    } catch (error) {
      throw handleApiError(error);
    }
  },

  logout: async (): Promise<void> => {
    try {
      await api.post('/auth/logout');
      localStorage.removeItem('auth_token');
    } catch (error) {
      throw handleApiError(error);
    }
  },

  getCurrentUser: async (): Promise<User> => {
    try {
      const response = await api.get('/auth/me');
      return response.data;
    } catch (error) {
      throw handleApiError(error);
    }
  },
};

// ============================================
// SCANS ENDPOINTS
// ============================================
export const scansApi = {
  getAll: async (): Promise<Scan[]> => {
    try {
      const response = await api.get('/scans');
      return response.data;
    } catch (error) {
      throw handleApiError(error);
    }
  },

  getById: async (id: string): Promise<Scan> => {
    try {
      const response = await api.get(`/scans/${id}`);
      return response.data;
    } catch (error) {
      throw handleApiError(error);
    }
  },

  create: async (config: ScanConfig): Promise<Scan> => {
    try {
      const response = await api.post('/scans', config);
      return response.data;
    } catch (error) {
      throw handleApiError(error);
    }
  },

  delete: async (id: string): Promise<void> => {
    try {
      await api.delete(`/scans/${id}`);
    } catch (error) {
      throw handleApiError(error);
    }
  },

  stop: async (id: string): Promise<Scan> => {
    try {
      const response = await api.post(`/scans/${id}/stop`);
      return response.data;
    } catch (error) {
      throw handleApiError(error);
    }
  },
};

// ============================================
// ATTACKS ENDPOINTS
// ============================================
export const attacksApi = {
  getAll: async (): Promise<Attack[]> => {
    try {
      const response = await api.get('/attacks');
      return response.data;
    } catch (error) {
      throw handleApiError(error);
    }
  },

  getById: async (id: string): Promise<Attack> => {
    try {
      const response = await api.get(`/attacks/${id}`);
      return response.data;
    } catch (error) {
      throw handleApiError(error);
    }
  },

  create: async (config: AttackConfig): Promise<Attack> => {
    try {
      const response = await api.post('/attacks', config);
      return response.data;
    } catch (error) {
      throw handleApiError(error);
    }
  },

  delete: async (id: string): Promise<void> => {
    try {
      await api.delete(`/attacks/${id}`);
    } catch (error) {
      throw handleApiError(error);
    }
  },

  stop: async (id: string): Promise<Attack> => {
    try {
      const response = await api.post(`/attacks/${id}/stop`);
      return response.data;
    } catch (error) {
      throw handleApiError(error);
    }
  },
};

// ============================================
// VULNERABILITIES ENDPOINTS
// ============================================
export const vulnerabilitiesApi = {
  getAll: async (): Promise<Vulnerability[]> => {
    try {
      const response = await api.get('/vulnerabilities');
      return response.data;
    } catch (error) {
      throw handleApiError(error);
    }
  },

  getByScan: async (scanId: string): Promise<Vulnerability[]> => {
    try {
      const response = await api.get(`/scans/${scanId}/vulnerabilities`);
      return response.data;
    } catch (error) {
      throw handleApiError(error);
    }
  },

  getById: async (id: string): Promise<Vulnerability> => {
    try {
      const response = await api.get(`/vulnerabilities/${id}`);
      return response.data;
    } catch (error) {
      throw handleApiError(error);
    }
  },
};

// ============================================
// REPORTS ENDPOINTS
// ============================================
export const reportsApi = {
  getAll: async (): Promise<Report[]> => {
    try {
      const response = await api.get('/reports');
      return response.data;
    } catch (error) {
      throw handleApiError(error);
    }
  },

  getById: async (id: string): Promise<Report> => {
    try {
      const response = await api.get(`/reports/${id}`);
      return response.data;
    } catch (error) {
      throw handleApiError(error);
    }
  },

  generate: async (scanId: string): Promise<Report> => {
    try {
      const response = await api.post(`/reports/generate/${scanId}`);
      return response.data;
    } catch (error) {
      throw handleApiError(error);
    }
  },

  download: async (id: string, format: 'pdf' | 'json' | 'html'): Promise<Blob> => {
    try {
      const response = await api.get(`/reports/${id}/download?format=${format}`, {
        responseType: 'blob',
      });
      return response.data;
    } catch (error) {
      throw handleApiError(error);
    }
  },
};

// ============================================
// DASHBOARD ENDPOINTS
// ============================================
export const dashboardApi = {
  getStats: async () => {
    try {
      const response = await api.get('/dashboard/stats');
      return response.data;
    } catch (error) {
      throw handleApiError(error);
    }
  },

  getRecentActivity: async () => {
    try {
      const response = await api.get('/dashboard/activity');
      return response.data;
    } catch (error) {
      throw handleApiError(error);
    }
  },
};
