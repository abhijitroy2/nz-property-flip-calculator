# Desktop App Quick Start Guide

## 🚀 Fastest Way to Get Started

### Step 1: Run Setup Script

Double-click or run from Command Prompt:
```cmd
desktop\setup_desktop.bat
```

This will:
- ✅ Check Python installation
- ✅ Create virtual environment
- ✅ Install all dependencies
- ✅ Test that everything works

### Step 2: Run the App

Double-click or run:
```cmd
desktop\run_desktop.bat
```

Or manually:
```cmd
venv_desktop\Scripts\activate
python -m desktop.app
```

## 📋 What You Need

1. **CSV File** with property data
   - Required column: `Address` or `Property Address`
   - Optional: `TradeMe URL`, `Bedrooms`, `Price`

2. **Output Folder** where reports will be saved
   - Default: `Documents\RealFlipReports`

## 🎯 First Run

1. **Open the app** - Settings window appears
2. **Click "Browse"** next to "CSV Files" → Select your CSV
3. **Click "Browse"** next to "Output Folder" → Choose where to save reports
4. **Click "Run Now"** → Wait for analysis to complete
5. **Check output folder** → Find `Results_*.json` and `Analysis_*.pdf` files

## ⚙️ Configuration

The app saves settings in: `%APPDATA%\RealFlip\config.json`

You can edit this file directly or use the GUI.

## 📊 Output Files

After analysis, you'll get:

- **Results_YYYYMMDD_HHMMSS.json** - Raw data
- **Analysis_YYYYMMDD_HHMMSS.pdf** - Formatted report (or .html if PDF fails)

## 🔄 Scheduled Runs

Set interval in minutes (e.g., 60 = every hour):
1. Enter number in "Interval (minutes)" field
2. Click "Apply"
3. App will run automatically at that interval

## 📧 Email Reports (Optional)

To enable email:
1. Edit `%APPDATA%\RealFlip\config.json`
2. Set `email.enabled: true`
3. Add SMTP credentials and recipients

## 🛠️ Troubleshooting

**"Module not found" errors:**
→ Run `desktop\setup_desktop.bat` again

**"No CSV paths configured":**
→ Use the GUI to browse and select your CSV file

**Analysis takes long:**
→ Normal! Scraping takes 2-5 minutes per property

**PDF not generated:**
→ Install WeasyPrint or use HTML output (works fine)

## 📝 Example CSV Format

```csv
Address,TradeMe URL,Bedrooms,Price
"123 Main St, Auckland",https://www.trademe.co.nz/property/123,3,750000
"456 Queen St, Wellington",,2,650000
```

## 🎮 Command Line Options

```cmd
# Run with GUI (default)
python -m desktop.app

# Run once without GUI
python -m desktop.app --run-once

# Show config file location
python -m desktop.app --show-config-path
```

## 💡 Tips

- Start with **1-2 properties** to test
- **First run is slowest** (no cache)
- **Subsequent runs are faster** (uses cached data)
- Check **console output** for progress updates
- Reports are **timestamped** - old ones aren't overwritten

## 📚 Full Documentation

See `desktop/SETUP_INSTRUCTIONS.md` for detailed setup guide.

