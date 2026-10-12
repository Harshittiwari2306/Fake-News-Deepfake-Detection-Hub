import axios from 'axios';

const getBaseUrl = (): string => {
  let url = (import.meta.env.VITE_API_URL || '').trim();
  if (!url) {
    return 'http://127.0.0.1:8000/api/v1';
  }
  // Remove trailing slashes and spaces
  url = url.replace(/\/+$/, '');
  
  // If user passed root url (e.g. https://xxx.onrender.com), append /api/v1 automatically
  if (!url.endsWith('/api/v1')) {
    url = `${url}/api/v1`;
  }
  return url;
};

export const API_BASE_URL = getBaseUrl();

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 60000, // 60s timeout to allow Render free tier instances to spin up
  headers: {
    'Content-Type': 'application/json',
  },
});

// Intercept to add token if exists
apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('truthguard_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export interface AnalysisResult {
  id?: number;
  analysis_type: string;
  prediction: string;
  confidence: number;
  risk_level: 'Low' | 'Medium' | 'High' | string;
  model_name: string;
  explanation: string;
  key_factors?: string[];
  metadata?: Record<string, any>;
  created_at?: string;
}

export interface FactCheckSource {
  title: string;
  source_name: string;
  url?: string;
  stance: string;
  snippet: string;
}

export interface FactCheckResponse {
  claim: string;
  verdict: string;
  confidence: number;
  summary: string;
  sources: FactCheckSource[];
  recommendation: string;
}

export interface DashboardStats {
  total_analyses: number;
  text_count: number;
  media_count: number;
  flagged_misleading: number;
  authentic_rate: number;
  recent_analyses: AnalysisResult[];
}

export const api = {
  // Text analysis
  analyzeText: async (params: { text: string; headline?: string; source_url?: string }): Promise<AnalysisResult> => {
    const res = await apiClient.post<AnalysisResult>('/analyze/text', params);
    return res.data;
  },

  // Image analysis
  analyzeImage: async (file: File): Promise<AnalysisResult> => {
    const formData = new FormData();
    formData.append('file', file);
    const res = await apiClient.post<AnalysisResult>('/analyze/image', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return res.data;
  },

  // Video analysis
  analyzeVideo: async (file: File): Promise<AnalysisResult> => {
    const formData = new FormData();
    formData.append('file', file);
    const res = await apiClient.post<AnalysisResult>('/analyze/video', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return res.data;
  },

  // Audio analysis
  analyzeAudio: async (file: File): Promise<AnalysisResult> => {
    const formData = new FormData();
    formData.append('file', file);
    const res = await apiClient.post<AnalysisResult>('/analyze/audio', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return res.data;
  },

  // Fact check
  factCheck: async (params: { claim: string; context?: string }): Promise<FactCheckResponse> => {
    const res = await apiClient.post<FactCheckResponse>('/factcheck', params);
    return res.data;
  },

  // Dashboard stats
  getDashboardStats: async (): Promise<DashboardStats> => {
    const res = await apiClient.get<DashboardStats>('/dashboard/stats');
    return res.data;
  },

  // Analysis history
  getHistory: async (limit: number = 50): Promise<AnalysisResult[]> => {
    const res = await apiClient.get<AnalysisResult[]>(`/dashboard/history?limit=${limit}`);
    return res.data;
  },
};
