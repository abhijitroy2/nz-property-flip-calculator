import re
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
from .base_scraper import BaseScraper

class SalesScraper(BaseScraper):
    """Scraper for recent comparable property sales"""
    
    def scrape(self, suburb, bedrooms, floor_area, months=3):
        """
        Find recent sales of comparable properties.
        
        Criteria:
        - Same suburb
        - Same number of bedrooms
        - ±20% floor area
        - Within last {months} months
        
        Args:
            suburb: Suburb name
            bedrooms: Number of bedrooms
            floor_area: Floor area in sqm
            months: Lookback period in months
        
        Returns:
            List of comparable sales or None
        """
        try:
            # Try multiple sources
            sales = self._scrape_realestate_co_nz(suburb, bedrooms, floor_area, months)
            if sales:
                return sales
            
            # Fallback to homes.co.nz
            sales = self._scrape_homes_co_nz(suburb, bedrooms, floor_area, months)
            if sales:
                return sales
            
            # If no sales found, return None (will use 90% of CV as per requirements)
            return None
        
        except Exception as e:
            print(f"Error scraping sales data: {e}")
            return None
    
    def _scrape_realestate_co_nz(self, suburb, bedrooms, floor_area, months):
        """Scrape sales from realestate.co.nz"""
        try:
            search_url = "https://www.realestate.co.nz/recently-sold"
            
            params = {
                'suburb': suburb,
                'bedrooms': bedrooms,
            }
            
            response = self.get(search_url, params=params)
            if not response:
                return None
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Parse sold properties
            sales = []
            listings = soup.find_all('div', class_=re.compile(r'listing|property|result', re.I))
            
            cutoff_date = datetime.now() - timedelta(days=months * 30)
            
            for listing in listings:
                sale_data = self._parse_sale_listing(listing, floor_area, cutoff_date)
                if sale_data:
                    sales.append(sale_data)
            
            return sales if sales else None
        
        except Exception as e:
            print(f"Error scraping realestate.co.nz: {e}")
            return None
    
    def _scrape_homes_co_nz(self, suburb, bedrooms, floor_area, months):
        """Scrape sales from homes.co.nz"""
        try:
            search_url = "https://homes.co.nz/sold"
            
            params = {'suburb': suburb}
            
            response = self.get(search_url, params=params)
            if not response:
                return None
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            sales = []
            listings = soup.find_all(['div', 'article'], class_=re.compile(r'property|listing|sale', re.I))
            
            cutoff_date = datetime.now() - timedelta(days=months * 30)
            
            for listing in listings:
                sale_data = self._parse_sale_listing(listing, floor_area, cutoff_date)
                if sale_data and sale_data.get('bedrooms') == bedrooms:
                    sales.append(sale_data)
            
            return sales if sales else None
        
        except Exception as e:
            print(f"Error scraping homes.co.nz: {e}")
            return None
    
    def _parse_sale_listing(self, listing_element, target_floor_area, cutoff_date):
        """Parse a single sale listing"""
        try:
            text_content = listing_element.get_text()
            
            # Extract price
            price_match = re.search(r'\$\s*([\d,]+)', text_content)
            if not price_match:
                return None
            
            price = float(price_match.group(1).replace(',', ''))
            
            # Extract bedrooms
            bed_match = re.search(r'(\d+)\s*bed', text_content, re.IGNORECASE)
            bedrooms = int(bed_match.group(1)) if bed_match else None
            
            # Extract floor area
            area_match = re.search(r'(\d+)\s*m[²2]', text_content, re.IGNORECASE)
            floor_area = int(area_match.group(1)) if area_match else None
            
            # Check floor area is within ±20%
            if floor_area and target_floor_area:
                area_diff = abs(floor_area - target_floor_area) / target_floor_area
                if area_diff > 0.20:  # More than 20% difference
                    return None
            
            # Extract sale date
            date_match = re.search(r'sold[:\s]+(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})', text_content, re.IGNORECASE)
            sale_date = None
            if date_match:
                try:
                    date_str = date_match.group(1)
                    # Try to parse various date formats
                    for fmt in ['%d/%m/%Y', '%d-%m-%Y', '%d/%m/%y', '%d-%m-%y']:
                        try:
                            sale_date = datetime.strptime(date_str, fmt).date()
                            break
                        except ValueError:
                            continue
                except Exception:
                    pass
            
            # Check if sale is recent enough
            if sale_date and sale_date < cutoff_date.date():
                return None
            
            # Extract address
            address_elem = listing_element.find(['h3', 'h4', 'a'], class_=re.compile(r'address|title', re.I))
            address = address_elem.get_text(strip=True) if address_elem else None
            
            return {
                'address': address,
                'bedrooms': bedrooms,
                'floor_area': floor_area,
                'sale_price': price,
                'sale_date': sale_date,
            }
        
        except Exception as e:
            print(f"Error parsing sale listing: {e}")
            return None

