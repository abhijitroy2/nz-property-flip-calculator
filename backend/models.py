from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Property(db.Model):
    __tablename__ = 'properties'
    
    id = db.Column(db.Integer, primary_key=True)
    address = db.Column(db.String(500), nullable=False, unique=True)
    suburb = db.Column(db.String(200))
    bedrooms = db.Column(db.Integer)
    bathrooms = db.Column(db.Integer)
    floor_area = db.Column(db.Float)  # in sqm
    asking_price = db.Column(db.Float)
    sale_method = db.Column(db.String(200))  # e.g., "Auction on 12 Nov", "Deadline sale"
    trademe_url = db.Column(db.String(1000))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    valuations = db.relationship('Valuation', backref='property', lazy=True, cascade='all, delete-orphan')
    analysis_results = db.relationship('AnalysisResult', backref='property', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'address': self.address,
            'suburb': self.suburb,
            'bedrooms': self.bedrooms,
            'bathrooms': self.bathrooms,
            'floor_area': self.floor_area,
            'asking_price': self.asking_price,
            'sale_method': self.sale_method,
            'trademe_url': self.trademe_url,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }


class Valuation(db.Model):
    __tablename__ = 'valuations'
    
    id = db.Column(db.Integer, primary_key=True)
    property_id = db.Column(db.Integer, db.ForeignKey('properties.id'), nullable=False)
    rv = db.Column(db.Float)  # Rateable Value
    cv = db.Column(db.Float)  # Capital Value
    source = db.Column(db.String(200))
    scraped_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'property_id': self.property_id,
            'rv': self.rv,
            'cv': self.cv,
            'source': self.source,
            'scraped_at': self.scraped_at.isoformat() if self.scraped_at else None,
        }


class RecentSale(db.Model):
    __tablename__ = 'recent_sales'
    
    id = db.Column(db.Integer, primary_key=True)
    address = db.Column(db.String(500), nullable=False)
    suburb = db.Column(db.String(200))
    bedrooms = db.Column(db.Integer)
    floor_area = db.Column(db.Float)
    sale_price = db.Column(db.Float)
    sale_date = db.Column(db.Date)
    scraped_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'address': self.address,
            'suburb': self.suburb,
            'bedrooms': self.bedrooms,
            'floor_area': self.floor_area,
            'sale_price': self.sale_price,
            'sale_date': self.sale_date.isoformat() if self.sale_date else None,
            'scraped_at': self.scraped_at.isoformat() if self.scraped_at else None,
        }


class AnalysisResult(db.Model):
    __tablename__ = 'analysis_results'
    
    id = db.Column(db.Integer, primary_key=True)
    property_id = db.Column(db.Integer, db.ForeignKey('properties.id'), nullable=False)
    
    # Input parameters
    pp = db.Column(db.Float)  # Purchase Price
    rv = db.Column(db.Float)  # Rateable Value
    cv = db.Column(db.Float)  # Capital Value
    tv = db.Column(db.Float)  # Target Value (sale price)
    ins = db.Column(db.Float)  # Insurance
    rb = db.Column(db.Float)  # Renovation Budget
    le = db.Column(db.Float)  # Legal Expenses
    cr = db.Column(db.Float)  # Council Rates
    com = db.Column(db.Float)  # Commission
    int_cost = db.Column(db.Float)  # Interest Cost
    int_rate = db.Column(db.Float)  # Interest Rate (%)
    renovation_months = db.Column(db.Integer)  # Renovation period in months
    
    # GST calculations
    gst_claimable = db.Column(db.Float)
    gst_payable = db.Column(db.Float)
    net_gst = db.Column(db.Float)
    
    # Results
    gross_profit = db.Column(db.Float)
    pre_tax_profit = db.Column(db.Float)
    post_tax_profit = db.Column(db.Float)
    
    # Recommendation
    recommended_pp = db.Column(db.Float)
    is_viable = db.Column(db.Boolean, default=False)
    
    analyzed_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'property_id': self.property_id,
            'pp': self.pp,
            'rv': self.rv,
            'cv': self.cv,
            'tv': self.tv,
            'ins': self.ins,
            'rb': self.rb,
            'le': self.le,
            'cr': self.cr,
            'com': self.com,
            'int_cost': self.int_cost,
            'int_rate': self.int_rate,
            'renovation_months': self.renovation_months,
            'gst_claimable': self.gst_claimable,
            'gst_payable': self.gst_payable,
            'net_gst': self.net_gst,
            'gross_profit': self.gross_profit,
            'pre_tax_profit': self.pre_tax_profit,
            'post_tax_profit': self.post_tax_profit,
            'recommended_pp': self.recommended_pp,
            'is_viable': self.is_viable,
            'analyzed_at': self.analyzed_at.isoformat() if self.analyzed_at else None,
        }

