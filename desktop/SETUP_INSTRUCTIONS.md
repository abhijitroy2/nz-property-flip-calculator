# Desktop App Setup Instructions

## Prerequisites

Before running the desktop app, ensure you have:

1. **Python 3.8 or higher** installed
   - Download from: https://www.python.org/downloads/
   - ✅ **IMPORTANT**: Check "Add Python to PATH" during installation
   - Verify installation: Open Command Prompt and run `python --version`

2. **Chrome/Chromium browser** (for web scraping)
   - The app uses Selenium with ChromeDriver
   - Chrome will be automatically downloaded if needed

## Step-by-Step Setup

### Step 1: Navigate to Project Directory

Open **Command Prompt** or **PowerShell** and navigate to the project:

```cmd
cd C:\Users\OEM\realflip2
```

### Step 2: Create Virtual Environment (Recommended)

Create a virtual environment to isolate dependencies:

```cmd
python -m venv venv_desktop
```

Activate the virtual environment:

```cmd
venv_desktop\Scripts\activate
```

You should see `(venv_desktop)` in your prompt.

### Step 3: Install Dependencies

Install all required Python packages:

```cmd
pip install --upgrade pip
```

Install main project dependencies (from root requirements.txt):

```cmd
pip install -r requirements.txt
```

Install additional desktop-specific dependencies:

```cmd
pip install apscheduler jinja2 weasyprint
```

**Note**: If `weasyprint` installation fails (it requires system libraries), you can skip it - the app will fall back to HTML output instead of PDF.

### Step 4: Verify Installation

Test that all imports work:

```cmd
python -c "from desktop import app; print('✓ Desktop app imports successful')"
```

If you see the success message, you're ready to run!

## Running the Desktop App

### Option 1: Run with Settings Window (Recommended for First Time)

This opens a GUI window where you can configure CSV paths, output directory, and schedule:

```cmd
python -m desktop.app
```

**What you'll see:**
- A Tkinter window with:
  - CSV Files: Browse button to select your CSV file(s)
  - Output Folder: Browse button to select where reports are saved
  - Interval (minutes): How often to run analysis (default: 60 minutes)
  - "Run Now" button: Execute analysis immediately

**First-time setup:**
1. Click "Browse" next to "CSV Files" and select your property CSV file
2. Click "Browse" next to "Output Folder" and choose where to save reports
3. Set interval (e.g., 60 minutes) and click "Apply"
4. Click "Run Now" to test the analysis

### Option 2: Run Once (Command Line)

Run a single analysis without opening the settings window:

```cmd
python -m desktop.app --run-once
```

This uses the existing configuration from `%APPDATA%\RealFlip\config.json`.

### Option 3: Show Config Path

See where the configuration file is stored:

```cmd
python -m desktop.app --show-config-path
```

## Configuration File

The app stores its configuration in:
```
%APPDATA%\RealFlip\config.json
```

You can manually edit this file if needed. Default structure:

```json
{
  "csv_paths": [],
  "output_dir": "C:\\Users\\OEM\\Documents\\RealFlipReports",
  "schedule": {
    "mode": "interval",
    "minutes": 60
  },
  "email": {
    "enabled": false,
    "smtp_host": "smtp.gmail.com",
    "smtp_port": 587,
    "username": "",
    "password": "",
    "recipients": []
  },
  "run_on_startup": false
}
```

## CSV File Format

Your CSV file should have these columns (auto-detected):

**Required:**
- `Address` or `Property Address` - Full property address

**Optional:**
- `TradeMe URL` or `Property Link` - Link to TradeMe listing
- `Bedrooms` - Number of bedrooms
- `Bathrooms` - Number of bathrooms
- `Area` - Floor area in square meters
- `Price` - Asking price

**Example CSV:**
```csv
Address,TradeMe URL,Bedrooms,Price
"123 Main St, Auckland",https://www.trademe.co.nz/property/...,3,750000
"456 Queen St, Wellington",https://www.trademe.co.nz/property/...,2,650000
```

## Output Files

After running analysis, you'll find in your output directory:

1. **JSON Results**: `Results_YYYYMMDD_HHMMSS.json`
   - Raw analysis data in JSON format
   - Contains all property details and scores

