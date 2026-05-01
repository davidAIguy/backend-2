import axios from 'axios';

const API_URL = (process.env.NEXT_PUBLIC_API_URL || 'https://voice-ai-platform-production-1048.up.railway.app').replace(/\/$/, '');

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  withCredentials: false,
  validateStatus: (status) => status < 500,
});

// Types
export interface Agent {
  id: string;
  name: string;
  description?: string;
  system_prompt: string;
  voice: string;
  llm_model: string;
  phone_number?: string;
  tools: any[];
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface Call {
  id: string;
  from_number: string;
  to_number: string;
  direction: 'inbound' | 'outbound';
  status: 'ringing' | 'in_progress' | 'completed' | 'failed' | 'no_answer' | 'busy';
  duration: number;
  cost: number;
  agent_id?: string;
  created_at: string;
}

export interface Transcript {
  id: string;
  call_id: string;
  transcript_text?: string;
  messages: any[];
  total_messages: number;
  duration: number;
}

export interface CostSummary {
  total_cost: number;
  total_calls: number;
  total_duration: number;
  avg_cost_per_call: number;
  avg_duration: number;
  avg_duration_per_call: number;
  twilio_cost: number;
  livekit_cost: number;
  llm_cost: number;
  transcription_cost: number;
  tool_cost: number;
}

export interface Tool {
  id: string;
  name: string;
  description?: string;
  type: string;
  config: any;
  parameters: any;
  is_active: boolean;
  total_calls: string;
}

// Agents API
export const agentsApi = {
  list: () => api.get<Agent[]>('/api/agents/'),
  get: (id: string) => api.get<Agent>(`/api/agents/${id}/`),
  create: (data: Partial<Agent>) => api.post<Agent>('/api/agents/', data),
  update: (id: string, data: Partial<Agent>) => api.put<Agent>(`/api/agents/${id}/`, data),
  delete: (id: string) => api.delete(`/api/agents/${id}/`),
  assignPhone: (id: string, phoneNumber: string) => 
    api.post<Agent>(`/api/agents/${id}/phone/`, null, { params: { phone_number: phoneNumber } }),
};

// Calls API
export const callsApi = {
  list: (params?: { page?: number; page_size?: number; agent_id?: string }) => 
    api.get<{ items: Call[]; total: number; page: number; page_size: number; pages: number }>('/api/calls/', { params }),
  get: (id: string) => api.get<Call>(`/api/calls/${id}/`),
  getWithTranscript: (id: string) => api.get(`/api/calls/${id}/full/`),
};

// Transcripts API
export const transcriptsApi = {
  getByCall: (callId: string) => api.get<Transcript>(`/api/transcripts/call/${callId}/`),
  get: (id: string) => api.get<Transcript>(`/api/transcripts/${id}/`),
};

// Costs API
export const costsApi = {
  getSummary: (params?: { agent_id?: string; start_date?: string; end_date?: string }) =>
    api.get<CostSummary>('/api/costs/summary/', { params }),
  getByAgent: () => api.get('/api/costs/by-agent/'),
  getByPeriod: (period: string) => api.get('/api/costs/by-period/', { params: { period } }),
};

// Tools API
export const toolsApi = {
  list: () => api.get<Tool[]>('/api/tools/'),
  get: (id: string) => api.get<Tool>(`/api/tools/${id}/`),
  create: (data: Partial<Tool>) => api.post<Tool>('/api/tools/', data),
  update: (id: string, data: Partial<Tool>) => api.put<Tool>(`/api/tools/${id}/`, data),
  delete: (id: string) => api.delete(`/api/tools/${id}/`),
};

export default api;
