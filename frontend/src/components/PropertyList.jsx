import React, { useState } from 'react';
import {
  Box,
  Paper,
  Typography,
  Button,
  Grid,
  CircularProgress,
  Alert,
} from '@mui/material';
import AnalyticsIcon from '@mui/icons-material/Analytics';
import PropertyCard from './PropertyCard';
import { analyzeProperties } from '../services/api';

function PropertyList({ properties, loading: parentLoading }) {
  const [analyzing, setAnalyzing] = useState(false);
  const [analyzed, setAnalyzed] = useState(false);
  const [analysisResults, setAnalysisResults] = useState([]);
  const [error, setError] = useState(null);

  const handleAnalyzeAll = async () => {
    setAnalyzing(true);
    setError(null);

    try {
      const response = await analyzeProperties(properties);

      if (response.success) {
        setAnalysisResults(response.results);
        setAnalyzed(true);
      } else {
        setError(response.error || 'Failed to analyze properties');
      }
    } catch (err) {
      setError(err.response?.data?.error || 'An error occurred during analysis');
    } finally {
      setAnalyzing(false);
    }
  };

  if (parentLoading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', p: 4 }}>
        <CircularProgress />
      </Box>
    );
  }

  if (properties.length === 0) {
    return (
      <Paper sx={{ p: 3, textAlign: 'center' }}>
        <Typography color="text.secondary">
          No properties found. Try adjusting your search criteria.
        </Typography>
      </Paper>
    );
  }

  return (
    <Box>
      <Paper sx={{ p: 2, mb: 3, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Typography variant="h6">
          Found {properties.length} {properties.length === 1 ? 'Property' : 'Properties'}
        </Typography>
        {!analyzed && (
          <Button
            variant="contained"
            color="secondary"
            startIcon={analyzing ? <CircularProgress size={20} /> : <AnalyticsIcon />}
            onClick={handleAnalyzeAll}
            disabled={analyzing}
          >
            {analyzing ? 'Analyzing...' : 'Analyze All Properties'}
          </Button>
        )}
      </Paper>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}

      {analyzing && (
        <Paper sx={{ p: 3, mb: 3, textAlign: 'center' }}>
          <CircularProgress sx={{ mb: 2 }} />
          <Typography variant="body1">
            Analyzing properties... This may take a few minutes as we scrape valuation data, recent sales, and insurance quotes.
          </Typography>
        </Paper>
      )}

      <Grid container spacing={3}>
        {analyzed ? (
          analysisResults.map((result) => (
            <Grid item xs={12} key={result.property.id}>
              <PropertyCard
                property={result.property}
                analysis={result.analysis}
                valuation={result.valuation}
              />
            </Grid>
          ))
        ) : (
          properties.map((property) => (
            <Grid item xs={12} key={property.id}>
              <PropertyCard property={property} />
            </Grid>
          ))
        )}
      </Grid>
    </Box>
  );
}

export default PropertyList;

