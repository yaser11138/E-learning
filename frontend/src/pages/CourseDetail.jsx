import React, { useEffect } from 'react';
import {
  Container,
  Grid,
  Typography,
  Box,
  Card,
  CardContent,
  Button,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  CircularProgress,
} from '@mui/material';
import {
  ExpandMore as ExpandMoreIcon,
  Lock as LockIcon,
  PlayCircle as PlayCircleIcon,
} from '@mui/icons-material';
import { useParams, useNavigate } from 'react-router-dom';
import { useDispatch, useSelector } from 'react-redux';
import { fetchCourseById } from '../store/slices/coursesSlice';

const CourseDetail = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const dispatch = useDispatch();
  const { currentCourse: course, loading } = useSelector((state) => state.courses);
  const { isAuthenticated } = useSelector((state) => state.auth);

  useEffect(() => {
    dispatch(fetchCourseById(id));
  }, [dispatch, id]);

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="80vh">
        <CircularProgress />
      </Box>
    );
  }

  if (!course) {
    return (
      <Container>
        <Typography variant="h5" align="center">
          Course not found
        </Typography>
      </Container>
    );
  }

  const handleEnroll = () => {
    if (!isAuthenticated) {
      navigate('/login');
    }
    // Add enrollment logic here
  };

  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      <Grid container spacing={3}>
        {/* Course Header */}
        <Grid item xs={12}>
          <Box
            sx={{
              backgroundImage: `url(${course.image})`,
              backgroundSize: 'cover',
              backgroundPosition: 'center',
              height: 300,
              position: 'relative',
              borderRadius: 2,
              mb: 4,
            }}
          >
            <Box
              sx={{
                position: 'absolute',
                bottom: 0,
                left: 0,
                right: 0,
                bgcolor: 'rgba(0, 0, 0, 0.7)',
                color: 'white',
                p: 3,
                borderBottomLeftRadius: 8,
                borderBottomRightRadius: 8,
              }}
            >
              <Typography variant="h4" gutterBottom>
                {course.title}
              </Typography>
              <Typography variant="subtitle1">
                By {course.instructor} • {course.totalStudents} students • Rating: {course.rating}
              </Typography>
            </Box>
          </Box>
        </Grid>

        {/* Course Content */}
        <Grid item xs={12} md={8}>
          <Typography variant="h5" gutterBottom>
            About This Course
          </Typography>
          <Typography paragraph>{course.description}</Typography>

          <Typography variant="h5" gutterBottom sx={{ mt: 4 }}>
            Course Curriculum
          </Typography>
          {course.curriculum.sections.map((section, index) => (
            <Accordion key={index}>
              <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                <Typography>{section.title}</Typography>
              </AccordionSummary>
              <AccordionDetails>
                <List>
                  {section.lessons.map((lesson, lessonIndex) => (
                    <ListItem key={lessonIndex}>
                      <ListItemIcon>
                        {lesson.isFree ? <PlayCircleIcon /> : <LockIcon />}
                      </ListItemIcon>
                      <ListItemText
                        primary={lesson.title}
                        secondary={`Duration: ${lesson.duration}`}
                      />
                    </ListItem>
                  ))}
                </List>
              </AccordionDetails>
            </Accordion>
          ))}
        </Grid>

        {/* Enrollment Card */}
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography variant="h5" gutterBottom>
                ${course.price}
              </Typography>
              <Button
                variant="contained"
                fullWidth
                size="large"
                onClick={handleEnroll}
                sx={{ mb: 2 }}
              >
                {isAuthenticated ? 'Enroll Now' : 'Login to Enroll'}
              </Button>
              <Typography variant="subtitle1" gutterBottom>
                This course includes:
              </Typography>
              <List>
                <ListItem>
                  <ListItemText primary="Full lifetime access" />
                </ListItem>
                <ListItem>
                  <ListItemText primary="Certificate of completion" />
                </ListItem>
                <ListItem>
                  <ListItemText primary="Downloadable resources" />
                </ListItem>
              </List>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Container>
  );
};

export default CourseDetail; 