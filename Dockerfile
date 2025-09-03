# Use a specific version for reproducibility
FROM python:3.10.13-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install system dependencies (Tesseract has been removed)
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        poppler-utils \
        curl \
    && apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Set the working directory
WORKDIR /app

# Create a non-root user and switch to it
RUN useradd --create-home appuser
USER appuser

# Install Python dependencies (leveraging build cache)
COPY --chown=appuser:appuser requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY --chown=appuser:appuser . .

# Expose the port the app runs on
EXPOSE 8000

# Add a health check for production reliability
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1

# Start the application
CMD ["bash", "start.sh"]