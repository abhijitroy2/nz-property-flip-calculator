import asyncio
from typing import List, Optional
from .base import Provider
from .property_valuation import PropertyValuationProvider
from .. import models

class NZComprehensiveProvider(Provider):
    """Comprehensive New Zealand data provider combining all free sources"""
    
    def __init__(self):
        self.valuation_provider = PropertyValuationProvider()
    
    async def fetch(self, address: str) -> models.DataPoints:
        """Fetch comprehensive data for a given address from all NZ sources"""
        
        # Fetch data from valuation provider
        valuation_data = await self.valuation_provider.fetch(address)
        
        # Return the valuation data
        return models.DataPoints(
            address=address,
            est_purchase_price=valuation_data.est_purchase_price,
            est_rehab_cost=valuation_data.est_rehab_cost,
            est_after_repair_value=valuation_data.est_after_repair_value,
            days_on_market_avg=valuation_data.days_on_market_avg,
            current_valuation_low=valuation_data.current_valuation_low,
            current_valuation_mid=valuation_data.current_valuation_mid,
            current_valuation_high=valuation_data.current_valuation_high,
            last_sale_price=valuation_data.last_sale_price,
            last_sale_date=valuation_data.last_sale_date,
            valuation_source=valuation_data.valuation_source,
            method_of_sale=valuation_data.method_of_sale
        )
    
    async def close(self):
        """Close all provider connections"""
        await self.valuation_provider.close()
    
    async def _get_connection_data(self, address: str) -> models.ConnectionData:
        """Get connection data for the address"""
        return models.ConnectionData()