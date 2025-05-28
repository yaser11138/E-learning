import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import { userAPI } from '../../services/api';

const initialState = {
  profile: null,
  dashboardStats: null,
  loading: false,
  error: null,
};

export const fetchUserProfile = createAsyncThunk(
  'auth/profile/',
  async (_, { rejectWithValue }) => {
    try {
      console.log('Fetching user profile...');
      const response = await userAPI.getProfile();
      console.log('Profile response:', response);
      if (!response.data) {
        throw new Error('No data received from profile endpoint');
      }
      return response.data;
    } catch (error) {
      console.error('Profile fetch error:', error);
      return rejectWithValue(
        error.response?.data?.message || 
        error.message || 
        'Failed to fetch profile'
      );
    }
  }
);

export const updateUserProfile = createAsyncThunk(
  'auth/profile',
  async (profileData, { rejectWithValue }) => {
    try {
      console.log('Updating profile...', profileData);
      const response = await userAPI.updateProfile(profileData);
      console.log('Profile update response:', response);
      if (!response.data) {
        throw new Error('No data received from profile update');
      }
      return response.data;
    } catch (error) {
      console.error('Profile update error:', error);
      return rejectWithValue(
        error.response?.data?.message || 
        error.message || 
        'Failed to update profile'
      );
    }
  }
);



const userSlice = createSlice({
  name: 'user',
  initialState,
  reducers: {
    clearError: (state) => {
      state.error = null;
    },
  },
  extraReducers: (builder) => {
    builder
      // Fetch user profile
      .addCase(fetchUserProfile.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchUserProfile.fulfilled, (state, action) => {
        state.loading = false;
        state.profile = action.payload;
      })
      .addCase(fetchUserProfile.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      })
      // Update user profile
      .addCase(updateUserProfile.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(updateUserProfile.fulfilled, (state, action) => {
        state.loading = false;
        state.profile = action.payload;
      })
      .addCase(updateUserProfile.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      });
  },
});

export const { clearError } = userSlice.actions;
export default userSlice.reducer; 