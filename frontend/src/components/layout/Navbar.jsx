import React, { useState, useEffect } from 'react';
import {
  AppBar,
  Toolbar,
  Typography,
  Button,
  IconButton,
  Drawer,
  List,
  ListItem,
  ListItemText,
  Box,
  useTheme,
  useMediaQuery,
  Menu,
  MenuItem,
} from '@mui/material';
import { Menu as MenuIcon, Add as AddIcon, School as SchoolIcon } from '@mui/icons-material';
import { Link as RouterLink, useNavigate } from 'react-router-dom';
import { useSelector, useDispatch } from 'react-redux';
import { logout } from '../../store/slices/authSlice';
import { authAPI } from '../../services/api';
import { coursesAPI } from '../../services/api';

const Navbar = () => {
  const [mobileOpen, setMobileOpen] = useState(false);
  const [anchorEl, setAnchorEl] = useState(null);
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('sm'));
  const navigate = useNavigate();
  const dispatch = useDispatch();
  const { isAuthenticated, user } = useSelector((state) => state.auth);
  const { profile } = useSelector((state) => state.user);
  // Debug logs
  useEffect(() => {
    console.log('Auth State:', { isAuthenticated, user });
  }, [isAuthenticated, user]);

  useEffect(() => {
    console.log('Profile State:', { profile });
  }, [profile]);

  const isInstructor = profile?.role === 'Instructor';

  useEffect(() => {
    console.log('Profile State:', { isInstructor });
  }, [isInstructor]);


  const handleDrawerToggle = () => {
    setMobileOpen(!mobileOpen);
  };

  const handleLogout = async () => {
    try {
      await authAPI.logout();
      dispatch(logout());
      navigate('/login');
    } catch (error) {
      console.error('Logout error:', error);
    }
  };

  const handleMenuOpen = (event) => {
    setAnchorEl(event.currentTarget);
  };

  const handleMenuClose = () => {
    setAnchorEl(null);
  };

  const handleMenuClick = (path) => {
    navigate(path);
    handleMenuClose();
  };

  const baseMenuItems = [
    { text: 'Home', path: '/' },
    { text: 'Courses', path: '/courses' },
  ];

  const instructorMenuItems = [
    { text: 'Create Course', path: '/course/create', icon: <AddIcon /> },
    { text: 'My Courses', path: '/instructor/courses', icon: <SchoolIcon /> },
  ];

  const authMenuItems = isAuthenticated
    ? [
        ...(isInstructor ? instructorMenuItems : []),
        { text: 'Dashboard', path: '/dashboard' },
        { text: 'Logout', action: handleLogout },
      ]
    : [
        { text: 'Login', path: '/login' },
        { text: 'Register', path: '/register' },
      ];

  const menuItems = [...baseMenuItems, ...authMenuItems];

  const drawer = (
    <List>
      {menuItems.map((item) => (
        <ListItem
          button
          key={item.text}
          onClick={() => {
            if (item.action) {
              item.action();
            } else {
              navigate(item.path);
            }
            handleDrawerToggle();
          }}
        >
          {item.icon && <Box sx={{ mr: 1 }}>{item.icon}</Box>}
          <ListItemText primary={item.text} />
        </ListItem>
      ))}
    </List>
  );

  return (
    <>
      <AppBar position="static">
        <Toolbar>
          {isMobile && (
            <IconButton
              color="inherit"
              aria-label="open drawer"
              edge="start"
              onClick={handleDrawerToggle}
              sx={{ mr: 2 }}
            >
              <MenuIcon />
            </IconButton>
          )}
          <Typography
            variant="h6"
            component={RouterLink}
            to="/"
            sx={{
              flexGrow: 1,
              textDecoration: 'none',
              color: 'inherit',
            }}
          >
            E-Learning Platform
          </Typography>
          {!isMobile && (
            <Box sx={{ display: 'flex', gap: 2 }}>
              {baseMenuItems.map((item) => (
                <Button
                  key={item.text}
                  color="inherit"
                  onClick={() => navigate(item.path)}
                >
                  {item.text}
                </Button>
              ))}
              
              {isAuthenticated && isInstructor && (
                <Button
                  color="inherit"
                  startIcon={<SchoolIcon />}
                  onClick={handleMenuOpen}
                >
                  Instructor
                </Button>
              )}

              {isAuthenticated ? (
                <>
                  <Button color="inherit" onClick={() => navigate('/dashboard')}>
                    Dashboard
                  </Button>
                  <Button color="inherit" onClick={handleLogout}>
                    Logout
                  </Button>
                </>
              ) : (
                <>
                  <Button color="inherit" onClick={() => navigate('/login')}>
                    Login
                  </Button>
                  <Button color="inherit" onClick={() => navigate('/register')}>
                    Register
                  </Button>
                </>
              )}
            </Box>
          )}
        </Toolbar>
      </AppBar>

      <Menu
        anchorEl={anchorEl}
        open={Boolean(anchorEl)}
        onClose={handleMenuClose}
      >
        {instructorMenuItems.map((item) => (
          <MenuItem
            key={item.text}
            onClick={() => handleMenuClick(item.path)}
          >
            <Box sx={{ display: 'flex', alignItems: 'center' }}>
              {item.icon && <Box sx={{ mr: 1 }}>{item.icon}</Box>}
              {item.text}
            </Box>
          </MenuItem>
        ))}
      </Menu>

      <Drawer
        variant="temporary"
        anchor="left"
        open={mobileOpen}
        onClose={handleDrawerToggle}
        ModalProps={{
          keepMounted: true,
        }}
      >
        {drawer}
      </Drawer>
    </>
  );
};

export default Navbar; 