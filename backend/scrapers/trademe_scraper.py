import re
from bs4 import BeautifulSoup
from .base_scraper import BaseScraper

class TrademePropertyScraper(BaseScraper):
    """Scraper for TradeMe property listings"""
    
    BASE_URL = "https://www.trademe.co.nz"
    
    def search_properties(self, max_price=None, bedrooms=None, cities=None, limit=50):
        """
        Search TradeMe for properties matching criteria.
        
        Args:
            max_price: Maximum purchase price
            bedrooms: Number of bedrooms
            cities: List of cities/regions to search
            limit: Maximum number of results
        
        Returns:
            List of property dictionaries
        """
        properties = []
        
        # Build search URL
        search_url = f"{self.BASE_URL}/a/property/residential/sale"
        params = {}
        
        if max_price:
            params['price_max'] = int(max_price)
        
        if bedrooms:
            params['bedrooms_min'] = int(bedrooms)
            params['bedrooms_max'] = int(bedrooms)
        
        if cities:
            # TradeMe uses region codes - simplified for now
            params['search_string'] = ','.join(cities)
        
        try:
            print(f"Attempting TradeMe search with URL: {search_url}")
            print(f"Parameters: {params}")
            
            response = self.get(search_url, params=params)
            if not response:
                print("Failed to fetch TradeMe search results - no response")
                return []
            
            print(f"TradeMe response status: {response.status_code}")
            print(f"Response length: {len(response.text)} characters")
            
            # Check if we got a valid response
            if response.status_code != 200:
                print(f"TradeMe returned status {response.status_code}")
                return []
            
            # Check if we got blocked or redirected
            if len(response.text) < 1000:
                print("TradeMe response too short - likely blocked or error page")
                return []
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Try multiple selectors for property listings
            selectors = [
                'div[class*="listing"]',
                'div[class*="property"]',
                'div[class*="result"]',
                'article',
                '.listing',
                '.property-listing',
                '.search-result'
            ]
            
            listings = []
            for selector in selectors:
                found = soup.select(selector)
                if found:
                    listings = found
                    print(f"Found {len(listings)} listings using selector: {selector}")
                    break
            
            if not listings:
                print("No property listings found with any selector")
                # Save HTML for debugging
                with open('debug_trademe_search.html', 'w', encoding='utf-8') as f:
                    f.write(response.text)
                print("Saved TradeMe response to debug_trademe_search.html for inspection")
                return []
            
            for listing in listings[:limit]:
                property_data = self._parse_listing(listing)
                if property_data:
                    properties.append(property_data)
            
            print(f"Successfully parsed {len(properties)} properties from TradeMe")
            
        except Exception as e:
            print(f"Error searching TradeMe: {e}")
            import traceback
            traceback.print_exc()
        
        return properties
    
    def scrape(self, url):
        """
        Scrape a specific TradeMe property listing.
        
        Args:
            url: TradeMe property URL
        
        Returns:
            Dictionary with property details
        """
        try:
            response = self.get(url)
            if not response:
                return None
            
            soup = BeautifulSoup(response.text, 'html.parser')
            return self._parse_property_page(soup, url)
            
        except Exception as e:
            print(f"Error scraping TradeMe URL {url}: {e}")
            return None
    
    def _parse_listing(self, listing_element):
        """Parse a single listing from search results"""
        try:
            # Extract title/address - try multiple approaches
            address = None
            title_selectors = [
                ['h1', 'h2', 'h3', 'h4'],
                ['a'],
                ['.title', '.heading', '.address', '.property-title']
            ]
            
            for selector_list in title_selectors:
                for selector in selector_list:
                    if selector.startswith('.'):
                        elem = listing_element.select_one(selector)
                    else:
                        elem = listing_element.find(selector)
                    if elem:
                        address = elem.get_text(strip=True)
                        break
                if address:
                    break
            
            # Extract URL - try multiple approaches
            url = None
            link_elem = listing_element.find('a', href=True)
            if link_elem:
                href = link_elem['href']
                if href.startswith('http'):
                    url = href
                elif href.startswith('/'):
                    url = f"{self.BASE_URL}{href}"
                else:
                    url = f"{self.BASE_URL}/{href}"
            
            # Extract price - try multiple approaches
            price = None
            price_patterns = [
                r'\$[\d,]+',
                r'[\d,]+',
                r'price[:\s]*\$?[\d,]+'
            ]
            
            text_content = listing_element.get_text()
            for pattern in price_patterns:
                price_match = re.search(pattern, text_content, re.IGNORECASE)
                if price_match:
                    price = self._extract_price(price_match.group(0))
                    if price and price > 100000:  # Reasonable property price
                        break
            
            # Extract bedrooms/bathrooms
            bedrooms = self._extract_number(text_content, r'(\d+)\s*bed')
            bathrooms = self._extract_number(text_content, r'(\d+)\s*bath')
            
            # Extract area
            area = self._extract_number(text_content, r'(\d+)\s*m[²2]')
            
            if address or url:
                return {
                    'address': address,
                    'trademe_url': url,
                    'asking_price': price,
                    'bedrooms': bedrooms,
                    'bathrooms': bathrooms,
                    'floor_area': area,
                }
        
        except Exception as e:
            print(f"Error parsing listing: {e}")
        
        return None
    
    def _parse_property_page(self, soup, url):
        """Parse a full property page"""
        try:
            # Extract address
            address_elem = soup.find(['h1', 'h2'], class_=re.compile(r'address|title|heading', re.I))
            address = address_elem.get_text(strip=True) if address_elem else None
            
            # Extract price
            price_text = soup.find(text=re.compile(r'\$[\d,]+'))
            price = self._extract_price(price_text) if price_text else None
            
            # Extract property details
            text_content = soup.get_text()
            bedrooms = self._extract_number(text_content, r'(\d+)\s*bed')
            bathrooms = self._extract_number(text_content, r'(\d+)\s*bath')
            floor_area = self._extract_number(text_content, r'(\d+)\s*m[²2]')
            
            # Extract suburb/location
            suburb = None
            location_elem = soup.find(class_=re.compile(r'location|suburb|region', re.I))
            if location_elem:
                suburb = location_elem.get_text(strip=True)
            
            return {
                'address': address,
                'trademe_url': url,
                'asking_price': price,
                'bedrooms': bedrooms,
                'bathrooms': bathrooms,
                'floor_area': floor_area,
                'suburb': suburb,
            }
        
        except Exception as e:
            print(f"Error parsing property page: {e}")
            return None
    
    def _extract_price(self, text):
        """Extract price from text"""
        if not text:
            return None
        
        match = re.search(r'\$\s*([\d,]+)', str(text))
        if match:
            try:
                return float(match.group(1).replace(',', ''))
            except ValueError:
                pass
        
        return None
    
    def _extract_number(self, text, pattern):
        """Extract a number using regex pattern"""
        if not text:
            return None
        
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            try:
                return int(match.group(1))
            except ValueError:
                pass
        
        return None

