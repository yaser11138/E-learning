import React, { useState } from 'react';
import {
  Box,
  Button,
  Container,
  TextField,
  Typography,
  Paper,
  Grid,
  FormControlLabel,
  Switch,
  CircularProgress,
  Alert,
} from '@mui/material';
import { useNavigate } from 'react-router-dom';
import { coursesAPI } from '../services/api';

const CourseCreation = () => {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [courseData, setCourseData] = useState({
    title: '',
    description: '',
    price: '',
    is_published: false,
    thumbnail: null,
  });

  const handleInputChange = (e) => {
    const { name, value, type, checked } = e.target;
    setCourseData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value,
    }));
  };

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      setCourseData(prev => ({
        ...prev,
        thumbnail: e.target.files[0],
      }));
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const formData = new FormData();
      formData.append('title', courseData.title);
      formData.append('description', courseData.description);
      formData.append('price', courseData.price);
      formData.append('is_published', String(courseData.is_published));
      if (courseData.thumbnail) {
        formData.append('thumbnail', courseData.thumbnail);
      }

      const response = await coursesAPI.createCourse(formData);
      navigate(`/courses/${response.data.slug}/edit`);
    } catch (err) {
      setError(err.response?.data?.message || 'Failed to create course');
      console.error('Error creating course:', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Container maxWidth="md" sx={{ py: 4 }}>
      <Paper elevation={3} sx={{ p: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          Create New Course
        </Typography>

        {error && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {error}
          </Alert>
        )}

        <Box component="form" onSubmit={handleSubmit} noValidate>
          <Grid container spacing={3}>
            <Grid item xs={12}>
              <TextField
                required
                fullWidth
                label="Course Title"
                name="title"
                value={courseData.title}
                onChange={handleInputChange}
              />
            </Grid>

            <Grid item xs={12}>
              <TextField
                required
                fullWidth
                multiline
                rows={4}
                label="Course Description"
                name="description"
                value={courseData.description}
                onChange={handleInputChange}
              />
            </Grid>

            <Grid item xs={12} sm={6}>
              <TextField
                required
                fullWidth
                type="number"
                label="Price"
                name="price"
                value={courseData.price}
                onChange={handleInputChange}
                InputProps={{
                  startAdornment: '$',
                }}
              />
            </Grid>

            <Grid item xs={12}>
              <Button
                variant="contained"
                component="label"
                fullWidth
              >
                Upload Thumbnail
                <input
                  type="file"
                  hidden
                  accept="image/*"
                  onChange={handleFileChange}
                />
              </Button>
              {courseData.thumbnail && (
                <Typography variant="body2" sx={{ mt: 1 }}>
                  Selected file: {courseData.thumbnail.name}
                </Typography>
              )}
            </Grid>

            <Grid item xs={12}>
              <FormControlLabel
                control={
                  <Switch
                    checked={courseData.is_published}
                    onChange={handleInputChange}
                    name="is_published"
                  />
                }
                label="Publish Course"
              />
            </Grid>

            <Grid item xs={12}>
              <Button
                type="submit"
                variant="contained"
                color="primary"
                fullWidth
                disabled={loading}
                sx={{ mt: 2 }}
              >
                {loading ? <CircularProgress size={24} /> : 'Create Course'}
              </Button>
            </Grid>
          </Grid>
        </Box>
      </Paper>
    </Container>
  );
};

export default CourseCreation; 