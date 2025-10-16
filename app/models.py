from pydantic import BaseModel
from typing import Optional, Dict, Any

class AddressInput(BaseModel):
    address: str

class DataPoints(BaseModel):
    address: str
    est_purchase_price: Optional[float] = None
    est_rehab_cost: Optional[float] = None
    est_after_repair_value: Optional[float] = None
    days_on_market_avg: Optional[int] = None
    # New valuation fields
    current_valuation_low: Optional[float] = None
    current_valuation_mid: Optional[float] = None
    current_valuation_high: Optional[float] = None
    last_sale_price: Optional[float] = None
    last_sale_date: Optional[str] = None
    valuation_source: Optional[str] = None
    method_of_sale: Optional[str] = None

class ScoringBreakdown(BaseModel):
    """Detailed scoring breakdown for individual criteria"""
    margin_score: Optional[float] = None
    margin_details: Optional[str] = None
    dom_score: Optional[float] = None
    dom_details: Optional[str] = None

class ConnectionData(BaseModel):
    """Data from individual connections"""
    property_valuation: Optional[Dict[str, Any]] = None

class AddressScore(BaseModel):
    address: str
    score: float
    notes: Optional[str] = None
    scoring_breakdown: Optional[ScoringBreakdown] = None
    connection_data: Optional[ConnectionData] = None