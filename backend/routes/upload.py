from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename
from utils.csv_parser import CSVParser
from utils.cache_manager import CacheManager
from scrapers.trademe_scraper import TrademePropertyScraper

upload_bp = Blueprint('upload', __name__)

@upload_bp.route('/api/upload', methods=['POST'])
def upload_csv():
    """
    Upload and parse CSV file with property data.
    
    CSV should contain columns for:
    - Address (required)
    - TradeMe URL (optional)
    - Bedrooms (optional)
    - Price (optional)
    
    Column names are auto-detected.
    """
    try:
        # Check if file was uploaded
        if 'file' not in request.files:
            return jsonify({
                'success': False,
                'error': 'No file uploaded'
            }), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({
                'success': False,
                'error': 'No file selected'
            }), 400
        
        # Check file extension
        if not file.filename.lower().endswith('.csv'):
            return jsonify({
                'success': False,
                'error': 'Only CSV files are supported'
            }), 400
        
        # Read file content
        file_content = file.read().decode('utf-8')
        
        # Parse CSV
        parser = CSVParser()
        properties = parser.parse(file_content)
        
        if not properties:
            return jsonify({
                'success': False,
                'error': 'No valid properties found in CSV'
            }), 400
        
        # Initialize components
        cache_manager = CacheManager()
        scraper = TrademePropertyScraper()
        
        # Process properties
        saved_properties = []
        
        for prop_data in properties:
            # Check if we need to scrape additional data from TradeMe URL
            if prop_data.get('trademe_url') and not prop_data.get('bedrooms'):
                print(f"Scraping TradeMe URL for additional data: {prop_data['trademe_url']}")
                scraped_data = scraper.scrape(prop_data['trademe_url'])
                
                if scraped_data:
                    # Merge scraped data with CSV data (CSV data takes precedence)
                    for key, value in scraped_data.items():
                        if key not in prop_data or prop_data[key] is None:
                            prop_data[key] = value
            
            # Save to cache/database
            property_obj = cache_manager.save_property(prop_data)
            saved_properties.append(property_obj.to_dict())
        
        return jsonify({
            'success': True,
            'count': len(saved_properties),
            'properties': saved_properties
        })
    
    except Exception as e:
        print(f"Error processing CSV upload: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

