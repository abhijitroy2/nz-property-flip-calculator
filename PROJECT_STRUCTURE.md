# Project Structure

## Overview

```
realflip2/
├── backend/                    # Flask API backend
│   ├── scrapers/              # Web scraping modules
│   ├── routes/                # API endpoints
│   ├── utils/                 # Utility functions
│   ├── models.py              # Database models
│   ├── calculator.py          # Financial calculations
│   ├── config.py              # Configuration
│   ├── app.py                 # Flask application
│   ├── run.py                 # Startup script
│   ├── requirements.txt       # Python dependencies
│   └── Dockerfile            # Docker configuration
│
├── frontend/                  # React frontend
│   ├── src/
│   │   ├── components/       # React components
│   │   ├── services/         # API client
│   │   ├── App.jsx           # Main app component
│   │   ├── main.jsx          # Entry point
│   │   └── index.css         # Global styles
│   ├── index.html            # HTML template
│   ├── vite.config.js        # Vite configuration
│   ├── package.json          # Node dependencies
│   └── Dockerfile            # Docker configuration
│
├── demo_properties.csv        # Sample data
├── docker-compose.yml         # Docker orchestration
├── .gitignore                # Git ignore rules
├── README.md                 # Main documentation
├── QUICKSTART.md             # Quick start guide
├── DEPLOYMENT.md             # Deployment guide
└── PROJECT_STRUCTURE.md      # This file
```

## Backend Structure

### `/backend/scrapers/`

Web scraping modules with polite rate limiting:

- **`base_scraper.py`**: Base class with rate limiting, user-agent rotation, and retry logic
- **`trademe_scraper.py`**: Scrapes TradeMe property listings and details
- **`valuation_scraper.py`**: Scrapes RV/CV values from homes.co.nz
- **`sales_scraper.py`**: Scrapes recent comparable property sales
- **`insurance_scraper.py`**: Attempts to scrape insurance quotes (with fallback)

### `/backend/routes/`

Flask API endpoints:

- **`search.py`**: 
  - `POST /api/search` - Search TradeMe properties
  - `GET /api/property/<id>` - Get property details

- **`analyze.py`**:
  - `POST /api/analyze` - Analyze properties for flip potential
  - `GET /api/analysis/<id>` - Get analysis results

- **`upload.py`**:
  - `POST /api/upload` - Upload and process CSV file

### `/backend/utils/`

Utility modules:

- **`cache_manager.py`**: Database caching with delta function (7-day cache)
- **`csv_parser.py`**: Flexible CSV parsing with auto-column detection
- **`similar_property_matcher.py`**: Find comparable properties (same suburb, bedrooms, ±20% area)

### Core Files

- **`models.py`**: SQLAlchemy database models (Property, Valuation, RecentSale, AnalysisResult)
- **`calculator.py`**: GST-aware profit calculations with tax considerations
- **`config.py`**: Configuration from environment variables
- **`app.py`**: Flask application factory with CORS and route registration

## Frontend Structure

### `/frontend/src/components/`

React components using Material-UI:

- **`SearchForm.jsx`**: Property search form with filters
- **`CSVUpload.jsx`**: Drag-and-drop CSV upload
- **`PropertyList.jsx`**: Display list of properties with analyze button
- **`PropertyCard.jsx`**: Individual property card with details
- **`ProfitCalculation.jsx`**: Profit breakdown display
- **`RecommendationBadge.jsx`**: Visual indicator for deal quality

### `/frontend/src/services/`

- **`api.js`**: Axios-based API client with all endpoint methods

## Database Schema

### Properties Table
```sql
id, address, suburb, bedrooms, bathrooms, floor_area,
asking_price, trademe_url, created_at, updated_at
```

### Valuations Table
```sql
id, property_id, rv, cv, source, scraped_at
```

### Recent Sales Table
```sql
id, address, suburb, bedrooms, floor_area,
sale_price, sale_date, scraped_at
```

### Analysis Results Table
```sql
id, property_id, pp, rv, cv, tv, ins, rb, le, cr, com,
gst_claimable, gst_payable, net_gst,
gross_profit, pre_tax_profit, post_tax_profit,
recommended_pp, is_viable, analyzed_at
```

