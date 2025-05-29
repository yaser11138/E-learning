import React, { useEffect, useState } from 'react';
import {
  Box,
  Container,
  Paper,
  Typography,
  Tabs,
  Tab,
  CircularProgress,
  Alert,
} from '@mui/material';
import { useParams } from 'react-router-dom';
import { useDispatch, useSelector } from 'react-redux';
import { fetchCourseById } from '../store/slices/coursesSlice';
import { coursesAPI } from '../services/api';
import ModuleManagement from '../components/ModuleManagement';
import ContentUpload from '../components/ContentUpload';

function TabPanel({ children, value, index }) {
  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`course-tabpanel-${index}`}
      aria-labelledby={`course-tab-${index}`}
    >
      {value === index && <Box sx={{ p: 3 }}>{children}</Box>}
    </div>
  );
}

const CourseEdit = () => {
  const { slug } = useParams();
  const dispatch = useDispatch();
  const { currentCourse: course, loading, error } = useSelector((state) => state.courses);
  const [modules, setModules] = useState([]);
  const [selectedModule, setSelectedModule] = useState(null);
  const [contents, setContents] = useState([]);
  const [activeTab, setActiveTab] = useState(0);

  useEffect(() => {
    dispatch(fetchCourseById(slug));
  }, [dispatch, slug]);

  useEffect(() => {
    if (course) {
      setModules(course.modules || []);
      if (course.modules?.length > 0) {
        setSelectedModule(course.modules[0]);
      }
    }
  }, [course]);

  useEffect(() => {
    const fetchModuleContents = async () => {
      if (selectedModule) {
        try {
          const response = await coursesAPI.getModuleContents(selectedModule.slug);
          setContents(response.data);
        } catch (err) {
          console.error('Error fetching module contents:', err);
        }
      }
    };

    fetchModuleContents();
  }, [selectedModule]);

  const handleTabChange = (event, newValue) => {
    setActiveTab(newValue);
  };

  const handleModuleSelect = (module) => {
    setSelectedModule(module);
  };

  const handleModulesUpdate = (updatedModules) => {
    setModules(updatedModules);
  };

  const handleContentsUpdate = (updatedContents) => {
    setContents(updatedContents);
  };

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', mt: 4 }}>
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

  if (!course) {
    return (
      <Container maxWidth="lg" sx={{ mt: 4 }}>
        <Alert severity="error">Course not found</Alert>
      </Container>
    );
  }

  return (
    <Container maxWidth="lg" sx={{ mt: 4 }}>
      <Paper elevation={3}>
        <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
          <Tabs value={activeTab} onChange={handleTabChange}>
            <Tab label="Course Details" />
            <Tab label="Modules" />
            <Tab label="Content" />
          </Tabs>
        </Box>

        <TabPanel value={activeTab} index={0}>
          <Typography variant="h4" gutterBottom>
            {course.title}
          </Typography>
          <Typography variant="body1" paragraph>
            {course.description}
          </Typography>
          <Typography variant="subtitle1">
            Price: ${course.price}
          </Typography>
          <Typography variant="subtitle1">
            Status: {course.is_published ? 'Published' : 'Draft'}
          </Typography>
        </TabPanel>

        <TabPanel value={activeTab} index={1}>
          <ModuleManagement
            courseSlug={slug}
            modules={modules}
            onModulesUpdate={handleModulesUpdate}
          />
        </TabPanel>

        <TabPanel value={activeTab} index={2}>
          {selectedModule ? (
            <ContentUpload
              moduleSlug={selectedModule.slug}
              contents={contents}
              onContentsUpdate={handleContentsUpdate}
            />
          ) : (
            <Alert severity="info">
              Please select a module to manage its contents
            </Alert>
          )}
        </TabPanel>
      </Paper>
    </Container>
  );
};

export default CourseEdit; 