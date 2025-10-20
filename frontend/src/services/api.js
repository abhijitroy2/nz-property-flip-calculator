import axios from 'axios';

// Use environment variable for API URL, fallback to relative path for development
const API_BASE_URL = import.meta.env.VITE_API_URL || '/api';

const api = axios.create({
  baseURL: API_BASE_URL,
});


export const analyzeProperties = async (properties) => {
  try {
    const response = await api.post(
      '/analyze',
      { properties: properties },
      { headers: { 'Content-Type': 'application/json' } }
    );
    return response.data;
  } catch (error) {
    console.error('Error analyzing properties:', error);
    throw error;
  }
};

export const uploadCSV = async (file) => {
  try {
    const formData = new FormData();
    formData.append('file', file);
    
    // Don't set Content-Type manually - let axios handle it with proper boundary
    const response = await api.post('/upload', formData);
    
    return response.data;
  } catch (error) {
    console.error('Error uploading CSV:', error);
    throw error;
  }
};

export const getProperty = async (propertyId) => {
  try {
    const response = await api.get(`/property/${propertyId}`);
    return response.data;
  } catch (error) {
    console.error('Error getting property:', error);
    throw error;
  }
};

export const getAnalysis = async (propertyId) => {
  try {
    const response = await api.get(`/analysis/${propertyId}`);
    return response.data;
  } catch (error) {
    console.error('Error getting analysis:', error);
    throw error;
  }
};

export default api;

