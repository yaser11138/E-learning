import axios from 'axios';

const API_URL = 'http://localhost:8000/api/v1';
const AUTH_URL = 'http://localhost:8000';

// Create axios instance with default config
const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  withCredentials: true, // Important for cookies
});

// Create auth instance with different base URL
const authApi = axios.create({
  baseURL: AUTH_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  withCredentials: true, // Important for cookies
});

// Remove token refresh logic since it's handled by cookies
const addAuthHeader = (config) => {
  return config;
};

// Add response interceptor for handling errors
const handleResponseError = async (error) => {
  if (error.response?.status === 401) {
    // Redirect to login on authentication error
    window.location.href = '/login';
  }
  return Promise.reject(error);
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
  getDashboard: () => api.get('/dashboard/'),
};

export default api; 