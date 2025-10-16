import asyncio
from typing import List, Dict, Any
from .models import AddressScore, ConnectionData
from .providers.nz_comprehensive import NZComprehensiveProvider
from .providers.trademe_scraper import TradeMeScraper
# from .providers.realestate_scraper import RealEstateScraper  # Removed
# from .providers.hougarden_scraper import HouGardenScraper  # Removed
from .scoring import score_datapoints

async def process_addresses(addresses: List[str]) -> List[AddressScore]:
    """Original function for backward compatibility"""
    provider = NZComprehensiveProvider()
    try:
        async def one(addr: str) -> AddressScore:
            dp = await provider.fetch(addr)
            score, notes, breakdown = score_datapoints(dp)
            
            # Create connection data from the comprehensive provider
            connection_data = await provider._get_connection_data(addr)
            
            return AddressScore(
                address=addr, 
                score=score, 
                notes=notes, 
                scoring_breakdown=breakdown,
                connection_data=connection_data
            )
        return await asyncio.gather(*[one(a) for a in addresses])
    finally:
        await provider.close()

async def process_addresses_with_urls(addresses: List[Dict[str, str]]) -> List[AddressScore]:
    """New function to process addresses with optional TradeMe, RealEstate, and HouGarden URLs"""
    provider = NZComprehensiveProvider()
    trademe_scraper = TradeMeScraper(
        username="abbey.roy@gmail.com",
        password="zebrastripes"
    )  # Initialize with auth token if needed
    # realestate_scraper = RealEstateScraper()  # Removed
    # hougarden_scraper = HouGardenScraper()  # Removed
    
    try:
        async def one(address_data: Dict[str, str]) -> AddressScore:
            addr = address_data["address"]
            trademe_url = address_data.get("trademe_url", "")
            # realestate_url = address_data.get("realestate_url", "")  # Removed
            # hougarden_url = address_data.get("hougarden_url", "")  # Removed
            
            # Get base data from comprehensive provider
            dp = await provider.fetch(addr)
            
            # If TradeMe URL is provided, scrape it for additional data
            if trademe_url:
                try:
                    scraper_data = await trademe_scraper.fetch(addr, trademe_url)
                    # Merge scraper data with comprehensive data
                    dp.current_valuation_low = scraper_data.current_valuation_low
                    dp.current_valuation_mid = scraper_data.current_valuation_mid
                    dp.current_valuation_high = scraper_data.current_valuation_high
                    dp.last_sale_price = scraper_data.last_sale_price
                    dp.last_sale_date = scraper_data.last_sale_date
                    dp.valuation_source = scraper_data.valuation_source
                    dp.method_of_sale = scraper_data.method_of_sale
                except Exception as e:
                    print(f"Error scraping TradeMe URL {trademe_url}: {e}")
            
            # RealEstate and HouGarden scrapers removed - only using TradeMe now
            
            score, notes, breakdown = score_datapoints(dp)
            
            # Create connection data with scraper data
            connection_data = ConnectionData(
                property_valuation = {
                    "current_valuation": dp.current_valuation_mid,
                    "last_sale_price": dp.last_sale_price,
                    "source": dp.valuation_source,
                    "method_of_sale": dp.method_of_sale,
                    "trademe_url": trademe_url,
                    "status": "success" if dp.current_valuation_mid else "error"
                }
            )
            
            return AddressScore(
                address=addr, 
                score=score, 
                notes=notes, 
                scoring_breakdown=breakdown,
                connection_data=connection_data
            )
        
        return await asyncio.gather(*[one(a) for a in addresses])
    finally:
        await provider.close()
        await trademe_scraper.close()
        # await realestate_scraper.close()  # Removed
        # await hougarden_scraper.close()  # Removed