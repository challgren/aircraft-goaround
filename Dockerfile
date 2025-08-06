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

# Setup s6-overlay service
RUN mkdir -p /etc/s6-overlay/s6-rc.d/go-around-tracker \
             /etc/s6-overlay/s6-rc.d/user/contents.d \
             /etc/s6-overlay/s6-rc.d/go-around-tracker/dependencies.d && \
    echo '#!/command/with-contenv bash' > /etc/s6-overlay/s6-rc.d/go-around-tracker/run && \
    echo 'exec python3 /app/go_around_tracker.py --web' >> /etc/s6-overlay/s6-rc.d/go-around-tracker/run && \
    chmod +x /etc/s6-overlay/s6-rc.d/go-around-tracker/run && \
    echo 'longrun' > /etc/s6-overlay/s6-rc.d/go-around-tracker/type && \
    touch /etc/s6-overlay/s6-rc.d/user/contents.d/go-around-tracker && \
    touch /etc/s6-overlay/s6-rc.d/go-around-tracker/dependencies.d/base

# Environment variables
ENV TAR1090_URL=http://tar1090:8080 \
    WEB_INTERFACE=true \
    WEB_PORT=8889 \
    UPDATE_INTERVAL=5

# Expose web port
EXPOSE 8889

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python3 -c "import requests; r = requests.get('http://localhost:8889/api/health'); exit(0 if r.status_code == 200 else 1)"