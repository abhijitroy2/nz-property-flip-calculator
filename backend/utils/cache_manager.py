from datetime import datetime, timedelta
from models import db, Property, Valuation, RecentSale
from config import Config

class CacheManager:
    """Manages database caching with delta function to avoid re-scraping recent data"""
    
    def __init__(self):
        self.cache_expiry_days = Config.CACHE_EXPIRY_DAYS
    
    def is_cache_valid(self, timestamp):
        """Check if cached data is still valid"""
        if not timestamp:
            return False
        
        expiry_date = datetime.utcnow() - timedelta(days=self.cache_expiry_days)
        return timestamp > expiry_date
    
    def get_cached_property(self, address=None, trademe_url=None):
        """Get cached property data"""
        query = Property.query
        
        if trademe_url:
            query = query.filter_by(trademe_url=trademe_url)
        elif address:
            query = query.filter_by(address=address)
        else:
            return None
        
        property_obj = query.first()
        
        if property_obj and self.is_cache_valid(property_obj.updated_at):
            return property_obj
        
        return None
    
    def get_cached_valuation(self, property_id):
        """Get cached valuation data"""
        valuation = Valuation.query.filter_by(property_id=property_id).order_by(Valuation.scraped_at.desc()).first()
        
        if valuation and self.is_cache_valid(valuation.scraped_at):
            return valuation
        
        return None
    
    def get_cached_sales(self, suburb, bedrooms, months=3):
        """Get cached recent sales data"""
        cutoff_date = datetime.utcnow() - timedelta(days=months * 30)
        
        sales = RecentSale.query.filter(
            RecentSale.suburb == suburb,
            RecentSale.bedrooms == bedrooms,
            RecentSale.scraped_at > cutoff_date
        ).all()
        
        # Check if we have valid cached sales
        if sales and all(self.is_cache_valid(sale.scraped_at) for sale in sales):
            return sales
        
        return None
    
    def save_property(self, property_data):
        """Save or update property in cache"""
        property_obj = Property.query.filter_by(address=property_data['address']).first()
        
        if property_obj:
            # Update existing
            for key, value in property_data.items():
                if hasattr(property_obj, key):
                    setattr(property_obj, key, value)
            property_obj.updated_at = datetime.utcnow()
        else:
            # Create new
            property_obj = Property(**property_data)
            db.session.add(property_obj)
        
        db.session.commit()
        return property_obj
    
    def save_valuation(self, property_id, valuation_data):
        """Save valuation data"""
        valuation = Valuation(
            property_id=property_id,
            rv=valuation_data.get('rv'),
            cv=valuation_data.get('cv'),
            source=valuation_data.get('source'),
            scraped_at=datetime.utcnow()
        )
        db.session.add(valuation)
        db.session.commit()
        return valuation
    
    def save_sales(self, sales_data):
        """Save recent sales data"""
        saved_sales = []
        
        for sale_data in sales_data:
            sale = RecentSale(**sale_data, scraped_at=datetime.utcnow())
            db.session.add(sale)
            saved_sales.append(sale)
        
        db.session.commit()
        return saved_sales
    
    def needs_update(self, model_instance):
        """Check if a model instance needs updating (delta function)"""
        if not model_instance:
            return True
        
        # Check based on updated_at or scraped_at
        timestamp = None
        if hasattr(model_instance, 'updated_at'):
            timestamp = model_instance.updated_at
        elif hasattr(model_instance, 'scraped_at'):
            timestamp = model_instance.scraped_at
        
        return not self.is_cache_valid(timestamp)

