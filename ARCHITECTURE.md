# System Architecture

## High-Level Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                        USER BROWSER                              │
│                     http://localhost:3000                        │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            │ HTTP/JSON
                            │
┌───────────────────────────▼─────────────────────────────────────┐
│                     REACT FRONTEND                               │
│  ┌─────────────┐  ┌──────────────┐  ┌─────────────────────┐   │
│  │ SearchForm  │  │  CSVUpload   │  │   PropertyList      │   │
│  └─────────────┘  └──────────────┘  └─────────────────────┘   │
│  ┌─────────────┐  ┌──────────────┐  ┌─────────────────────┐   │
│  │PropertyCard │  │Profit        │  │ Recommendation      │   │
│  │             │  │Calculation   │  │ Badge               │   │
│  └─────────────┘  └──────────────┘  └─────────────────────┘   │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │              API Service (Axios)                         │  │
│  └──────────────────────────────────────────────────────────┘  │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            │ REST API
                            │
┌───────────────────────────▼─────────────────────────────────────┐
│                     FASTAPI BACKEND                              │
│                   http://localhost:5000                          │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                    API Routes                            │  │
│  │  ┌─────────────┐ ┌─────────────┐ ┌─────────────────┐   │  │
│  │  │   Search    │ │   Analyze   │ │     Upload      │   │  │
│  │  │   /search   │ │   /analyze  │ │     /upload     │   │  │
│  │  └─────────────┘ └─────────────┘ └─────────────────┘   │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                  Business Logic                          │  │
│  │  ┌─────────────────────────────────────────────────┐    │  │
│  │  │          Property Flip Calculator                │    │  │
│  │  │  • GST calculations                              │    │  │
│  │  │  • Tax calculations (33%)                        │    │  │
│  │  │  • Profit projections                            │    │  │
│  │  │  • Purchase price recommendations                │    │  │
│  │  └─────────────────────────────────────────────────┘    │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                    Utilities                             │  │
│  │  ┌──────────────┐ ┌──────────────┐ ┌───────────────┐   │  │
│  │  │Cache Manager │ │  CSV Parser  │ │Similar Property│   │  │
│  │  │(7-day cache) │ │(auto-detect) │ │    Matcher     │   │  │
│  │  └──────────────┘ └──────────────┘ └───────────────┘   │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                  Web Scrapers                            │  │
│  │  ┌──────────────┐ ┌──────────────┐ ┌───────────────┐   │  │
│  │  │   TradeMe    │ │  Valuation   │ │     Sales     │   │  │
│  │  │   Scraper    │ │   Scraper    │ │    Scraper    │   │  │
│  │  └──────────────┘ └──────────────┘ └───────────────┘   │  │
│  │  ┌──────────────┐ ┌──────────────────────────────────┐ │  │
│  │  │  Insurance   │ │      Base Scraper                │ │  │
│  │  │   Scraper    │ │  • Rate limiting (2-5s)          │ │  │
│  │  └──────────────┘ │  • User-agent rotation           │ │  │
│  │                    │  • Retry logic (3x)              │ │  │
│  │                    └──────────────────────────────────┘ │  │
│  └──────────────────────────────────────────────────────────┘  │
│                            │                                     │
│                            │ SQLAlchemy ORM                      │
└────────────────────────────┼─────────────────────────────────────┘
                             │
                             │
┌────────────────────────────▼─────────────────────────────────────┐
│                    POSTGRESQL DATABASE                           │
│                   localhost:5432/nz_property_flip                │
│                                                                  │
│  ┌─────────────────┐  ┌─────────────────┐  ┌────────────────┐ │
│  │   properties    │  │   valuations    │  │  recent_sales  │ │
│  │                 │  │                 │  │                │ │
│  │ • address       │  │ • property_id   │  │ • address      │ │
│  │ • suburb        │  │ • rv            │  │ • suburb       │ │
│  │ • bedrooms      │  │ • cv            │  │ • bedrooms     │ │
│  │ • bathrooms     │  │ • source        │  │ • floor_area   │ │
│  │ • floor_area    │  │ • scraped_at    │  │ • sale_price   │ │
│  │ • asking_price  │  │                 │  │ • sale_date    │ │
│  │ • trademe_url   │  └─────────────────┘  │ • scraped_at   │ │
│  │ • created_at    │                       └────────────────┘ │
│  │ • updated_at    │  ┌─────────────────────────────────────┐ │
│  └─────────────────┘  │     analysis_results                │ │
│                       │                                     │ │
│                       │ • property_id                       │ │
│                       │ • pp, rv, cv, tv                    │ │
│                       │ • ins, rb, le, cr, com              │ │
│                       │ • gst_claimable, gst_payable        │ │
│                       │ • gross_profit                      │ │
│                       │ • pre_tax_profit                    │ │
│                       │ • post_tax_profit                   │ │
│                       │ • recommended_pp                    │ │
│                       │ • is_viable                         │ │
│                       │ • analyzed_at                       │ │
│                       └─────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────────┘
                             │
                             │ HTTP Requests
                             │
