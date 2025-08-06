# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with
code in this repository.

## Project Overview

Aircraft Go-Around Tracker is a Python-based detection system for monitoring
aircraft via TAR1090 feeds. It identifies go-around events (aborted landings)
in real-time by analyzing altitude, vertical rate, and flight path data, with
a Flask web interface for visualization.

## Key Architecture

### Core Components

1. **go_around_tracker.py** - Monolithic Python application (~1200 lines) containing:
   - `TAR1090Monitor` - Main monitoring class that polls TAR1090 for aircraft data
   - `GoAroundDetector` - Analyzes flight paths for go-around patterns
   - Flask web server with embedded HTML templates (MAP_HTML_TEMPLATE, HISTORY_HTML_TEMPLATE)
   - Go-around event logging to CSV files

2. **Docker Structure**:
   - Based on `ghcr.io/sdr-enthusiasts/docker-baseimage:base`
   - Uses s6-overlay v3 for process management
   - Service configuration in `/etc/s6-overlay/s6-rc.d/go-around-tracker/`
   - Health check via API endpoint

3. **Web Interface**:
   - Self-contained HTML/JavaScript in Python string templates
   - Dynamic base URL detection for reverse proxy support
   - Color-coded aircraft indicators
   - Real-time updates via polling `/api/go_arounds` endpoint

## Essential Commands

### Building and Testing

```bash
# Build Docker image locally
docker build -t aircraft-goaround:dev .

# Multi-architecture build
docker buildx build --platform linux/amd64,linux/arm64,linux/arm/v7 \
  -t aircraft-goaround:dev .

# Run locally with Docker
docker run -it --rm -p 8889:8889 -e TAR1090_URL=http://your-tar1090:80 aircraft-goaround:dev

# Run Python directly (for development)
python3 go_around_tracker.py --server http://your-tar1090:80 --web --web-port 8889
```

### Testing Connection

```bash
# Test TAR1090 connection
python3 go_around_tracker.py --server http://your-tar1090:80 --test
```

### CI/CD and Linting

The project uses GitHub Actions for automated checks:

- **hadolint** - Dockerfile linting
- **shellcheck** - Shell script validation  
- **markdownlint** - Markdown formatting
- **deploy** - Multi-arch build and push to GHCR on main branch changes

To run linters locally:

```bash
hadolint Dockerfile
markdownlint *.md
```

## Important Implementation Details

### S6-Overlay Service

The s6 service configuration for Docker container operation:

- Run script uses `#!/command/with-contenv bash`
- Service runs as root
- Located at `/etc/s6-overlay/s6-rc.d/go-around-tracker/run`

### Reverse Proxy Support

The application supports mounting at subpaths (e.g., `/goaround/`):

- JavaScript dynamically detects base URL from `window.location.pathname`
- All navigation uses relative links
- API calls use computed `baseUrl + '/api/...'`
- ProxyFix middleware handles X-Forwarded headers

### Go-Around Detection Parameters

Key thresholds that affect detection sensitivity:

- Low altitude: < 2000 ft (configurable)
- Minimum climb rate: 1000 ft/min
- Rapid climb rate: 1500 ft/min  
- Altitude recovery: 500 ft gain from minimum
- Time window: 120 seconds lookback

### API Endpoints

- `/` - Main map view with live go-around tracking
- `/history` - Historical go-around viewer
- `/api/go_arounds` - Current aircraft and go-around data (JSON)
- `/api/go_around_history` - Historical events from CSV (JSON)
- `/api/health` - Health check with detailed status

### CSV Data Files

Go-around detections are logged to:

- `/app/data/go_around_detections.csv`

Each entry includes timestamp, aircraft info, altitude data, climb rate,
duration, confidence, and TAR1090 URL.

## Common Issues and Solutions

1. **Docker s6 service fails**: Check shebang in run script is
   `#!/command/with-contenv bash`

2. **No aircraft showing**: Verify TAR1090_URL is accessible and returns data
   at `/data/aircraft.json`

3. **No go-arounds detected**: These are rare events (1-3 per 1000
   approaches) - monitor near busy airports

4. **Reverse proxy issues**: Ensure proxy sets proper headers and uses
   `proxy_redirect / /subpath/`

5. **Markdown linting failures**: Files must end with newline, code blocks
   need surrounding blank lines

## Testing TAR1090 Connection

The application expects TAR1090 API format:

```bash
curl http://your-tar1090/data/aircraft.json
```

Should return JSON with `aircraft` or `ac` array containing objects with:

- `hex`: ICAO identifier
- `lat`, `lon`: Position
- `alt_baro` or `alt_geom`: Altitude
- `baro_rate` or `vert_rate`: Vertical rate
- `flight`: Callsign

## Go-Around Detection Logic

The detector identifies go-arounds by:

1. Tracking aircraft altitude history (10-minute window)
2. Finding recent altitude minimums
3. Detecting rapid climb rates (> 1000 ft/min)
4. Measuring altitude recovery from minimum
5. Identifying descent-to-climb transitions
6. Calculating confidence score based on multiple factors

Confidence scoring weights:

- Low altitude (< 2000 ft): +0.3
- Rapid climb (> 1500 ft/min): +0.4
- Normal climb (> 1000 ft/min): +0.2
- Altitude recovery (> 500 ft): +0.3
- Descent-to-climb transition: +0.2

Go-around is confirmed when confidence >= 0.6
