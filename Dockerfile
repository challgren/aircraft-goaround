FROM ghcr.io/sdr-enthusiasts/docker-baseimage:base

# Install Python and dependencies
RUN set -x && \
    apt-get update && \
    apt-get install -y --no-install-recommends \
        python3 \
        python3-pip \
        python3-venv && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Create app directory and data directory
WORKDIR /app

# Copy requirements and install Python packages
COPY requirements.txt .
RUN mkdir -p /app/data && \
    python3 -m pip install --no-cache-dir --break-system-packages -r requirements.txt

# Copy application
COPY go_around_tracker.py .

# Copy rootfs
COPY rootfs/ /

# Environment variables
ENV TAR1090_URL=http://tar1090:8080 \
    WEB_INTERFACE=true \
    WEB_PORT=8889 \
    UPDATE_INTERVAL=5

# Expose web port
EXPOSE 8889

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python3 /scripts/healthcheck.py