2. **PDF Report**: `Analysis_YYYYMMDD_HHMMSS.pdf`
   - Formatted report with all properties
   - If PDF generation fails, you'll get an HTML file instead

## Troubleshooting

### Issue: "ModuleNotFoundError: No module named 'desktop'"

**Solution**: Make sure you're in the project root directory and the virtual environment is activated.

```cmd
cd C:\Users\OEM\realflip2
venv_desktop\Scripts\activate
python -m desktop.app
```

### Issue: "ModuleNotFoundError: No module named 'app'"

**Solution**: The desktop app depends on the main app modules. Make sure you've installed all dependencies:

```cmd
pip install -r requirements.txt
```

### Issue: "Tkinter not found"

**Solution**: Tkinter should be included with Python. If missing:
- Reinstall Python and make sure to check "tcl/tk" components
- Or install: `pip install tk`

### Issue: "WeasyPrint installation fails"

**Solution**: This is optional. The app will work without it, just generating HTML instead of PDF. To install WeasyPrint on Windows:

1. Install GTK3 runtime: https://github.com/tschoonj/GTK-for-Windows-Runtime-Environment-Installer
2. Then: `pip install weasyprint`

Or skip it entirely - HTML reports work fine.

### Issue: "ChromeDriver not found"

**Solution**: The app uses `webdriver-manager` which should auto-download ChromeDriver. If it fails:
- Make sure Chrome browser is installed
- Or manually download ChromeDriver from: https://chromedriver.chromium.org/

### Issue: "No CSV paths configured"

**Solution**: 
1. Run the app with GUI: `python -m desktop.app`
2. Click "Browse" next to CSV Files and select your CSV
3. Or manually edit `%APPDATA%\RealFlip\config.json` and add CSV paths

### Issue: Analysis takes too long

**Solution**: This is normal! The app scrapes multiple websites for each property:
- First property: 2-5 minutes
- Subsequent properties: Faster (uses cache when possible)
- 10 properties: 10-30 minutes total

Be patient - the app is being polite with rate limiting.

## Building Standalone EXE (Optional)

If you want to create a standalone Windows executable:

```cmd
python desktop/build_exe.py
```

This will create `dist\RealFlipBatchAnalyzer_v2.exe` that you can run without Python installed.

**Note**: Building the EXE requires PyInstaller:
```cmd
pip install pyinstaller
```

## Email Configuration (Optional)

To enable email reports:

1. Edit `%APPDATA%\RealFlip\config.json`
2. Set `email.enabled` to `true`
3. Configure SMTP settings:
   - For Gmail: Use an "App Password" (not your regular password)
   - Enable 2-factor authentication first
   - Generate app password: https://myaccount.google.com/apppasswords

Example email config:
```json
"email": {
  "enabled": true,
  "smtp_host": "smtp.gmail.com",
  "smtp_port": 587,
  "username": "your.email@gmail.com",
  "password": "your-app-password",
  "recipients": ["recipient@example.com"]
}
```

## Quick Start Checklist

- [ ] Python 3.8+ installed
- [ ] Virtual environment created and activated
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] Desktop dependencies installed (`pip install apscheduler jinja2`)
- [ ] CSV file prepared with property data
- [ ] Run `python -m desktop.app` to open settings
- [ ] Configure CSV path and output directory
- [ ] Click "Run Now" to test

## Next Steps

Once the app is running:

1. **Test with a small CSV** (1-2 properties) first
2. **Check output directory** for results
3. **Review the JSON and PDF/HTML reports**
4. **Set up scheduling** if you want automatic runs
5. **Configure email** if you want reports sent automatically

## Getting Help

If you encounter issues:

1. Check the console output for error messages
2. Verify all dependencies are installed
3. Ensure CSV file format is correct
4. Check that output directory is writable
5. Review logs in `%LOCALAPPDATA%\RealFlip\logs\` (if logging is enabled)

## Command Reference

```cmd
# Activate virtual environment
venv_desktop\Scripts\activate

# Run with GUI
python -m desktop.app

# Run once (no GUI)
python -m desktop.app --run-once

# Show config path
python -m desktop.app --show-config-path

# Build EXE
python desktop/build_exe.py
```