## Data Flow

### Search Flow
```
User Input → SearchForm → API /search → TrademePropertyScraper
→ Cache → Database → PropertyList → Display
```

### Analysis Flow
```
Property IDs → API /analyze → Parallel Scraping:
  ├─ ValuationScraper (RV/CV)
  ├─ SalesScraper (comparable sales)
  └─ InsuranceScraper (quotes)
→ Calculator → GST & Tax Calculations
→ Database → Display Results
```

### CSV Upload Flow
```
CSV File → CSVParser (auto-detect columns)
→ For each property:
  ├─ Check cache
  ├─ Scrape TradeMe URL if needed
  └─ Save to database
→ Display in PropertyList
```

## Configuration Files

### Backend Environment (`.env`)
```env
DATABASE_URL          # PostgreSQL connection
CACHE_EXPIRY_DAYS     # Cache validity period
RATE_LIMIT_*          # Scraping delays
DEFAULT_*             # Financial defaults
TAX_RATE, GST_RATE    # Tax configuration
```

### Frontend (Vite)
```javascript
// vite.config.js
server.port           # Dev server port
server.proxy          # API proxy configuration
```

## Key Features

### 1. Intelligent Caching
- 7-day cache for scraped data
- Delta function checks freshness before re-scraping
- Reduces load on external sites

### 2. Polite Scraping
- 2-5 second delays between requests
- User-agent rotation
- Retry logic with backoff
- Graceful fallbacks

### 3. Financial Calculations
```
GST Entity Considerations:
- GST claimable on purchase, renovations, legal fees
- GST payable on sale
- Net GST affects final profit

Tax Calculation:
- 33% tax rate on pre-tax profit
- Minimum $25k post-tax profit threshold
- Automatic PP recommendations for unviable deals
```

### 4. Flexible CSV Import
- Auto-detects column names
- Required: Address
- Optional: TradeMe URL, Bedrooms, Price
- Scrapes missing data from TradeMe

### 5. Modern UI
- Material-UI components
- Responsive design
- Real-time loading states
- Color-coded recommendations
- Detailed profit breakdowns

## Extension Points

### Adding New Scrapers
1. Extend `BaseScraper` in `/backend/scrapers/`
2. Implement `scrape()` method
3. Add to relevant route handler

### Adding New Financial Parameters
1. Update `calculator.py` formulas
2. Add fields to `AnalysisResult` model
3. Update frontend `ProfitCalculation.jsx`

### Adding New Search Criteria
1. Update `SearchForm.jsx` with new field
2. Add parameter to `/api/search` endpoint
3. Update `TrademePropertyScraper.search_properties()`

## Testing

### Manual Testing
```bash
# Test backend API directly
curl http://localhost:5000/health
curl -X POST http://localhost:5000/api/search \
  -H "Content-Type: application/json" \
  -d '{"max_price": 800000, "bedrooms": 3}'

# Test CSV upload
curl -X POST http://localhost:5000/api/upload \
  -F "file=@demo_properties.csv"
```

### Database Queries
```sql
-- Check cached properties
SELECT * FROM properties ORDER BY created_at DESC LIMIT 10;

-- View analysis results
SELECT p.address, a.post_tax_profit, a.is_viable
FROM properties p
JOIN analysis_results a ON p.id = a.property_id
ORDER BY a.post_tax_profit DESC;

-- Cache statistics
SELECT source, COUNT(*), MAX(scraped_at)
FROM valuations
GROUP BY source;
```

## Performance Optimization

### Backend
- Use connection pooling
- Add database indexes
- Implement async scraping
- Add Redis for session caching

### Frontend
- Code splitting
- Lazy loading components
- Image optimization
- Progressive web app (PWA)

### Database
- Index on address, suburb, bedrooms
- Partition by date for sales table
- Regular VACUUM and ANALYZE

## Security Notes

- No authentication implemented (local use)
- CORS enabled for localhost
- SQL injection protection (SQLAlchemy)
- XSS protection (React escaping)
- Rate limiting on scraping only

For production deployment, add:
- JWT authentication
- API rate limiting
- HTTPS/SSL
- Input validation
- Logging and monitoring

