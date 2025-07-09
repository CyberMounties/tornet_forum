# Use Python 3.9 slim base image for smaller size
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Copy requirements first to leverage Docker cache
COPY requirements.txt .

# Install dependencies and system packages for fonts
RUN apt-get update && apt-get install -y --no-install-recommends \
    fonts-dejavu-core \
    && rm -rf /var/lib/apt/lists/* \
    && pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY app.py models.py populate_db.py sellers_simulator.py shoutbox_simulator.py entrypoint.sh ./
COPY templates/ ./templates/
COPY static/ ./static/

# Create directories for database and CAPTCHA images
RUN mkdir -p instance static/captchas

# Make entrypoint executable
RUN chmod +x entrypoint.sh

# Expose port for Flask app
EXPOSE 5000

# Use entrypoint script
ENTRYPOINT ["./entrypoint.sh"]