import React from 'react';
import {
  Box,
  Container,
  Typography,
  Button,
  Grid,
  Card,
  CardContent,
  CardMedia,
} from '@mui/material';
import { useNavigate } from 'react-router-dom';

const Home = () => {
  const navigate = useNavigate();

  const featuredCourses = [
    {
      id: 1,
      title: 'Web Development Bootcamp',
      description: 'Learn modern web development from scratch',
      image: 'https://source.unsplash.com/random/300x200?web',
    },
    {
      id: 2,
      title: 'Data Science Fundamentals',
      description: 'Master the basics of data science and analytics',
      image: 'https://source.unsplash.com/random/300x200?data',
    },
    {
      id: 3,
      title: 'Mobile App Development',
      description: 'Create amazing mobile applications',
      image: 'https://source.unsplash.com/random/300x200?mobile',
    },
  ];

  return (
    <Box>
      {/* Hero Section */}
      <Box
        sx={{
          bgcolor: 'primary.main',
          color: 'white',
          py: 8,
          mb: 6,
        }}
      >
        <Container maxWidth="lg">
          <Grid container spacing={4} alignItems="center">
            <Grid item xs={12} md={6}>
              <Typography variant="h2" component="h1" gutterBottom>
                Learn Without Limits
              </Typography>
              <Typography variant="h5" paragraph>
                Start, switch, or advance your career with thousands of courses from expert instructors.
              </Typography>
              <Button
                variant="contained"
                color="secondary"
                size="large"
                onClick={() => navigate('/courses')}
                sx={{ mt: 2 }}
              >
                Explore Courses
              </Button>
            </Grid>
            <Grid item xs={12} md={6}>
              <Box
                component="img"
                src="https://source.unsplash.com/random/600x400?education"
                alt="Learning"
                sx={{
                  width: '100%',
                  borderRadius: 2,
                  boxShadow: 3,
                }}
              />
            </Grid>
          </Grid>
        </Container>
      </Box>

      {/* Featured Courses Section */}
      <Container maxWidth="lg">
        <Typography variant="h3" component="h2" gutterBottom>
          Featured Courses
        </Typography>
        <Grid container spacing={4}>
          {featuredCourses.map((course) => (
            <Grid item key={course.id} xs={12} sm={6} md={4}>
              <Card
                sx={{
                  height: '100%',
                  display: 'flex',
                  flexDirection: 'column',
                  cursor: 'pointer',
                  '&:hover': {
                    transform: 'translateY(-4px)',
                    transition: 'transform 0.2s ease-in-out',
                  },
                }}
                onClick={() => navigate(`/courses/${course.id}`)}
              >
                <CardMedia
                  component="img"
                  height="200"
                  image={course.image}
                  alt={course.title}
                />
                <CardContent>
                  <Typography gutterBottom variant="h5" component="h3">
                    {course.title}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    {course.description}
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
          ))}
        </Grid>
      </Container>
    </Box>
  );
};

export default Home; 