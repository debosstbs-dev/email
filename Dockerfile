# Use Python 3.11 slim image as base
FROM python:3.11-slim

# Set working directory in container
WORKDIR /app

# Copy all application files first
COPY . .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Create necessary directories if they don't exist
RUN mkdir -p /app/static
RUN mkdir -p /app/uploads

# Set permissions
RUN chmod -R 755 /app

# Expose port
EXPOSE 8000

# Command to run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"] 
