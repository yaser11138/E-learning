import React, { useEffect, useState } from 'react';
import {
  Container,
  Grid,
  Paper,
  Typography,
  Box,
  Card,
  CardContent,
  CircularProgress,
  List,
  ListItem,
  ListItemText,
  Divider,
  Chip
} from '@mui/material';
import { useSelector } from 'react-redux';
import api from '../services/api';
import { formatDistanceToNow, isValid } from 'date-fns';

const StatCard = ({ title, value, subtitle }) => (
  <Card>
    <CardContent>
      <Typography color="textSecondary" gutterBottom>
        {title}
      </Typography>
      <Typography variant="h4" component="div">
        {value}
      </Typography>
      {subtitle && (
        <Typography variant="body2" color="textSecondary">
          {subtitle}
        </Typography>
      )}
    </CardContent>
  </Card>
);

const formatDate = (dateString) => {
  if (!dateString) return 'N/A';
  const date = new Date(dateString);
  return isValid(date) ? formatDistanceToNow(date, { addSuffix: true }) : 'N/A';
};

const Dashboard = () => {
  const [loading, setLoading] = useState(true);
  const [dashboardData, setDashboardData] = useState(null);

  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        const response = await api.get('/dashboard/');
        setDashboardData(response.data);
      } catch (error) {
        console.error('Error fetching dashboard data:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchDashboardData();
  }, []);

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="80vh">
        <CircularProgress />
      </Box>
    );
  }

  if (dashboardData?.role === 'student') {
    const { statistics, recent_courses, enrolled_courses } = dashboardData;
    
    return (
      <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
        <Typography variant="h4" gutterBottom>
          Student Dashboard
        </Typography>
        
        {/* Statistics Cards */}
        <Grid container spacing={3} sx={{ mb: 4 }}>
          <Grid item xs={12} sm={6} md={3}>
            <StatCard
              title="Total Courses"
              value={statistics.totalCourses}
              subtitle="Enrolled Courses"
            />
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <StatCard
              title="Completed"
              value={statistics.completedCourses}
              subtitle="Courses Finished"
            />
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <StatCard
              title="In Progress"
              value={statistics.inProgressCourses}
              subtitle="Active Courses"
            />
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <StatCard
              title="Average Progress"
              value={`${statistics.averageProgress}%`}
              subtitle="Across All Courses"
            />
          </Grid>
        </Grid>

        <Grid container spacing={3}>
          {/* Recent Courses */}
          <Grid item xs={12} md={4}>
            <Paper sx={{ p: 2 }}>
              <Typography variant="h6" gutterBottom>
                Recently Accessed
              </Typography>
              <List>
                {recent_courses.map((course) => (
                  <React.Fragment key={course.id}>
                    <ListItem>
                      <ListItemText
                        primary={course.course?.title || 'Unknown Course'}
                        secondary={`${course.progress_percentage || 0}% complete`}
                      />
                      <Typography variant="caption" color="textSecondary">
                        {formatDate(course.last_accessed)}
                      </Typography>
                    </ListItem>
                    <Divider />
                  </React.Fragment>
                ))}
              </List>
            </Paper>
          </Grid>

          {/* All Courses */}
          <Grid item xs={12} md={8}>
            <Paper sx={{ p: 2 }}>
              <Typography variant="h6" gutterBottom>
                All Courses
              </Typography>
              <List>
                {enrolled_courses.map((course) => (
                  <ListItem key={course.id}>
                    <ListItemText
                      primary={course.course?.title || 'Unknown Course'}
                      secondary={`Started ${formatDate(course.started_at)}`}
                    />
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                      <Typography variant="body2" color="textSecondary">
                        {course.progress_percentage || 0}%
                      </Typography>
                      {course.completed && (
                        <Chip
                          label="Completed"
                          color="success"
                          size="small"
                        />
                      )}
                    </Box>
                  </ListItem>
                ))}
              </List>
            </Paper>
          </Grid>
        </Grid>
      </Container>
    );
  }

  if (dashboardData?.role === 'teacher') {
    const { statistics, top_courses, courses } = dashboardData;
    
    return (
      <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
        <Typography variant="h4" gutterBottom>
          Teacher Dashboard
        </Typography>
        
        {/* Statistics Cards */}
        <Grid container spacing={3} sx={{ mb: 4 }}>
          <Grid item xs={12} sm={6} md={3}>
            <StatCard
              title="Active Courses"
              value={statistics.activeCourses}
              subtitle="Currently Active"
            />
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <StatCard
              title="Total Students"
              value={statistics.totalStudents}
              subtitle="Enrolled Students"
            />
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <StatCard
              title="Total Revenue"
              value={`$${statistics.totalRevenue}`}
              subtitle="From All Courses"
            />
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <StatCard
              title="Avg Students/Course"
              value={statistics.averageStudentsPerCourse}
              subtitle="Per Course"
            />
          </Grid>
        </Grid>

        <Grid container spacing={3}>
          {/* Top Performing Courses */}
          <Grid item xs={12} md={4}>
            <Paper sx={{ p: 2 }}>
              <Typography variant="h6" gutterBottom>
                Top Performing Courses
              </Typography>
              <List>
                {top_courses.map((course) => (
                  <React.Fragment key={course.id}>
                    <ListItem>
                      <ListItemText
                        primary={course.title}
                        secondary={`${course.enrollments?.length || 0} students enrolled`}
                      />
                      <Typography variant="caption" color="textSecondary">
                        ${course.price}
                      </Typography>
                    </ListItem>
                    <Divider />
                  </React.Fragment>
                ))}
              </List>
            </Paper>
          </Grid>

          {/* All Courses */}
          <Grid item xs={12} md={8}>
            <Paper sx={{ p: 2 }}>
              <Typography variant="h6" gutterBottom>
                All Courses
              </Typography>
              <List>
                {courses.map((course) => (
                  <ListItem key={course.id}>
                    <ListItemText
                      primary={course.title}
                      secondary={`Created ${formatDate(course.created_at)}`}
                    />
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                      <Typography variant="body2" color="textSecondary">
                        {course.enrollments?.length || 0} students
                      </Typography>
                      <Chip
                        label={course.is_active ? "Active" : "Inactive"}
                        color={course.is_active ? "success" : "default"}
                        size="small"
                      />
                    </Box>
                  </ListItem>
                ))}
              </List>
            </Paper>
          </Grid>
        </Grid>
      </Container>
    );
  }

  return null;
};

export default Dashboard; 