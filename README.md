# NZ Property Flip Calculator

A comprehensive web application for analyzing New Zealand property flipping opportunities. This tool searches properties, scrapes valuation data, and calculates potential profits with GST considerations.

## Features

- **Property Search**: Search TradeMe for properties by price, bedrooms, and location
- **CSV Upload**: Bulk upload properties with addresses and TradeMe URLs
- **Automated Data Scraping**:
  - Property valuations (RV/CV) from homes.co.nz
  - Recent comparable sales data
  - Insurance quotes from major NZ providers
- **Financial Analysis**:
  - GST-aware profit calculations (entity is GST registered)
  - Pre-tax and post-tax profit projections
  - Recommended purchase prices for unviable deals
- **Intelligent Caching**: Delta function to avoid re-scraping recent data (7-day cache)
- **Modern UI**: React frontend with Material-UI components

## Technology Stack

- **Backend**: Python Flask with REST API
- **Frontend**: React with Material-UI
- **Database**: PostgreSQL
- **Scraping**: BeautifulSoup4, Selenium with polite rate limiting

## Prerequisites

- Python 3.8+
- Node.js 16+
- PostgreSQL 12+

## Installation

### 1. Clone the Repository

```bash
git clone <repository-url>
cd realflip2
```

### 2. Setup PostgreSQL Database

```bash
# Create database
createdb nz_property_flip

# Or using psql
psql -U postgres
CREATE DATABASE nz_property_flip;
\q
```

### 3. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env

# Edit .env with your database credentials
# DATABASE_URL=postgresql://username:password@localhost:5432/nz_property_flip
```

### 4. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install
```

## Running the Application

### Start Backend Server

```bash
cd backend
python app.py

# Backend will run on http://localhost:5000
```

### Start Frontend Development Server

```bash
cd frontend
npm run dev

# Frontend will run on http://localhost:3000
```

### Access the Application

Open your browser and navigate to:
```
http://localhost:3000
```

## Usage

### Search Mode

1. Navigate to the "Search Properties" tab
2. Enter search criteria:
   - Maximum price
   - Number of bedrooms
   - Select cities/regions
3. Click "Search Properties"
4. Once results appear, click "Analyze All Properties"
5. Review profit calculations and recommendations

### CSV Upload Mode

1. Navigate to the "Upload CSV" tab
2. Prepare a CSV file with columns:
   - `Address` (required)
   - `TradeMe URL` (optional)
   - `Bedrooms` (optional)
   - `Price` (optional)
3. Drag and drop or click to upload
4. Click "Upload and Process"
5. Properties will be processed and analyzed

## Financial Calculations

### Formula

The calculator uses the following approach:

```
PP = Purchase Price (85% of RV if not specified)
RV = Rateable Value
CV = Capital Value
TV = Target Value (average of comparable sales, or 90% of CV)
INS = Insurance ($1800 default)
RB = Renovation Budget ($100,000)
LE = Legal Expenses ($2,500)
CR = Council Rates ($2,000)
COM = Commission (1.8% of TV)

GST Claimable = GST on (PP + RB + LE)
GST Payable = GST on TV
Net GST = GST Payable - GST Claimable

Gross Profit = TV - PP - RB - LE - CR - INS - COM
Pre-tax Profit = Gross Profit - Net GST
Post-tax Profit = Pre-tax Profit × (1 - 0.33)
```

### Viability Threshold

- Properties with **post-tax profit ≥ $25,000** are considered viable
- For unviable properties, the system recommends a purchase price to achieve $25,000-$30,000 profit

## Configuration

Edit `backend/.env` to customize:

```env
# Financial defaults
DEFAULT_INSURANCE=1800
DEFAULT_RENOVATION_BUDGET=100000
DEFAULT_LEGAL_EXPENSES=2500
DEFAULT_COUNCIL_RATES=2000
COMMISSION_RATE=0.018
TAX_RATE=0.33
GST_RATE=0.15

# Profit thresholds
MIN_PROFIT_THRESHOLD=25000
TARGET_PROFIT_MIN=25000
TARGET_PROFIT_MAX=30000

# Scraping settings
CACHE_EXPIRY_DAYS=7
RATE_LIMIT_MIN_DELAY=2
RATE_LIMIT_MAX_DELAY=5
```

## Scraping Strategy

The application uses polite scraping practices:

- **Rate Limiting**: 2-5 second delays between requests
- **User-Agent Rotation**: Randomized user agents
- **Caching**: 7-day cache to minimize repeated requests
- **Graceful Fallbacks**: Estimated values when scraping fails
- **Retry Logic**: Automatic retries with exponential backoff

## Database Schema

### Properties
- address, suburb, bedrooms, bathrooms, floor_area
- asking_price, trademe_url
- created_at, updated_at

### Valuations
- property_id, rv, cv, source
- scraped_at

### RecentSales
- address, suburb, bedrooms, floor_area
- sale_price, sale_date
- scraped_at

### AnalysisResults
- property_id, pp, rv, cv, tv
- ins, rb, le, cr, com
- gst_claimable, gst_payable, net_gst
- gross_profit, pre_tax_profit, post_tax_profit
- recommended_pp, is_viable
- analyzed_at

## Troubleshooting

### Database Connection Issues

```bash
# Check PostgreSQL is running
# Windows:
pg_ctl status

# Mac/Linux:
pg_isready

# Verify connection string in .env
DATABASE_URL=postgresql://username:password@localhost:5432/nz_property_flip
```

### Scraping Failures

- **Insurance quotes often fail**: The app falls back to $1800 default
- **TradeMe may block requests**: Anti-bot measures are in place, but heavy usage may trigger blocks
- **Rate limiting**: Scraping many properties takes time (intentionally slow to be polite)

### Frontend Not Connecting to Backend

- Ensure backend is running on port 5000
- Check CORS settings in `backend/app.py`
- Verify proxy settings in `frontend/vite.config.js`

## Future Enhancements

- Selenium integration for JavaScript-heavy sites
- More insurance providers
- Historical price trends
- Export analysis reports to PDF
- Android app deployment
- Cloud hosting setup

## License

Proprietary - For internal use only

## Support

For issues or questions, contact the development team.

