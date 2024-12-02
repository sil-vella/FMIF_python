#
#
#
# Populate the database with this script from inside the container.
# First copy the celeb_data folder if necessary. then exec in the flask container with 
# docker exec -it fmif_flask /bin/bash
# cd into the populate_db file dir and run script
#
#
#

import json
import psycopg2

# File path to the JSON data
json_file_path = 'categoriesed_celeb_names_for_db_populate.json'

# Database configuration for accessing the PostgreSQL container
db_config = {
    "dbname": "fmif_postgres_db",
    "user": "fmif_postgress_user",
    "password": "obqnvW8O1vZbRtsX",
    "host": "fmif_db",  # enter  db container name here
    "port": "5432"
}

# Load JSON data from a file
def load_json_data(file_path):
    with open(file_path, 'r') as f:
        return json.load(f)

# Check or insert a category in the 'categories' table
def check_or_insert_category(cursor, category_name):
    try:
        cursor.execute("SELECT id FROM categories WHERE category_name = %s", (category_name,))
        result = cursor.fetchone()
        if result:
            return result[0]  # Return category ID
        else:
            cursor.execute("INSERT INTO categories (category_name) VALUES (%s) RETURNING id", (category_name,))
            return cursor.fetchone()[0]
    except Exception as e:
        print(f"Error with category '{category_name}': {e}")
        raise

# Check or insert a celebrity in the 'celebs' table
def check_or_insert_celeb(cursor, celeb_name, origin, category_id):
    try:
        cursor.execute("SELECT id FROM celebs WHERE name = %s", (celeb_name,))
        result = cursor.fetchone()
        if result:
            celeb_id = result[0]
        else:
            cursor.execute("INSERT INTO celebs (name, origin) VALUES (%s, %s) RETURNING id", (celeb_name, origin))
            celeb_id = cursor.fetchone()[0]

        # Ensure the celeb is linked to the category in 'celebs_categories'
        cursor.execute("INSERT INTO celebs_categories (celeb_id, category_id) VALUES (%s, %s) ON CONFLICT DO NOTHING", (celeb_id, category_id))
        return celeb_id
    except Exception as e:
        print(f"Error with celeb '{celeb_name}': {e}")
        raise

# Remove categories and their associated celebrities not in the JSON data
def remove_unused_categories_and_celebs(cursor, data):
    cursor.execute("SELECT id, category_name FROM categories")
    db_categories = cursor.fetchall()
    json_categories = set(data.keys())

    for db_category in db_categories:
        category_id, db_category_name = db_category
        if db_category_name not in json_categories:
            cursor.execute("DELETE FROM celebs_categories WHERE category_id = %s", (category_id,))
            cursor.execute("DELETE FROM categories WHERE id = %s", (category_id,))
            print(f"Deleted category '{db_category_name}' and associated celebrities")

# Remove celebrities from the database if they are not in the JSON file for a specific category
def remove_unused_celebs(cursor, category_id, json_celebs):
    cursor.execute("""
        SELECT celebs.name 
        FROM celebs 
        JOIN celebs_categories ON celebs.id = celebs_categories.celeb_id
        WHERE celebs_categories.category_id = %s
    """, (category_id,))
    db_celebs = {celeb[0] for celeb in cursor.fetchall()}

    json_celebs = {celeb if isinstance(celeb, str) else celeb['name'] for celeb in json_celebs}

    for db_celeb in db_celebs - json_celebs:
        cursor.execute("DELETE FROM celebs WHERE name = %s AND id IN (SELECT celeb_id FROM celebs_categories WHERE category_id = %s)", (db_celeb, category_id))
        print(f"Deleted celebrity '{db_celeb}' from category_id {category_id}")

# Process the data and insert it into the database
def process_data(data, conn):
    if not data:
        print("JSON data is empty. No updates to process.")
        return
    with conn.cursor() as cursor:
        remove_unused_categories_and_celebs(cursor, data)

        for category, celebs in data.items():
            category_id = check_or_insert_category(cursor, category)

            remove_unused_celebs(cursor, category_id, celebs)

            for celeb in celebs:
                if isinstance(celeb, str):
                    check_or_insert_celeb(cursor, celeb, None, category_id)
                elif isinstance(celeb, dict):
                    check_or_insert_celeb(cursor, celeb["name"], celeb.get("origin"), category_id)

        conn.commit()

# Main function to load data and insert it into the database
def main():
    data = load_json_data(json_file_path)

    try:
        conn = psycopg2.connect(**db_config)
        print("Connected to the database.")
        process_data(data, conn)
        print("Database updated successfully.")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    main()
