# Quick Start Guide

## Prerequisites

1. **Python 3.8+** installed
2. **Node.js 16+** installed
3. **PostgreSQL 12+** installed and running

## Windows Quick Setup

1. Open Command Prompt or PowerShell as Administrator
2. Navigate to the project directory:
   ```cmd
   cd C:\Users\OEM\realflip2
   ```

3. Run the setup script:
   ```cmd
   setup.bat
   ```

4. Follow the prompts to configure the database

## Manual Setup (If script fails)

### Backend

```cmd
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

Create `backend\.env` file:
```env
DATABASE_URL=postgresql://postgres:your_password@localhost:5432/nz_property_flip
CACHE_EXPIRY_DAYS=7
RATE_LIMIT_MIN_DELAY=2
RATE_LIMIT_MAX_DELAY=5
DEFAULT_INSURANCE=1800
DEFAULT_RENOVATION_BUDGET=100000
DEFAULT_LEGAL_EXPENSES=2500
DEFAULT_COUNCIL_RATES=2000
COMMISSION_RATE=0.018
TAX_RATE=0.33
GST_RATE=0.15
MIN_PROFIT_THRESHOLD=25000
TARGET_PROFIT_MIN=25000
TARGET_PROFIT_MAX=30000
```

### Database

```cmd
psql -U postgres
CREATE DATABASE nz_property_flip;
\q
```

### Frontend

```cmd
cd frontend
npm install
```

## Running the Application

### Terminal 1 - Backend

```cmd
cd backend
venv\Scripts\activate
python app.py
```

Backend will start on http://localhost:5000

### Terminal 2 - Frontend

```cmd
cd frontend
npm run dev
```

Frontend will start on http://localhost:3000

### Access the App

Open your browser: http://localhost:3000

## First Use

1. **Search Mode**:
   - Go to "Search Properties" tab
   - Enter max price (e.g., 800000)
   - Select bedrooms (e.g., 3)
   - Pick cities (e.g., Auckland, Wellington)
   - Click "Search Properties"
   - Wait for results
   - Click "Analyze All Properties"
   - Review profit calculations

2. **CSV Mode**:
   - Create a CSV with columns: Address, TradeMe URL
   - Go to "Upload CSV" tab
   - Drag and drop your CSV file
   - Click "Upload and Process"
   - Review results

## Expected CSV Format

```csv
Address,TradeMe URL,Bedrooms,Price
"123 Main St, Auckland",https://www.trademe.co.nz/property/...,3,750000
"456 Queen St, Wellington",https://www.trademe.co.nz/property/...,4,850000
```

## Troubleshooting

### Port Already in Use

If port 5000 or 3000 is in use:

Backend - Edit `backend/app.py`, change:
```python
app.run(debug=True, host='0.0.0.0', port=5001)  # Changed to 5001
```

Frontend - Edit `frontend/vite.config.js`, change:
```javascript
server: {
  port: 3001,  // Changed to 3001
  ...
}
```

### Database Connection Error

1. Ensure PostgreSQL is running:
   ```cmd
   pg_ctl status
   ```

2. Check your `.env` file has correct credentials

3. Test connection:
   ```cmd
   psql -U postgres -d nz_property_flip
   ```

### Module Not Found Errors

Backend:
```cmd
cd backend
venv\Scripts\activate
pip install -r requirements.txt
```

Frontend:
```cmd
cd frontend
npm install
```

### Scraping Issues

- **Slow scraping**: This is intentional (polite scraping with 2-5s delays)
- **Insurance quotes fail**: Normal - app uses $1800 default
- **TradeMe blocking**: If heavily used, may need to wait or use different IP

## Performance Notes

- First search/analysis is slow (scraping + no cache)
- Subsequent analyses are faster (7-day cache)
- Analyzing 10 properties may take 5-10 minutes
- Progress shown in backend terminal

## Need Help?

1. Check backend terminal for error messages
2. Check browser console (F12) for frontend errors
3. Review logs in `backend/` directory
4. Ensure all services (PostgreSQL, backend, frontend) are running

## Sample Data

Example CSV for testing (save as `test_properties.csv`):

```csv
Address,TradeMe URL
"39 Canal Road, Avondale, Auckland",
"123 Lambton Quay, Wellington",
"456 Worcester Street, Christchurch"
```

