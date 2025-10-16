import csv
import io
import re

class CSVParser:
    """Flexible CSV parser with auto-detection of columns"""
    
    def parse(self, file_content):
        """
        Parse CSV file and auto-detect address and TradeMe URL columns.
        
        Args:
            file_content: String content of CSV file or file-like object
        
        Returns:
            List of dictionaries with parsed data
        """
        # Handle both string content and file-like objects
        if isinstance(file_content, str):
            csv_file = io.StringIO(file_content)
        elif isinstance(file_content, bytes):
            csv_file = io.StringIO(file_content.decode('utf-8'))
        else:
            csv_file = file_content
        
        # Read CSV
        reader = csv.DictReader(csv_file)
        headers = reader.fieldnames
        
        if not headers:
            raise ValueError("CSV file has no headers")
        
        # Auto-detect column mappings
        column_mapping = self._detect_columns(headers)
        print(f"CSV Column mapping detected: {column_mapping}")
        
        # Parse rows
        properties = []
        for row in reader:
            property_data = self._parse_row(row, column_mapping)
            if property_data:
                print(f"Parsed property: {property_data}")
                properties.append(property_data)
        
        return properties
    
    def _detect_columns(self, headers):
        """Auto-detect which columns contain address and TradeMe URL"""
        mapping = {
            'address': None,
            'trademe_url': None,
            'bedrooms': None,
            'bathrooms': None,
            'area': None,
            'price': None,
        }
        
        # Normalize headers for comparison
        normalized_headers = {h: self._normalize_header(h) for h in headers}
        
        # Detect address column - prioritize exact matches first
        for header in headers:
            if header.lower() in ['property address', 'address']:
                mapping['address'] = header
                break
        
        # If no exact match, try keyword matching
        if not mapping['address']:
            address_keywords = ['address', 'property', 'location', 'street', 'road', 'place']
            for header, normalized in normalized_headers.items():
                if any(keyword in normalized for keyword in address_keywords):
                    mapping['address'] = header
                    break
        
        # Detect TradeMe URL column - prioritize exact matches first
        for header in headers:
            if header.lower() in ['property link', 'link', 'url']:
                mapping['trademe_url'] = header
                break
        
        # If no exact match, try keyword matching
        if not mapping['trademe_url']:
            url_keywords = ['trademe', 'url', 'link', 'listing', 'propertylink', 'property link']
            for header, normalized in normalized_headers.items():
                if any(keyword in normalized for keyword in url_keywords):
                    mapping['trademe_url'] = header
                    break
        
        # Detect bedrooms column - prioritize exact matches first
        for header in headers:
            if header.lower() in ['bedrooms', 'bedroom', 'bed']:
                mapping['bedrooms'] = header
                break
        
        # If no exact match, try keyword matching
        if not mapping['bedrooms']:
            bed_keywords = ['bed', 'bedroom', 'bedrooms']
            for header, normalized in normalized_headers.items():
                if any(keyword in normalized for keyword in bed_keywords):
                    mapping['bedrooms'] = header
                    break
        
        # Detect bathrooms column - prioritize exact matches first
        for header in headers:
            if header.lower() in ['bathrooms', 'bathroom', 'bath']:
                mapping['bathrooms'] = header
                break
        
        # If no exact match, try keyword matching
        if not mapping['bathrooms']:
            bath_keywords = ['bath', 'bathroom', 'bathrooms']
            for header, normalized in normalized_headers.items():
                if any(keyword in normalized for keyword in bath_keywords):
                    mapping['bathrooms'] = header
                    break
        
        # Detect area column - prioritize exact matches first
        for header in headers:
            if header.lower() in ['area', 'floor area', 'sqm', 'm2']:
                mapping['area'] = header
                break
        
        # If no exact match, try keyword matching
        if not mapping['area']:
            area_keywords = ['area', 'floor', 'sqm', 'm2', 'square']
            for header, normalized in normalized_headers.items():
                if any(keyword in normalized for keyword in area_keywords):
                    mapping['area'] = header
                    break
        
        # Detect price column - prioritize exact matches first
        for header in headers:
            if header.lower() in ['price', 'cost', 'amount']:
                mapping['price'] = header
                break
        
        # If no exact match, try keyword matching
        if not mapping['price']:
            price_keywords = ['price', 'cost', 'amount', 'asking', 'auction', 'sale']
            for header, normalized in normalized_headers.items():
                if any(keyword in normalized for keyword in price_keywords):
                    mapping['price'] = header
                    break
        
        return mapping
    
    def _normalize_header(self, header):
        """Normalize header for comparison"""
        # Remove special characters, convert to lowercase
        normalized = re.sub(r'[^a-z0-9]', '', header.lower())
        return normalized
    
    def _extract_price_from_text(self, text):
        """Extract numeric price from various text formats"""
        if not text:
            return None
        
        # Look for explicit price patterns
        # "Asking price $599,900"
        asking_match = re.search(r'asking\s+price\s*\$?([\d,]+)', text, re.IGNORECASE)
        if asking_match:
            try:
                return float(asking_match.group(1).replace(',', ''))
            except ValueError:
                pass
        
        # "Declared Reserve $499,999"
        reserve_match = re.search(r'reserve\s*\$?([\d,]+)', text, re.IGNORECASE)
        if reserve_match:
            try:
                return float(reserve_match.group(1).replace(',', ''))
            except ValueError:
                pass
        
        # Simple dollar amount "$599,900"
        dollar_match = re.search(r'\$([\d,]+)', text)
        if dollar_match:
            try:
                return float(dollar_match.group(1).replace(',', ''))
            except ValueError:
                pass
        
        # If it's just a number (like "599900")
        number_match = re.search(r'^([\d,]+)$', text.strip())
        if number_match:
            try:
                return float(number_match.group(1).replace(',', ''))
            except ValueError:
                pass
        
        # For auction/deadline sales, return None (no specific price)
        return None
    
    def _is_valid_url(self, url):
        """Check if a string is a valid URL"""
        if not url:
            return False
        
        # Must start with http:// or https://
        if not url.lower().startswith(('http://', 'https://')):
            return False
        
        # Must contain a domain
        if '.' not in url:
            return False
        
        # Should not contain common date patterns
        date_patterns = [
            r'listed\s+\w+,\s+\d+\s+\w+',  # "Listed Thu, 2 Oct"
            r'\d{1,2}\s+\w+\s+\d{4}',      # "2 Oct 2024"
            r'\w+\s+\d{1,2},\s+\d{4}',     # "Oct 2, 2024"
        ]
        
        for pattern in date_patterns:
            if re.search(pattern, url, re.IGNORECASE):
                return False
        
        return True
    
    def _extract_area_from_text(self, text):
        """Extract numeric area from text like '345 m2' or '345 m²'"""
        if not text:
            return None
        
        # Look for number followed by m2, m², or similar
        area_match = re.search(r'(\d+(?:\.\d+)?)\s*m[²2]?', text, re.IGNORECASE)
        if area_match:
            try:
                return float(area_match.group(1))
            except ValueError:
                pass
        
        # If it's just a number, assume it's area in m2
        number_match = re.search(r'^(\d+(?:\.\d+)?)$', text.strip())
        if number_match:
            try:
                return float(number_match.group(1))
            except ValueError:
                pass
        
        return None
    
    def _parse_row(self, row, column_mapping):
        """Parse a single row using column mapping"""
        property_data = {}
        
        # Extract address (required)
        if column_mapping['address']:
            address = row.get(column_mapping['address'], '').strip()
            if not address:
                return None  # Skip rows without address
            property_data['address'] = address
        else:
            # If no address column found, try first column
            first_value = list(row.values())[0].strip() if row else ''
            if not first_value:
                return None
            property_data['address'] = first_value
        
        # Extract TradeMe URL (optional)
        if column_mapping['trademe_url']:
            url = row.get(column_mapping['trademe_url'], '').strip()
            if url and self._is_valid_url(url):
                property_data['trademe_url'] = url
        
        # Extract bedrooms (optional)
        if column_mapping['bedrooms']:
            bedrooms_str = row.get(column_mapping['bedrooms'], '').strip()
            if bedrooms_str:
                try:
                    property_data['bedrooms'] = int(bedrooms_str)
                except ValueError:
                    pass
        
        # Extract bathrooms (optional)
        if column_mapping['bathrooms']:
            bathrooms_str = row.get(column_mapping['bathrooms'], '').strip()
            if bathrooms_str:
                try:
                    property_data['bathrooms'] = int(bathrooms_str)
                except ValueError:
                    pass
        
        # Extract area (optional)
        if column_mapping['area']:
            area_str = row.get(column_mapping['area'], '').strip()
            if area_str:
                area = self._extract_area_from_text(area_str)
                if area:
                    property_data['floor_area'] = area
        
        # Extract price (optional)
        if column_mapping['price']:
            price_str = row.get(column_mapping['price'], '').strip()
            if price_str:
                # Extract numeric price from various formats
                price = self._extract_price_from_text(price_str)
                if price:
                    property_data['asking_price'] = price
                else:
                    # Store the sale method if no specific price
                    property_data['sale_method'] = price_str
        
        return property_data

