# 🏠 Get Started with NZ Property Flip Calculator

## What You Have Now

A complete web application that:
- ✅ Searches TradeMe for properties
- ✅ Uploads CSV files with property data
- ✅ Scrapes property valuations (RV/CV)
- ✅ Finds comparable sales
- ✅ Gets insurance quotes
- ✅ Calculates GST-aware profits
- ✅ Recommends purchase prices
- ✅ Beautiful modern UI

## Fastest Way to Start (Windows)

### Step 1: Install Prerequisites (if not already installed)

1. **PostgreSQL**: https://www.postgresql.org/download/windows/
   - Remember the password you set for 'postgres' user

2. **Python 3.8+**: https://www.python.org/downloads/
   - ✅ Check "Add Python to PATH" during installation

3. **Node.js 16+**: https://nodejs.org/
   - Download LTS version

### Step 2: Run Setup

Open Command Prompt in the `C:\Users\OEM\realflip2` folder:

```cmd
setup.bat
```

Follow the prompts and enter your PostgreSQL password when asked.

### Step 3: Start the Application

**Terminal 1 - Backend:**
```cmd
cd app
python main.py
```

**Terminal 2 - Frontend:**
```cmd
cd frontend
npm run dev
```

### Step 4: Open Your Browser

Go to: **http://localhost:3000**

## First Property Analysis

### Option 1: Search TradeMe

1. Click "Search Properties" tab
2. Enter:
   - Max Price: `800000`
   - Bedrooms: `3`
   - Select cities: `Auckland`, `Wellington`
3. Click "Search Properties" (takes ~30 seconds)
4. Click "Analyze All Properties" (takes 2-5 mins per property)
5. Review profit calculations

### Option 2: Upload CSV

1. Click "Upload CSV" tab
2. Use the provided `demo_properties.csv` or create your own:
   ```csv
   Address,TradeMe URL,Bedrooms,Price
   "123 Main St, Auckland",,3,750000
   ```
3. Drag and drop the file
4. Click "Upload and Process"
5. Properties will appear in the results tab

## Understanding the Results

### Property Card Shows:
- 📍 Address and location
- 🛏️ Bedrooms, bathrooms, floor area
- 💰 Asking price
- 🔗 TradeMe link

### After Analysis:
- 📊 **Gross Profit** - Before GST/tax
- 💵 **Pre-tax Profit** - After GST considerations
- 💰 **Post-tax Profit** - Your actual profit (after 33% tax)

### Color-Coded Badges:
- 🟢 **Excellent Deal** - Profit > $50k
- 🟢 **Good Deal** - Profit $25k-$50k
- 🟡 **Marginal** - Profit $10k-$25k
- 🔴 **Not Viable** - Profit < $10k

### Recommendations:
For unviable properties, you'll see:
> **Recommended Purchase Price: $XXX,XXX**
> At this price, you would achieve $25,000-$30,000 post-tax profit.

## Key Features

### Intelligent Caching ⚡
- First analysis: Slow (scraping data)
- Subsequent: Fast (using cached data)
- Cache expires after 7 days

### GST Considerations 💼
The calculator knows you're GST registered:
- ✅ Claims GST on purchase, renovations, legal fees
- ✅ Charges GST on sale
- ✅ Calculates net GST impact on profit

### Financial Defaults 📋
You can change these in `backend/.env`:
- Insurance: $1,800
- Renovation Budget: $100,000
- Legal Expenses: $2,500
- Council Rates: $2,000
- Commission: 1.8% of sale price
- Tax Rate: 33%

### Data Sources 🌐
The app automatically scrapes:
- **TradeMe**: Property listings and details
- **homes.co.nz**: RV/CV valuations
- **realestate.co.nz**: Recent sales data
- **Insurance providers**: Quotes (with fallback)

## Tips for Best Results

### 1. Be Patient
- Scraping takes time (2-5 second delays between requests)
- First property: ~2-5 minutes
- Subsequent (cached): ~10-30 seconds

### 2. Use Complete Addresses
Better: `"123 Main Street, Ponsonby, Auckland"`
Worse: `"123 Main St"`

### 3. Provide TradeMe URLs When Possible
- More accurate data
- Gets bedrooms, bathrooms, floor area
- More reliable pricing

### 4. Check the Detailed Breakdown
Click "Show Detailed Breakdown" to see:
- All cost components
- GST calculations
- Data sources

## Common Questions

### Q: Why is it taking so long?
**A:** The app scrapes multiple websites for each property:
- TradeMe for property details
- homes.co.nz for valuations
- realestate.co.nz for recent sales
- Insurance providers for quotes
Each has 2-5 second delays to be polite.

### Q: Why did some data say "N/A"?
**A:** Scraping might have failed. The app uses intelligent fallbacks:
- If RV not found: Uses CV
- If no recent sales: Uses 90% of CV
- If insurance fails: Uses $1800 default

### Q: Can I change the financial assumptions?
**A:** Yes! Edit `backend/.env`:
```env
DEFAULT_RENOVATION_BUDGET=150000
DEFAULT_INSURANCE=2000
MIN_PROFIT_THRESHOLD=30000
```
Then restart the backend.

### Q: The search isn't finding properties
**A:** TradeMe's anti-scraping measures may block requests. Try:
1. Wait a few minutes
2. Use more specific search criteria
3. Use CSV upload with direct addresses instead

### Q: Can I analyze properties again?
**A:** Yes! The app uses 7-day cache, so re-analyzing within a week is instant. After 7 days, it will re-scrape fresh data.

## Stopping the Application

### Backend (Terminal 1):
Press `CTRL+C`

### Frontend (Terminal 2):
Press `CTRL+C`

### Restart Anytime:
Just run the same commands again. Your data is safely stored in PostgreSQL.

## Next Steps

1. ✅ **Test with demo data**: Use `demo_properties.csv`
2. 📝 **Create your own CSV**: Add properties you're interested in
3. 🔍 **Search TradeMe**: Find properties in your target areas
4. 📊 **Review recommendations**: Look for deals with $25k+ profit
5. ⚙️ **Customize settings**: Adjust defaults in `.env`

## Need Help?

- 📖 **Full documentation**: See `README.md`
- 🚀 **Quick setup**: See `QUICKSTART.md`
- 🏗️ **Architecture**: See `PROJECT_STRUCTURE.md`
- 🚢 **Deployment**: See `DEPLOYMENT.md`

## What's Happening Behind the Scenes?

When you click "Analyze":
1. 🔍 Searches cache for existing data
2. 🌐 Scrapes homes.co.nz for RV/CV values
3. 🏘️ Finds recent sales in same area
4. 🏢 Attempts insurance quotes
5. 🧮 Calculates GST impact
6. 💰 Computes pre/post-tax profit
7. 📊 Generates recommendation
8. 💾 Saves to database for future speed

All politely and automatically!

## You're Ready! 🎉

Open http://localhost:3000 and start finding profitable property flips!

Remember:
- ✅ First property takes longest (building cache)
- ✅ Profit must be $25k+ to be viable
- ✅ Green badges = good deals
- ✅ Red badges = negotiate lower price
- ✅ All calculations include GST impact

Happy property flipping! 🏠💰

