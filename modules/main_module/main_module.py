import random
import os
from flask import json, jsonify, request, url_for, send_from_directory
from modules.base_module.module_base import ModuleBase
from services.api.base_api_service import BaseApiService

class MainModule(ModuleBase):
    def initialize(self):
        print("Main Module initialized.")
        self.api_service = BaseApiService()

        base_dir = os.path.dirname(os.path.abspath(__file__))  
        file_path = os.path.join(base_dir, '../../celebs_data/celeb_data.json')

        # Load celeb_data.json
        try:
            with open(file_path) as f:
                self.celeb_data = json.load(f)
            print(f"celeb_data.json loaded successfully from {file_path}.")
        except Exception as e:
            print(f"Error loading celeb_data.json from {file_path}: {str(e)}")
            self.celeb_data = None

    def get_routes(self):
        return [
            ('/get-categories', self.get_categories),
            ('/get-celeb-details', self.get_celeb_details),
            ('/celebs_data/images/<filename>', self.serve_image),

        ]

    def get_categories(self):
        try:
            categories = self.api_service.fetch_from_db("SELECT category_name FROM celeb_categories;")
            category_list = [category[0].replace('_', ' ').title() for category in categories]
            print("Fetched categories (formatted):", category_list)
            return jsonify(category_list), 200
        except Exception as e:
            print(f"Error fetching categories: {str(e)}")
            return jsonify({"error": str(e)}), 500

    def serve_image(self, filename):
        # Serve the images from the celebs_data/images directory
        image_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../../celebs_data/images')
        return send_from_directory(image_dir, filename)

    def get_celeb_details(self):
        try:
            if not self.celeb_data:
                return jsonify({"error": "Celebrity data is not available."}), 500

            # Get the category passed as a query parameter
            category = request.args.get('category')
            if not category:
                return jsonify({"error": "Category is required"}), 400

            # Fetch celeb names linked to the passed category name from the database
            celebs = self.api_service.fetch_from_db("""
                SELECT celebs.name 
                FROM celebs 
                LEFT JOIN celeb_categories 
                ON celebs.category_id = celeb_categories.id
                WHERE LOWER(celeb_categories.category_name) = LOWER(%s);
            """, (category,))

            celeb_list = [celeb[0].replace('_', ' ').title() for celeb in celebs]
            if not celeb_list:
                return jsonify({"name": None, "categories": [], "facts": [], "image": None}), 200

            # Select a random celebrity from the list
            selected_celeb = random.choice(celeb_list)

            # Format the selected celebrity's name
            formatted_celeb_name = selected_celeb.lower().replace(' ', '_')

            if formatted_celeb_name not in self.celeb_data:
                return jsonify({"name": selected_celeb, "categories": [], "facts": [], "image": None}), 200

            celeb_details = self.celeb_data[formatted_celeb_name]

            # Get the image directory
            image_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../../celebs_data/images')

            # Find all images that start with the formatted celeb name
            image_files = [img for img in os.listdir(image_dir) if img.startswith(formatted_celeb_name)]

            # If an image is found, construct the full URL
            if image_files:
                selected_image = random.choice(image_files)
                image_url = f"{request.host_url}celebs_data/images/{selected_image}"
            else:
                image_url = None  # No image found

            # Return the selected celebrity's name, details, and image URL
            response_data = {
                "name": selected_celeb,
                "categories": celeb_details.get("categories", []),
                "facts": celeb_details.get("facts", []),
                "image": image_url
            }

            print(f"Selected celeb: {selected_celeb}, Details: {response_data}")
            return jsonify(response_data), 200

        except Exception as e:
            print(f"Error fetching celebs: {str(e)}")
            return jsonify({"error": str(e)}), 500