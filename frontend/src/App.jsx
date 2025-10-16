import React, { useState } from 'react';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import { Container, Box, Typography, AppBar, Toolbar } from '@mui/material';
import CssBaseline from '@mui/material/CssBaseline';

import CSVUpload from './components/CSVUpload';
import PropertyList from './components/PropertyList';

const theme = createTheme({
  palette: {
    primary: {
      main: '#1976d2',
    },
    secondary: {
      main: '#dc004e',
    },
    success: {
      main: '#2e7d32',
    },
    warning: {
      main: '#ed6c02',
    },
  },
});

function App() {
  const [properties, setProperties] = useState([]);
  const [loading, setLoading] = useState(false);

  const handleUploadResults = (results) => {
    setProperties(results);
  };

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Box sx={{ flexGrow: 1 }}>
        <AppBar position="static">
          <Toolbar>
            <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
              NZ Property Flip Calculator
            </Typography>
          </Toolbar>
        </AppBar>

        <Container maxWidth="xl" sx={{ mt: 4, mb: 4 }}>
          <Box sx={{ mt: 3 }}>
            <CSVUpload onResults={handleUploadResults} />
            
            {properties.length > 0 && (
              <PropertyList 
                properties={properties} 
                loading={loading}
              />
            )}
          </Box>
        </Container>
      </Box>
    </ThemeProvider>
  );
}

export default App;

