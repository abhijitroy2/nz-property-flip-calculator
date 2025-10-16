import re
from bs4 import BeautifulSoup
from .base_scraper import BaseScraper
from config import Config

class InsuranceScraper(BaseScraper):
    """
    Scraper for house insurance quotes.
    
    Note: Insurance sites are difficult to scrape and often require
    detailed forms. This implementation attempts scraping but falls back
    to default value as per requirements.
    """
    
    def scrape(self, address, replacement_value=None):
        """
        Attempt to get insurance quote.
        
        Args:
            address: Property address
            replacement_value: Estimated replacement value
        
        Returns:
            Insurance cost (falls back to Config.DEFAULT_INSURANCE)
        """
        # Try to scrape from major providers
        quote = self._try_scrape_quote(address, replacement_value)
        
        if quote:
            return quote
        
        # Fallback to default as per requirements
        print(f"Insurance scraping failed, using default: ${Config.DEFAULT_INSURANCE}")
        return Config.DEFAULT_INSURANCE
    
    def _try_scrape_quote(self, address, replacement_value):
        """Attempt to scrape insurance quotes"""
        try:
            # Try AMI (one of NZ's major insurers)
            quote = self._scrape_ami(address, replacement_value)
            if quote:
                return quote
            
            # Try State Insurance
            quote = self._scrape_state(address, replacement_value)
            if quote:
                return quote
            
            # Try AA Insurance
            quote = self._scrape_aa_insurance(address, replacement_value)
            if quote:
                return quote
        
        except Exception as e:
            print(f"Error scraping insurance quotes: {e}")
        
        return None
    
    def _scrape_ami(self, address, replacement_value):
        """Attempt to scrape AMI insurance quote"""
        try:
            # AMI requires complex form submission
            # Most insurance sites use JavaScript-heavy forms
            # This is a simplified attempt
            
            url = "https://www.ami.co.nz/home-insurance"
            response = self.get(url)
            
            if not response:
                return None
            
            soup = BeautifulSoup(response.text, 'html.parser')
            text = soup.get_text()
            
            # Look for any price information
            price_matches = re.findall(r'\$\s*([\d,]+(?:\.\d{2})?)', text)
            
            # Insurance quotes typically range from $1000-$3000 for houses
            for match in price_matches:
                try:
                    price = float(match.replace(',', ''))
                    if 1000 <= price <= 5000:  # Reasonable range for house insurance
                        print(f"Found potential AMI quote: ${price}")
                        return price
                except ValueError:
                    continue
        
        except Exception as e:
            print(f"Error scraping AMI: {e}")
        
        return None
    
    def _scrape_state(self, address, replacement_value):
        """Attempt to scrape State Insurance quote"""
        try:
            url = "https://www.state.co.nz/home-insurance"
            response = self.get(url)
            
            if not response:
                return None
            
            soup = BeautifulSoup(response.text, 'html.parser')
            text = soup.get_text()
            
            price_matches = re.findall(r'\$\s*([\d,]+(?:\.\d{2})?)', text)
            
            for match in price_matches:
                try:
                    price = float(match.replace(',', ''))
                    if 1000 <= price <= 5000:
                        print(f"Found potential State quote: ${price}")
                        return price
                except ValueError:
                    continue
        
        except Exception as e:
            print(f"Error scraping State: {e}")
        
        return None
    
    def _scrape_aa_insurance(self, address, replacement_value):
        """Attempt to scrape AA Insurance quote"""
        try:
            url = "https://www.aainsurance.co.nz/home-insurance"
            response = self.get(url)
            
            if not response:
                return None
            
            soup = BeautifulSoup(response.text, 'html.parser')
            text = soup.get_text()
            
            price_matches = re.findall(r'\$\s*([\d,]+(?:\.\d{2})?)', text)
            
            for match in price_matches:
                try:
                    price = float(match.replace(',', ''))
                    if 1000 <= price <= 5000:
                        print(f"Found potential AA quote: ${price}")
                        return price
                except ValueError:
                    continue
        
        except Exception as e:
            print(f"Error scraping AA Insurance: {e}")
        
        return None

