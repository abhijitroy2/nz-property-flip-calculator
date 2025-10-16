import React from 'react';
import { Chip } from '@mui/material';
import ThumbUpIcon from '@mui/icons-material/ThumbUp';
import ThumbDownIcon from '@mui/icons-material/ThumbDown';
import WarningIcon from '@mui/icons-material/Warning';

function RecommendationBadge({ analysis }) {
  if (!analysis) return null;

  const postTaxProfit = analysis.post_tax_profit || 0;
  const isViable = analysis.is_viable;

  let label, color, icon;

  if (isViable && postTaxProfit >= 50000) {
    label = 'Excellent Deal';
    color = 'success';
    icon = <ThumbUpIcon />;
  } else if (isViable) {
    label = 'Good Deal';
    color = 'success';
    icon = <ThumbUpIcon />;
  } else if (postTaxProfit >= 10000) {
    label = 'Marginal';
    color = 'warning';
    icon = <WarningIcon />;
  } else {
    label = 'Not Viable';
    color = 'error';
    icon = <ThumbDownIcon />;
  }

  return (
    <Chip
      label={label}
      color={color}
      icon={icon}
      size="medium"
      sx={{ fontWeight: 'bold' }}
    />
  );
}

export default RecommendationBadge;

