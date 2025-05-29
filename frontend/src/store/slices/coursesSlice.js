import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import { coursesAPI } from '../../services/api';
import { enrollmentAPI } from '../../services/api';

const initialState = {
  courses: [],
  enrolledCourses: [],
  currentCourse: null,
  loading: false,
  error: null,
};

export const fetchCourses = createAsyncThunk(
  'courses/fetchAll',
  async (_, { rejectWithValue }) => {
    try {
      const response = await coursesAPI.getAllCourses();
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data?.message || 'Failed to fetch courses');
    }
  }
);

export const fetchInstructorCourses = createAsyncThunk(
  'courses/fetchInstructor',
  async (_, { rejectWithValue }) => {
    try {
      const response = await coursesAPI.getInstructorCourses();
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data?.message || 'Failed to fetch instructor courses');
    }
  }
);

export const fetchCourseById = createAsyncThunk(
  'courses/fetchById',
  async (slug, { rejectWithValue }) => {
    try {
      const response = await coursesAPI.getCourse(slug);
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data?.message || 'Failed to fetch course');
    }
  }
);

export const createCourse = createAsyncThunk(
  'courses/create',
  async (courseData, { rejectWithValue }) => {
    try {
      const response = await coursesAPI.createCourse(courseData);
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data?.message || 'Failed to create course');
    }
  }
);

export const updateCourse = createAsyncThunk(
  'courses/update',
  async ({ slug, courseData }, { rejectWithValue }) => {
    try {
      const response = await coursesAPI.updateCourse(slug, courseData);
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data?.message || 'Failed to update course');
    }
  }
);

export const fetchEnrolledCourses = createAsyncThunk(
  'courses/fetchEnrolled',
  async (_, { rejectWithValue }) => {
    try {
      const response = await enrollmentAPI.getStudentEnrollments();
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data?.message || 'Failed to fetch enrolled courses');
    }
  }
);

export const enrollInCourse = createAsyncThunk(
  'courses/enroll',
  async (courseId, { rejectWithValue }) => {
    try {
      const response = await enrollmentAPI.enrollInCourse(courseId);
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data?.message || 'Failed to enroll in course');
    }
  }
);

const coursesSlice = createSlice({
  name: 'courses',
  initialState,
  reducers: {
    clearError: (state) => {
      state.error = null;
    },
  },
  extraReducers: (builder) => {
    builder
      // Fetch all courses
      .addCase(fetchCourses.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchCourses.fulfilled, (state, action) => {
        state.loading = false;
        state.courses = action.payload;
      })
      .addCase(fetchCourses.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      })
      // Fetch instructor courses
      .addCase(fetchInstructorCourses.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchInstructorCourses.fulfilled, (state, action) => {
        state.loading = false;
        state.courses = action.payload;
      })
      .addCase(fetchInstructorCourses.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      })
      // Fetch course by ID
      .addCase(fetchCourseById.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchCourseById.fulfilled, (state, action) => {
        state.loading = false;
        state.currentCourse = action.payload;
      })
      .addCase(fetchCourseById.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      })
      // Create course
      .addCase(createCourse.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(createCourse.fulfilled, (state, action) => {
        state.loading = false;
        state.courses.push(action.payload);
      })
      .addCase(createCourse.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      })
      // Update course
      .addCase(updateCourse.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(updateCourse.fulfilled, (state, action) => {
        state.loading = false;
        const index = state.courses.findIndex(course => course.slug === action.payload.slug);
        if (index !== -1) {
          state.courses[index] = action.payload;
        }
        state.currentCourse = action.payload;
      })
      .addCase(updateCourse.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      })
      // Fetch enrolled courses
      .addCase(fetchEnrolledCourses.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchEnrolledCourses.fulfilled, (state, action) => {
        state.loading = false;
        state.enrolledCourses = action.payload;
      })
      .addCase(fetchEnrolledCourses.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      })
      // Enroll in course
      .addCase(enrollInCourse.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(enrollInCourse.fulfilled, (state, action) => {
        state.loading = false;
        state.enrolledCourses.push(action.payload);
      })
      .addCase(enrollInCourse.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      });
  },
});

export const { clearError } = coursesSlice.actions;
export default coursesSlice.reducer; 