┌────────────────────────────▼─────────────────────────────────────┐
│                    EXTERNAL DATA SOURCES                         │
│                                                                  │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────┐ │
│  │   TradeMe.co.nz  │  │   homes.co.nz    │  │ realestate   │ │
│  │                  │  │                  │  │   .co.nz     │ │
│  │ Property listings│  │ RV/CV valuations │  │ Recent sales │ │
│  └──────────────────┘  └──────────────────┘  └──────────────┘ │
│                                                                  │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────┐ │
│  │  AMI Insurance   │  │ State Insurance  │  │ AA Insurance │ │
│  │                  │  │                  │  │              │ │
│  │   House quotes   │  │   House quotes   │  │ House quotes │ │
│  └──────────────────┘  └──────────────────┘  └──────────────┘ │
└──────────────────────────────────────────────────────────────────┘
```

## Data Flow Diagrams

### Search Flow

```
User Input
    │
    ├─ Max Price: $800,000
    ├─ Bedrooms: 3
    └─ Cities: Auckland, Wellington
    │
    ▼
SearchForm Component
    │
    │ POST /api/search
    ▼
FastAPI Search Route
    │
    ├─ Check Cache (7 days)
    │   └─ Cache Hit? → Return cached
    │
    ▼
TradeMe Scraper
    │
    ├─ Rate Limiting (2-5s)
    ├─ User-Agent Rotation
    └─ Parse HTML
    │
    ▼
Extract Property Data
    │
    ├─ Address
    ├─ Bedrooms, Bathrooms
    ├─ Floor Area
    ├─ Asking Price
    └─ TradeMe URL
    │
    ▼
Cache in PostgreSQL
    │
    ▼
Return to Frontend
    │
    ▼
PropertyList Component
    │
    └─ Display Results
```

### Analysis Flow

```
Property IDs
    │
    ▼
Analyze Button Clicked
    │
    │ POST /api/analyze
    ▼
FastAPI Analyze Route
    │
    ▼
For Each Property (Sequential):
    │
    ├─────────────────────────────────┬──────────────────────────┐
    │                                 │                          │
    ▼                                 ▼                          ▼
Valuation Scraper              Sales Scraper            Insurance Scraper
    │                                 │                          │
    ├─ Check Cache                    ├─ Check Cache            ├─ Try 3 providers
    ├─ Scrape homes.co.nz             ├─ Find comparables       │   • AMI
    ├─ Extract RV/CV                  │   • Same suburb          │   • State
    └─ Cache result                   │   • Same bedrooms        │   • AA
                                      │   • ±20% floor area      │
                                      │   • Last 3 months        ├─ Fallback: $1800
                                      └─ Calculate average       │
                                                                 │
    └──────────────────────┬──────────────────┬─────────────────┘
                           │                  │
                           ▼                  │
                   All Data Collected         │
                           │                  │
                           ▼                  │
                Property Flip Calculator      │
                           │                  │
    ┌──────────────────────┴────────────────────────────────┐
    │                                                        │
    │  Calculate:                                           │
    │  1. Purchase Price (PP) = 85% of RV or asking price   │
    │  2. Target Value (TV) = avg comparable sales or 90% CV│
    │  3. GST Claimable = GST on (PP + RB + LE)            │
    │  4. GST Payable = GST on TV                           │
    │  5. Net GST = GST Payable - GST Claimable            │
    │  6. Gross Profit = TV - PP - costs                    │
    │  7. Pre-tax Profit = Gross Profit - Net GST          │
    │  8. Post-tax Profit = Pre-tax × 0.67                 │
    │  9. Recommended PP (if not viable)                    │
    │                                                        │
    └────────────────────────┬───────────────────────────────┘
                             │
                             ▼
                  Save to analysis_results
                             │
                             ▼
                  Return Complete Analysis
                             │
                             ▼
                     Frontend Display
                             │
    ┌────────────────────────┼────────────────────────┐
    │                        │                        │
    ▼                        ▼                        ▼
