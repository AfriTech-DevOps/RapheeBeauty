# Stage 1: Build the application
FROM python:3.9

WORKDIR /app

# Copy only requirements to cache them in Docker layer
COPY requirements.txt .

# Install dependencies
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY . .

# Expose the port Gunicorn will listen on
EXPOSE 8000

# Define environment variables
ENV PORT=8000

# Use Gunicorn with explicit path to the executable to serve the application
CMD ["/usr/local/bin/gunicorn", "--bind", "0.0.0.0", "-w", "4", "app:app"]
