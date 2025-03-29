from flask import Flask, jsonify
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import app from parent directory
from app import app as flask_app

@flask_app.route('/api/health', methods=['GET'])
def health_check():
    """API endpoint to check if the application is running"""
    return jsonify({
        'status': 'ok',
        'message': 'Smart Seating Arrangement API is running',
        'environment': 'production' if os.environ.get('VERCEL_REGION') else 'development',
        'version': '2.1.0',
        'prediction_type': 'rule-based',
        'config': {
            'max_upload_size_mb': int(os.environ.get('MAX_UPLOAD_SIZE_MB', 16)),
            'session_lifetime_hours': int(os.environ.get('SESSION_LIFETIME_HOURS', 1))
        }
    })

# This is needed for Vercel
app = flask_app 