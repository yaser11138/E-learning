import axios from 'axios';

const API_URL = 'http://localhost:8000/api/v1';
const AUTH_URL = 'http://localhost:8000';

// Create axios instance with default config
const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Create auth instance with different base URL
const authApi = axios.create({
  baseURL: AUTH_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Token refresh logic
let isRefreshing = false;
let failedQueue = [];

const processQueue = (error, token = null) => {
  failedQueue.forEach(prom => {
    if (error) {
      prom.reject(error);
    } else {
      prom.resolve(token);
    }
  });
  failedQueue = [];
};

const refreshToken = async () => {
  try {
    const refreshToken = localStorage.getItem('refreshToken');
    if (!refreshToken) {
      throw new Error('No refresh token available');
    }

    const response = await authApi.post('/auth/token/refresh/', {
      refresh: refreshToken
    });

    const { access } = response.data;
    localStorage.setItem('token', access);
    return access;
  } catch (error) {
    // If refresh fails, clear tokens and redirect to login
    localStorage.removeItem('token');
    localStorage.removeItem('refreshToken');
    window.location.href = '/login';
    throw error;
  }
};

// Add request interceptor for authentication
const addAuthHeader = (config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
};

// Add response interceptor for token refresh
const handleResponseError = async (error) => {
  const originalRequest = error.config;

  // If error is not 401 or request has already been retried, reject
  if (error.response?.status !== 401 || originalRequest._retry) {
    return Promise.reject(error);
  }

  if (isRefreshing) {
    // If token refresh is in progress, queue the request
    return new Promise((resolve, reject) => {
      failedQueue.push({ resolve, reject });
    })
      .then(token => {
        originalRequest.headers.Authorization = `Bearer ${token}`;
        return api(originalRequest);
      })
      .catch(err => Promise.reject(err));
  }

  originalRequest._retry = true;
  isRefreshing = true;

  try {
    const newToken = await refreshToken();
    originalRequest.headers.Authorization = `Bearer ${newToken}`;
    processQueue(null, newToken);
    return api(originalRequest);
  } catch (error) {
    processQueue(error, null);
    return Promise.reject(error);
  } finally {
    isRefreshing = false;
  }
};

// Apply interceptors
api.interceptors.request.use(addAuthHeader);
authApi.interceptors.request.use(addAuthHeader);
api.interceptors.response.use(null, handleResponseError);
authApi.interceptors.response.use(null, handleResponseError);

// Auth API
export const authAPI = {
  login: (credentials) => authApi.post('auth/dj-rest-auth/login/', credentials),
  register: (userData) => authApi.post('auth/register/student/', userData),
  logout: () => authApi.post('auth/dj-rest-auth/logout/'),
  updateProfile: (data) => authApi.put('/auth/profile/', data),
  refreshToken: () => authApi.post('auth/dj-rest-auth/token/refresh/', {
    refresh: localStorage.getItem('refreshToken')
  }),
};

// Courses API
export const coursesAPI = {
  // Instructor endpoints
  getAllCourses: () => api.get('/content/courses/'),
  getCourseById: (id) => api.get(`/content/courses/${id}/`),
  createCourse: (courseData) => api.post('/content/courses/', courseData),
  updateCourse: (id, courseData) => api.put(`/content/courses/${id}/`, courseData),
  deleteCourse: (id) => api.delete(`/content/courses/${id}/`),
  
  // Student endpoints
  getEnrolledCourses: () => api.get('/student/courses/'),
  enrollInCourse: (courseId) => api.post(`/enrollment/enroll/${courseId}/`),
  getCourseProgress: (courseId) => api.get(`/student/courses/${courseId}/progress/`),
  
  // Content endpoints
  getCourseContent: (courseId) => api.get(`/content/courses/${courseId}/content/`),
  uploadContent: (courseId, contentData) => api.post(`/content/courses/${courseId}/content/`, contentData),
};

// User API
export const userAPI = {
  getProfile: () => authApi.get('/auth/profile/'),
  getDashboard: () => api.get('/student/dashboard/'),
};

export default api; 