const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? 'http://localhost:8000/api';

type ErrorPayload = { detail?: unknown };

export class ApiError extends Error {
  constructor(message: string, readonly status: number) {
    super(message);
    this.name = 'ApiError';
  }
}

function messageForStatus(status: number, detail: unknown): string {
  if (status === 401) return 'Your session is missing or expired. Please sign in again.';
  if (status === 403) return 'Your account is not permitted to perform this action.';
  if (status === 409 && typeof detail === 'string') return detail;
  if (status === 404 && typeof detail === 'string') return detail;
  if (status === 400 && typeof detail === 'string') return detail;
  if (status === 422) return 'Please check the submitted information and try again.';
  if (status >= 500) return 'The server could not complete the request. Please try again.';
  return typeof detail === 'string' ? detail : 'The request could not be completed.';
}

export async function apiRequest<T>(path: string, init?: RequestInit): Promise<T> {
  let response: Response;
  try {
    response = await fetch(`${API_BASE}${path}`, init);
  } catch {
    throw new ApiError('TurfMate API is unavailable. Check your connection and try again.', 0);
  }

  let payload: T & ErrorPayload;
  try {
    payload = await response.json() as T & ErrorPayload;
  } catch {
    if (!response.ok) {
      throw new ApiError(messageForStatus(response.status, undefined), response.status);
    }
    throw new ApiError('The server returned an unreadable response. Please try again.', response.status);
  }

  if (!response.ok) {
    throw new ApiError(messageForStatus(response.status, payload?.detail), response.status);
  }
  return payload;
}

export function apiErrorMessage(error: unknown, fallback: string): string {
  return error instanceof ApiError ? error.message : fallback;
}
