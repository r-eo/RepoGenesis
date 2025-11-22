from flask import Flask
from flask_cors import CORS
from config import Config
from services.db_manager import init_db
from routes.auth_routes import auth_bp
from routes.sleep_routes import sleep_bp
from routes.social_routes import social_bp

app = Flask(__name__)
app.config.from_object(Config)
CORS(app, resources={r"/api/*": {"origins": "*"}}, supports_credentials=True)

# Initialize DB
with app.app_context():
    init_db()

# Register Blueprints
app.register_blueprint(auth_bp, url_prefix='/api/auth')
app.register_blueprint(sleep_bp, url_prefix='/api/sleep')
app.register_blueprint(social_bp, url_prefix='/api/social')

@app.route('/')
def index():
    return "Sleep-Quest Backend is Running! Use the React Client to interact."

@app.route('/admin/clear-all-data', methods=['POST'])
def clear_all_data():
    """Admin endpoint to clear all user data"""
    from services.db_manager import execute_query
    try:
        execute_query('DELETE FROM active_sessions')
        execute_query('DELETE FROM sleep_logs')
        execute_query('DELETE FROM sleep_events')
        execute_query('DELETE FROM user_reliability')
        execute_query('DELETE FROM friends')
        execute_query('DELETE FROM users')
        return {"message": "All user data cleared successfully"}, 200
    except Exception as e:
        return {"error": str(e)}, 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
