import axios from 'axios';

const API_BASE_URL = '/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});


export const analyzeProperties = async (propertyIds) => {
  try {
    const response = await api.post('/analyze', { property_ids: propertyIds });
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
    
    const response = await api.post('/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    
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

