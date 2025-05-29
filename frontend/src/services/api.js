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
};

// Courses API
export const coursesAPI = {
  // Course Management
  getInstructorCourses: () => api.get('/content/courses/'),
  getCourse: (slug) => api.get(`/content/courses/${slug}/`),
  createCourse: (courseData) => {
    const formData = new FormData();
    Object.keys(courseData).forEach(key => {
      formData.append(key, courseData[key]);
    });
    return api.post('/content/courses/', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
  },
  updateCourse: (slug, courseData) => {
    const formData = new FormData();
    Object.keys(courseData).forEach(key => {
      formData.append(key, courseData[key]);
    });
    return api.patch(`/content/courses/${slug}/`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
  },
  deleteCourse: (slug) => api.delete(`/content/courses/${slug}/`),

  // Module Management
  getModules: (courseSlug) => api.get(`/content/course/${courseSlug}/modules/`),
  createModule: (courseSlug, moduleData) => api.post(`/content/course/${courseSlug}/modules/`, moduleData),
  updateModule: (moduleId, moduleData) => api.patch(`/content/modules/${moduleId}/`, moduleData),
  deleteModule: (moduleId) => api.delete(`/content/modules/${moduleId}/`),

  // Content Management
  getModuleContents: (moduleSlug) => api.get(`/content/modules/${moduleSlug}/contents/`),
  uploadContent: (moduleSlug, contentData) => {
    const formData = new FormData();
    Object.keys(contentData).forEach(key => {
      formData.append(key, contentData[key]);
    });
    return api.post(`/content/module/${moduleSlug}/contents/`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
  },
  updateContent: (contentId, contentData) => {
    const formData = new FormData();
    Object.keys(contentData).forEach(key => {
      formData.append(key, contentData[key]);
    });
    return api.patch(`/content/contents/${contentId}/`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
  },
  deleteContent: (contentId) => api.delete(`/content/contents/${contentId}/`),
  // Student endpoints
  getAllCourses: () => api.get('/student/courses/'),
  getCourseProgress: (courseId) => api.get(`/student/course/${courseId}/progress/`),
  updateContentProgress: (contentId, progressData) => api.post(`/student/content/${contentId}/progress/`, progressData),
};

// Enrollment API
export const enrollmentAPI = {
  // Student enrollment endpoints
  enrollInCourse: (courseSlug) => api.post(`/enrollment/courses/${courseSlug}/enroll/`),
  getStudentEnrollments: () => api.get('/enrollment/enrollments/'),
  
  // Instructor enrollment endpoints
  getInstructorEnrollments: () => api.get('/enrollment/instructor/enrollments/'),
  getCourseEnrollments: (courseSlug) => api.get(`/enrollment/instructor/courses/${courseSlug}/enrollments/`),
};

// User API
export const userAPI = {
  getProfile: () => authApi.get('/auth/profile/'),
  updateProfile: (profileData) => authApi.put('/auth/profile/', profileData),
  getDashboard: () => api.get('/dashboard/'),
};

export default api; 