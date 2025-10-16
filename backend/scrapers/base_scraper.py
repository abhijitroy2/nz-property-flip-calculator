import time
import random
import requests
from abc import ABC, abstractmethod

class BaseScraper(ABC):
    """Base class for all scrapers with rate limiting and polite scraping"""
    
    USER_AGENTS = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15',
    ]
    
    def __init__(self, min_delay=2, max_delay=5):
        self.min_delay = min_delay
        self.max_delay = max_delay
        self.last_request_time = 0
        self.session = requests.Session()
        self.session.headers.update(self._get_headers())
    
    def _get_headers(self):
        """Get randomized headers"""
        return {
            'User-Agent': random.choice(self.USER_AGENTS),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-NZ,en-US;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Cache-Control': 'max-age=0',
        }
    
    def _enforce_rate_limit(self):
        """Enforce polite rate limiting between requests"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        
        if time_since_last < self.min_delay:
            sleep_time = random.uniform(self.min_delay, self.max_delay)
            print(f"Rate limiting: sleeping for {sleep_time:.2f} seconds...")
            time.sleep(sleep_time)
        else:
            # Random small delay even if enough time has passed
            time.sleep(random.uniform(0.5, 1.5))
        
        self.last_request_time = time.time()
    
    def _rotate_user_agent(self):
        """Rotate user agent for next request"""
        self.session.headers.update({
            'User-Agent': random.choice(self.USER_AGENTS)
        })
    
    def get(self, url, **kwargs):
        """Make a GET request with rate limiting and retries"""
        self._enforce_rate_limit()
        self._rotate_user_agent()
        
        max_retries = 3
        for attempt in range(max_retries):
            try:
                response = self.session.get(url, timeout=30, **kwargs)
                response.raise_for_status()
                return response
            except requests.RequestException as e:
                print(f"Request failed (attempt {attempt + 1}/{max_retries}): {e}")
                if attempt < max_retries - 1:
                    time.sleep(random.uniform(2, 5))
                else:
                    raise
        
        return None
    
    @abstractmethod
    def scrape(self, *args, **kwargs):
        """Scrape data - to be implemented by subclasses"""
        pass

