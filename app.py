from flask import Flask, render_template, redirect, url_for
from flask_cors import CORS
from flask_session import Session
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

def create_app():
    app = Flask(__name__, template_folder='templates')
    
    # Configure CORS
    CORS(app, origins=['http://localhost:3000', 'http://127.0.0.1:3000'], 
         methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
         allow_headers=['Content-Type', 'Authorization'])
    
    # App configuration
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-secret-key-here')
    app.config['WTF_CSRF_ENABLED'] = False  # Disable CSRF for API endpoints
    
    # Session configuration for temporary user data storage
    app.config['SESSION_TYPE'] = 'filesystem'
    app.config['SESSION_PERMANENT'] = False
    app.config['PERMANENT_SESSION_LIFETIME'] = 1800  # 30 minutes
    
    # Initialize session
    Session(app)
    
    # Register blueprints 
    from auth.routes import auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')

    from functionality.routes import func_bp
    app.register_blueprint(func_bp, url_prefix='/func')
    
    # Home route
    @app.route('/')
    def home():
        return render_template('index.html')
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)
    app.run(debug=True, host='0.0.0.0', port=5000)
    
