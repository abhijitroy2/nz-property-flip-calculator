import React from 'react';
import { Box, Grid, Typography, Paper, Alert } from '@mui/material';
import TrendingUpIcon from '@mui/icons-material/TrendingUp';
import TrendingDownIcon from '@mui/icons-material/TrendingDown';

function ProfitCalculation({ analysis }) {
  const formatCurrency = (value) => {
    if (!value) return 'N/A';
    return new Intl.NumberFormat('en-NZ', {
      style: 'currency',
      currency: 'NZD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(value);
  };

  const isViable = analysis.is_viable;
  const profitColor = isViable ? 'success.main' : 'error.main';

  return (
    <Box>
      <Grid container spacing={2}>
        <Grid item xs={12} md={4}>
          <Paper
            sx={{
              p: 2,
              backgroundColor: 'primary.light',
              color: 'primary.contrastText',
            }}
          >
            <Typography variant="caption">Gross Profit</Typography>
            <Typography variant="h6">
              {formatCurrency(analysis.gross_profit)}
            </Typography>
          </Paper>
        </Grid>

        <Grid item xs={12} md={4}>
          <Paper
            sx={{
              p: 2,
              backgroundColor: 'info.light',
              color: 'info.contrastText',
            }}
          >
            <Typography variant="caption">Pre-Tax Profit</Typography>
            <Typography variant="h6">
              {formatCurrency(analysis.pre_tax_profit)}
            </Typography>
          </Paper>
        </Grid>

        <Grid item xs={12} md={4}>
          <Paper
            sx={{
              p: 2,
              backgroundColor: isViable ? 'success.light' : 'error.light',
              color: isViable ? 'success.contrastText' : 'error.contrastText',
            }}
          >
            <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
              <Box>
                <Typography variant="caption">Post-Tax Profit</Typography>
                <Typography variant="h6">
                  {formatCurrency(analysis.post_tax_profit)}
                </Typography>
              </Box>
              {isViable ? (
                <TrendingUpIcon fontSize="large" />
              ) : (
                <TrendingDownIcon fontSize="large" />
              )}
            </Box>
          </Paper>
        </Grid>

        {!isViable && analysis.recommended_pp && (
          <Grid item xs={12}>
            <Alert severity="warning">
              <Typography variant="body2" gutterBottom>
                <strong>Below Minimum Profit Threshold</strong>
              </Typography>
              <Typography variant="body2">
                This property generates less than $25,000 in post-tax profit. Consider negotiating the purchase price.
              </Typography>
              <Typography variant="body2" sx={{ mt: 1 }}>
                <strong>Recommended Purchase Price: {formatCurrency(analysis.recommended_pp)}</strong>
              </Typography>
              <Typography variant="caption">
                At this price, you would achieve $25,000-$30,000 post-tax profit.
              </Typography>
            </Alert>
          </Grid>
        )}

        {isViable && (
          <Grid item xs={12}>
            <Alert severity="success">
              <Typography variant="body2">
                <strong>✓ Viable Investment</strong> - This property meets the minimum profit threshold of $25,000 post-tax.
              </Typography>
            </Alert>
          </Grid>
        )}
      </Grid>
    </Box>
  );
}

export default ProfitCalculation;

