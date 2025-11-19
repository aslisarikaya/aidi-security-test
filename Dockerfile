# Use official Python runtime
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install app dependencies
RUN pip install --no-cache-dir flask requests

# Copy all source code into the container
COPY src/ /app/

# Expose the app port (optional)
EXPOSE 5000

# Run the Flask application
CMD ["python", "server.py"]
