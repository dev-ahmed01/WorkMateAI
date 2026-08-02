// Typed Fetch Client Wrapper for WorkMate AI FastAPI Endpoints

export interface ApiErrorPayload {
  error_code: string;
  message: string;
  details?: Record<string, any>;
}

export class ApiError extends Error {
  error_code: string;
  details?: Record<string, any>;

  constructor(payload: ApiErrorPayload, public status: number) {
    super(payload.message);
    this.name = 'ApiError';
    this.error_code = payload.error_code || 'UNKNOWN_ERROR';
    this.details = payload.details;
  }
}

// Data Transfer Object Definitions matching Backend Schemas
export interface Citation {
  document_id: string;
  document_title: string;
  version_number: number;
  chunk_id: string;
  excerpt: string;
}

export interface CopilotResponse {
  message_id: string;
  answer: string;
  citations: Citation[];
  confidence_score: number;
  is_grounded: boolean;
  requires_escalation: boolean;
  active_sop_id?: string;
  active_step_number?: number;
  active_step_title?: string;
}

export interface KnowledgeDocument {
  id: string;
  title: string;
  department_id: string;
  category: string;
  status: 'DRAFT' | 'PROCESSING' | 'PUBLISHED' | 'ARCHIVED';
  current_version: number;
  created_at: string;
  updated_at: string;
}

export interface MetricCardData {
  title: string;
  value: string | number;
  change?: string;
  trend?: 'up' | 'down' | 'neutral';
}

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000/api/v1';

export async function apiClient<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const token = typeof window !== 'undefined' ? localStorage.getItem('token') : null;

  const headers: Record<string, string> = {
    ...(options.headers as Record<string, string>),
  };

  if (token) {
    headers['Authorization'] = Bearer \;
  }

  if (!(options.body instanceof FormData)) {
    headers['Content-Type'] = 'application/json';
  }

  const response = await fetch(\\, {
    ...options,
    headers,
  });

  if (!response.ok) {
    let errorPayload: ApiErrorPayload;
    try {
      errorPayload = await response.json();
    } catch {
      errorPayload = {
        error_code: 'HTTP_ERROR',
        message: response.statusText || 'An unexpected error occurred.',
      };
    }
    throw new ApiError(errorPayload, response.status);
  }

  return response.json() as Promise<T>;
}
