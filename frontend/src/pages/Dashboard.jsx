import React, { useEffect } from 'react';
import {
  Container,
  Grid,
  Paper,
  Typography,
  Box,
  LinearProgress,
  Card,
  CardContent,
  CardMedia,
  Button,
  CircularProgress,
} from '@mui/material';
import { useDispatch, useSelector } from 'react-redux';
import { useNavigate } from 'react-router-dom';
import { fetchDashboardData } from '../store/slices/userSlice';
import { fetchEnrolledCourses } from '../store/slices/coursesSlice';

const Dashboard = () => {
  const navigate = useNavigate();
  const dispatch = useDispatch();
  const { profile, dashboardStats, loading: userLoading } = useSelector((state) => state.user);
  const { enrolledCourses, loading: coursesLoading } = useSelector((state) => state.courses);

  useEffect(() => {
    dispatch(fetchDashboardData());
    dispatch(fetchEnrolledCourses());
  }, [dispatch]);

  if (userLoading || coursesLoading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="80vh">
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      <Grid container spacing={3}>
        {/* User Stats */}
        <Grid item xs={12}>
          <Paper sx={{ p: 2, display: 'flex', flexDirection: 'column' }}>
            <Typography variant="h6" gutterBottom>
              Welcome back, {profile?.firstName}!
            </Typography>
            <Grid container spacing={2}>
              <Grid item xs={12} sm={6} md={3}>
                <Paper sx={{ p: 2, textAlign: 'center' }}>
                  <Typography variant="h4">{dashboardStats?.totalCourses || 0}</Typography>
                  <Typography color="textSecondary">Total Courses</Typography>
                </Paper>
              </Grid>
              <Grid item xs={12} sm={6} md={3}>
                <Paper sx={{ p: 2, textAlign: 'center' }}>
                  <Typography variant="h4">{dashboardStats?.completedCourses || 0}</Typography>
                  <Typography color="textSecondary">Completed</Typography>
                </Paper>
              </Grid>
              <Grid item xs={12} sm={6} md={3}>
                <Paper sx={{ p: 2, textAlign: 'center' }}>
                  <Typography variant="h4">{dashboardStats?.inProgressCourses || 0}</Typography>
                  <Typography color="textSecondary">In Progress</Typography>
                </Paper>
              </Grid>
              <Grid item xs={12} sm={6} md={3}>
                <Paper sx={{ p: 2, textAlign: 'center' }}>
                  <Typography variant="h4">{dashboardStats?.certificates || 0}</Typography>
                  <Typography color="textSecondary">Certificates</Typography>
                </Paper>
              </Grid>
            </Grid>
          </Paper>
        </Grid>

        {/* Enrolled Courses */}
        <Grid item xs={12}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              Your Courses
            </Typography>
            <Grid container spacing={3}>
              {enrolledCourses.map((course) => (
                <Grid item xs={12} sm={6} md={4} key={course.id}>
                  <Card>
                    <CardMedia
                      component="img"
                      height="140"
                      image={course.image}
                      alt={course.title}
                    />
                    <CardContent>
                      <Typography gutterBottom variant="h6" component="div">
                        {course.title}
                      </Typography>
                      <Typography variant="body2" color="text.secondary" gutterBottom>
                        {course.description}
                      </Typography>
                      <Box sx={{ mt: 2 }}>
                        <Typography variant="body2" color="text.secondary">
                          Progress
                        </Typography>
                        <LinearProgress
                          variant="determinate"
                          value={course.progress || 0}
                          sx={{ mt: 1 }}
                        />
                        <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                          {course.progress || 0}% Complete
                        </Typography>
                      </Box>
                      <Button
                        variant="contained"
                        fullWidth
                        sx={{ mt: 2 }}
                        onClick={() => navigate(`/courses/${course.id}`)}
                      >
                        Continue Learning
                      </Button>
                    </CardContent>
                  </Card>
                </Grid>
              ))}
            </Grid>
          </Paper>
        </Grid>
      </Grid>
    </Container>
  );
};

export default Dashboard; 