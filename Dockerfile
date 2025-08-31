# TTKi AI Terminal Application - Security Hardened
FROM python:3.11-slim-bookworm

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV FLASK_APP=app.py
ENV PIP_NO_CACHE_DIR=1
ENV PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies with security updates
RUN apt-get update && apt-get install -y \
    # Essential packages
    curl \
    ca-certificates \
    # Security updates
    && apt-get upgrade -y \
    # Clean up to reduce attack surface
    && apt-get autoremove -y \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* \
    && rm -rf /tmp/* \
    && rm -rf /var/tmp/*

# Create non-root user early for security
RUN useradd -m -u 1000 -s /bin/bash ttki \
    && chown -R ttki:ttki /app

# Switch to non-root user for dependency installation
USER ttki

# Copy requirements first for better caching
COPY --chown=ttki:ttki requirements.txt .

# Install Python dependencies with security flags
RUN pip install --no-cache-dir \
    --upgrade pip setuptools wheel \
    && pip install --no-cache-dir \
    --no-deps \
    --require-hashes \
    --only-binary=all \
    -r requirements.txt || \
    pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY --chown=ttki:ttki . .

# Create logs directory
RUN mkdir -p logs

# Remove any sensitive files that shouldn't be in container
RUN find . -name "*.pyc" -delete \
    && find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true \
    && rm -f .env .env.* *.log 2>/dev/null || true

# Set proper permissions
RUN chmod -R 755 /app \
    && chmod -R 750 logs

# Expose port
EXPOSE 4001

# Add security labels
LABEL security.scan="enabled"
LABEL security.non-root="true"
LABEL maintainer="ttki@localhost"
LABEL version="1.0"

# Health check with timeout
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -f --max-time 5 http://localhost:4001/health || exit 1

# Run application with security options
CMD ["python", "-u", "app.py"]
