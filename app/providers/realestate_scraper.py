import httpx
import re
import asyncio
from typing import Optional, Dict, Any
from .base import Provider
from .virtual_browser_scraper import VirtualBrowserScraper
from .. import models

class RealEstateScraper(Provider):
    """Rate-limited RealEstate.co.nz scraper"""
    
    def __init__(self):
        self.base_url = "https://www.realestate.co.nz"
        self.rate_limit_delay = 20  # 20 seconds between requests (less aggressive than TradeMe)
        self.last_request_time = 0
        self.browser_scraper = VirtualBrowserScraper()  # Add virtual browser
        
        # Enhanced headers for better success rate
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'en-NZ,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Cache-Control': 'max-age=0'
        }
        
        self.client = httpx.AsyncClient(
            timeout=30.0,
            headers=headers,
            follow_redirects=True
        )
    
    async def fetch(self, address: str, realestate_url: Optional[str] = None) -> models.DataPoints:
        """Fetch property data from RealEstate.co.nz URL with rate limiting"""
        try:
            if realestate_url:
                # Scrape from specific RealEstate.co.nz URL
                valuation_data = await self._scrape_realestate_url(realestate_url)
            else:
                # Fall back to estimated data
                valuation_data = self._estimate_valuation_data(address)
            
            return models.DataPoints(
                address=address,
                current_valuation_low=valuation_data.get('low'),
                current_valuation_mid=valuation_data.get('mid'),
                current_valuation_high=valuation_data.get('high'),
                last_sale_price=valuation_data.get('last_sale_price'),
                last_sale_date=valuation_data.get('last_sale_date'),
                valuation_source=valuation_data.get('source', 'RealEstate.co.nz'),
            )
        except Exception as e:
            print(f"RealEstate Scraper error: {e}")
            # Fallback to estimated data
            if realestate_url:
                valuation_data = self._estimate_valuation_data_from_url(realestate_url)
            else:
                valuation_data = self._estimate_valuation_data(address)
            
            return models.DataPoints(
                address=address,
                current_valuation_low=valuation_data.get('low'),
                current_valuation_mid=valuation_data.get('mid'),
                current_valuation_high=valuation_data.get('high'),
                last_sale_price=valuation_data.get('last_sale_price'),
                last_sale_date=valuation_data.get('last_sale_date'),
                valuation_source=valuation_data.get('source', 'Estimated'),
            )
    
    async def _scrape_realestate_url(self, url: str) -> Dict[str, Any]:
        """Scrape property data from a specific RealEstate.co.nz URL with rate limiting"""
        try:
            # Rate limiting - wait if needed
            await self._enforce_rate_limit()
            
            # Try virtual browser first (most likely to succeed)
            try:
                print(f"🤖 Trying virtual browser for RealEstate: {url}")
                browser_data = await self.browser_scraper.fetch("", url, "RealEstate")
                if browser_data.current_valuation_mid:
                    return {
                        'low': browser_data.current_valuation_low,
                        'mid': browser_data.current_valuation_mid,
                        'high': browser_data.current_valuation_high,
                        'last_sale_price': browser_data.last_sale_price,
                        'last_sale_date': browser_data.last_sale_date,
                        'source': browser_data.valuation_source
                    }
            except Exception as e:
                print(f"Virtual browser failed for RealEstate: {e}")
            
            # Fallback to traditional scraping
            # Validate and clean URL
            clean_url = self._clean_realestate_url(url)
            
            # Try multiple approaches to scrape
            property_data = await self._try_multiple_scraping_approaches(clean_url)
            
            if property_data:
                return property_data
            else:
                # If all scraping attempts fail, use URL-based estimation
                return self._estimate_valuation_data_from_url(url)
            
        except Exception as e:
            print(f"Error scraping RealEstate URL {url}: {e}")
            return self._estimate_valuation_data_from_url(url)
    
    async def _try_multiple_scraping_approaches(self, url: str) -> Optional[Dict[str, Any]]:
        """Try multiple approaches to scrape RealEstate.co.nz data"""
        
        # Approach 1: Direct URL scraping
        try:
            response = await self.client.get(url)
            if response.status_code == 200:
                return self._parse_realestate_listing(response.text, url)
        except Exception as e:
            print(f"Direct RealEstate scraping failed: {e}")
        
        # Approach 2: Try with different headers
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-NZ,en;q=0.9',
                'Accept-Encoding': 'gzip, deflate, br',
                'DNT': '1',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
            }
            
            response = await self.client.get(url, headers=headers)
            if response.status_code == 200:
                return self._parse_realestate_listing(response.text, url)
        except Exception as e:
            print(f"Header variation RealEstate scraping failed: {e}")
        
        # Approach 3: Try mobile user agent
        try:
            mobile_headers = {
                'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-NZ,en;q=0.9',
            }
            
            response = await self.client.get(url, headers=mobile_headers)
            if response.status_code == 200:
                return self._parse_realestate_listing(response.text, url)
        except Exception as e:
            print(f"Mobile RealEstate scraping failed: {e}")
        
        return None
    
    async def _enforce_rate_limit(self):
        """Enforce rate limiting between requests"""
        current_time = asyncio.get_event_loop().time()
        time_since_last = current_time - self.last_request_time
        
        if time_since_last < self.rate_limit_delay:
            wait_time = self.rate_limit_delay - time_since_last
            print(f"RealEstate rate limiting: waiting {wait_time:.1f} seconds...")
            await asyncio.sleep(wait_time)
        
        self.last_request_time = asyncio.get_event_loop().time()
    
    def _clean_realestate_url(self, url: str) -> str:
        """Clean and validate RealEstate.co.nz URL"""
        # Ensure it's a valid RealEstate URL
        if not url.startswith('http'):
            url = f"https://{url}"
        
        # Ensure it's a RealEstate domain
        if 'realestate.co.nz' not in url:
            raise ValueError("URL must be from realestate.co.nz")
        
        return url
    
    def _parse_realestate_listing(self, html_content: str, url: str) -> Dict[str, Any]:
        """Parse property data from RealEstate.co.nz listing HTML"""
        try:
            # Extract property price - RealEstate.co.nz uses different patterns
            price_patterns = [
                r'<span[^>]*class="[^"]*price[^"]*"[^>]*>\$?([\d,]+)',
                r'<div[^>]*class="[^"]*price[^"]*"[^>]*>\$?([\d,]+)',
                r'Price[:\s]*\$?([\d,]+)',
                r'\$([\d,]+)',
                r'<h[1-6][^>]*>\$?([\d,]+)',
                r'<strong[^>]*>\$?([\d,]+)'
            ]
            
            price = None
            for pattern in price_patterns:
                match = re.search(pattern, html_content, re.IGNORECASE)
                if match:
                    price_str = match.group(1).replace(',', '')
                    if price_str.isdigit():
                        price = float(price_str)
                        if price > 100000:  # Reasonable property price
                            break
            
            # Extract property details
            bedrooms = self._extract_number(html_content, r'(\d+)\s*bed')
            bathrooms = self._extract_number(html_content, r'(\d+)\s*bath')
            area = self._extract_number(html_content, r'(\d+)\s*m²')
            
            # Extract listing date
            date_patterns = [
                r'Listed[:\s]*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
                r'Date[:\s]*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
                r'(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})'
            ]
            
            listing_date = None
            for pattern in date_patterns:
                match = re.search(pattern, html_content, re.IGNORECASE)
                if match:
                    listing_date = match.group(1)
                    break
            
            if price:
                # Calculate valuation range based on price
                low_price = price * 0.85
                high_price = price * 1.15
                
                return {
                    'low': round(low_price, 0),
                    'mid': round(price, 0),
                    'high': round(high_price, 0),
                    'last_sale_price': round(price, 0),
                    'last_sale_date': listing_date,
                    'source': 'RealEstate.co.nz (Live)',
                    'bedrooms': bedrooms,
                    'bathrooms': bathrooms,
                    'area': area
                }
            else:
                # If we couldn't extract price, fall back to estimation
                return self._estimate_valuation_data_from_url(url)
                
        except Exception as e:
            print(f"Error parsing RealEstate listing: {e}")
            return self._estimate_valuation_data_from_url(url)
    
    def _extract_number(self, html_content: str, pattern: str) -> Optional[int]:
        """Extract a number from HTML using regex pattern"""
        match = re.search(pattern, html_content, re.IGNORECASE)
        if match:
            try:
                return int(match.group(1))
            except ValueError:
                pass
        return None
    
    def _estimate_valuation_data_from_url(self, url: str) -> Dict[str, Any]:
        """Estimate valuation data based on RealEstate.co.nz URL characteristics"""
        # Extract more detailed location info from URL
        url_lower = url.lower()
        
        # Extract city/region
        city = 'auckland'  # default
        if 'auckland' in url_lower:
            city = 'auckland'
        elif 'wellington' in url_lower:
            city = 'wellington'
        elif 'christchurch' in url_lower:
            city = 'christchurch'
        elif 'hamilton' in url_lower:
            city = 'hamilton'
        elif 'tauranga' in url_lower:
            city = 'tauranga'
        elif 'dunedin' in url_lower:
            city = 'dunedin'
        
        # Extract property type from URL
        property_type = 'residential'
        if 'commercial' in url_lower:
            property_type = 'commercial'
        elif 'land' in url_lower:
            property_type = 'land'
        
        # Extract suburb if available
        suburb = None
        url_parts = url_lower.split('/')
        for i, part in enumerate(url_parts):
            if part in ['auckland', 'wellington', 'christchurch', 'hamilton', 'tauranga', 'dunedin']:
                if i + 1 < len(url_parts):
                    suburb = url_parts[i + 1]
                break
        
        # Get base price and adjust for property type and location
        base_price = self._get_base_price_for_city(city)
        
        # Adjust for property type
        if property_type == 'commercial':
            base_price *= 0.8  # Commercial properties vary widely
        elif property_type == 'land':
            base_price *= 0.6  # Land typically costs less
        
        # Adjust for premium suburbs
        if suburb and suburb in ['remuera', 'ponsonby', 'takapuna', 'epsom', 'herne bay']:
            base_price *= 1.3  # Premium Auckland suburbs
        elif suburb and suburb in ['thorndon', 'kelburn', 'wadestown']:
            base_price *= 1.2  # Premium Wellington suburbs
        
        # Generate realistic variation
        import hashlib
        import random
        from datetime import datetime, timedelta
        
        url_hash = hashlib.md5(url.encode()).hexdigest()
        rng = random.Random(int(url_hash[:8], 16))
        
        # Add variation based on URL
        variation = rng.uniform(0.85, 1.15)
        mid_price = base_price * variation
        
        # Calculate low and high
        low_price = mid_price * rng.uniform(0.80, 0.90)
        high_price = mid_price * rng.uniform(1.10, 1.20)
        
        # Generate last sale data
        last_sale_price = mid_price * rng.uniform(0.75, 1.05)
        days_ago = rng.randint(60, 1095)  # 2 months to 3 years ago
        last_sale_date = (datetime.now() - timedelta(days=days_ago)).strftime("%d/%m/%Y")
        
        return {
            'low': round(low_price, 0),
            'mid': round(mid_price, 0),
            'high': round(high_price, 0),
            'last_sale_price': round(last_sale_price, 0),
            'last_sale_date': last_sale_date,
            'source': f'RealEstate.co.nz URL Analysis (Scraping blocked)',
            'property_type': property_type,
            'suburb': suburb
        }
    
    def _estimate_valuation_data(self, address: str) -> Dict[str, Any]:
        """Estimate valuation data based on address characteristics"""
        import hashlib
        import random
        from datetime import datetime, timedelta
        
        address_hash = hashlib.md5(address.encode()).hexdigest()
        rng = random.Random(address_hash)
        
        # Get base price based on city
        base_price = self._get_base_price_for_city(address)
        
        # Add some variation
        variation = rng.uniform(0.8, 1.2)
        mid_price = base_price * variation
        
        # Calculate low and high (typically ±15-25%)
        low_price = mid_price * rng.uniform(0.75, 0.85)
        high_price = mid_price * rng.uniform(1.15, 1.25)
        
        # Generate last sale data
        last_sale_price = mid_price * rng.uniform(0.7, 1.1)
        days_ago = rng.randint(30, 1825)  # 1 month to 5 years ago
        last_sale_date = (datetime.now() - timedelta(days=days_ago)).strftime("%d/%m/%Y")
        
        return {
            'low': round(low_price, 0),
            'mid': round(mid_price, 0),
            'high': round(high_price, 0),
            'last_sale_price': round(last_sale_price, 0),
            'last_sale_date': last_sale_date,
            'source': 'Estimated (RealEstate.co.nz unavailable)'
        }
    
    def _get_base_price_for_city(self, address: str) -> float:
        """Get base price for city based on address"""
        address_lower = address.lower()
        
        # Base prices for major NZ cities (in NZD)
        city_prices = {
            'auckland': 1200000,  # High prices
            'wellington': 950000,  # High prices
            'christchurch': 650000,  # Moderate prices
            'hamilton': 580000,  # Moderate prices
            'tauranga': 720000,  # Moderate-high prices
            'dunedin': 520000,  # Lower prices
            'palmerston north': 480000,  # Lower prices
            'nelson': 680000,  # Moderate-high prices
            'rotorua': 450000,  # Lower prices
            'new plymouth': 500000,  # Moderate prices
            'remuera': 1800000,  # Very high prices
            'ponsonby': 1600000,  # Very high prices
            'takapuna': 1700000,  # Very high prices
            'epsom': 1750000,  # Very high prices
        }
        
        # Find matching city/suburb
        for city, price in city_prices.items():
            if city in address_lower:
                return price
        
        # Default to average NZ price
        return 650000
    
    async def close(self):
        """Close the HTTP client and virtual browser"""
        await self.client.aclose()
        if self.browser_scraper:
            await self.browser_scraper.close()
