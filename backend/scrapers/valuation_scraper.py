import re
from bs4 import BeautifulSoup
from .base_scraper import BaseScraper

class ValuationScraper(BaseScraper):
    """Scraper for property valuations from homes.co.nz and similar sites"""
    
    HOMES_CO_NZ_URL = "https://homes.co.nz"
    
    def scrape(self, address):
        """
        Scrape RV/CV values for a property.
        
        Args:
            address: Property address
        
        Returns:
            Dictionary with rv, cv, and source
        """
        # Try homes.co.nz first
        result = self._scrape_homes_co_nz(address)
        if result:
            return result
        
        # Fallback: estimate based on address
        return self._estimate_valuation(address)
    
    def _scrape_homes_co_nz(self, address):
        """Scrape valuation from homes.co.nz"""
        try:
            # Clean address for search
            search_address = self._clean_address(address)
            search_url = f"{self.HOMES_CO_NZ_URL}/address"
            
            params = {'q': search_address}
            response = self.get(search_url, params=params)
            
            if not response:
                return None
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Look for valuation information
            rv = None
            cv = None
            
            # Common patterns for RV/CV on homes.co.nz
            text_content = soup.get_text()
            
            # Try to find Rateable Value
            rv_match = re.search(r'rateable\s+value[:\s]+\$?\s*([\d,]+)', text_content, re.IGNORECASE)
            if rv_match:
                rv = float(rv_match.group(1).replace(',', ''))
            
            # Try to find Capital Value
            cv_match = re.search(r'capital\s+value[:\s]+\$?\s*([\d,]+)', text_content, re.IGNORECASE)
            if cv_match:
                cv = float(cv_match.group(1).replace(',', ''))
            
            # Sometimes they use different labels
            if not cv:
                val_match = re.search(r'(?:estimated\s+)?value[:\s]+\$?\s*([\d,]+)', text_content, re.IGNORECASE)
                if val_match:
                    cv = float(val_match.group(1).replace(',', ''))
            
            if rv or cv:
                return {
                    'rv': rv,
                    'cv': cv or rv,  # Use RV if CV not found
                    'source': 'homes.co.nz'
                }
        
        except Exception as e:
            print(f"Error scraping homes.co.nz: {e}")
        
        return None
    
    def _estimate_valuation(self, address):
        """Estimate valuation based on address location"""
        import hashlib
        
        address_lower = address.lower()
        
        # Base values by city/region
        city_values = {
            'auckland': 1200000,
            'wellington': 950000,
            'christchurch': 650000,
            'hamilton': 580000,
            'tauranga': 720000,
            'dunedin': 520000,
            'palmerston north': 480000,
            'nelson': 680000,
            'rotorua': 450000,
            'napier': 550000,
            'hastings': 520000,
            'new plymouth': 500000,
            # Premium Auckland suburbs
            'remuera': 2000000,
            'ponsonby': 1800000,
            'parnell': 1900000,
            'takapuna': 1700000,
            'epsom': 1750000,
            'herne bay': 2200000,
            'mission bay': 1650000,
        }
        
        # Find matching city
        base_value = 650000  # Default NZ average
        for city, value in city_values.items():
            if city in address_lower:
                base_value = value
                break
        
        # Add deterministic variation based on address
        hash_val = int(hashlib.md5(address.encode()).hexdigest()[:8], 16)
        variation = 0.85 + (hash_val % 30) / 100  # 0.85 to 1.15
        
        estimated_cv = base_value * variation
        estimated_rv = estimated_cv * 0.95  # RV typically slightly lower
        
        return {
            'rv': round(estimated_rv, -3),  # Round to nearest 1000
            'cv': round(estimated_cv, -3),
            'source': 'Estimated (scraping unavailable)'
        }
    
    def _clean_address(self, address):
        """Clean address for search"""
        # Remove extra whitespace
        address = re.sub(r'\s+', ' ', address.strip())
        # Remove "New Zealand", "NZ"
        address = address.replace('New Zealand', '').replace('NZ', '').replace('  ', ' ')
        return address.strip()

