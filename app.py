from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from modules.base_module.module_factory import ModuleFactory
from modules.base_module.module_manager import ModuleManager
import os

app = Flask(__name__)
CORS(app)  # Enable CORS

# Configure your Flask app for JWT (provide a secret key)
app.config['JWT_SECRET_KEY'] = os.getenv("JWT_SECRET_KEY")  # Remove the comma

# Initialize JWTManager
jwt = JWTManager(app)

# Initialize the module factory
module_factory = ModuleFactory()

# Initialize the module manager
module_manager = ModuleManager()

# Load modules using the factory and add them to the manager
modules = module_factory.load_modules()  # Make sure LoginModule is included
module_manager.initialize_modules(modules)

# Register the module routes with the Flask app
module_manager.register_routes(app)

@app.route('/')
def home():
    return "FMIF Python Backend"

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
