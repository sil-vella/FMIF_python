from flask import request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token
from modules.base_module.module_base import ModuleBase
from services.api.base_api_service import BaseApiService

class LoginModule(ModuleBase):
    """
    Login module for handling user authentication and registration.
    Inherits from ModuleBase.
    """
    def initialize(self):
        """Initialize the module, called when loaded."""
        print("Login module initialized")
        # Create an instance of BaseApiService to manage DB connection
        self.api_service = BaseApiService()

    def get_routes(self):
        """Define routes for the login module."""
        return [
            ('/register', self.register, ['POST']),
            ('/login', self.login, ['POST']),
        ]

    def register(self):
        """Handle user registration."""
        try:
            data = request.json
            username = data.get('username')
            password = data.get('password')

            if not username or not password:
                return jsonify({"message": "Username and password are required"}), 400

            # Use fetch_from_db to check if the username already exists
            query = "SELECT id FROM users WHERE username = %s"
            existing_user = self.api_service.fetch_from_db(query, (username,))

            if existing_user:
                return jsonify({"message": "Username already taken"}), 400

            # Hash the password
            hashed_password = generate_password_hash(password)

            # Insert user into the database
            cursor = self.api_service.db_connection.cursor()
            cursor.execute("INSERT INTO users (username, hashed_password) VALUES (%s, %s)", (username, hashed_password))

            self.api_service.db_connection.commit()
            cursor.close()

            return jsonify({"message": "User registered successfully"}), 201

        except Exception as e:
            return jsonify({"message": f"Error registering user: {str(e)}"}), 500


    def login(self):
        """Handle user login and return JWT if successful."""
        try:
            data = request.json
            username = data.get('username')
            password = data.get('password')

            # Log the input data
            print(f"Received login request. Username: {username}, Password: {password}")

            if not username or not password:
                print("Missing username or password.")
                return jsonify({"message": "Username and password are required"}), 400

            # Fetch the user's password hash
            query = "SELECT id, hashed_password FROM users WHERE username = %s"
            print(f"Executing query: {query} with username: {username}")
            user_data = self.api_service.fetch_from_db(query, (username,))

            # Log if the user was found
            if not user_data:
                print(f"User not found for username: {username}")
                return jsonify({'message': 'Invalid username or password'}), 401

            user_id, stored_password_hash = user_data[0][0], user_data[0][1]

            # Log the fetched user ID and password hash
            print(f"Fetched user_id: {user_id}, password_hash: {stored_password_hash}")

            # Verify the password
            password_valid = check_password_hash(stored_password_hash, password)
            print(f"Password valid: {password_valid}")

            if password_valid:
                # Convert user_id to string explicitly
                user_id_str = str(user_id)
                print(f"user_id value before token creation: {user_id_str} (type: {type(user_id_str)})")

                # Create JWT token using the user_id as identity
                token = create_access_token(identity=user_id_str)
                print(f"Token created successfully: {token}")

                # Return the token in the response
                return jsonify({'token': token}), 200
            else:
                print("Password verification failed.")
                return jsonify({'message': 'Invalid username or password'}), 401

        except Exception as e:
            print(f"Exception occurred: {str(e)}")
            self.api_service.db_connection.rollback()  # Rollback the transaction on error
            return jsonify({"message": f"Error during login: {str(e)}"}), 500
