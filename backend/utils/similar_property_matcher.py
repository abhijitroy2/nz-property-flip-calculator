class SimilarPropertyMatcher:
    """Find comparable/similar properties based on criteria"""
    
    def find_comparables(self, sales, target_suburb, target_bedrooms, target_floor_area):
        """
        Filter sales to find comparable properties.
        
        Criteria:
        - Same suburb
        - Same number of bedrooms
        - ±20% floor area
        
        Args:
            sales: List of RecentSale objects or dictionaries
            target_suburb: Target suburb
            target_bedrooms: Target number of bedrooms
            target_floor_area: Target floor area in sqm
        
        Returns:
            List of comparable sales
        """
        if not sales:
            return []
        
        comparables = []
        
        for sale in sales:
            # Extract data whether it's a model object or dictionary
            if hasattr(sale, 'suburb'):
                suburb = sale.suburb
                bedrooms = sale.bedrooms
                floor_area = sale.floor_area
            else:
                suburb = sale.get('suburb')
                bedrooms = sale.get('bedrooms')
                floor_area = sale.get('floor_area')
            
            # Check suburb match
            if not self._suburbs_match(suburb, target_suburb):
                continue
            
            # Check bedrooms match
            if bedrooms != target_bedrooms:
                continue
            
            # Check floor area within ±20%
            if floor_area and target_floor_area:
                area_diff_pct = abs(floor_area - target_floor_area) / target_floor_area
                if area_diff_pct > 0.20:  # More than 20% difference
                    continue
            
            comparables.append(sale)
        
        return comparables
    
    def _suburbs_match(self, suburb1, suburb2):
        """Check if two suburbs match (case-insensitive, flexible)"""
        if not suburb1 or not suburb2:
            return False
        
        # Normalize suburbs
        s1 = suburb1.lower().strip()
        s2 = suburb2.lower().strip()
        
        return s1 == s2
    
    def calculate_average_sale_price(self, comparables):
        """Calculate average sale price from comparable sales"""
        if not comparables:
            return None
        
        total = 0
        count = 0
        
        for sale in comparables:
            # Extract price whether it's a model object or dictionary
            if hasattr(sale, 'sale_price'):
                price = sale.sale_price
            else:
                price = sale.get('sale_price')
            
            if price:
                total += price
                count += 1
        
        if count == 0:
            return None
        
        return total / count

