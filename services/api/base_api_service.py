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
        if not self.db_connection:
            print("Database connection not found. Attempting to reconnect...")
            self.db_connection = self.connect_to_db()

        conn = self.db_connection
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute(query, params)
                results = cursor.fetchall()
                cursor.close()
                print(f"Fetched results: {results}")  # Debugging output
                return results
            except Exception as e:
                print(f"Error executing query: {e}")
                return None
        else:
            print("Database connection is not available")
            return None

    def execute_query(self, query, params=None):
        """Execute a database query that modifies data."""
        if not self.db_connection:
            print("Database connection not found. Attempting to reconnect...")
            self.db_connection = self.connect_to_db()

        conn = self.db_connection
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute(query, params)
                conn.commit()  # Commit the transaction for data modification
                cursor.close()
                print("Query executed successfully")  # Debugging output
            except Exception as e:
                print(f"Error executing query: {e}")
                conn.rollback()  # Rollback the transaction on error
        else:
            print("Database connection is not available")