PropertyCard          ProfitCalculation      RecommendationBadge
    │                        │                        │
    ├─ Property details      ├─ Gross Profit         ├─ Excellent Deal
    ├─ Costs breakdown       ├─ Pre-tax Profit       ├─ Good Deal
    └─ GST summary           └─ Post-tax Profit      ├─ Marginal
                                                      └─ Not Viable
```

### CSV Upload Flow

```
User Selects CSV File
    │
    ▼
CSVUpload Component
    │
    ├─ Drag & Drop
    └─ or File Browse
    │
    │ POST /api/upload (multipart/form-data)
    ▼
FastAPI Upload Route
    │
    ▼
CSV Parser
    │
    ├─ Read CSV
    ├─ Auto-detect columns:
    │   ├─ Address (required)
    │   ├─ TradeMe URL (optional)
    │   ├─ Bedrooms (optional)
    │   └─ Price (optional)
    │
    ▼
For Each Row:
    │
    ├─ Has TradeMe URL?
    │   │
    │   ├─ Yes: Scrape additional data
    │   │   ├─ Bedrooms
    │   │   ├─ Bathrooms
    │   │   ├─ Floor Area
    │   │   └─ Suburb
    │   │
    │   └─ No: Use CSV data only
    │
    ▼
Cache in PostgreSQL
    │
    ▼
Return Property List
    │
    ▼
Display in PropertyList
    │
    └─ Ready for Analysis
```

## Caching Strategy

```
Request for Data
    │
    ▼
Cache Manager
    │
    ├─ Check database
    │   │
    │   ├─ Data exists?
    │   │   │
    │   │   ├─ Yes: Check timestamp
    │   │   │   │
    │   │   │   ├─ < 7 days old? → Return cached data ✓
    │   │   │   └─ ≥ 7 days old? → Fetch fresh data
    │   │   │
    │   │   └─ No: Fetch fresh data
    │
    ▼
Fetch Fresh Data
    │
    ├─ Scrape website
    ├─ Extract data
    └─ Save to cache
    │
    ▼
