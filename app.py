from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from plugins.base_plugin.plugin_factory import pluginFactory
from plugins.base_plugin.plugin_manager import pluginManager
import os

app = Flask(__name__)
CORS(app)  # Enable CORS

# Configure your Flask app for JWT (provide a secret key)
app.config['JWT_SECRET_KEY'] = os.getenv("JWT_SECRET_KEY")  # Remove the comma

# Initialize JWTManager
jwt = JWTManager(app)

# Initialize the plugin factory
plugin_factory = pluginFactory()

# Initialize the plugin manager
plugin_manager = pluginManager()

# Load plugins using the factory and add them to the manager
plugins = plugin_factory.load_plugins()  # Make sure Loginplugin is included
plugin_manager.initialize_plugins(plugins)

# Register the plugin routes with the Flask app
plugin_manager.register_routes(app)

@app.route('/')
def home():
    return "FMIF Python Backend"

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
