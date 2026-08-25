import axios from 'axios';

const API_BASE = import.meta.env.VITE_API_URL || '';

// ── In-memory token store (immune to XSS) ─────────────────────────────────────
let _accessToken: string | null = null;

export function setAccessToken(token: string | null): void {
  _accessToken = token;
}

export function getAccessToken(): string | null {
  return _accessToken;
}

// ── Axios instance ─────────────────────────────────────────────────────────────
export const api = axios.create({
  baseURL: API_BASE,
  headers: { 'Content-Type': 'application/json' },
  withCredentials: true, // send httpOnly refresh cookie on every request
});

// Attach access token from memory
api.interceptors.request.use((config) => {
  if (_accessToken) config.headers.Authorization = `Bearer ${_accessToken}`;
  return config;
});

// ── Refresh-and-retry interceptor ─────────────────────────────────────────────
let _isRefreshing = false;
type Resolver = { resolve: (token: string) => void; reject: (err: unknown) => void };
let _refreshQueue: Resolver[] = [];

api.interceptors.response.use(
  (r) => r,
  async (error) => {
    // Paid actions (issue navigator, document generate, lawyer match, research search)
    // 403 with this shape when the account isn't approved yet — send the user to pay/
    // request approval instead of showing a raw error. Endpoints that stream via plain
    // fetch() (not this axios instance) check for this same shape inline.
    if (error.response?.status === 403 && error.response?.data?.detail?.error === 'access_pending') {
      window.dispatchEvent(new Event('lawgic:access-pending'));
      return Promise.reject(error);
    }

    const original = error.config;

    // Only retry on 401; skip refresh endpoint itself to avoid infinite loops
    if (
      error.response?.status !== 401 ||
      original._retry ||
      original.url?.includes('/auth/refresh')
    ) {
      return Promise.reject(error);
    }

    original._retry = true;

    if (_isRefreshing) {
      // Queue this request until the in-flight refresh completes
      return new Promise<string>((resolve, reject) => {
        _refreshQueue.push({ resolve, reject });
      }).then((token) => {
        original.headers.Authorization = `Bearer ${token}`;
        return api(original);
      });
    }

    _isRefreshing = true;

    try {
      const res = await axios.post(
        `${API_BASE}/api/v1/auth/refresh`,
        {},
        { withCredentials: true }
      );
      const newToken: string = res.data.access_token;
      setAccessToken(newToken);
      _refreshQueue.forEach((q) => q.resolve(newToken));
      _refreshQueue = [];
      original.headers.Authorization = `Bearer ${newToken}`;
      return api(original);
    } catch (refreshErr) {
      _refreshQueue.forEach((q) => q.reject(refreshErr));
      _refreshQueue = [];
      setAccessToken(null);
      window.dispatchEvent(new Event('lawgic:logout'));
      return Promise.reject(error);
    } finally {
      _isRefreshing = false;
    }
  }
);

// ── API modules ────────────────────────────────────────────────────────────────

export const authAPI = {
  register: (data: unknown) => api.post('/api/v1/auth/register', data).then((r) => r.data),
  login: (data: unknown) => api.post('/api/v1/auth/login', data).then((r) => r.data),
  me: () => api.get('/api/v1/auth/me').then((r) => r.data),
  googleAuth: (token: string) => api.post('/api/v1/auth/google', { token }).then((r) => r.data),
  requestOtp: (phone: string) => api.post('/api/v1/auth/otp/request', { phone }).then((r) => r.data),
  verifyOtp: (phone: string, otp: string, full_name?: string) =>
    api.post('/api/v1/auth/otp/verify', { phone, otp, full_name }).then((r) => r.data),
  // withCredentials already set on instance — cookie auto-sent
  refresh: () => api.post('/api/v1/auth/refresh').then((r) => r.data),
  logout: () => api.post('/api/v1/auth/logout').then((r) => r.data),
};

