import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8080';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export interface UserPreferences {
  topics: string[];
}

export interface RegisterRequest {
  email: string;
  preferences: UserPreferences;
  timezone: string;
  briefing_time: string;
}

export interface QueryRequest {
  email: string;
  query: string;
  max_results?: number;
}

export interface Article {
  title: string;
  url: string;
  summary: string;
}

export interface QueryResponse {
  success: boolean;
  query: string;
  articles: Article[];
  total_found: number;
  total_returned: number;
  errors?: string[];
}

export interface MetricsResponse {
  email: string;
  total_articles_sent: number;
  last_briefing_at: string | null;
  topics: string[];
  created_at: string;
}

export interface UserResponse {
  email: string;
  preferences: {
    topics: string[];
  };
  timezone: string;
  briefing_time: string;
  created_at: string;
}

export interface UpdatePreferencesRequest {
  preferences?: UserPreferences;
  timezone?: string;
  briefing_time?: string;
}

export const api = {
  async register(data: RegisterRequest) {
    const response = await apiClient.post('/api/register', data);
    return response.data;
  },

  async query(data: QueryRequest): Promise<QueryResponse> {
    const response = await apiClient.post('/api/query', data);
    return response.data;
  },

  async getMetrics(email: string): Promise<MetricsResponse> {
    const response = await apiClient.get(`/api/metrics/${email}`);
    return response.data;
  },

  async getAllUsers(): Promise<UserResponse[]> {
    const response = await apiClient.get('/api/users');
    return response.data;
  },

  async getPreferences(email: string): Promise<UserResponse> {
    const response = await apiClient.get(`/api/preferences/${email}`);
    return response.data;
  },

  async updatePreferences(email: string, data: UpdatePreferencesRequest) {
    const response = await apiClient.put(`/api/preferences/${email}`, data);
    return response.data;
  },

  async deleteUser(email: string) {
    const response = await apiClient.delete(`/api/preferences/${email}`);
    return response.data;
  },

  async health() {
    const response = await apiClient.get('/api/health');
    return response.data;
  },
};

export default apiClient;
