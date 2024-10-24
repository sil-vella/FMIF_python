import psycopg2
import os

class BaseApiService:
 
    def __init__(self):
        self.db_connection = self.connect_to_db()
 
    def connect_to_db(self):
        """Establish a connection to the database and return the connection object."""
        try:
            connection = psycopg2.connect(
                user=os.getenv("POSTGRES_USER"),
                password=os.getenv("POSTGRES_PASSWORD"),
                host=os.getenv("DB_HOST", "127.0.0.1"),
                port=os.getenv("DB_PORT", "5432"),
                database=os.getenv("POSTGRES_DB")
            )
            print("Database connection established")
            return connection
        except Exception as e:
            print(f"Error connecting to database: {e}")
            return None

    def fetch_from_db(self, query, params=None):
        """Helper method to execute a query and fetch results."""
        conn = self.db_connection
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute(query, params)  # Parameterized query
                results = cursor.fetchall()
                cursor.close()
                return results
            except Exception as e:
                print(f"Error executing query: {e}")
                return None
        else:
            return "Failed to connect to the database"
