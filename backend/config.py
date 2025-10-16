import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Database
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'postgresql://postgres:postgres@localhost:5432/nz_property_flip')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Scraping
    CACHE_EXPIRY_DAYS = int(os.getenv('CACHE_EXPIRY_DAYS', 7))
    RATE_LIMIT_MIN_DELAY = int(os.getenv('RATE_LIMIT_MIN_DELAY', 2))
    RATE_LIMIT_MAX_DELAY = int(os.getenv('RATE_LIMIT_MAX_DELAY', 5))
    
    # Financial Defaults
    DEFAULT_INSURANCE = float(os.getenv('DEFAULT_INSURANCE', 1800))
    DEFAULT_RENOVATION_BUDGET = float(os.getenv('DEFAULT_RENOVATION_BUDGET', 100000))
    DEFAULT_LEGAL_EXPENSES = float(os.getenv('DEFAULT_LEGAL_EXPENSES', 2500))
    DEFAULT_COUNCIL_RATES = float(os.getenv('DEFAULT_COUNCIL_RATES', 2000))
    COMMISSION_RATE = float(os.getenv('COMMISSION_RATE', 0.018))
    DEFAULT_INTEREST_RATE = float(os.getenv('DEFAULT_INTEREST_RATE', 0.075))  # 7.5% annually
    DEFAULT_RENOVATION_MONTHS = int(os.getenv('DEFAULT_RENOVATION_MONTHS', 6))  # 6 months
    TAX_RATE = float(os.getenv('TAX_RATE', 0.33))
    GST_RATE = float(os.getenv('GST_RATE', 0.15))
    
    # Profit Targets
    MIN_PROFIT_THRESHOLD = float(os.getenv('MIN_PROFIT_THRESHOLD', 25000))
    TARGET_PROFIT_MIN = float(os.getenv('TARGET_PROFIT_MIN', 25000))
    TARGET_PROFIT_MAX = float(os.getenv('TARGET_PROFIT_MAX', 30000))

