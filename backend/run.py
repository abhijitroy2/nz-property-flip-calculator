#!/usr/bin/env python3
"""
Simple runner script for the Flask application.
Run with: python run.py
"""

from app import create_app

if __name__ == '__main__':
    app = create_app()
    print("\n" + "="*60)
    print("🏠 NZ Property Flip Calculator Backend")
    print("="*60)
    print("Server starting on: http://localhost:5000")
    print("API endpoints available at: http://localhost:5000/api/")
    print("Press CTRL+C to stop the server")
    print("="*60 + "\n")
    
    app.run(debug=True, host='0.0.0.0', port=5000)

