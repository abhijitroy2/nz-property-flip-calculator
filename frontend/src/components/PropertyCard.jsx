import React, { useState } from 'react';
import {
  Card,
  CardContent,
  Typography,
  Grid,
  Chip,
  Box,
  Divider,
  Button,
  Collapse,
  Link,
} from '@mui/material';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import ExpandLessIcon from '@mui/icons-material/ExpandLess';
import HomeIcon from '@mui/icons-material/Home';
import BedIcon from '@mui/icons-material/Bed';
import BathtubIcon from '@mui/icons-material/Bathtub';
import SquareFootIcon from '@mui/icons-material/SquareFoot';
import ProfitCalculation from './ProfitCalculation';
import RecommendationBadge from './RecommendationBadge';

function PropertyCard({ property, analysis, valuation }) {
  const [expanded, setExpanded] = useState(false);

  const formatCurrency = (value) => {
    if (!value) return 'N/A';
    return new Intl.NumberFormat('en-NZ', {
      style: 'currency',
      currency: 'NZD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(value);
  };

  return (
    <Card sx={{ position: 'relative' }}>
      {analysis && (
        <Box sx={{ position: 'absolute', top: 16, right: 16 }}>
          <RecommendationBadge analysis={analysis} />
        </Box>
      )}

      <CardContent>
        <Grid container spacing={2}>
          <Grid item xs={12}>
            <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
              <HomeIcon sx={{ mr: 1, color: 'primary.main' }} />
              <Typography variant="h6">{property.address}</Typography>
            </Box>
            {property.suburb && (
              <Typography variant="body2" color="text.secondary" gutterBottom>
                {property.suburb}
              </Typography>
            )}
          </Grid>

          <Grid item xs={12} sm={6} md={3}>
            <Box sx={{ display: 'flex', alignItems: 'center' }}>
              <BedIcon sx={{ mr: 1, fontSize: 'small', color: 'text.secondary' }} />
              <Typography variant="body2">
                {property.bedrooms ? `${property.bedrooms} bed` : 'N/A'}
              </Typography>
            </Box>
          </Grid>

          <Grid item xs={12} sm={6} md={3}>
            <Box sx={{ display: 'flex', alignItems: 'center' }}>
              <BathtubIcon sx={{ mr: 1, fontSize: 'small', color: 'text.secondary' }} />
              <Typography variant="body2">
                {property.bathrooms ? `${property.bathrooms} bath` : 'N/A'}
              </Typography>
            </Box>
          </Grid>

          <Grid item xs={12} sm={6} md={3}>
            <Box sx={{ display: 'flex', alignItems: 'center' }}>
              <SquareFootIcon sx={{ mr: 1, fontSize: 'small', color: 'text.secondary' }} />
              <Typography variant="body2">
                {property.floor_area ? `${property.floor_area} m²` : 'N/A'}
              </Typography>
            </Box>
          </Grid>

          <Grid item xs={12} sm={6} md={3}>
            <Typography variant="body2" color="text.secondary">
              {property.asking_price ? 'Asking Price' : 'Sale Method'}
            </Typography>
            <Typography variant="h6" color="primary">
              {property.asking_price ? formatCurrency(property.asking_price) : (property.sale_method || 'N/A')}
            </Typography>
          </Grid>

          {property.trademe_url && (
            <Grid item xs={12}>
              <Link 
                href={property.trademe_url} 
                target="_blank" 
                rel="noopener noreferrer"
                sx={{ textDecoration: 'none', color: 'primary.main' }}
              >
                View on TradeMe
              </Link>
            </Grid>
          )}

          {analysis && (
            <>
              <Grid item xs={12}>
                <Divider sx={{ my: 1 }} />
              </Grid>

              <Grid item xs={12}>
                <ProfitCalculation analysis={analysis} valuation={valuation} />
              </Grid>

              <Grid item xs={12}>
                <Button
                  fullWidth
                  onClick={() => setExpanded(!expanded)}
                  endIcon={expanded ? <ExpandLessIcon /> : <ExpandMoreIcon />}
                >
                  {expanded ? 'Hide' : 'Show'} Detailed Breakdown
                </Button>
              </Grid>

              <Grid item xs={12}>
                <Collapse in={expanded}>
                  <Box sx={{ mt: 2 }}>
                    <Typography variant="subtitle2" gutterBottom>
                      Financial Breakdown
                    </Typography>
                    <Grid container spacing={1}>
                      <Grid item xs={6}>
                        <Typography variant="body2" color="text.secondary">
                          Purchase Price (PP):
                        </Typography>
                      </Grid>
                      <Grid item xs={6}>
                        <Typography variant="body2">{formatCurrency(analysis.pp)}</Typography>
                      </Grid>

                      <Grid item xs={6}>
                        <Typography variant="body2" color="text.secondary">
                          Rateable Value (RV):
                        </Typography>
                      </Grid>
                      <Grid item xs={6}>
                        <Typography variant="body2">{formatCurrency(analysis.rv)}</Typography>
                      </Grid>

                      <Grid item xs={6}>
                        <Typography variant="body2" color="text.secondary">
                          Capital Value (CV):
                        </Typography>
                      </Grid>
                      <Grid item xs={6}>
                        <Typography variant="body2">{formatCurrency(analysis.cv)}</Typography>
                      </Grid>

                      <Grid item xs={6}>
                        <Typography variant="body2" color="text.secondary">
                          Target Sale Value (TV):
                        </Typography>
                      </Grid>
                      <Grid item xs={6}>
                        <Typography variant="body2" fontWeight="bold">
                          {formatCurrency(analysis.tv)}
                        </Typography>
                      </Grid>

                      <Grid item xs={12}>
                        <Divider sx={{ my: 1 }} />
                      </Grid>

                      <Grid item xs={6}>
                        <Typography variant="body2" color="text.secondary">
                          Renovation Budget (RB):
                        </Typography>
                      </Grid>
                      <Grid item xs={6}>
                        <Typography variant="body2">{formatCurrency(analysis.rb)}</Typography>
                      </Grid>

                      <Grid item xs={6}>
                        <Typography variant="body2" color="text.secondary">
                          Insurance (INS):
                        </Typography>
                      </Grid>
                      <Grid item xs={6}>
                        <Typography variant="body2">{formatCurrency(analysis.ins)}</Typography>
                      </Grid>

                      <Grid item xs={6}>
                        <Typography variant="body2" color="text.secondary">
                          Legal Expenses (LE):
                        </Typography>
                      </Grid>
                      <Grid item xs={6}>
                        <Typography variant="body2">{formatCurrency(analysis.le)}</Typography>
                      </Grid>

                      <Grid item xs={6}>
                        <Typography variant="body2" color="text.secondary">
                          Council Rates (CR):
                        </Typography>
                      </Grid>
                      <Grid item xs={6}>
                        <Typography variant="body2">{formatCurrency(analysis.cr)}</Typography>
                      </Grid>

                      <Grid item xs={6}>
                        <Typography variant="body2" color="text.secondary">
                          Commission (COM):
                        </Typography>
                      </Grid>
                      <Grid item xs={6}>
                        <Typography variant="body2">{formatCurrency(analysis.com)}</Typography>
                      </Grid>

                      <Grid item xs={6}>
                        <Typography variant="body2" color="text.secondary">
                          Interest Cost (INT):
                        </Typography>
                      </Grid>
                      <Grid item xs={6}>
                        <Typography variant="body2">{formatCurrency(analysis.int_cost)}</Typography>
                      </Grid>

                      <Grid item xs={6}>
                        <Typography variant="body2" color="text.secondary">
                          Interest Rate:
                        </Typography>
                      </Grid>
                      <Grid item xs={6}>
                        <Typography variant="body2">{analysis.int_rate}% p.a.</Typography>
                      </Grid>

                      <Grid item xs={6}>
                        <Typography variant="body2" color="text.secondary">
                          Renovation Period:
                        </Typography>
                      </Grid>
                      <Grid item xs={6}>
                        <Typography variant="body2">{analysis.renovation_months} months</Typography>
                      </Grid>

                      <Grid item xs={12}>
                        <Divider sx={{ my: 1 }} />
                      </Grid>

                      <Grid item xs={6}>
                        <Typography variant="body2" color="text.secondary">
                          GST Claimable:
                        </Typography>
                      </Grid>
                      <Grid item xs={6}>
                        <Typography variant="body2" color="success.main">
                          {formatCurrency(analysis.gst_claimable)}
                        </Typography>
                      </Grid>

                      <Grid item xs={6}>
                        <Typography variant="body2" color="text.secondary">
                          GST Payable:
                        </Typography>
                      </Grid>
                      <Grid item xs={6}>
                        <Typography variant="body2" color="error.main">
                          {formatCurrency(analysis.gst_payable)}
                        </Typography>
                      </Grid>

                      <Grid item xs={6}>
                        <Typography variant="body2" color="text.secondary">
                          Net GST:
                        </Typography>
                      </Grid>
                      <Grid item xs={6}>
                        <Typography variant="body2">
                          {formatCurrency(analysis.net_gst)}
                        </Typography>
                      </Grid>
                    </Grid>

                    {valuation && (
                      <Box sx={{ mt: 2 }}>
                        <Typography variant="caption" color="text.secondary">
                          Valuation Source: {valuation.source}
                        </Typography>
                      </Box>
                    )}
                  </Box>
                </Collapse>
              </Grid>
            </>
          )}
        </Grid>
      </CardContent>
    </Card>
  );
}

export default PropertyCard;

