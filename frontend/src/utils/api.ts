const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api';

export const api = {
  get: async (endpoint: string) => request(endpoint, { method: 'GET' }),
  post: async (endpoint: string, data?: any) => request(endpoint, { method: 'POST', body: JSON.stringify(data) }),
  put: async (endpoint: string, data: any) => request(endpoint, { method: 'PUT', body: JSON.stringify(data) }),
  delete: async (endpoint: string) => request(endpoint, { method: 'DELETE' }),
};

async function request(endpoint: string, options: RequestInit = {}) {
  const token = localStorage.getItem('access_token');
  
  const headers = new Headers(options.headers || {});
  headers.set('Content-Type', 'application/json');
  if (token) {
    headers.set('Authorization', `Bearer ${token}`);
  }

  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    ...options,
    headers,
  });

  if (!response.ok) {
    if (response.status === 401) {
      localStorage.removeItem('access_token');
      localStorage.removeItem('user');
      window.location.href = '/login';
    }
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.message || 'An error occurred with the request');
  }

  if (response.status !== 204) {
    return response.json();
  }
}
