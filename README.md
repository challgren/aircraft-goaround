# Aircraft Go-Around Tracker - Real-time Aborted Landing Detection

[![Docker Image Size](https://ghcr-badge.deta.dev/challgren/aircraft-goaround/size)](https://github.com/challgren/aircraft-goaround/pkgs/container/aircraft-goaround)
[![License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![GitHub Issues](https://img.shields.io/github/issues/challgren/aircraft-goaround)](https://github.com/challgren/aircraft-goaround/issues)

Real-time aircraft go-around detection system that monitors TAR1090 feeds to
identify and track aborted landing attempts, providing instant alerts and
comprehensive analysis of these critical safety maneuvers.

![Go-Around Tracker Screenshot](docs/images/screenshot.png)

## 🛬 What is a Go-Around?

A go-around (also called aborted landing, missed approach, or wave-off) occurs
when an aircraft on final approach or that has already touched down aborts the
landing and rapidly climbs to circle back for another attempt. Go-arounds occur
in approximately 1-3 per 1000 approaches and are a normal safety procedure.

## 🎯 Features

### Go-Around Detection

- **Real-time Monitoring**: Continuously analyzes aircraft altitude and
  vertical rate patterns
- **Multi-factor Detection**: Uses altitude minimums, climb rates, and flight
  path analysis
- **Confidence Scoring**: Assigns confidence levels (0-1.0) based on detection criteria
- **Severity Classification**: Categorizes events as HIGH, MEDIUM, or LOW severity

### Web Interface

- **Live Map View**: Real-time visualization of active go-arounds with flight paths
- **Color-coded Aircraft**: Red for active go-arounds, orange for potential,
  blue for normal
- **Historical Tracking**: Browse and filter all detected go-around events
- **Statistics Dashboard**: Daily detection counts and performance metrics
- **TAR1090 Integration**: Direct links to view events in TAR1090

### Data & Integration

- **CSV Logging**: Automatic logging of all go-around events for analysis
- **Real-time Statistics**: Track daily detections and event severity
- **Multi-source Support**: Works with any TAR1090-compatible data source
- **Docker Support**: Easy deployment with multi-architecture container support

## 🚀 Quick Start

### Using Docker (Recommended)

```bash
docker run -d \
  --name=aircraft-goaround \
  -p 8889:8889 \
  -e TAR1090_URL=http://your-tar1090:80 \
  -v ./data:/app/data \
  --restart unless-stopped \
  ghcr.io/challgren/aircraft-goaround:latest
```

### With Public TAR1090 URL

If your TAR1090 instance is accessible at a different URL for users (e.g.,
through a reverse proxy):

```bash
docker run -d \
  --name=aircraft-goaround \
  -p 8889:8889 \
  -e TAR1090_URL=http://tar1090:80 \
  -e PUBLIC_TAR1090_URL=https://radar.example.com/map \
  -v ./data:/app/data \
  --restart unless-stopped \
  ghcr.io/challgren/aircraft-goaround:latest
```

### Using Docker Compose

```yaml
version: '3.8'

services:
  aircraft-goaround:
    image: ghcr.io/challgren/aircraft-goaround:latest
    container_name: aircraft-goaround
    restart: unless-stopped
    ports:
      - 8889:8889
    environment:
      - TAR1090_URL=http://tar1090:80
      - LOW_ALTITUDE_THRESHOLD=2000
      - MIN_CLIMB_RATE=1000
      - RAPID_CLIMB_RATE=1500
    volumes:
      - ./data:/app/data
```

### Manual Installation

```bash
# Clone the repository
git clone https://github.com/challgren/aircraft-goaround.git
cd aircraft-goaround

# Install dependencies
pip install -r requirements.txt

# Run the application
python3 go_around_tracker.py --server http://your-tar1090:8080 --web
```

## 📋 Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `TAR1090_URL` | Internal URL of your TAR1090 instance | `http://tar1090:80` |
| `PUBLIC_TAR1090_URL` | Public TAR1090 URL (optional) | Same as `TAR1090_URL` |
| `WEB_PORT` | Port for web interface | `8889` |
| `WEB_INTERFACE` | Enable web interface | `true` |
| `UPDATE_INTERVAL` | Data refresh interval (seconds) | `5` |

### Detection Parameters

| Variable | Description | Default |
|----------|-------------|---------|
| `LOW_ALTITUDE_THRESHOLD` | Maximum altitude for detection (ft) | `2000` |
| `MIN_CLIMB_RATE` | Minimum climb rate threshold (ft/min) | `1000` |
| `RAPID_CLIMB_RATE` | Rapid climb indicator (ft/min) | `1500` |
| `ALTITUDE_RECOVERY` | Required altitude gain (ft) | `500` |
| `TIME_WINDOW` | Detection lookback window (seconds) | `120` |

### Command Line Arguments

```bash
python3 go_around_tracker.py [options]

Options:
  --server URL        TAR1090 server URL
  --interval SECONDS  Update interval (default: 5)
  --web              Enable web interface
  --web-port PORT    Web interface port (default: 8889)
  --test             Test connection and exit
```

## 🏥 Health Monitoring

### Docker Health Check

The container includes comprehensive health checks that monitor:

- Python process status
- Web server responsiveness
- API endpoint availability
- TAR1090 connection status
- CSV file writability

Health check configuration:

- **Start Period**: 40 seconds
- **Check Interval**: 30 seconds
- **Timeout**: 10 seconds per check
- **Retries**: 3 failures before marking unhealthy

### Health API Endpoint

Access health status at: `http://localhost:8889/api/health`

```json
{
  "status": "healthy",
  "running": true,
  "server_url": "http://tar1090:80",
  "total_aircraft": 142,
  "active_go_arounds": 2,
  "potential_go_arounds": 5,
  "detected_today": 8,
  "last_update": "2024-01-15T10:30:45"
}
```

## 🖥️ Web Interface

### Live View

Access at: `http://localhost:8889`

- Real-time go-around detection with visual indicators
- Color-coded aircraft (red: active, orange: potential, blue: normal)
- Interactive map controls and statistics dashboard
- Auto-refresh every 5 seconds

### History View

Access at: `http://localhost:8889/history`

- Browse all historical go-around events
- Filter by callsign, date range, altitude threshold
- Severity classification (HIGH/MEDIUM/LOW)
- Direct links to TAR1090 replay

### API Endpoints

- `/api/go_arounds`: Current go-around data (JSON)
- `/api/go_around_history`: Historical events (JSON)
- `/api/health`: Health check endpoint

### Reverse Proxy Support

The application works seamlessly behind reverse proxies including when mounted
at a subpath.

#### Nginx Configuration Example

For mounting at `/goaround/`:

```nginx
location /goaround/ {
    proxy_pass http://aircraft-goaround:8889/;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection $http_connection;
    proxy_set_header Host $http_host;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    proxy_set_header X-Forwarded-Prefix /goaround;
    proxy_redirect / /goaround/;
}
```

## 📊 Detection Algorithm

The system detects go-arounds by analyzing:

1. **Low Altitude**: Aircraft below 2000 ft (configurable threshold)
2. **Rapid Climb Rate**: Vertical rate exceeding 1000-1500 ft/min
3. **Altitude Recovery**: Significant altitude gain from recent minimum
4. **Descent-to-Climb Transition**: Rapid change from descending to climbing

### Severity Classification

- **HIGH**: Min altitude < 500 ft and climb rate > 2000 ft/min
- **MEDIUM**: Min altitude < 1000 ft and climb rate > 1500 ft/min  
- **LOW**: All other detected go-arounds

## 💾 Data Storage

Go-around events are logged to CSV with the following fields:

| Field | Description |
|-------|-------------|
| `timestamp` | Detection time (ISO format) |
| `hex_id` | Aircraft ICAO hex identifier |
| `callsign` | Flight callsign |
| `lat`, `lon` | Geographic coordinates |
| `min_altitude` | Lowest altitude during approach (ft) |
| `max_climb_rate` | Maximum climb rate (ft/min) |
| `duration` | Duration of maneuver (seconds) |
| `confidence` | Detection confidence (0.0-1.0) |
| `tar1090_url` | Link to TAR1090 replay |

## 📚 Common Go-Around Reasons

Based on aviation statistics, go-arounds occur for these reasons:

### Weather (Most Common)

- Strong winds or wind shear
- Poor visibility (fog, heavy rain)
- Thunderstorms or microbursts

### Runway Issues

- Runway occupied by another aircraft
- Animals or debris on runway
- Slow-to-clear traffic

### Unstabilized Approach

- Too high or too fast on approach
- Incorrect aircraft configuration
- ATC spacing requirements

### Technical Issues

- Landing gear problems
- System warnings or alerts
- Bird strikes

## 🛠️ Troubleshooting

### No Aircraft Showing

- Verify TAR1090 URL is correct and accessible
- Check that `/data/aircraft.json` endpoint returns data
- Ensure TAR1090 is receiving ADS-B data

```bash
# Test TAR1090 connection
curl http://your-tar1090:80/data/aircraft.json
```

### No Go-Arounds Detected

- Go-arounds are relatively rare events (1-3 per 1000 approaches)
- Monitor areas near busy airports for higher detection rates
- Verify aircraft have altitude and vertical rate data available

### Connection Issues

```bash
# Test with the application
python3 go_around_tracker.py --server http://your-tar1090:80 --test

# Check Docker logs
docker logs aircraft-goaround
```

### Docker Health Check Failed

```bash
# Check container health
docker inspect aircraft-goaround --format='{{.State.Health.Status}}'

# View health check logs
docker inspect aircraft-goaround --format='{{range .State.Health.Log}}{{.Output}}{{end}}'
```

## 📦 Building from Source

### Docker Build

```bash
# Build for current architecture
docker build -t aircraft-goaround:local .

# Multi-architecture build
docker buildx build --platform linux/amd64,linux/arm64,linux/arm/v7 \
  -t aircraft-goaround:local .
```

### Development Setup

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run in development mode
python3 go_around_tracker.py --server http://localhost:8080 --web
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE)
file for details.

## 🙏 Acknowledgments

- Based on the architecture of
  [Aircraft Patterns](https://github.com/challgren/aircraft-patterns) detector
- Uses [TAR1090](https://github.com/wiedehopf/tar1090) for ADS-B data
- Inspired by the aviation safety community
- Aircraft visualization concepts from tar1090 project

## 📞 Support

For issues, questions, or suggestions, please
[open an issue](https://github.com/challgren/aircraft-goaround/issues) on
GitHub.

---

Made with ❤️ for the aviation community
