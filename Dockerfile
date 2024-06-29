# Use the official Python image from the Docker Hub
FROM python:3.9-slim

# Set environment variables
ENV PYTHONUNBUFFERED 1
ENV FLASK_APP app.py

# Set working directory
# Create a non-root user and group
RUN addgroup --system mygroup && adduser --system --group myuser
USER myuser
WORKDIR /home/myuser

# Install dependencies
COPY --chown=myuser:myuser requirements.txt requirements.txt
# Upgrade pip and install the Python dependencies
RUN python -m pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

ENV PATH="/home/myuser/.local/bin:${PATH}"

COPY --chown=myuser:myuser . .

# Expose the port on which the app will run
EXPOSE 5000

# Command to run the Flask application
CMD ["flask", "run", "--host=0.0.0.0"]
