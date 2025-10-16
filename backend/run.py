#!/usr/bin/env python3
"""
Simple runner script for the Flask application.
Run with: python run.py
"""

import os
from app import create_app

if __name__ == '__main__':
    app = create_app()
    
    # Get port from environment variable (Railway provides this)
    port = int(os.environ.get('PORT', 5000))
    
    print("\n" + "="*60)
    print("🏠 NZ Property Flip Calculator Backend")
    print("="*60)
    print(f"Server starting on: http://0.0.0.0:{port}")
    print(f"API endpoints available at: http://0.0.0.0:{port}/api/")
    print("Press CTRL+C to stop the server")
    print("="*60 + "\n")
    
    app.run(debug=False, host='0.0.0.0', port=port)

