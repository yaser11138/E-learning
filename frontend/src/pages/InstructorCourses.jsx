import React, { useEffect } from 'react';
import {
  Container,
  Typography,
  Grid,
  Card,
  CardContent,
  CardMedia,
  Button,
  Box,
  CircularProgress,
  Alert,
} from '@mui/material';
import { useNavigate } from 'react-router-dom';
import { useDispatch, useSelector } from 'react-redux';
import { fetchInstructorCourses } from '../store/slices/coursesSlice';

const InstructorCourses = () => {
  const navigate = useNavigate();
  const dispatch = useDispatch();
  const { courses = [], loading, error } = useSelector((state) => state.courses);

  useEffect(() => {
    dispatch(fetchInstructorCourses());
  }, [dispatch]);

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="60vh">
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return (
      <Container maxWidth="lg" sx={{ mt: 4 }}>
        <Alert severity="error">{error}</Alert>
      </Container>
    );
  }

  return (
    <Container maxWidth="lg" sx={{ mt: 4 }}>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={4}>
        <Typography variant="h4" component="h1">
          My Courses
        </Typography>
        <Button
          variant="contained"
          color="primary"
          onClick={() => navigate('/course/create')}
        >
          Create New Course
        </Button>
      </Box>

      {!Array.isArray(courses) || courses.length === 0 ? (
        <Typography variant="h6" color="textSecondary" align="center">
          You haven't created any courses yet.
        </Typography>
      ) : (
        <Grid container spacing={4}>
          {courses.map((course) => (
            <Grid item xs={12} sm={6} md={4} key={course.id}>
              <Card>
                <CardMedia
                  component="img"
                  height="140"
                  image={course.thumbnail || 'https://via.placeholder.com/300x140'}
                  alt={course.title}
                />
                <CardContent>
                  <Typography gutterBottom variant="h6" component="h2">
                    {course.title}
                  </Typography>
                  <Typography variant="body2" color="textSecondary" noWrap>
                    {course.description}
                  </Typography>
                  <Box mt={2} display="flex" justifyContent="space-between">
                    <Button
                      size="small"
                      color="primary"
                      onClick={() => navigate(`/content/courses/${course.slug}/edit`)}
                    >
                      Edit
                    </Button>
                    <Typography variant="body2" color="textSecondary">
                      ${course.price}
                    </Typography>
                  </Box>
                </CardContent>
              </Card>
            </Grid>
          ))}
        </Grid>
      )}
    </Container>
  );
};

export default InstructorCourses; 