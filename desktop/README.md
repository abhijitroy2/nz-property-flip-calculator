# RealFlip Desktop Batch Analyzer

A Windows desktop application that runs property analysis in batch mode, generating PDF reports and optionally sending them via email.

## Features

- **Batch Processing**: Analyze multiple properties from CSV files
- **PDF Reports**: Generate consolidated PDF reports with property details and financial analysis
- **Email Delivery**: Optional email sending with PDF attachments
- **Scheduling**: Configurable schedule for automatic runs
- **Settings UI**: Simple Tkinter interface for configuration
- **Headless Operation**: Runs without GUI for automation

## Installation

### Option 1: Run from Source (Development)

1. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   pip install pyinstaller weasyprint
   ```

2. Run the application:
   ```bash
   # Open settings window
   python -m desktop.app
   
   # Run once (batch mode)
   python -m desktop.app --run-once
   ```

### Option 2: Build Windows EXE

1. Build the executable:
   ```bash
   python desktop/build_exe.py
   ```

2. Find the built EXE in `dist/RealFlipBatchAnalyzer.exe`

3. Copy the EXE to any location and run it

## Configuration

The app stores configuration in `%APPDATA%/RealFlip/config.json`.

### Default Configuration

```json
{
  "csv_path": "C:/Data/properties.csv",
  "output_dir": "C:/Data/Reports",
  "run_interval_minutes": 60,
  "enable_email": false,
  "email_recipients": [],
  "smtp_server": "smtp.gmail.com",
  "smtp_port": 587,
  "smtp_username": "",
  "smtp_password": ""
}
```

### Configuration Options

- **csv_path**: Path to your CSV file with property data
- **output_dir**: Directory where PDF reports and JSON results are saved
- **run_interval_minutes**: How often to run analysis (in minutes)
- **enable_email**: Whether to send email reports
- **email_recipients**: List of email addresses to receive reports
- **smtp_server**: SMTP server (e.g., smtp.gmail.com)
- **smtp_port**: SMTP port (usually 587 for TLS)
- **smtp_username**: Your email username
- **smtp_password**: Your email password or app password

## CSV Format

The CSV should have the same format as used by the web application:

```csv
address,bedrooms,bathrooms,floor_area,land_area,asking_price,target_value
"123 Main St, Auckland",3,2,120,600,750000,800000
"456 Queen St, Wellington",2,1,80,400,650000,700000
```

## Usage

### Settings Window

1. Run the app to open the settings window
2. Configure CSV path, output directory, and email settings
3. Set schedule interval (minutes between runs)
4. Click "Start Scheduler" to begin automatic runs
5. Click "Run Now" for immediate analysis

### Command Line

```bash
# Show help
python -m desktop.app --help

# Run once without opening settings
python -m desktop.app --run-once

# Show config file location
python -m desktop.app --show-config-path
```

### Output Files

The app creates timestamped files in your output directory:

- `YYYYMMDD_HHMM_Analysis.pdf` - Consolidated PDF report
- `YYYYMMDD_HHMM_Results.json` - Raw analysis data

## Email Setup

### Gmail Setup

1. Enable 2-factor authentication on your Google account
2. Generate an "App Password" for the application
3. Use your Gmail address as username and the app password as password

### Other Email Providers

Configure SMTP settings for your email provider:
- **Outlook/Hotmail**: smtp-mail.outlook.com, port 587
- **Yahoo**: smtp.mail.yahoo.com, port 587
- **Custom SMTP**: Check with your email provider

## Troubleshooting

### Common Issues

1. **PDF Generation Fails**: 
   - Install WeasyPrint: `pip install weasyprint`
   - Or the app will fall back to HTML output

2. **Email Sending Fails**:
   - Check SMTP credentials
   - Ensure app passwords are used for Gmail
   - Check firewall/antivirus settings

3. **CSV Parsing Errors**:
   - Ensure CSV has proper headers
   - Check for special characters in data
   - Verify file encoding (UTF-8 recommended)

### Logs

Logs are stored in `%LOCALAPPDATA%/RealFlip/logs/` with rotation.

### Dependencies

The app reuses the existing web application's analysis pipeline:
- Property scoring and analysis
- Financial calculations
- Web scraping (when available)
- GST-aware profit calculations

## Security Notes

- Configuration files are stored in user directories (no admin required)
- Email passwords are stored in plain text (consider using app passwords)
- The app only reads CSV files and writes to configured output directories

## Support

For issues or questions, check the main project documentation or create an issue in the repository.
