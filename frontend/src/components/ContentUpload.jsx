import React, { useState } from 'react';
import {
  Box,
  Button,
  Card,
  CardContent,
  CardActions,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Typography,
  IconButton,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  FormControlLabel,
  Switch,
  CircularProgress,
  Alert,
} from '@mui/material';
import DeleteIcon from '@mui/icons-material/Delete';
import EditIcon from '@mui/icons-material/Edit';
import AddIcon from '@mui/icons-material/Add';
import { coursesAPI } from '../services/api';

const ContentUpload = ({ moduleSlug, contents, onContentsUpdate }) => {
  const [openDialog, setOpenDialog] = useState(false);
  const [editingContent, setEditingContent] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [contentData, setContentData] = useState({
    title: '',
    description: '',
    resourcetype: 'TextContent',
    text: '',
    is_free: false,
    file: null,
  });

  const handleOpenDialog = (content) => {
    if (content) {
      setEditingContent(content);
      setContentData({
        title: content.title,
        description: content.description || '',
        resourcetype: content.resourcetype,
        text: content.text || '',
        is_free: content.is_free,
        file: null,
      });
    } else {
      setEditingContent(null);
      setContentData({
        title: '',
        description: '',
        resourcetype: 'TextContent',
        text: '',
        is_free: false,
        file: null,
      });
    }
    setOpenDialog(true);
  };

  const handleCloseDialog = () => {
    setOpenDialog(false);
    setEditingContent(null);
    setContentData({
      title: '',
      description: '',
      resourcetype: 'TextContent',
      text: '',
      is_free: false,
      file: null,
    });
    setError(null);
  };

  const handleInputChange = (e) => {
    const { name, value, type, checked } = e.target;
    setContentData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value,
    }));
  };

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      setContentData(prev => ({
        ...prev,
        file: e.target.files[0],
      }));
    }
  };

  const handleSubmit = async () => {
    setLoading(true);
    setError(null);
    try {
      const formData = new FormData();
      formData.append('title', contentData.title);
      formData.append('description', contentData.description);
      formData.append('resourcetype', contentData.resourcetype);
      formData.append('is_free', String(contentData.is_free));

      if (contentData.resourcetype === 'TextContent') {
        formData.append('text', contentData.text);
      } else if (contentData.file) {
        const fileField = `${contentData.resourcetype.toLowerCase()}_file`;
        formData.append(fileField, contentData.file);
      }

      if (editingContent) {
        const response = await coursesAPI.updateContent(editingContent.id, formData);
        onContentsUpdate(
          contents.map(c => (c.id === response.data.id ? response.data : c))
        );
      } else {
        const response = await coursesAPI.uploadContent(moduleSlug, formData);
        onContentsUpdate([...contents, response.data]);
      }
      handleCloseDialog();
    } catch (err) {
      setError(err.response?.data?.message || 'Failed to save content');
      console.error('Error saving content:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (contentId) => {
    try {
      await coursesAPI.deleteContent(contentId);
      onContentsUpdate(contents.filter(c => c.id !== contentId));
    } catch (err) {
      setError(err.response?.data?.message || 'Failed to delete content');
      console.error('Error deleting content:', err);
    }
  };

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2 }}>
        <Typography variant="h6">Module Contents</Typography>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={() => handleOpenDialog()}
        >
          Add Content
        </Button>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}

      {contents.map(content => (
        <Card key={content.id} sx={{ mb: 2 }}>
          <CardContent>
            <Typography variant="h6">{content.title}</Typography>
            <Typography variant="body2" color="text.secondary">
              {content.description}
            </Typography>
            <Typography variant="caption" color="text.secondary">
              Type: {content.resourcetype}
            </Typography>
          </CardContent>
          <CardActions>
            <IconButton
              onClick={() => handleOpenDialog(content)}
              size="small"
            >
              <EditIcon />
            </IconButton>
            <IconButton
              onClick={() => handleDelete(content.id)}
              size="small"
              color="error"
            >
              <DeleteIcon />
            </IconButton>
          </CardActions>
        </Card>
      ))}

      <Dialog open={openDialog} onClose={handleCloseDialog} maxWidth="md" fullWidth>
        <DialogTitle>
          {editingContent ? 'Edit Content' : 'Create New Content'}
        </DialogTitle>
        <DialogContent>
          <TextField
            autoFocus
            margin="dense"
            name="title"
            label="Content Title"
            type="text"
            fullWidth
            value={contentData.title}
            onChange={handleInputChange}
          />
          <TextField
            margin="dense"
            name="description"
            label="Content Description"
            type="text"
            fullWidth
            multiline
            rows={2}
            value={contentData.description}
            onChange={handleInputChange}
          />
          <FormControl fullWidth margin="dense">
            <InputLabel>Content Type</InputLabel>
            <Select
              name="resourcetype"
              value={contentData.resourcetype}
              onChange={handleInputChange}
              label="Content Type"
            >
              <MenuItem value="TextContent">Text</MenuItem>
              <MenuItem value="VideoContent">Video</MenuItem>
              <MenuItem value="ImageContent">Image</MenuItem>
              <MenuItem value="FileContent">File</MenuItem>
            </Select>
          </FormControl>

          {contentData.resourcetype === 'TextContent' ? (
            <TextField
              margin="dense"
              name="text"
              label="Content Text"
              type="text"
              fullWidth
              multiline
              rows={6}
              value={contentData.text}
              onChange={handleInputChange}
            />
          ) : (
            <Button
              variant="contained"
              component="label"
              fullWidth
              sx={{ mt: 2 }}
            >
              Upload {contentData.resourcetype.replace('Content', '')}
              <input
                type="file"
                hidden
                accept={
                  contentData.resourcetype === 'VideoContent'
                    ? 'video/*'
                    : contentData.resourcetype === 'ImageContent'
                    ? 'image/*'
                    : '*'
                }
                onChange={handleFileChange}
              />
            </Button>
          )}

          <FormControlLabel
            control={
              <Switch
                checked={contentData.is_free}
                onChange={handleInputChange}
                name="is_free"
              />
            }
            label="Free Content"
            sx={{ mt: 2 }}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseDialog}>Cancel</Button>
          <Button
            onClick={handleSubmit}
            variant="contained"
            disabled={loading}
          >
            {loading ? (
              <CircularProgress size={24} />
            ) : editingContent ? (
              'Update'
            ) : (
              'Create'
            )}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default ContentUpload; 