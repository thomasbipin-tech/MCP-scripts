// Small typed fetch wrapper for the DealProof API. No axios, no state libs —
// just fetch + localStorage, per the frontend build constraints.

export const API_BASE = (import.meta.env.VITE_API_BASE as string | undefined) ?? '/api'

const TOKEN_KEY = 'dp_token'

export function getToken(): string | null {
  return localStorage.getItem(TOKEN_KEY)
}

export function setToken(token: string): void {
  localStorage.setItem(TOKEN_KEY, token)
}

export function clearToken(): void {
  localStorage.removeItem(TOKEN_KEY)
}

export class ApiError extends Error {
  status: number
  constructor(status: number, message: string) {
    super(message)
    this.name = 'ApiError'
    this.status = status
  }
}

function redirectToLogin(): void {
  clearToken()
  if (window.location.hash !== '#/login') {
    window.location.hash = '#/login'
  }
}

function authHeaders(extra?: Record<string, string>): Record<string, string> {
  const token = getToken()
  return {
    ...(extra ?? {}),
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
  }
}

async function extractErrorMessage(res: Response): Promise<string> {
  try {
    const body = await res.json()
    if (body && typeof body.detail === 'string') return body.detail
    if (body && body.detail) return JSON.stringify(body.detail)
  } catch {
    // response wasn't JSON — fall through to the generic message
  }
  return `Request failed (${res.status})`
}

async function handleResponse<T>(res: Response): Promise<T> {
  if (res.status === 401) {
    redirectToLogin()
    throw new ApiError(401, 'Unauthorized')
  }
  if (!res.ok) {
    throw new ApiError(res.status, await extractErrorMessage(res))
  }
  if (res.status === 204) {
    return undefined as T
  }
  const text = await res.text()
  return (text ? JSON.parse(text) : undefined) as T
}

export async function apiGet<T>(path: string): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, { headers: authHeaders() })
  return handleResponse<T>(res)
}

export async function apiPost<T>(path: string, body?: unknown): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    method: 'POST',
    headers: authHeaders(body === undefined ? undefined : { 'Content-Type': 'application/json' }),
    body: body === undefined ? undefined : JSON.stringify(body),
  })
  return handleResponse<T>(res)
}

export async function apiDelete<T>(path: string): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, { method: 'DELETE', headers: authHeaders() })
  return handleResponse<T>(res)
}

export async function apiPostForm<T>(path: string, form: FormData): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    method: 'POST',
    // Do NOT set Content-Type — the browser sets the multipart boundary.
    headers: authHeaders(),
    body: form,
  })
  return handleResponse<T>(res)
}

// For binary responses (the PDF export) that still need the auth header, so a
// plain <a href> won't work.
export async function apiGetBlob(path: string): Promise<Blob> {
  const res = await fetch(`${API_BASE}${path}`, { headers: authHeaders() })
  if (res.status === 401) {
    redirectToLogin()
    throw new ApiError(401, 'Unauthorized')
  }
  if (!res.ok) {
    throw new ApiError(res.status, await extractErrorMessage(res))
  }
  return res.blob()
}
