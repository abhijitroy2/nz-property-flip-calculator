from fastapi import FastAPI, UploadFile, File, Request, HTTPException, Form
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
import csv, io
from datetime import datetime, date, timedelta
import os
import re
import time
import asyncio
from typing import List, Dict, Any
import logging

app = FastAPI(title="NZ Property Flip Calculator", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Import pipeline functions
from .pipeline import process_addresses, process_addresses_with_urls

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/health")
async def health_check():
    """Health check endpoint for Railway"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

# API Routes for React frontend
@app.post("/api/upload")
async def upload_csv(file: UploadFile = File(...)):
    """Upload and process CSV file with property data"""
    try:
        # Log the upload attempt with more details
        logging.info(f"Upload attempt: filename={file.filename}, content_type={file.content_type}, size={file.size}")
        
        # Check if file is provided
        if not file.filename:
            logging.error("No filename provided")
            raise HTTPException(status_code=400, detail="No file provided")
        
        # Check file extension
        if not file.filename.lower().endswith((".csv", ".txt")):
            logging.error(f"Invalid file type: {file.filename}")
            raise HTTPException(status_code=400, detail="Only CSV or TXT files supported")

        # Read file content
        content = await file.read()
        logging.info(f"File size: {len(content)} bytes")
        
        if len(content) == 0:
            raise HTTPException(status_code=400, detail="File is empty")
        
        # Parse CSV content with better error handling
        try:
            buf = io.StringIO(content.decode("utf-8", errors="ignore"))
            reader = csv.reader(buf, quoting=csv.QUOTE_ALL, skipinitialspace=True)
            rows = list(reader)
            # Filter out empty rows
            rows = [row for row in rows if any(cell.strip() for cell in row)]
        except Exception as e:
            logging.error(f"CSV parsing error: {str(e)}")
            raise HTTPException(status_code=400, detail=f"Failed to parse CSV: {str(e)}")

        if not rows:
            logging.warning("No data found in file")
            return {
                "success": True,
                "properties": [], 
                "count": 0,
                "total": 0,
                "message": "No data found in file"
            }

        headers = [h.strip() for h in rows[0]]
        logging.info(f"CSV headers: {headers}")
        logging.info(f"Found {len(rows)} total rows (including header)")
        
        properties = []
        
        # Process each row as a property
        for i, row in enumerate(rows[1:], 1):
            if len(row) < len(headers):
                row.extend([''] * (len(headers) - len(row)))
            
            # Create raw property data from CSV
            raw_property_data = dict(zip(headers, row))
            
            # Extract suburb from address
            full_address = raw_property_data.get('Property Address', raw_property_data.get('Address', ''))
            suburb = ''
            if full_address and ',' in full_address:
                # Extract suburb (usually the part after the last comma)
                address_parts = [part.strip() for part in full_address.split(',')]
                if len(address_parts) >= 2:
                    suburb = address_parts[-1]  # Last part is usually the city/suburb
            
            # Map CSV columns to expected property fields
            property_data = {
                'address': full_address,
                'suburb': suburb,
                'bedrooms': raw_property_data.get('Bedrooms', ''),
                'bathrooms': raw_property_data.get('Bathrooms', ''),
                'floor_area': raw_property_data.get('Area', '').replace(' m2', '').replace('m2', '').strip(),
                'asking_price': raw_property_data.get('Price', '').replace('Asking $', '').replace('$', '').replace(',', '').strip(),
                'sale_method': raw_property_data.get('Open Home Status', ''),
                'trademe_url': raw_property_data.get('Property Link', raw_property_data.get('TradeMe URL', '')),
                'id': i,  # Add ID for frontend
                # Keep all original data for debugging
                'raw_data': raw_property_data
            }
            
            # Clean up numeric fields
            try:
                if property_data['bedrooms']:
                    property_data['bedrooms'] = int(property_data['bedrooms'])
            except (ValueError, TypeError):
                property_data['bedrooms'] = None
                
            try:
                if property_data['bathrooms']:
                    property_data['bathrooms'] = int(property_data['bathrooms'])
            except (ValueError, TypeError):
                property_data['bathrooms'] = None
                
            try:
                if property_data['floor_area']:
                    property_data['floor_area'] = float(property_data['floor_area'])
            except (ValueError, TypeError):
                property_data['floor_area'] = None
                
            try:
                if property_data['asking_price']:
                    property_data['asking_price'] = float(property_data['asking_price'])
            except (ValueError, TypeError):
                property_data['asking_price'] = None
            
            properties.append(property_data)
            logging.info(f"Processed row {i}: {property_data}")
        
        logging.info(f"Successfully processed {len(properties)} properties")
        return {
            "success": True,
            "properties": properties, 
            "count": len(properties),
            "total": len(properties)
        }
        
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        # Log unexpected errors
        logging.error(f"Unexpected error in upload: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.post("/api/analyze")
async def analyze_properties(request: Dict[str, Any]):
    """Analyze properties for flip potential"""
    property_ids = request.get("property_ids", [])
    properties = request.get("properties", [])
    
    if not properties:
        raise HTTPException(status_code=400, detail="No properties provided")
    
    try:
        # Convert properties to address format for pipeline
        addresses = []
        for prop in properties:
            if isinstance(prop, dict):
                address_data = {
                    "address": prop.get("address", prop.get("propertyaddress", "")),
                    "trademe_url": prop.get("trademe_url", prop.get("trademeurl", ""))
                }
                if address_data["address"]:
                    addresses.append(address_data)
            elif isinstance(prop, str):
                addresses.append({"address": prop, "trademe_url": ""})
        
        if not addresses:
            raise HTTPException(status_code=400, detail="No valid addresses found")
        
        # Process addresses through pipeline
        results = await process_addresses_with_urls(addresses)
        
        # Import the financial calculator
        try:
            import sys
            import os
            
            # Add backend directory to path
            backend_path = os.path.join(os.path.dirname(__file__), '..', 'backend')
            if backend_path not in sys.path:
                sys.path.insert(0, backend_path)
            
            from calculator import PropertyFlipCalculator
            from config import Config
            
            # Initialize calculator
            calculator = PropertyFlipCalculator()
        except ImportError as e:
            logging.error(f"Failed to import financial calculator: {e}")
            # Create a simple fallback calculator
            class FallbackCalculator:
                def calculate(self, pp, tv, rv=None, cv=None, ins=None, rb=None, le=None, cr=None, int_rate=None, renovation_months=None):
                    # Simple fallback calculations
                    ins = ins or 1800
                    rb = rb or 100000
                    le = le or 2500
                    cr = cr or 2000
                    int_rate = int_rate or 0.075
                    renovation_months = renovation_months or 6
                    
                    com = tv * 0.018  # 1.8% commission
                    int_cost = (pp + rb) * (int_rate / 12) * renovation_months
                    
                    gst_claimable = (pp + rb + le) * 0.15
                    gst_payable = tv * 0.15
                    net_gst = gst_payable - gst_claimable
                    
                    gross_profit = tv - pp - rb - le - cr - ins - com - int_cost
                    pre_tax_profit = gross_profit - net_gst
                    post_tax_profit = pre_tax_profit * 0.67  # 33% tax
                    
                    is_viable = post_tax_profit >= 25000
                    recommended_pp = None
                    if not is_viable:
                        # Simple recommendation
                        recommended_pp = tv * 0.6  # 60% of target value
                    
                    return {
                        'pp': round(pp, 2),
                        'tv': round(tv, 2),
                        'rv': round(rv or tv * 0.9, 2),
                        'cv': round(cv or tv * 0.9, 2),
                        'rb': round(rb, 2),
                        'ins': round(ins, 2),
                        'le': round(le, 2),
                        'cr': round(cr, 2),
                        'com': round(com, 2),
                        'int': round(int_cost, 2),
                        'int_rate': round(int_rate * 100, 2),
                        'renovation_months': renovation_months,
                        'gst_claimable': round(gst_claimable, 2),
                        'gst_payable': round(gst_payable, 2),
                        'net_gst': round(net_gst, 2),
                        'gross_profit': round(gross_profit, 2),
                        'pre_tax_profit': round(pre_tax_profit, 2),
                        'post_tax_profit': round(post_tax_profit, 2),
                        'is_viable': is_viable,
                        'recommended_pp': round(recommended_pp, 2) if recommended_pp else None
                    }
            
            calculator = FallbackCalculator()
        
        # Format results for frontend - match with original properties
        analysis_results = []
        try:
            for i, result in enumerate(results):
                # Find the corresponding property by address
                matching_property = None
                for prop in properties:
                    if prop.get('address', '').strip() == result.address.strip():
                        matching_property = prop
                        break
                
                # If no exact match, use the property at the same index
                if not matching_property and i < len(properties):
                    matching_property = properties[i]
                
                # Extract financial data from the analysis result
                connection_data = result.connection_data.dict() if result.connection_data else {}
                property_valuation = connection_data.get('property_valuation', {})
                
                # Get property values for financial calculations
                asking_price = matching_property.get('asking_price', 0) if matching_property else 0
                if isinstance(asking_price, str):
                    asking_price = asking_price.replace('$', '').replace(',', '').replace('Asking ', '').strip()
                    try:
                        asking_price = float(asking_price) if asking_price else 0
                    except:
                        asking_price = 0
                
                # Use current valuation as target value, fallback to asking price
                target_value = property_valuation.get('current_valuation', asking_price * 1.1)
                if not target_value:
                    target_value = asking_price * 1.1
                
                # Use 85% of asking price as purchase price
                purchase_price = asking_price * 0.85 if asking_price > 0 else 0
                
                # Perform financial calculations
                try:
                    logging.info(f"Calculating finances for {result.address}: PP={purchase_price}, TV={target_value}")
                    calc_result = calculator.calculate(
                        pp=purchase_price,
                        tv=target_value,
                        rv=property_valuation.get('current_valuation'),
                        cv=property_valuation.get('current_valuation')
                    )
                    logging.info(f"Calculation result: {calc_result}")
                    
                    # Create analysis result with financial data
                    analysis_data = {
                        "score": result.score,
                        "notes": result.notes,
                        "scoring_breakdown": result.scoring_breakdown.dict() if result.scoring_breakdown else None,
                        "connection_data": result.connection_data.dict() if result.connection_data else None,
                        # Financial calculation fields (matching frontend expectations)
                        "pp": calc_result.get('pp', 0),
                        "rv": calc_result.get('rv', 0),
                        "cv": calc_result.get('cv', 0),
                        "tv": calc_result.get('tv', 0),
                        "rb": calc_result.get('rb', 0),
                        "ins": calc_result.get('ins', 0),
                        "le": calc_result.get('le', 0),
                        "cr": calc_result.get('cr', 0),
                        "com": calc_result.get('com', 0),
                        "int": calc_result.get('int', 0),
                        "int_rate": calc_result.get('int_rate', 0),
                        "renovation_months": calc_result.get('renovation_months', 0),
                        "gst_claimable": calc_result.get('gst_claimable', 0),
                        "gst_payable": calc_result.get('gst_payable', 0),
                        "net_gst": calc_result.get('net_gst', 0),
                        "gross_profit": calc_result.get('gross_profit', 0),
                        "pre_tax_profit": calc_result.get('pre_tax_profit', 0),
                        "post_tax_profit": calc_result.get('post_tax_profit', 0),
                        "recommended_pp": calc_result.get('recommended_pp', 0),
                        "is_viable": calc_result.get('is_viable', False)
                    }
                except Exception as e:
                    logging.error(f"Financial calculation error for {result.address}: {e}")
                    # Fallback to basic analysis without financial data
                    analysis_data = {
                        "score": result.score,
                        "notes": result.notes,
                        "scoring_breakdown": result.scoring_breakdown.dict() if result.scoring_breakdown else None,
                        "connection_data": result.connection_data.dict() if result.connection_data else None,
                        "pp": 0,
                        "rv": 0,
                        "cv": 0,
                        "tv": 0,
                        "rb": 0,
                        "ins": 0,
                        "le": 0,
                        "cr": 0,
                        "com": 0,
                        "int": 0,
                        "int_rate": 0,
                        "renovation_months": 0,
                        "gst_claimable": 0,
                        "gst_payable": 0,
                        "net_gst": 0,
                        "gross_profit": 0,
                        "pre_tax_profit": 0,
                        "post_tax_profit": 0,
                        "recommended_pp": 0,
                        "is_viable": False
                    }
                
                analysis_results.append({
                    "property": matching_property or {
                        "id": i + 1,
                        "address": result.address,
                        "suburb": "",
                        "bedrooms": None,
                        "bathrooms": None,
                        "floor_area": None,
                        "asking_price": None,
                        "sale_method": "",
                        "trademe_url": ""
                    },
                    "analysis": analysis_data,
                    "valuation": {
                        "source": "analysis",
                        "score": result.score
                    }
                })
        except Exception as e:
            logging.error(f"Error processing analysis results: {e}")
            raise HTTPException(status_code=500, detail=f"Analysis processing failed: {str(e)}")
        
        return {
            "success": True,
            "results": analysis_results, 
            "total": len(analysis_results)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@app.get("/api/property/{property_id}")
async def get_property(property_id: str):
    """Get individual property details"""
    # This would typically fetch from database
    # For now, return a placeholder
    return {"id": property_id, "message": "Property endpoint not yet implemented"}

@app.get("/api/analysis/{property_id}")
async def get_analysis(property_id: str):
    """Get analysis results for a property"""
    # This would typically fetch from database
    # For now, return a placeholder
    return {"id": property_id, "message": "Analysis endpoint not yet implemented"}

@app.post("/preview")
async def preview(file: UploadFile = File(...)):
    if not file.filename.lower().endswith((".csv", ".txt")):
        return JSONResponse(status_code=400, content={"error": "Only CSV or TXT files supported"})

    content = await file.read()
    try:
        buf = io.StringIO(content.decode("utf-8", errors="ignore"))
        reader = csv.reader(buf)
        rows = list(reader)
    except Exception:
        return JSONResponse(status_code=400, content={"error": "Failed to parse CSV/TXT"})

    if not rows:
        return {"headers": [], "rows": []}

    raw_headers = [h.strip() for h in rows[0]]

    def normalize(name: str) -> str:
        return "".join(ch for ch in name.lower() if ch.isalnum())

    header_map = {normalize(h): idx for idx, h in enumerate(raw_headers)}
    addr_idx = header_map.get("propertyaddress", 0 if raw_headers else None)
    list_idx = header_map.get("listingdate", 1 if len(raw_headers) > 1 else None)

    def parse_listing_date(value: str):
        if not value:
            return None
        raw = value.strip()
        lower = raw.lower()

        # Remove optional leading label like "listed"
        if lower.startswith("listed "):
            lower = lower[len("listed "):]
            raw = raw[len("Listed "):] if raw.startswith("Listed ") else raw.split(" ", 1)[1]

        today_local = date.today()

        # Relative day terms
        if lower == "today":
            return today_local
        if lower == "yesterday":
            return today_local - timedelta(days=1)

        # "x days ago"
        import re
        m = re.match(r"^(\d{1,3})\s+days?\s+ago$", lower)
        if m:
            days = int(m.group(1))
            return today_local - timedelta(days=days)

        # Formats like "Thu, 2 Oct" or "2 Oct" (assume current year)
        month_map = {
            'jan': 1, 'january': 1,
            'feb': 2, 'february': 2,
            'mar': 3, 'march': 3,
            'apr': 4, 'april': 4,
            'may': 5,
            'jun': 6, 'june': 6,
            'jul': 7, 'july': 7,
            'aug': 8, 'august': 8,
            'sep': 9, 'sept': 9, 'september': 9,
            'oct': 10, 'october': 10,
            'nov': 11, 'november': 11,
            'dec': 12, 'december': 12,
        }

        def parse_day_month(s: str):
            s = s.strip().replace(",", " ")
            parts = [p for p in s.split() if p]
            # Remove leading weekday if present
            if parts and parts[0][:3].lower() in ["mon","tue","wed","thu","fri","sat","sun"]:
                parts = parts[1:]
            if len(parts) >= 2:
                try:
                    day = int(parts[0])
                    mon_key = parts[1].lower()
                    if mon_key in month_map:
                        month = month_map[mon_key]
                        return date(today_local.year, month, day)
                except Exception:
                    return None
            return None

        dm = parse_day_month(raw)
        if dm:
            return dm

        # Try common absolute formats
        formats = [
            "%Y-%m-%d",
            "%d/%m/%Y",
            "%m/%d/%Y",
            "%d-%m-%Y",
            "%Y/%m/%d",
            "%d %b %Y",
            "%d %B %Y",
            "%b %d, %Y",
            "%B %d, %Y",
        ]
        for fmt in formats:
            try:
                return datetime.strptime(raw, fmt).date()
            except Exception:
                continue
        # Last resort: ISO parser
        try:
            return date.fromisoformat(raw)
        except Exception:
            return None

    # We will return all original headers and insert derived columns:
    # 1) PotentialValue before PropertyLink
    # 2) Days on Market / Forced Sale columns after Listing Date (or at start if no Listing Date)
    output_headers = list(raw_headers)
    prop_link_raw_idx = header_map.get("propertylink")
    list_idx_raw = list_idx

    pv_insert_pos = prop_link_raw_idx if (prop_link_raw_idx is not None and prop_link_raw_idx <= len(output_headers)) else len(output_headers)
    output_headers.insert(pv_insert_pos, "PotentialValue")

    # Adjust derived insert position if PotentialValue was inserted before it
    insert_pos = (list_idx_raw + 1) if (list_idx_raw is not None and list_idx_raw < len(raw_headers)) else 0
    if pv_insert_pos <= insert_pos:
        insert_pos += 1
    for label in ["Days on Market", "Forced Sale Likelihood", "Forced Sale Triggers", "Forced Sale Rationale"]:
        output_headers.insert(insert_pos, label)
        insert_pos += 1
    output_rows = []
    today = date.today()

    # Locate optional indices used for enrichment/sorting
    title_idx = header_map.get("propertytitle")
    area_idx = header_map.get("area")
    prop_link_idx = prop_link_raw_idx

    very_strong_patterns = [
        r"\bmortgagee\b",
        r"\bmortgage(s|e)?\b",
        r"\bdeceased estate\b",
        r"\bmust\s+sell\b",
        r"\bno\s+plan\s*b\b",
        r"\burgent(\s+sale)?\b",
        r"\bas[-\s]?is(\s*\/\s*where[-\s]?is)?\b",
        r"\bfire\s+sale\b",
    ]
    medium_patterns = [
        r"\bvendor\s+relocated\b",
        r"\bvendor\s+committed\b",
        r"\bfinal\s+call\b",
        r"\blast\s+chance\b",
        r"\bpriced\s+to\s+sell\b",
        r"\bmust\s+be\s+sold\b",
        r"\bmotivated\s+vendor\b",
        r"\bno\s+plan\s*b\b",
    ]
    weak_patterns = [
        r"\bopportunity\b",
        r"\binvestors?\b",
        r"\baffordable\b",
        r"\bbrand\s+new\b",
        r"\bpriced\s+to\s+sell\b",
    ]

    def analyze_forced_sale(title: str):
        if not title:
            return 0.0, [], ""
        text = title.lower()
        matches = []
        score = 0.0
        # Collect matches per tier
        tier = None
        for pat in very_strong_patterns:
            m = re.search(pat, text)
            if m:
                matches.append(m.group(0))
                score = max(score, 1.0)
                tier = "very strong"
        if score < 1.0:
            for pat in medium_patterns:
                m = re.search(pat, text)
                if m:
                    matches.append(m.group(0))
                    score = max(score, 0.6)
                    if not tier:
                        tier = "medium"
        if score < 0.6:
            for pat in weak_patterns:
                m = re.search(pat, text)
                if m:
                    matches.append(m.group(0))
                    score = max(score, 0.2)
                    if not tier:
                        tier = "weak"
        rationale = "" if not matches else f"Signals: {', '.join(sorted(set(matches)))} ({tier})"
        return round(score, 2), matches, rationale
    def parse_area(value: str) -> float:
        if not value:
            return 0.0
        txt = value.lower().replace(",", " ")
        # extract first number (int or float)
        m = re.search(r"(\d+(?:\.\d+)?)", txt)
        return float(m.group(1)) if m else 0.0

    # Selenium setup (only if at least one PropertyLink exists)
    def make_driver():
        try:
            from selenium import webdriver
            from selenium.webdriver.chrome.options import Options as ChromeOptions
            from selenium.webdriver.chrome.service import Service as ChromeService
            from webdriver_manager.chrome import ChromeDriverManager
        except Exception:
            return None
        options = ChromeOptions()
        headless_env = os.getenv("HEADLESS", "true").lower()
        headless = headless_env not in ("0", "false", "no")
        if headless:
            options.add_argument("--headless=new")
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_argument("--window-size=1280,2000")
        service = ChromeService(ChromeDriverManager().install())
        try:
            return webdriver.Chrome(service=service, options=options)
        except Exception:
            return None

    def extract_potential_value_from_html(html: str) -> str:
        if not html:
            return ""
        anchor_words = ["homesestimate", "homes estimate", "estimate", "valuation", "value"]
        lower_html = html.lower()
        # Find nearest anchor occurrence
        pos = -1
        for word in anchor_words:
            pos = lower_html.find(word)
            if pos != -1:
                break
        # Search within a window for dollar amounts
        if pos == -1:
            window = html
        else:
            start = max(0, pos - 4000)
            end = min(len(html), pos + 8000)
            window = html[start:end]
        m = re.search(r"\$\s*([0-9]{1,3}(?:,[0-9]{3})+|[0-9]+)(?:\.[0-9]{1,2})?", window)
        return m.group(0) if m else ""

    def fetch_potential_value(driver, url: str) -> str:
        if not driver or not url:
            return ""
        try:
            driver.get(url)
            time.sleep(1.2)
            # Gradual scroll to trigger lazy sections
            total_height = driver.execute_script("return Math.max(document.body.scrollHeight, document.documentElement.scrollHeight);")
            y = 0
            step = 700
            deadline = time.monotonic() + float(os.getenv("PV_PER_URL_TIMEOUT_SECS", "10"))
            for _ in range(12):
                driver.execute_script(f"window.scrollTo(0, {y});")
                time.sleep(0.35)
                html = driver.page_source
                val = extract_potential_value_from_html(html)
                if val:
                    return val
                y += step
                if y >= total_height:
                    break
                if time.monotonic() > deadline:
                    break
            # Final attempt
            return extract_potential_value_from_html(driver.page_source)
        except Exception:
            return ""

    enriched_rows = []
    need_driver = any((len(r) > prop_link_idx and r[prop_link_idx]) for r in rows[1:]) if prop_link_idx is not None else False
    driver = make_driver() if need_driver else None
    for r in rows[1:]:
        # Normalize row length to headers
        current = list(r) + [""] * max(0, len(raw_headers) - len(r))

        listing_raw = (current[list_idx].strip() if list_idx is not None and list_idx < len(current) else "")
        listing_dt = parse_listing_date(listing_raw)
        dom_val = (today - listing_dt).days if listing_dt else 0

        fs_score, fs_triggers, fs_rationale = analyze_forced_sale(
            current[title_idx].strip() if title_idx is not None and title_idx < len(current) else ""
        )

        area_val = parse_area(current[area_idx]) if area_idx is not None and area_idx < len(current) else 0.0
        # PotentialValue via PropertyLink
        potential_value = ""
        if prop_link_idx is not None and prop_link_idx < len(current):
            url = (current[prop_link_idx] or "").strip()
            if url and driver:
                potential_value = fetch_potential_value(driver, url)
                time.sleep(1.0)  # small delay to be gentle

        # Build output row: start with original columns
        out_row = [*current[:len(raw_headers)]]
        # Insert PotentialValue before PropertyLink
        pv_at = prop_link_raw_idx if (prop_link_raw_idx is not None and prop_link_raw_idx <= len(raw_headers)) else len(out_row)
        out_row.insert(pv_at, potential_value)
        # Insert derived values at the same position used for headers, accounting for PV if inserted before
        insert_at = (list_idx + 1) if (list_idx is not None and list_idx < len(raw_headers)) else 0
        if pv_at <= insert_at:
            insert_at += 1
        derived_values = [dom_val, f"{fs_score}", ", ".join(sorted(set(fs_triggers))) if fs_triggers else "", fs_rationale]
        for offset, val in enumerate(derived_values):
            out_row.insert(insert_at + offset, val)

        enriched_rows.append((out_row, dom_val, fs_score, area_val))

    # Sort by: Days on Market desc, Forced Sale Likelihood desc, Area desc
    enriched_rows.sort(key=lambda t: (t[1], t[2], t[3]), reverse=True)

    output_rows = [t[0] for t in enriched_rows]

    if driver:
        try:
            driver.quit()
        except Exception:
            pass

    return {"headers": output_headers, "rows": output_rows}