Return Data
```

## Security Architecture

```
┌─────────────────────────────────────────────────────┐
│                   Security Layers                    │
│                                                      │
│  Frontend (React)                                    │
│  ├─ XSS Protection (React automatic escaping)       │
│  ├─ CORS: localhost only                            │
│  └─ No sensitive data storage                       │
│                                                      │
│  Backend (FastAPI)                                   │
│  ├─ SQL Injection Protection (SQLAlchemy ORM)       │
│  ├─ Input validation on all endpoints               │
│  ├─ CORS whitelist (localhost:3000, 5173)           │
│  ├─ Rate limiting on scrapers (not API)             │
│  └─ Environment variables for secrets                │
│                                                      │
│  Database (PostgreSQL)                               │
│  ├─ Password authentication                          │
│  ├─ Localhost binding only                          │
│  └─ SSL/TLS ready (not enabled by default)          │
│                                                      │
│  Scraping                                            │
│  ├─ Polite delays (2-5 seconds)                     │
│  ├─ User-agent rotation                              │
│  ├─ Respect for robots.txt                          │
│  └─ Graceful failure handling                       │
│                                                      │
│  ⚠️  NOT IMPLEMENTED (Local use only):               │
│  ├─ User authentication                              │
│  ├─ API rate limiting                                │
│  ├─ HTTPS/SSL                                        │
│  └─ Input sanitization beyond SQLAlchemy             │
└─────────────────────────────────────────────────────┘
```

## Deployment Architectures

### Local Development (Current)

```
┌──────────────────────────────────────┐
│         Developer Machine             │
│                                       │
│  ┌─────────────┐  ┌───────────────┐ │
│  │   React     │  │    FastAPI    │ │
│  │   :3000     │  │    :5000      │ │
│  └─────────────┘  └───────────────┘ │
│         │                │           │
│         └────────┬───────┘           │
│                  │                   │
│          ┌───────▼────────┐          │
│          │   PostgreSQL   │          │
│          │     :5432      │          │
│          └────────────────┘          │
└──────────────────────────────────────┘
```

### Docker Deployment

```
┌──────────────────────────────────────────────┐
│            Docker Host                        │
│                                               │
│  ┌──────────────┐  ┌─────────────────────┐  │
│  │  Frontend    │  │      Backend        │  │
│  │  Container   │  │      Container      │  │
│  │              │  │                     │  │
│  │  Node:18     │  │   Python:3.11       │  │
│  │  Port 3000   │  │   Port 5000         │  │
│  └──────────────┘  └─────────────────────┘  │
│         │                     │               │
│         └──────────┬──────────┘               │
│                    │                          │
│         ┌──────────▼───────────┐              │
│         │    PostgreSQL        │              │
│         │    Container         │              │
│         │                      │              │
│         │   Postgres:15        │              │
│         │   Port 5432          │              │
│         │   Volume: postgres_data             │
│         └──────────────────────┘              │
│                                               │
│  Docker Compose Network                       │
└──────────────────────────────────────────────┘
```

### Production (Cloud VM)

```
                        Internet
                           │
                    ┌──────▼──────┐
                    │   Nginx     │
                    │   :80/443   │
                    └──────┬──────┘
                           │
            ┌──────────────┴──────────────┐
            │                             │
    ┌───────▼────────┐          ┌────────▼────────┐
    │  React Build   │          │  FastAPI (Uvicorn)│
    │  (Static)      │          │  Systemd Service │
    │                │          │  :5000           │
    └────────────────┘          └────────┬─────────┘
                                         │
                                ┌────────▼──────────┐
                                │   PostgreSQL      │
                                │   Managed Service │
                                │   (Cloud)         │
                                └───────────────────┘
```

## Performance Characteristics

### Response Times (Typical)

```
Endpoint              First Hit    Cached      Notes
────────────────────────────────────────────────────────
/api/search           20-40s       0.5-2s      TradeMe scraping
/api/analyze (1 prop) 120-300s     5-15s       Multiple scrapers
/api/upload           5-10s        instant     CSV parsing only
/api/property/<id>    instant      instant     Database query
/api/analysis/<id>    instant      instant     Database query
```

### Bottlenecks

```
Operation               Time      Bottleneck
────────────────────────────────────────────────
TradeMe scraping        15-30s    Rate limiting + parsing
Valuation scraping      20-40s    Rate limiting + parsing
Sales scraping          30-60s    Rate limiting + parsing
Insurance scraping      45-90s    JavaScript rendering (often fails)
Database queries        <0.1s     None (indexed)
React rendering         <0.5s     None
```

### Scalability Limits (Current Implementation)

```
Concurrent Users:        1-5      (No session management)
Properties per hour:     20-40    (Rate limiting)
Database size:           100k+    (PostgreSQL handles well)
Cache effectiveness:     70-90%   (7-day expiry)
```

## Technology Dependencies

```
Backend:
├─ Python 3.8+
├─ FastAPI 0.104+
├─ SQLAlchemy (ORM)
├─ PostgreSQL driver
├─ BeautifulSoup4 (HTML parsing)
├─ Selenium (optional, for JS sites)
├─ Requests (HTTP client)
└─ python-dotenv (config)

Frontend:
├─ Node.js 16+
├─ React 18
├─ Vite (build tool)
├─ Material-UI 5
├─ Axios (HTTP client)
└─ React-Dropzone (file upload)

Infrastructure:
├─ PostgreSQL 12+
├─ Chrome/Chromium (for Selenium)
└─ npm (package manager)
```

## Summary

This architecture provides:
- ✅ Clear separation of concerns
- ✅ RESTful API design
- ✅ Intelligent caching for performance
- ✅ Polite web scraping practices
- ✅ GST-aware financial calculations
- ✅ Scalable database schema
- ✅ Modern, responsive UI
- ✅ Multiple deployment options
- ✅ Comprehensive error handling
- ✅ Extensive documentation

**Status**: Production-ready for local use, extendable for cloud deployment.

