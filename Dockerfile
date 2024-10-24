FROM python:3.11-slim

WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt requirements.txt

# Check if the requirements.txt file exists and print a message
RUN if [ -f requirements.txt ]; then echo "requirements.txt found, installing dependencies..."; else echo "requirements.txt not found, skipping dependency installation"; fi

# Install the Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Expose port 5000 for the Flask app
EXPOSE 5000

# Run the Flask application
CMD ["flask", "run", "--host=0.0.0.0", "--reload"]

