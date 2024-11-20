# Use Python slim image instead of Alpine
FROM python:3.9-slim

# Install curl and other dependencies
RUN apt-get update && \
    apt-get install -y curl netcat-traditional && \
    rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first to leverage Docker cache
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Make sure scripts are executable
RUN chmod +x /app/app.py

# Expose port
EXPOSE 5000

# Command to run the application
CMD ["python3", "-u", "app.py"] 