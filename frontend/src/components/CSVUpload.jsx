import React, { useState, useCallback } from 'react';
import {
  Box,
  Paper,
  Typography,
  Button,
  Alert,
  CircularProgress,
  List,
  ListItem,
  ListItemText,
} from '@mui/material';
import UploadFileIcon from '@mui/icons-material/UploadFile';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import { uploadCSV } from '../services/api';

function CSVUpload({ onResults }) {
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);
  const [isDragOver, setIsDragOver] = useState(false);

  const handleDrop = useCallback((e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragOver(false);

    const droppedFile = e.dataTransfer.files[0];
    if (droppedFile && droppedFile.name.endsWith('.csv')) {
      setFile(droppedFile);
      setError(null);
    } else {
      setError('Please upload a CSV file');
    }
  }, []);

  const handleDragOver = useCallback((e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragOver(true);
  }, []);

  const handleDragLeave = useCallback((e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragOver(false);
  }, []);

  const handleFileSelect = (e) => {
    const selectedFile = e.target.files[0];
    if (selectedFile) {
      setFile(selectedFile);
      setError(null);
    }
  };

  const handleUpload = async () => {
    if (!file) {
      setError('Please select a file first');
      return;
    }

    setLoading(true);
    setError(null);
    setSuccess(null);

    try {
      const response = await uploadCSV(file);

      if (response.success) {
        setSuccess(`Successfully uploaded ${response.count} properties`);
        onResults(response.properties || []);
      } else {
        setError(response.error || 'Failed to upload CSV');
      }
    } catch (err) {
      setError(err.response?.data?.error || 'An error occurred during upload');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Paper sx={{ p: 3 }}>
      <Typography variant="h5" gutterBottom>
        Upload CSV File
      </Typography>
      <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
        Upload a CSV file with property addresses and TradeMe URLs. Columns are auto-detected.
      </Typography>

      <Box
        sx={{
          border: isDragOver ? '2px dashed #1976d2' : '2px dashed #ccc',
          borderRadius: 2,
          p: 4,
          textAlign: 'center',
          backgroundColor: isDragOver ? 'rgba(25, 118, 210, 0.05)' : 'transparent',
          cursor: 'pointer',
          transition: 'all 0.3s',
          mb: 3,
        }}
        onDrop={handleDrop}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onClick={() => document.getElementById('csv-file-input').click()}
      >
        <input
          id="csv-file-input"
          type="file"
          accept=".csv"
          onChange={handleFileSelect}
          style={{ display: 'none' }}
        />
        <UploadFileIcon sx={{ fontSize: 64, color: '#1976d2', mb: 2 }} />
        <Typography variant="h6" gutterBottom>
          {file ? file.name : 'Drop CSV file here or click to browse'}
        </Typography>
        <Typography variant="body2" color="text.secondary">
          Supported columns: Address, TradeMe URL, Bedrooms, Price
        </Typography>
      </Box>

      {file && (
        <Box sx={{ mb: 3 }}>
          <Typography variant="subtitle2" gutterBottom>
            Expected CSV Format:
          </Typography>
          <List dense>
            <ListItem>
              <ListItemText
                primary="Address (required)"
                secondary="Full property address"
              />
            </ListItem>
            <ListItem>
              <ListItemText
                primary="TradeMe URL (optional)"
                secondary="Link to TradeMe listing"
              />
            </ListItem>
            <ListItem>
              <ListItemText
                primary="Bedrooms (optional)"
                secondary="Number of bedrooms"
              />
            </ListItem>
            <ListItem>
              <ListItemText
                primary="Price (optional)"
                secondary="Asking price"
              />
            </ListItem>
          </List>
        </Box>
      )}

      <Button
        variant="contained"
        size="large"
        onClick={handleUpload}
        disabled={!file || loading}
        startIcon={loading ? <CircularProgress size={20} /> : <UploadFileIcon />}
        fullWidth
      >
        {loading ? 'Uploading...' : 'Upload and Process'}
      </Button>

      {error && (
        <Alert severity="error" sx={{ mt: 2 }}>
          {error}
        </Alert>
      )}

      {success && (
        <Alert severity="success" icon={<CheckCircleIcon />} sx={{ mt: 2 }}>
          {success}
        </Alert>
      )}
    </Paper>
  );
}

export default CSVUpload;

