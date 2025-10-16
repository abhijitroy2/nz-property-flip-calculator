# NZ Property Flip Calculator - Setup Instructions

## 🚀 Quick Start Guide

### Prerequisites
Your friend needs to install:
1. **Node.js** (v18 or higher) - Download from https://nodejs.org/
2. **Python** (v3.9 or higher) - Download from https://python.org/
3. **PostgreSQL** - Download from https://postgresql.org/

### Installation Steps

#### 1. Backend Setup
```bash
# Navigate to backend folder
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

# Set up environment variables
copy .env.example .env
# Edit .env file with your database credentials

# Run the backend
python run.py
```

#### 2. Frontend Setup
```bash
# Navigate to frontend folder (in a new terminal)
cd frontend

# Install dependencies
npm install

# Start the frontend
npm run dev
```

#### 3. Database Setup
```bash
# Create database in PostgreSQL
createdb nz_property_flip

# Or using psql:
psql -U postgres
CREATE DATABASE nz_property_flip;
```

### Usage
1. Backend runs on: http://localhost:5000
2. Frontend runs on: http://localhost:3000
3. Upload CSV files with property data
4. Click "Analyze All Properties" to see financial calculations

### CSV Format
Your CSV should have columns like:
- Property Address
- Property Link (TradeMe URL)
- Bedrooms
- Bathrooms
- Area
- Price

### Features
- ✅ Interest cost calculations
- ✅ GST and tax calculations
- ✅ Profit recommendations
- ✅ Auto-detection of CSV columns
- ✅ TradeMe link integration

## 🆘 Troubleshooting

**If you get errors:**
1. Make sure all prerequisites are installed
2. Check that PostgreSQL is running
3. Verify database credentials in .env file
4. Ensure ports 3000 and 5000 are available

**For help:** Check the main README.md file for detailed documentation.
