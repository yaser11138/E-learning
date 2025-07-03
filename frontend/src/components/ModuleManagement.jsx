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
  List,
  ListItem,
  Alert,
} from '@mui/material';
import { DragDropContext, Droppable, Draggable } from '@hello-pangea/dnd';
import DeleteIcon from '@mui/icons-material/Delete';
import EditIcon from '@mui/icons-material/Edit';
import AddIcon from '@mui/icons-material/Add';
import { coursesAPI } from '../services/api';

const ModuleManagement = ({ courseSlug, modules, onModulesUpdate }) => {
  const [openDialog, setOpenDialog] = useState(false);
  const [editingModule, setEditingModule] = useState(null);
  const [error, setError] = useState(null);
  const [moduleData, setModuleData] = useState({
    title: '',
    description: '',
  });

  const handleOpenDialog = (module) => {
    if (module) {
      setEditingModule(module);
      setModuleData({
        title: module.title,
        description: module.description,
      });
    } else {
      setEditingModule(null);
      setModuleData({
        title: '',
        description: '',
      });
    }
    setOpenDialog(true);
  };

  const handleCloseDialog = () => {
    setOpenDialog(false);
    setEditingModule(null);
    setModuleData({
      title: '',
      description: '',
    });
    setError(null);
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setModuleData(prev => ({
      ...prev,
      [name]: value,
    }));
  };

  const handleSubmit = async () => {
    try {
      if (editingModule) {
        const response = await coursesAPI.updateModule(editingModule.id, moduleData);
        onModulesUpdate(
          modules.map(m => (m.id === response.data.id ? response.data : m))
        );
      } else {
        const response = await coursesAPI.createModule(courseSlug, moduleData);
        onModulesUpdate([...modules, response.data]);
      }
      handleCloseDialog();
    } catch (err) {
      setError(err.response?.data?.message || 'Failed to save module');
      console.error('Error saving module:', err);
    }
  };

  const handleDelete = async (moduleId) => {
    try {
      await coursesAPI.deleteModule(moduleId);
      onModulesUpdate(modules.filter(m => m.id !== moduleId));
    } catch (err) {
      setError(err.response?.data?.message || 'Failed to delete module');
      console.error('Error deleting module:', err);
    }
  };

  const handleDragEnd = (result) => {
    if (!result.destination) return;

    const items = Array.from(modules);
    const [reorderedItem] = items.splice(result.source.index, 1);
    items.splice(result.destination.index, 0, reorderedItem);

    // Update order in backend
    const updatedModules = items.map((module, index) => ({
      ...module,
      order: index,
    }));

    onModulesUpdate(updatedModules);
  };

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2 }}>
        <Typography variant="h6">Course Modules</Typography>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={() => handleOpenDialog()}
        >
          Add Module
        </Button>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}

      <DragDropContext onDragEnd={handleDragEnd}>
        <Droppable droppableId="modules">
          {(provided) => (
            <List {...provided.droppableProps} ref={provided.innerRef}>
              {modules.map((module, index) => (
                <Draggable
                  key={module.id}
                  draggableId={String(module.id)}
                  index={index}
                >
                  {(provided) => (
                    <ListItem
                      ref={provided.innerRef}
                      {...provided.draggableProps}
                      {...provided.dragHandleProps}
                      sx={{ mb: 1 }}
                    >
                      <Card sx={{ width: '100%' }}>
                        <CardContent>
                          <Typography variant="h6">{module.title}</Typography>
                          <Typography variant="body2" color="text.secondary">
                            {module.description}
                          </Typography>
                        </CardContent>
                        <CardActions>
                          <IconButton
                            onClick={() => handleOpenDialog(module)}
                            size="small"
                          >
                            <EditIcon />
                          </IconButton>
                          <IconButton
                            onClick={() => handleDelete(module.id)}
                            size="small"
                            color="error"
                          >
                            <DeleteIcon />
                          </IconButton>
                        </CardActions>
                      </Card>
                    </ListItem>
                  )}
                </Draggable>
              ))}
              {provided.placeholder}
            </List>
          )}
        </Droppable>
      </DragDropContext>

      <Dialog open={openDialog} onClose={handleCloseDialog}>
        <DialogTitle>
          {editingModule ? 'Edit Module' : 'Create New Module'}
        </DialogTitle>
        <DialogContent>
          <TextField
            autoFocus
            margin="dense"
            name="title"
            label="Module Title"
            type="text"
            fullWidth
            value={moduleData.title}
            onChange={handleInputChange}
          />
          <TextField
            margin="dense"
            name="description"
            label="Module Description"
            type="text"
            fullWidth
            multiline
            rows={4}
            value={moduleData.description}
            onChange={handleInputChange}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseDialog}>Cancel</Button>
          <Button onClick={handleSubmit} variant="contained">
            {editingModule ? 'Update' : 'Create'}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default ModuleManagement; 