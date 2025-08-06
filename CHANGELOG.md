# Changelog

All notable changes to Aircraft Go-Around Tracker will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2025-01-06

### Added

- Initial release of Aircraft Go-Around Tracker
- Real-time go-around (aborted landing) detection system
- Multi-factor detection algorithm using altitude, climb rate, and flight path
- Web interface with live map visualization
- Color-coded aircraft indicators (red: active, orange: potential, blue: normal)
- Historical go-around viewer with filtering capabilities
- Severity classification system (HIGH/MEDIUM/LOW)
- CSV logging of all detected go-arounds
- Direct TAR1090 integration with replay links
- Docker support with multi-architecture builds
- Configurable detection parameters
- Statistics dashboard with daily tracking
- Comprehensive health monitoring
- API endpoints for data access

### Features

- Go-Around Detection
  - Low altitude threshold detection (< 2000 ft default)
  - Rapid climb rate identification (> 1000 ft/min)
  - Altitude recovery tracking (500 ft gain)
  - Descent-to-climb transition detection
  - Confidence scoring (0.0-1.0)

- Web Interface
  - Live go-around tracking map
  - Real-time statistics display
  - History page with advanced filters
  - TAR1090 replay integration
  - Auto-refresh every 5 seconds

- Data Analysis
  - Severity classification based on altitude and climb rate
  - Duration tracking for each event
  - Maximum climb rate recording
  - Geographic position logging

### Technical

- Python 3.8+ support
- Flask web framework
- TAR1090 API integration
- Docker containerization
- S6-overlay process management
- Multi-architecture support (amd64, arm64, arm/v7)
- Health check API
- Reverse proxy support

### Configuration

- Environment variable based configuration
- Adjustable detection thresholds
- Configurable update intervals
- Flexible TAR1090 URL support

## [Unreleased]

### Planned Features

- Email/webhook notifications for go-arounds
- Airport proximity detection
- Weather correlation analysis
- Enhanced statistics and reporting
- Multiple TAR1090 source support
- Database storage option
- Historical trend analysis
- Machine learning improvements

---

For detailed release notes, see [GitHub Releases](https://github.com/challgren/aircraft-goaround/releases)
