from flask import Flask
from flask_cors import CORS
from config import Config
from models import db
from routes import analyze_bp, upload_bp
import os

def create_app():
    """Create and configure the Flask application"""
    print("Creating Flask application...")
    app = Flask(__name__)
    app.config.from_object(Config)
    print("Flask app created and configured")
    
    # Enable CORS for React frontend and production
    CORS(app, resources={
        r"/api/*": {
            "origins": ["http://localhost:3000", "http://localhost:5173", "*"],
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type"]
        }
    })
    
    # Initialize database
    db.init_app(app)
    
    # Register blueprints
    app.register_blueprint(analyze_bp)
    app.register_blueprint(upload_bp)
    
    # Create tables if they don't exist (with error handling)
    with app.app_context():
        try:
            db.create_all()
            print("Database tables created successfully")
        except Exception as e:
            print(f"Database connection failed: {e}")
            print("App will continue without database initialization")
    
    @app.route('/')
    def index():
        return {
            'message': 'NZ Property Flip Calculator API',
            'version': '1.0.0',
            'endpoints': {
                'analyze': '/api/analyze',
                'upload': '/api/upload',
            }
        }
    
    @app.route('/health')
    def health():
        return {'status': 'healthy'}
    
    return app

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app = create_app()
    app.run(debug=False, host='0.0.0.0', port=port)