export const accessAPI = {
  status: () => api.get('/api/v1/access/status').then((r) => r.data),
  paymentInfo: () => api.get('/api/v1/access/payment-info').then((r) => r.data),
  submitRequest: (data: { utr_reference?: string; note?: string }) =>
    api.post('/api/v1/access/requests', data).then((r) => r.data),
  adminListRequests: (status = 'pending') =>
    api.get(`/api/v1/access/admin/requests?status=${status}`).then((r) => r.data),
  adminApprove: (id: number) => api.post(`/api/v1/access/admin/requests/${id}/approve`).then((r) => r.data),
  adminReject: (id: number) => api.post(`/api/v1/access/admin/requests/${id}/reject`).then((r) => r.data),
};

export const casesAPI = {
  list: (page = 1, limit = 20) =>
    api.get(`/api/v1/cases?skip=${(page - 1) * limit}&limit=${limit}`).then((r) => r.data),
  create: (data: unknown) => api.post('/api/v1/cases', data).then((r) => r.data),
  get: (id: number) => api.get(`/api/v1/cases/${id}`).then((r) => r.data),
  update: (id: number, data: unknown) => api.put(`/api/v1/cases/${id}`, data).then((r) => r.data),
  delete: (id: number) => api.delete(`/api/v1/cases/${id}`),
};

export const documentsAPI = {
  list: () => api.get('/api/v1/documents').then((r) => r.data),
  get: (id: number) => api.get(`/api/v1/documents/${id}`).then((r) => r.data),
  delete: (id: number) => api.delete(`/api/v1/documents/${id}`),
  getTemplates: () => api.get('/api/v1/documents/templates').then((r) => r.data),
  getTemplate: (id: string) => api.get(`/api/v1/documents/templates/${id}`).then((r) => r.data),
};

export const lawyersAPI = {
  list: (params?: unknown) => api.get('/api/v1/lawyers', { params }).then((r) => r.data),
  get: (id: number) => api.get(`/api/v1/lawyers/${id}`).then((r) => r.data),
  match: (data: unknown) => api.post('/api/v1/lawyers/match', data).then((r) => r.data),
};

export const researchAPI = {
  search: (data: unknown) => api.post('/api/v1/research/search', data).then((r) => r.data),
};

export const educationAPI = {
  getCourses: () => api.get('/api/v1/education/courses').then((r) => r.data),
  getCourse: (id: string) => api.get(`/api/v1/education/courses/${id}`).then((r) => r.data),
  submitQuiz: (id: string, answers: number[]) =>
    api.post(`/api/v1/education/courses/${id}/quiz/submit`, { answers }).then((r) => r.data),
};

export const chatAPI = {
  message: (data: unknown) => api.post('/api/v1/chat/message', data).then((r) => r.data),
  history: (sessionId: string) => api.get(`/api/v1/chat/history/${sessionId}`).then((r) => r.data),
};

export const paymentsAPI = {
  plans: () => api.get('/api/v1/payments/plans').then((r) => r.data),
  subscription: () => api.get('/api/v1/payments/subscription').then((r) => r.data),
  createOrder: (plan: string) => api.post('/api/v1/payments/create-order', { plan }).then((r) => r.data),
  verify: (data: { razorpay_order_id: string; razorpay_payment_id: string; razorpay_signature: string }) =>
    api.post('/api/v1/payments/verify', data).then((r) => r.data),
  cancel: () => api.post('/api/v1/payments/cancel').then((r) => r.data),
};

export const generateSessionId = () => Math.random().toString(36).slice(2) + Date.now().toString(36);

export const getSSEUrl = (path: string) => `${API_BASE}${path}`;

export const getWSUrl = (sessionId: string, token: string) => {
  // In dev, API_BASE is empty so fall back to window.location.host (proxied by Vite).
  // In production, API_BASE is the Render backend URL (https://…); convert to wss://.
  if (API_BASE) {
    const wsBase = API_BASE.replace(/^https?/, (p: string) => (p === 'https' ? 'wss' : 'ws'));
    return `${wsBase}/api/v1/chat/ws/${sessionId}?token=${token}`;
  }
  const wsProto = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
  return `${wsProto}//${window.location.host}/api/v1/chat/ws/${sessionId}?token=${token}`;
};
