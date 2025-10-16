from flask import Blueprint, request, jsonify
from models import db, Property, AnalysisResult
from scrapers.valuation_scraper import ValuationScraper
from scrapers.sales_scraper import SalesScraper
from scrapers.insurance_scraper import InsuranceScraper
from utils.cache_manager import CacheManager
from utils.similar_property_matcher import SimilarPropertyMatcher
from calculator import PropertyFlipCalculator
from config import Config

analyze_bp = Blueprint('analyze', __name__)

@analyze_bp.route('/api/analyze', methods=['POST'])
def analyze_properties():
    """
    Analyze properties for flip potential.
    
    Request body:
    {
        "property_ids": [1, 2, 3]
    }
    """
    try:
        data = request.get_json()
        property_ids = data.get('property_ids', [])
        
        if not property_ids:
            return jsonify({
                'success': False,
                'error': 'No property IDs provided'
            }), 400
        
        # Initialize components
        valuation_scraper = ValuationScraper()
        sales_scraper = SalesScraper()
        insurance_scraper = InsuranceScraper()
        cache_manager = CacheManager()
        matcher = SimilarPropertyMatcher()
        calculator = PropertyFlipCalculator()
        
        results = []
        
        for property_id in property_ids:
            property_obj = Property.query.get(property_id)
            
            if not property_obj:
                continue
            
            print(f"\nAnalyzing property: {property_obj.address}")
            
            # Get or scrape valuation (RV/CV)
            valuation = cache_manager.get_cached_valuation(property_id)
            
            if not valuation or cache_manager.needs_update(valuation):
                print("Scraping valuation data...")
                valuation_data = valuation_scraper.scrape(property_obj.address)
                valuation = cache_manager.save_valuation(property_id, valuation_data)
            
            rv = valuation.rv
            cv = valuation.cv
            
            # Determine purchase price (PP)
            # If asking price is provided, use it; otherwise use 85% of RV
            if property_obj.asking_price:
                pp = property_obj.asking_price
            else:
                pp = rv * 0.85 if rv else (cv * 0.85 if cv else None)
            
            if not pp:
                print(f"Cannot determine purchase price for {property_obj.address}")
                continue
            
            # Get recent comparable sales to determine TV (target value)
            suburb = property_obj.suburb
            bedrooms = property_obj.bedrooms
            floor_area = property_obj.floor_area
            
            tv = None  # Target Value (estimated sale price)
            
            if suburb and bedrooms:
                # Try to get cached sales
                cached_sales = cache_manager.get_cached_sales(suburb, bedrooms)
                
                if not cached_sales or cache_manager.needs_update(cached_sales[0] if cached_sales else None):
                    print("Scraping recent sales data...")
                    sales_data = sales_scraper.scrape(suburb, bedrooms, floor_area)
                    
                    if sales_data:
                        cache_manager.save_sales(sales_data)
                        cached_sales = sales_data
                
                if cached_sales:
                    # Find comparable properties
                    comparables = matcher.find_comparables(cached_sales, suburb, bedrooms, floor_area)
                    
                    if comparables:
                        tv = matcher.calculate_average_sale_price(comparables)
                        print(f"Found {len(comparables)} comparable sales, avg price: ${tv:.2f}")
            
            # If no comparable sales found, use 90% of CV as per requirements
            if not tv:
                tv = cv * 0.90 if cv else None
                print(f"No comparable sales, using 90% of CV: ${tv:.2f}")
            
            if not tv:
                print(f"Cannot determine target value for {property_obj.address}")
                continue
            
            # Get insurance quote
            ins = insurance_scraper.scrape(property_obj.address, replacement_value=cv)
            
            # Calculate profit
            calculation = calculator.calculate(
                pp=pp,
                tv=tv,
                rv=rv,
                cv=cv,
                ins=ins,
                int_rate=Config.DEFAULT_INTEREST_RATE,
                renovation_months=Config.DEFAULT_RENOVATION_MONTHS
            )
            
            # Save analysis result
            analysis = AnalysisResult(
                property_id=property_id,
                **calculation
            )
            db.session.add(analysis)
            db.session.commit()
            
            # Compile result
            result = {
                'property': property_obj.to_dict(),
                'analysis': analysis.to_dict(),
                'valuation': valuation.to_dict(),
            }
            
            results.append(result)
        
        return jsonify({
            'success': True,
            'count': len(results),
            'results': results
        })
    
    except Exception as e:
        print(f"Error in analyze: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@analyze_bp.route('/api/analysis/<int:property_id>', methods=['GET'])
def get_analysis(property_id):
    """Get the most recent analysis for a property"""
    try:
        cache_mgr = CacheManager()
        analysis = AnalysisResult.query.filter_by(property_id=property_id).order_by(AnalysisResult.analyzed_at.desc()).first()
        
        if not analysis:
            return jsonify({
                'success': False,
                'error': 'No analysis found for this property'
            }), 404
        
        property_obj = Property.query.get(property_id)
        valuation = cache_mgr.get_cached_valuation(property_id)
        
        return jsonify({
            'success': True,
            'property': property_obj.to_dict() if property_obj else None,
            'analysis': analysis.to_dict(),
            'valuation': valuation.to_dict() if valuation else None,
        })
    
    except Exception as e:
        print(f"Error getting analysis: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

