import random
import os
from flask import Flask, json, jsonify, request, send_from_directory
from plugins.base_plugin.plugin_base import pluginBase
from services.api.base_api_service import BaseApiService

class Mainplugin(pluginBase):
    def initialize(self):
        print("Main plugin initialized.")
        self.api_service = BaseApiService()

        file_path = '/app/celebs_data/celeb_data.json'  # Use container path

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
            ('/celebs_data/images/<path:filename>', self.serve_image, ['GET']),
        ]


    def get_categories(self):
        try:
            categories = self.api_service.fetch_from_db("SELECT category_name FROM categories;")
            if not categories:
                print("No categories found.")
                return jsonify([]), 200
            
            print(f"Raw category data: {categories}")
            category_list = [category[0].replace('_', ' ').title() for category in categories]
            print("Fetched categories (formatted):", category_list)
            return jsonify(category_list), 200
        except Exception as e:
            print(f"Error fetching categories: {str(e)}")
            return jsonify({"error": str(e)}), 500

    def get_celeb_details(self):
        try:
            if not self.celeb_data:
                return jsonify({"error": "Celebrity data is not available."}), 500

            category = request.args.get('category')
            if not category:
                return jsonify({"error": "Category is required"}), 400

            # Normalize category by replacing spaces with underscores
            normalized_category = category.replace(" ", "_")

            celebs = self.api_service.fetch_from_db("""
                SELECT celebs.name 
                FROM celebs 
                JOIN celebs_categories ON celebs.id = celebs_categories.celeb_id
                JOIN categories ON celebs_categories.category_id = categories.id
                WHERE LOWER(categories.category_name) = LOWER(%s);
            """, (normalized_category,))

            celeb_list = [celeb[0].replace('_', ' ').title() for celeb in celebs]
            if not celeb_list:
                return jsonify({"name": None, "categories": [], "facts": [], "image": None}), 200

            selected_celeb = random.choice(celeb_list)
            formatted_celeb_name = selected_celeb.lower().replace(' ', '_')

            if formatted_celeb_name not in self.celeb_data:
                return jsonify({"name": selected_celeb, "categories": [], "facts": [], "image": None}), 200

            celeb_details = self.celeb_data[formatted_celeb_name]
            image_files = [img for img in os.listdir('/app/celebs_data/images') if img.startswith(formatted_celeb_name)]

            # Select a random image from the list of matching images
            image_url = f"{request.host_url}celebs_data/images/{random.choice(image_files)}" if image_files else None

            selected_facts = random.sample(celeb_details.get("facts", []), min(len(celeb_details.get("facts", [])), 3))
            remaining_celebs = [celeb for celeb in celeb_list if celeb != selected_celeb]
            other_celebs = random.sample(remaining_celebs, min(len(remaining_celebs), 2))

            response_data = {
                "name": selected_celeb,
                "categories": celeb_details.get("categories", []),
                "facts": selected_facts,
                "image": image_url,
                "other_celebs": other_celebs
            }

            print(f"Selected celeb: {selected_celeb}, Details: {response_data}")
            return jsonify(response_data), 200

        except Exception as e:
            print(f"Error fetching celebs: {str(e)}")
            return jsonify({"error": str(e)}), 500

    def serve_image(self, filename):
        print(f"Request for image: {filename}")
        return send_from_directory('/app/celebs_data/images', filename)