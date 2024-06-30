# Use the official Python image from the Docker Hub
FROM python:3.9-slim

# Set environment variables
ENV PYTHONUNBUFFERED 1
ENV FLASK_APP app.main

# Set working directory
WORKDIR /app

# Install dependencies
COPY requirements.txt /app/
# Upgrade pip and install the Python dependencies
RUN python -m pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy the Flask project into the container
COPY . /app/

# Expose the port on which the app will run
EXPOSE 5000

# Command to run the Flask application
CMD ["flask", "run", "--host=0.0.0.0"]
