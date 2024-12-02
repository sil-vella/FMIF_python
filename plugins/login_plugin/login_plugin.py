from flask import request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from plugins.base_plugin.plugin_base import pluginBase
from services.api.base_api_service import BaseApiService
from datetime import datetime, timedelta

# Initialize Limiter globally (to be used across the app)
limiter = Limiter(
    key_func=get_remote_address,  # Use client IP for rate-limiting
    default_limits=["200 per day", "50 per hour"]  # Default limits
)

# Constants for failed login handling
MAX_FAILED_ATTEMPTS = 5
BLOCK_DURATION_MINUTES = 15

class Loginplugin(pluginBase):
    """
    Login plugin for handling user authentication and registration.
    Inherits from pluginBase.
    """
    def initialize(self):
        """Initialize the plugin, called when loaded."""
        print("Login plugin initialized")
        self.api_service = BaseApiService()

    def get_routes(self):
        """Define routes for the login plugin."""
        return [
            ('/register', self.register, ['POST']),
            ('/login', self.login, ['POST']),
            ('/update-points', self.update_points, ['POST']),  # Add this route

        ]

    @limiter.limit("5 per minute")  # Apply rate-limiting to the register route
    def register(self):
        """Handle user registration."""
        try:
            data = request.json
            username = data.get('username')
            password = data.get('password')

            if not username or not password:
                return jsonify({"message": "Username and password are required"}), 400

            query = "SELECT id FROM users WHERE username = %s"
            existing_user = self.api_service.fetch_from_db(query, (username,))
            if existing_user:
                return jsonify({"message": "Username already taken"}), 400

            hashed_password = generate_password_hash(password)

            cursor = self.api_service.db_connection.cursor()
            cursor.execute("INSERT INTO users (username, password_hash) VALUES (%s, %s)", (username, hashed_password))
            self.api_service.db_connection.commit()
            cursor.close()

            return jsonify({"message": "User registered successfully"}), 201
        except Exception as e:
            return jsonify({"message": f"Error registering user: {str(e)}"}), 500

    @limiter.limit("5 per minute")  # Apply rate-limiting to the login route
    def login(self):
        """Handle user login and return JWT if successful."""
        try:
            ip_address = get_remote_address()
            data = request.json
            username = data.get('username')
            password = data.get('password')

            if not username or not password:
                return jsonify({"message": "Username and password are required"}), 400

            # Check if the IP is blocked
            query = """
                SELECT is_blocked, attempt_time 
                FROM failed_login_attempts 
                WHERE ip_address = %s AND is_blocked = TRUE
                ORDER BY attempt_time DESC LIMIT 1
            """
            result = self.api_service.fetch_from_db(query, (ip_address,))
            if result and result[0][0]:  # If is_blocked is True
                blocked_time = result[0][1]
                if (datetime.now() - blocked_time).total_seconds() < BLOCK_DURATION_MINUTES * 60:
                    return jsonify({"message": "Your IP is temporarily blocked. Try again later."}), 403

            # Fetch user credentials, level, and points
            query = "SELECT id, password_hash, level, points FROM users WHERE username = %s"
            user_data = self.api_service.fetch_from_db(query, (username,))
            if not user_data:
                self.log_failed_attempt(ip_address, username)
                return jsonify({'message': 'Invalid username or password'}), 401

            user_id, stored_password_hash, level, points = user_data[0]

            if not check_password_hash(stored_password_hash, password):
                self.log_failed_attempt(ip_address, username)
                return jsonify({'message': 'Invalid username or password'}), 401

            # Successful login, reset attempts
            self.reset_failed_attempts(ip_address)

            # Generate JWT token
            token = create_access_token(identity=str(user_id))

            # Return the token along with level and points
            return jsonify({
                'token': token,
                'level': level,
                'points': points
            }), 200
        except Exception as e:
            self.api_service.db_connection.rollback()
            return jsonify({"message": f"Error during login: {str(e)}"}), 500

    def log_failed_attempt(self, ip_address, username):
        """Log a failed login attempt and block IP if necessary."""
        try:
            query = "INSERT INTO failed_login_attempts (ip_address, username_attempted) VALUES (%s, %s)"
            self.api_service.execute_query(query, (ip_address, username))

            # Count recent failed attempts
            query = """
                SELECT COUNT(*) 
                FROM failed_login_attempts 
                WHERE ip_address = %s AND attempt_time > NOW() - INTERVAL '1 hour'
            """
            attempts = self.api_service.fetch_from_db(query, (ip_address,))[0][0]

            if attempts >= MAX_FAILED_ATTEMPTS:
                query = "UPDATE failed_login_attempts SET is_blocked = TRUE WHERE ip_address = %s"
                self.api_service.execute_query(query, (ip_address,))
        except Exception as e:
            print(f"Error logging failed attempt: {e}")

    def reset_failed_attempts(self, ip_address):
        """Reset failed login attempts for the IP."""
        try:
            query = "DELETE FROM failed_login_attempts WHERE ip_address = %s"
            self.api_service.execute_query(query, (ip_address,))
        except Exception as e:
            print(f"Error resetting failed attempts: {e}")

    def update_points(self):
        """Handle updating user points."""
        try:
            data = request.json
            username = data.get('username')
            points = data.get('points')

            if not username or points is None:
                return jsonify({"message": "Username and points are required"}), 400

            # Update points in the database
            query = "UPDATE users SET points = %s WHERE username = %s"
            self.api_service.execute_query(query, (points, username))

            # Fetch updated points to confirm
            query = "SELECT points FROM users WHERE username = %s"
            updated_points = self.api_service.fetch_from_db(query, (username,))
            if not updated_points:
                return jsonify({"message": "User not found"}), 404

            return jsonify({
                "success": True,
                "updated_points": updated_points[0][0]
            }), 200
        except Exception as e:
            print(f"Error updating points: {e}")
            return jsonify({"message": f"Error updating points: {str(e)}"}), 500
