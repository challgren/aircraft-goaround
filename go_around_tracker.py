#!/usr/bin/env python3
"""
TAR1090 Go-Around Detector
A Python application to monitor aircraft and detect go-around (aborted landing) events.
"""

# HTML template for the map viewer
MAP_HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Go-Around Tracker</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
    <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
    <script>
        // Determine base URL from current location
        const pathname = window.location.pathname;
        // Handle both root and subpath deployments
        const baseUrl = pathname.endsWith('/') ? pathname.slice(0, -1) : 
                       pathname.endsWith('/history') ? pathname.replace(/\/history$/, '') : 
                       pathname;
        
        // Aircraft icon shapes from tar1090
        const aircraftShapes = {
            'default': {
                svg: '<path d="M 12 2 L 12 8 L 20 14 L 20 16 L 12 13 L 12 18 L 15 20 L 15 21 L 12 20 L 9 21 L 9 20 L 12 18 L 12 13 L 4 16 L 4 14 L 12 8 L 12 2 Z"/>',
                width: 24,
                height: 24,
                viewBox: '0 0 24 24',
                scale: 1.0
            }
        };
        
        function getAircraftIcon(typeDesignator, category) {
            return aircraftShapes['default'];
        }
    </script>
    <style>
        body {
            margin: 0;
            padding: 0;
            font-family: Arial, sans-serif;
        }
        .header {
            background: white;
            padding: 10px 30px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
            display: flex;
            justify-content: space-between;
            align-items: center;
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            z-index: 1001;
        }
        .header h1 {
            margin: 0;
            color: #333;
            font-size: 20px;
        }
        .nav-links {
            display: flex;
            gap: 20px;
        }
        .nav-links a {
            text-decoration: none;
            color: #007bff;
            padding: 8px 16px;
            border-radius: 4px;
            transition: background 0.3s;
        }
        .nav-links a:hover {
            background: #f0f0f0;
        }
        .nav-links a.active {
            background: #007bff;
            color: white;
        }
        #map {
            height: 100vh;
            width: 100%;
            margin-top: 50px;
        }
        .stats {
            position: absolute;
            bottom: 20px;
            left: 20px;
            background: white;
            padding: 15px;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.2);
            z-index: 1000;
            min-width: 250px;
        }
        .stats h3 {
            margin: 0 0 10px 0;
            color: #333;
        }
        .stats-grid {
            display: grid;
            grid-template-columns: auto auto;
            gap: 5px 15px;
            font-size: 14px;
        }
        .stats-label {
            color: #666;
        }
        .stats-value {
            font-weight: bold;
            text-align: right;
        }
        .go-around-indicator {
            background: #ff4444;
            color: white;
            padding: 2px 6px;
            border-radius: 3px;
            font-size: 12px;
        }
        .potential-indicator {
            background: #ff8844;
            color: white;
            padding: 2px 6px;
            border-radius: 3px;
            font-size: 12px;
        }
        .legend {
            position: absolute;
            top: 70px;
            right: 20px;
            background: white;
            padding: 15px;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.2);
            z-index: 1000;
        }
        .legend h4 {
            margin: 0 0 10px 0;
            color: #333;
        }
        .legend-item {
            display: flex;
            align-items: center;
            margin: 5px 0;
            font-size: 14px;
        }
        .legend-color {
            width: 20px;
            height: 20px;
            margin-right: 10px;
            border-radius: 3px;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>🛬 Go-Around Tracker</h1>
        <div class="nav-links">
            <a href="./" class="active">Live Map</a>
            <a href="history">History</a>
        </div>
    </div>
    <div id="map"></div>
    <div class="stats">
        <h3>📊 Statistics</h3>
        <div class="stats-grid">
            <div class="stats-label">Total Aircraft:</div>
            <div class="stats-value" id="total-aircraft">0</div>
            <div class="stats-label">Active Go-Arounds:</div>
            <div class="stats-value" id="active-go-arounds">0</div>
            <div class="stats-label">Potential Go-Arounds:</div>
            <div class="stats-value" id="potential-go-arounds">0</div>
            <div class="stats-label">Detected Today:</div>
            <div class="stats-value" id="detected-today">0</div>
        </div>
    </div>
    <div class="legend">
        <h4>Legend</h4>
        <div class="legend-item">
            <div class="legend-color" style="background: #ff4444;"></div>
            <span>Active Go-Around</span>
        </div>
        <div class="legend-item">
            <div class="legend-color" style="background: #ff8844;"></div>
            <span>Potential Go-Around</span>
        </div>
        <div class="legend-item">
            <div class="legend-color" style="background: #0066ff;"></div>
            <span>Normal Flight</span>
        </div>
    </div>
    <script>
        // Initialize map
        const map = L.map('map').setView([39.8283, -98.5795], 4);
        
        // Add base layers
        const osmLayer = L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '© OpenStreetMap contributors'
        });
        
        const darkLayer = L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}.png', {
            attribution: '© CartoDB'
        });
        
        osmLayer.addTo(map);
        
        const baseLayers = {
            "OpenStreetMap": osmLayer,
            "Dark Mode": darkLayer
        };
        
        L.control.layers(baseLayers).addTo(map);
        
        // Store aircraft markers and paths
        const aircraftMarkers = {};
        const aircraftPaths = {};
        
        function createAircraftIcon(status = 'normal', heading = 0) {
            const iconDef = getAircraftIcon();
            
            let color;
            if (status === 'go_around') {
                color = '#ff4444';
            } else if (status === 'potential') {
                color = '#ff8844';
            } else {
                color = '#0066ff';
            }
            
            const svgIcon = L.divIcon({
                html: `<svg width="${iconDef.width}" height="${iconDef.height}" 
                           viewBox="${iconDef.viewBox}" 
                           style="transform: rotate(${heading}deg); fill: ${color};">
                           ${iconDef.svg}
                       </svg>`,
                iconSize: [iconDef.width, iconDef.height],
                iconAnchor: [iconDef.width/2, iconDef.height/2],
                className: 'aircraft-icon'
            });
            
            return svgIcon;
        }
        
        function updateMap() {
            fetch(baseUrl + '/api/go_arounds')
                .then(response => response.json())
                .then(data => {
                    // Update stats
                    document.getElementById('total-aircraft').textContent = data.total_aircraft || 0;
                    document.getElementById('active-go-arounds').textContent = data.active_go_arounds || 0;
                    document.getElementById('potential-go-arounds').textContent = data.potential_go_arounds || 0;
                    document.getElementById('detected-today').textContent = data.detected_today || 0;
                    
                    // Track active aircraft
                    const activeHexIds = new Set();
                    
                    // Update go-around aircraft
                    if (data.go_arounds) {
                        data.go_arounds.forEach(goAround => {
                            const hexId = goAround.hex_id;
                            activeHexIds.add(hexId);
                            
                            if (aircraftMarkers[hexId]) {
                                // Update existing marker
                                aircraftMarkers[hexId].setLatLng([goAround.current_lat, goAround.current_lon]);
                                aircraftMarkers[hexId].setIcon(createAircraftIcon('go_around', goAround.heading || 0));
                            } else {
                                // Create new marker
                                const marker = L.marker([goAround.current_lat, goAround.current_lon], {
                                    icon: createAircraftIcon('go_around', goAround.heading || 0)
                                }).addTo(map);
                                
                                marker.bindPopup(`
                                    <div style="min-width: 200px;">
                                        <h4 style="margin: 5px 0;">
                                            <span class="go-around-indicator">GO-AROUND</span> 
                                            ${goAround.callsign || goAround.hex_id}
                                        </h4>
                                        <div><strong>Min Altitude:</strong> ${goAround.min_altitude?.toLocaleString() || 'N/A'} ft</div>
                                        <div><strong>Current Altitude:</strong> ${goAround.current_alt?.toLocaleString() || 'N/A'} ft</div>
                                        <div><strong>Max Climb Rate:</strong> ${goAround.max_climb_rate?.toFixed(0) || 'N/A'} ft/min</div>
                                        <div><strong>Duration:</strong> ${goAround.duration || 0} seconds</div>
                                        ${goAround.tar1090_url ? `<div><a href="${goAround.tar1090_url}" target="_blank">View in TAR1090</a></div>` : ''}
                                    </div>
                                `);
                                
                                aircraftMarkers[hexId] = marker;
                            }
                            
                            // Update path
                            if (goAround.recent_path && goAround.recent_path.length > 1) {
                                if (aircraftPaths[hexId]) {
                                    aircraftPaths[hexId].setLatLngs(goAround.recent_path.map(p => [p.lat, p.lon]));
                                } else {
                                    aircraftPaths[hexId] = L.polyline(
                                        goAround.recent_path.map(p => [p.lat, p.lon]),
                                        {color: '#ff4444', weight: 2, opacity: 0.7}
                                    ).addTo(map);
                                }
                            }
                        });
                    }
                    
                    // Update potential go-around aircraft
                    if (data.potential_go_arounds_list) {
                        data.potential_go_arounds_list.forEach(aircraft => {
                            const hexId = aircraft.hex_id;
                            activeHexIds.add(hexId);
                            
                            if (aircraftMarkers[hexId]) {
                                aircraftMarkers[hexId].setLatLng([aircraft.current_lat, aircraft.current_lon]);
                                aircraftMarkers[hexId].setIcon(createAircraftIcon('potential', aircraft.heading || 0));
                            } else {
                                const marker = L.marker([aircraft.current_lat, aircraft.current_lon], {
                                    icon: createAircraftIcon('potential', aircraft.heading || 0)
                                }).addTo(map);
                                
                                marker.bindPopup(`
                                    <div style="min-width: 200px;">
                                        <h4 style="margin: 5px 0;">
                                            <span class="potential-indicator">POTENTIAL</span>
                                            ${aircraft.callsign || aircraft.hex_id}
                                        </h4>
                                        <div><strong>Altitude:</strong> ${aircraft.current_alt?.toLocaleString() || 'N/A'} ft</div>
                                        <div><strong>Vertical Rate:</strong> ${aircraft.vert_rate?.toFixed(0) || 'N/A'} ft/min</div>
                                    </div>
                                `);
                                
                                aircraftMarkers[hexId] = marker;
                            }
                        });
                    }
                    
                    // Remove markers for aircraft no longer active
                    Object.keys(aircraftMarkers).forEach(hexId => {
                        if (!activeHexIds.has(hexId)) {
                            map.removeLayer(aircraftMarkers[hexId]);
                            delete aircraftMarkers[hexId];
                            
                            if (aircraftPaths[hexId]) {
                                map.removeLayer(aircraftPaths[hexId]);
                                delete aircraftPaths[hexId];
                            }
                        }
                    });
                })
                .catch(error => console.error('Error fetching data:', error));
        }
        
        // Update map every 5 seconds
        updateMap();
        setInterval(updateMap, 5000);
    </script>
</body>
</html>
'''

HISTORY_HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Go-Around History</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body {
            margin: 0;
            padding: 0;
            font-family: Arial, sans-serif;
            background: #f5f5f5;
        }
        .header {
            background: white;
            padding: 10px 30px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .header h1 {
            margin: 0;
            color: #333;
            font-size: 20px;
        }
        .nav-links {
            display: flex;
            gap: 20px;
        }
        .nav-links a {
            text-decoration: none;
            color: #007bff;
            padding: 8px 16px;
            border-radius: 4px;
            transition: background 0.3s;
        }
        .nav-links a:hover {
            background: #f0f0f0;
        }
        .nav-links a.active {
            background: #007bff;
            color: white;
        }
        .container {
            max-width: 1400px;
            margin: 20px auto;
            padding: 0 20px;
        }
        .filters {
            background: white;
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 20px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }
        .filters h3 {
            margin-top: 0;
            color: #333;
        }
        .filter-row {
            display: flex;
            gap: 20px;
            flex-wrap: wrap;
            align-items: center;
        }
        .filter-group {
            display: flex;
            flex-direction: column;
            gap: 5px;
        }
        .filter-group label {
            font-size: 12px;
            color: #666;
            text-transform: uppercase;
        }
        .filter-group input, .filter-group select {
            padding: 8px;
            border: 1px solid #ddd;
            border-radius: 4px;
            font-size: 14px;
        }
        .filter-group button {
            padding: 8px 16px;
            background: #007bff;
            color: white;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            font-size: 14px;
        }
        .filter-group button:hover {
            background: #0056b3;
        }
        .events-table {
            background: white;
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }
        table {
            width: 100%;
            border-collapse: collapse;
        }
        th {
            background: #f8f9fa;
            padding: 12px;
            text-align: left;
            font-weight: 600;
            color: #333;
            border-bottom: 2px solid #dee2e6;
        }
        td {
            padding: 12px;
            border-bottom: 1px solid #dee2e6;
        }
        tr:hover {
            background: #f8f9fa;
        }
        .severity-high {
            color: #dc3545;
            font-weight: bold;
        }
        .severity-medium {
            color: #fd7e14;
            font-weight: bold;
        }
        .severity-low {
            color: #28a745;
        }
        .tar1090-link {
            color: #007bff;
            text-decoration: none;
        }
        .tar1090-link:hover {
            text-decoration: underline;
        }
        .no-data {
            text-align: center;
            padding: 40px;
            color: #666;
        }
        .stats-summary {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 20px;
        }
        .stat-card {
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }
        .stat-card h4 {
            margin: 0 0 10px 0;
            color: #666;
            font-size: 14px;
            text-transform: uppercase;
        }
        .stat-card .value {
            font-size: 28px;
            font-weight: bold;
            color: #333;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>🛬 Go-Around History</h1>
        <div class="nav-links">
            <a href="./">Live Map</a>
            <a href="history" class="active">History</a>
        </div>
    </div>
    
    <div class="container">
        <div class="stats-summary">
            <div class="stat-card">
                <h4>Total Go-Arounds</h4>
                <div class="value" id="total-events">0</div>
            </div>
            <div class="stat-card">
                <h4>Last 24 Hours</h4>
                <div class="value" id="last-24h">0</div>
            </div>
            <div class="stat-card">
                <h4>Last 7 Days</h4>
                <div class="value" id="last-7d">0</div>
            </div>
            <div class="stat-card">
                <h4>Average Min Altitude</h4>
                <div class="value" id="avg-altitude">0 ft</div>
            </div>
        </div>
        
        <div class="filters">
            <h3>🔍 Filters</h3>
            <div class="filter-row">
                <div class="filter-group">
                    <label>Callsign</label>
                    <input type="text" id="filter-callsign" placeholder="e.g., UAL123">
                </div>
                <div class="filter-group">
                    <label>Date From</label>
                    <input type="datetime-local" id="filter-date-from">
                </div>
                <div class="filter-group">
                    <label>Date To</label>
                    <input type="datetime-local" id="filter-date-to">
                </div>
                <div class="filter-group">
                    <label>Min Altitude Below (ft)</label>
                    <input type="number" id="filter-altitude" placeholder="e.g., 1000">
                </div>
                <div class="filter-group">
                    <label>&nbsp;</label>
                    <button onclick="applyFilters()">Apply Filters</button>
                </div>
                <div class="filter-group">
                    <label>&nbsp;</label>
                    <button onclick="resetFilters()" style="background: #6c757d;">Reset</button>
                </div>
            </div>
        </div>
        
        <div class="events-table">
            <table>
                <thead>
                    <tr>
                        <th>Timestamp</th>
                        <th>Callsign</th>
                        <th>Hex ID</th>
                        <th>Min Altitude</th>
                        <th>Max Climb Rate</th>
                        <th>Duration</th>
                        <th>Severity</th>
                        <th>Location</th>
                        <th>TAR1090</th>
                    </tr>
                </thead>
                <tbody id="events-tbody">
                    <tr>
                        <td colspan="9" class="no-data">Loading go-around events...</td>
                    </tr>
                </tbody>
            </table>
        </div>
    </div>
    
    <script>
        const pathname = window.location.pathname;
        // Handle both root and subpath deployments
        const baseUrl = pathname.endsWith('/history') ? pathname.replace(/\/history$/, '') : 
                       pathname.endsWith('/') ? pathname.slice(0, -1) : 
                       pathname;
        
        let allEvents = [];
        
        function formatDate(dateStr) {
            const date = new Date(dateStr);
            return date.toLocaleString();
        }
        
        function calculateSeverity(minAltitude, maxClimbRate) {
            if (minAltitude < 500 && maxClimbRate > 2000) return 'high';
            if (minAltitude < 1000 && maxClimbRate > 1500) return 'medium';
            return 'low';
        }
        
        function loadHistory() {
            fetch(baseUrl + '/api/go_around_history')
                .then(response => response.json())
                .then(data => {
                    allEvents = data.events || [];
                    updateStats();
                    renderTable(allEvents);
                })
                .catch(error => {
                    console.error('Error loading history:', error);
                    document.getElementById('events-tbody').innerHTML = 
                        '<tr><td colspan="9" class="no-data">Error loading history</td></tr>';
                });
        }
        
        function updateStats() {
            const now = new Date();
            const last24h = new Date(now - 24 * 60 * 60 * 1000);
            const last7d = new Date(now - 7 * 24 * 60 * 60 * 1000);
            
            const events24h = allEvents.filter(e => new Date(e.timestamp) > last24h);
            const events7d = allEvents.filter(e => new Date(e.timestamp) > last7d);
            
            document.getElementById('total-events').textContent = allEvents.length;
            document.getElementById('last-24h').textContent = events24h.length;
            document.getElementById('last-7d').textContent = events7d.length;
            
            if (allEvents.length > 0) {
                const avgAlt = allEvents.reduce((sum, e) => sum + (e.min_altitude || 0), 0) / allEvents.length;
                document.getElementById('avg-altitude').textContent = avgAlt.toFixed(0) + ' ft';
            }
        }
        
        function renderTable(events) {
            const tbody = document.getElementById('events-tbody');
            
            if (events.length === 0) {
                tbody.innerHTML = '<tr><td colspan="9" class="no-data">No go-around events found</td></tr>';
                return;
            }
            
            tbody.innerHTML = events.map(event => {
                const severity = calculateSeverity(event.min_altitude, event.max_climb_rate);
                const severityClass = 'severity-' + severity;
                
                return `
                    <tr>
                        <td>${formatDate(event.timestamp)}</td>
                        <td><strong>${event.callsign || 'Unknown'}</strong></td>
                        <td>${event.hex_id}</td>
                        <td>${event.min_altitude?.toLocaleString() || 'N/A'} ft</td>
                        <td>${event.max_climb_rate?.toFixed(0) || 'N/A'} ft/min</td>
                        <td>${event.duration || 0} sec</td>
                        <td><span class="${severityClass}">${severity.toUpperCase()}</span></td>
                        <td>${event.lat?.toFixed(4)}, ${event.lon?.toFixed(4)}</td>
                        <td>
                            ${event.tar1090_url ? 
                                `<a href="${event.tar1090_url}" target="_blank" class="tar1090-link">View ↗</a>` : 
                                'N/A'}
                        </td>
                    </tr>
                `;
            }).join('');
        }
        
        function applyFilters() {
            const callsign = document.getElementById('filter-callsign').value.toLowerCase();
            const dateFrom = document.getElementById('filter-date-from').value;
            const dateTo = document.getElementById('filter-date-to').value;
            const maxAltitude = document.getElementById('filter-altitude').value;
            
            let filtered = allEvents;
            
            if (callsign) {
                filtered = filtered.filter(e => 
                    (e.callsign || '').toLowerCase().includes(callsign)
                );
            }
            
            if (dateFrom) {
                filtered = filtered.filter(e => new Date(e.timestamp) >= new Date(dateFrom));
            }
            
            if (dateTo) {
                filtered = filtered.filter(e => new Date(e.timestamp) <= new Date(dateTo));
            }
            
            if (maxAltitude) {
                filtered = filtered.filter(e => (e.min_altitude || 0) <= parseFloat(maxAltitude));
            }
            
            renderTable(filtered);
        }
        
        function resetFilters() {
            document.getElementById('filter-callsign').value = '';
            document.getElementById('filter-date-from').value = '';
            document.getElementById('filter-date-to').value = '';
            document.getElementById('filter-altitude').value = '';
            renderTable(allEvents);
        }
        
        // Load history on page load
        loadHistory();
        
        // Refresh every 30 seconds
        setInterval(loadHistory, 30000);
    </script>
</body>
</html>
'''

import argparse
import csv
import json
import logging
import math
import os
import sys
import time
from collections import deque
from dataclasses import dataclass, asdict, field
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Deque
from pathlib import Path

import requests
from flask import Flask, Response, jsonify, request
from werkzeug.middleware.proxy_fix import ProxyFix

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class Position:
    lat: float
    lon: float
    timestamp: float
    altitude: Optional[float] = None
    speed: Optional[float] = None
    vert_rate: Optional[float] = None  # Vertical rate in ft/min

@dataclass
class Aircraft:
    hex_id: str
    callsign: str
    path: Deque[Position] = field(default_factory=lambda: deque(maxlen=120))  # Keep last 10 minutes at 5s intervals
    last_update: float = 0
    type: Optional[str] = None
    category: Optional[str] = None
    
    # Go-around detection state
    min_altitude_recent: Optional[float] = None  # Minimum altitude in recent history
    min_altitude_time: Optional[float] = None    # Time of minimum altitude
    is_climbing_rapidly: bool = False
    go_around_detected: bool = False
    go_around_start_time: Optional[float] = None
    max_climb_rate: Optional[float] = None       # Maximum climb rate during go-around

@dataclass
class GoAroundDetection:
    is_go_around: bool
    confidence: float  # 0.0 to 1.0
    min_altitude: float
    current_altitude: float
    climb_rate: float  # ft/min
    trigger_reason: str  # Description of why go-around was detected

@dataclass
class GoAroundLog:
    """Log entry for a detected go-around event."""
    timestamp: datetime
    hex_id: str
    callsign: str
    lat: float
    lon: float
    min_altitude: float
    max_climb_rate: float
    duration: int  # seconds
    confidence: float
    tar1090_url: str


class GoAroundDetector:
    def __init__(
        self,
        low_altitude_threshold: float = 2000,  # ft - below this is considered low
        min_climb_rate: float = 1000,          # ft/min - minimum climb rate for go-around
        rapid_climb_rate: float = 1500,        # ft/min - rapid climb indicator
        altitude_recovery: float = 500,        # ft - must climb this much from minimum
        time_window: int = 120                 # seconds - look back window
    ):
        self.low_altitude_threshold = low_altitude_threshold
        self.min_climb_rate = min_climb_rate
        self.rapid_climb_rate = rapid_climb_rate
        self.altitude_recovery = altitude_recovery
        self.time_window = time_window
    
    def detect_go_around(self, aircraft: Aircraft) -> GoAroundDetection:
        """
        Detect if an aircraft is performing a go-around maneuver.
        
        A go-around is characterized by:
        1. Low altitude (typically < 2000 ft AGL, but we use MSL)
        2. Sudden increase in vertical rate (climb)
        3. Altitude recovery from a recent minimum
        """
        
        if len(aircraft.path) < 3:
            return GoAroundDetection(False, 0.0, 0, 0, 0, "Insufficient data")
        
        current_pos = aircraft.path[-1]
        current_time = current_pos.timestamp
        
        # Need altitude and vertical rate data
        if current_pos.altitude is None or current_pos.vert_rate is None:
            return GoAroundDetection(False, 0.0, 0, 0, 0, "No altitude/vert_rate data")
        
        # Find minimum altitude in recent history
        min_alt = current_pos.altitude
        min_alt_time = current_time
        positions_in_window = []
        
        for pos in aircraft.path:
            if current_time - pos.timestamp <= self.time_window:
                positions_in_window.append(pos)
                if pos.altitude is not None and pos.altitude < min_alt:
                    min_alt = pos.altitude
                    min_alt_time = pos.timestamp
        
        if len(positions_in_window) < 3:
            return GoAroundDetection(False, 0.0, 0, 0, 0, "Insufficient recent data")
        
        # Calculate altitude recovery
        altitude_recovery = current_pos.altitude - min_alt
        
        # Time since minimum altitude
        time_since_min = current_time - min_alt_time
        
        # Detect go-around conditions
        confidence = 0.0
        reasons = []
        
        # Check if aircraft was at low altitude
        if min_alt < self.low_altitude_threshold:
            confidence += 0.3
            reasons.append(f"Low altitude: {min_alt:.0f}ft")
        
        # Check for significant climb rate
        if current_pos.vert_rate >= self.rapid_climb_rate:
            confidence += 0.4
            reasons.append(f"Rapid climb: {current_pos.vert_rate:.0f}ft/min")
        elif current_pos.vert_rate >= self.min_climb_rate:
            confidence += 0.2
            reasons.append(f"Climbing: {current_pos.vert_rate:.0f}ft/min")
        
        # Check for altitude recovery
        if altitude_recovery >= self.altitude_recovery and time_since_min < 60:
            confidence += 0.3
            reasons.append(f"Altitude recovery: {altitude_recovery:.0f}ft in {time_since_min:.0f}s")
        
        # Additional check: rapid change from descent to climb
        if len(positions_in_window) >= 5:
            # Check if aircraft was descending before the minimum
            for i in range(len(positions_in_window) - 2):
                if positions_in_window[i].vert_rate is not None and positions_in_window[i+1].vert_rate is not None:
                    vert_rate_change = positions_in_window[i+1].vert_rate - positions_in_window[i].vert_rate
                    if positions_in_window[i].vert_rate < -500 and vert_rate_change > 1000:
                        confidence += 0.2
                        reasons.append("Rapid transition from descent to climb")
                        break
        
        # Determine if it's a go-around based on confidence
        is_go_around = confidence >= 0.6
        
        return GoAroundDetection(
            is_go_around=is_go_around,
            confidence=min(confidence, 1.0),
            min_altitude=min_alt,
            current_altitude=current_pos.altitude,
            climb_rate=current_pos.vert_rate,
            trigger_reason="; ".join(reasons) if reasons else "No triggers"
        )


class TAR1090Monitor:
    def __init__(self, server_url: str, update_interval: int = 5):
        self.server_url = server_url.rstrip('/')
        self.update_interval = update_interval
        self.aircraft: Dict[str, Aircraft] = {}
        self.detector = GoAroundDetector()
        self.running = False
        self.session = requests.Session()
        self.session.timeout = 10
        
        # Statistics
        self.total_requests = 0
        self.failed_requests = 0
        self.last_update = None
        self.go_arounds_detected_today = 0
        self.last_detection_date = datetime.now().date()
        
        # Active go-arounds
        self.active_go_arounds: Dict[str, dict] = {}
        
        # CSV logging
        self.data_dir = Path("/app/data")
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.csv_file = self.data_dir / "go_around_detections.csv"
        self.init_csv_file()
    
    def init_csv_file(self):
        """Initialize CSV file with headers if it doesn't exist."""
        if not self.csv_file.exists():
            with open(self.csv_file, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([
                    'timestamp', 'hex_id', 'callsign', 'lat', 'lon',
                    'min_altitude', 'max_climb_rate', 'duration', 'confidence', 'tar1090_url'
                ])
    
    def log_go_around(self, log_entry: GoAroundLog):
        """Log a go-around event to CSV file."""
        with open(self.csv_file, 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([
                log_entry.timestamp.isoformat(),
                log_entry.hex_id,
                log_entry.callsign,
                log_entry.lat,
                log_entry.lon,
                log_entry.min_altitude,
                log_entry.max_climb_rate,
                log_entry.duration,
                log_entry.confidence,
                log_entry.tar1090_url
            ])
    
    def fetch_aircraft_data(self) -> bool:
        """Fetch aircraft data from TAR1090 server."""
        try:
            url = f"{self.server_url}/data/aircraft.json"
            response = self.session.get(url)
            response.raise_for_status()
            
            data = response.json()
            self.total_requests += 1
            self.last_update = datetime.now()
            
            # Reset daily counter if new day
            if self.last_update.date() != self.last_detection_date:
                self.go_arounds_detected_today = 0
                self.last_detection_date = self.last_update.date()
            
            current_time = time.time()
            
            # Process aircraft data
            aircraft_list = data.get('aircraft', data.get('ac', []))
            active_hex_ids = set()
            
            for ac_data in aircraft_list:
                if not ac_data.get('hex') or ac_data.get('lat') is None or ac_data.get('lon') is None:
                    continue
                
                hex_id = ac_data['hex']
                active_hex_ids.add(hex_id)
                
                # Create or update aircraft
                if hex_id not in self.aircraft:
                    self.aircraft[hex_id] = Aircraft(
                        hex_id=hex_id,
                        callsign=ac_data.get('flight', hex_id).strip()
                    )
                
                aircraft = self.aircraft[hex_id]
                aircraft.last_update = current_time
                aircraft.callsign = ac_data.get('flight', aircraft.callsign).strip()
                aircraft.type = ac_data.get('t')
                aircraft.category = ac_data.get('category')
                
                # Get altitude and vertical rate
                altitude = ac_data.get('alt_baro') or ac_data.get('alt_geom')
                vert_rate = ac_data.get('baro_rate') or ac_data.get('vert_rate')
                
                # Convert to float if needed
                if altitude is not None:
                    try:
                        altitude = float(altitude)
                    except (ValueError, TypeError):
                        altitude = None
                
                if vert_rate is not None:
                    try:
                        vert_rate = float(vert_rate)
                    except (ValueError, TypeError):
                        vert_rate = None
                
                speed = ac_data.get('gs')
                if speed is not None:
                    try:
                        speed = float(speed)
                    except (ValueError, TypeError):
                        speed = None
                
                # Create new position
                new_pos = Position(
                    lat=float(ac_data['lat']),
                    lon=float(ac_data['lon']),
                    timestamp=current_time,
                    altitude=altitude,
                    speed=speed,
                    vert_rate=vert_rate
                )
                
                # Add to path
                aircraft.path.append(new_pos)
                
                # Detect go-around
                detection = self.detector.detect_go_around(aircraft)
                
                if detection.is_go_around:
                    if hex_id not in self.active_go_arounds:
                        # New go-around detected
                        self.active_go_arounds[hex_id] = {
                            'aircraft': aircraft,
                            'detection': detection,
                            'start_time': current_time,
                            'min_altitude': detection.min_altitude,
                            'max_climb_rate': detection.climb_rate
                        }
                        self.go_arounds_detected_today += 1
                        
                        logger.info(f"Go-around detected: {aircraft.callsign} ({hex_id}) - {detection.trigger_reason}")
                    else:
                        # Update existing go-around
                        go_around_data = self.active_go_arounds[hex_id]
                        go_around_data['detection'] = detection
                        go_around_data['max_climb_rate'] = max(
                            go_around_data['max_climb_rate'],
                            detection.climb_rate
                        )
                else:
                    # Check if go-around has ended
                    if hex_id in self.active_go_arounds:
                        go_around_data = self.active_go_arounds[hex_id]
                        duration = int(current_time - go_around_data['start_time'])
                        
                        # Log the completed go-around
                        if duration > 10:  # Only log if it lasted more than 10 seconds
                            log_entry = GoAroundLog(
                                timestamp=datetime.now(),
                                hex_id=hex_id,
                                callsign=aircraft.callsign,
                                lat=new_pos.lat,
                                lon=new_pos.lon,
                                min_altitude=go_around_data['min_altitude'],
                                max_climb_rate=go_around_data['max_climb_rate'],
                                duration=duration,
                                confidence=go_around_data['detection'].confidence,
                                tar1090_url=f"{self.server_url}/?icao={hex_id}"
                            )
                            self.log_go_around(log_entry)
                            logger.info(f"Go-around completed: {aircraft.callsign} ({hex_id}) - Duration: {duration}s")
                        
                        del self.active_go_arounds[hex_id]
            
            # Clean up old aircraft
            for hex_id in list(self.aircraft.keys()):
                if hex_id not in active_hex_ids:
                    if current_time - self.aircraft[hex_id].last_update > 60:
                        del self.aircraft[hex_id]
                        if hex_id in self.active_go_arounds:
                            del self.active_go_arounds[hex_id]
            
            return True
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to fetch aircraft data: {e}")
            self.failed_requests += 1
            return False
    
    def run(self):
        """Main monitoring loop."""
        self.running = True
        logger.info(f"Starting TAR1090 monitor for {self.server_url}")
        
        while self.running:
            try:
                self.fetch_aircraft_data()
                time.sleep(self.update_interval)
            except KeyboardInterrupt:
                logger.info("Monitoring stopped by user")
                self.running = False
            except Exception as e:
                logger.error(f"Unexpected error: {e}")
                time.sleep(self.update_interval)
    
    def get_status(self) -> dict:
        """Get current monitoring status."""
        return {
            'running': self.running,
            'server_url': self.server_url,
            'total_aircraft': len(self.aircraft),
            'active_go_arounds': len(self.active_go_arounds),
            'potential_go_arounds': sum(
                1 for a in self.aircraft.values() 
                if a.path and a.path[-1].altitude and a.path[-1].altitude < 2000
            ),
            'detected_today': self.go_arounds_detected_today,
            'total_requests': self.total_requests,
            'failed_requests': self.failed_requests,
            'last_update': self.last_update.isoformat() if self.last_update else None
        }
    
    def get_go_around_data(self) -> dict:
        """Get current go-around data for API."""
        go_arounds = []
        potential_go_arounds = []
        
        for hex_id, go_around_data in self.active_go_arounds.items():
            aircraft = go_around_data['aircraft']
            detection = go_around_data['detection']
            current_pos = aircraft.path[-1] if aircraft.path else None
            
            if current_pos:
                go_arounds.append({
                    'hex_id': hex_id,
                    'callsign': aircraft.callsign,
                    'current_lat': current_pos.lat,
                    'current_lon': current_pos.lon,
                    'current_alt': current_pos.altitude,
                    'vert_rate': current_pos.vert_rate,
                    'speed': current_pos.speed,
                    'min_altitude': detection.min_altitude,
                    'max_climb_rate': go_around_data['max_climb_rate'],
                    'confidence': detection.confidence,
                    'duration': int(time.time() - go_around_data['start_time']),
                    'trigger_reason': detection.trigger_reason,
                    'tar1090_url': f"{self.server_url}/?icao={hex_id}",
                    'recent_path': [{'lat': p.lat, 'lon': p.lon} for p in list(aircraft.path)[-20:]]
                })
        
        # Find potential go-arounds (low altitude aircraft)
        for hex_id, aircraft in self.aircraft.items():
            if hex_id not in self.active_go_arounds and aircraft.path:
                current_pos = aircraft.path[-1]
                if current_pos.altitude and current_pos.altitude < 2000:
                    potential_go_arounds.append({
                        'hex_id': hex_id,
                        'callsign': aircraft.callsign,
                        'current_lat': current_pos.lat,
                        'current_lon': current_pos.lon,
                        'current_alt': current_pos.altitude,
                        'vert_rate': current_pos.vert_rate,
                        'speed': current_pos.speed
                    })
        
        status = self.get_status()
        return {
            **status,
            'go_arounds': go_arounds,
            'potential_go_arounds_list': potential_go_arounds
        }
    
    def get_history(self) -> dict:
        """Get historical go-around data from CSV."""
        events = []
        
        if self.csv_file.exists():
            with open(self.csv_file, 'r') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    events.append({
                        'timestamp': row['timestamp'],
                        'hex_id': row['hex_id'],
                        'callsign': row['callsign'],
                        'lat': float(row['lat']),
                        'lon': float(row['lon']),
                        'min_altitude': float(row['min_altitude']) if row['min_altitude'] else None,
                        'max_climb_rate': float(row['max_climb_rate']) if row['max_climb_rate'] else None,
                        'duration': int(row['duration']) if row['duration'] else 0,
                        'confidence': float(row['confidence']) if row['confidence'] else 0,
                        'tar1090_url': row['tar1090_url']
                    })
        
        # Sort by timestamp (newest first)
        events.sort(key=lambda x: x['timestamp'], reverse=True)
        
        return {'events': events}


def create_flask_app(monitor: TAR1090Monitor) -> Flask:
    """Create Flask application for web interface."""
    app = Flask(__name__)
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)
    
    @app.route('/')
    def index():
        """Main map view."""
        return Response(MAP_HTML_TEMPLATE, content_type='text/html')
    
    @app.route('/history')
    def history():
        """Historical go-arounds view."""
        return Response(HISTORY_HTML_TEMPLATE, content_type='text/html')
    
    @app.route('/api/go_arounds')
    def api_go_arounds():
        """API endpoint for current go-around data."""
        return jsonify(monitor.get_go_around_data())
    
    @app.route('/api/go_around_history')
    def api_history():
        """API endpoint for historical go-around data."""
        return jsonify(monitor.get_history())
    
    @app.route('/api/health')
    def api_health():
        """Health check endpoint."""
        status = monitor.get_status()
        is_healthy = status['running'] and status.get('last_update') is not None
        
        return jsonify({
            'status': 'healthy' if is_healthy else 'unhealthy',
            **status
        }), 200 if is_healthy else 503
    
    return app


def main():
    parser = argparse.ArgumentParser(description='TAR1090 Go-Around Detector')
    parser.add_argument(
        '--server',
        default=os.environ.get('TAR1090_URL', 'http://localhost:8080'),
        help='TAR1090 server URL'
    )
    parser.add_argument(
        '--interval',
        type=int,
        default=int(os.environ.get('UPDATE_INTERVAL', '5')),
        help='Update interval in seconds'
    )
    parser.add_argument(
        '--web',
        action='store_true',
        default=os.environ.get('WEB_INTERFACE', 'false').lower() == 'true',
        help='Enable web interface'
    )
    parser.add_argument(
        '--web-port',
        type=int,
        default=int(os.environ.get('WEB_PORT', '8889')),
        help='Web interface port'
    )
    parser.add_argument(
        '--test',
        action='store_true',
        help='Test mode - check connection and exit'
    )
    
    args = parser.parse_args()
    
    # Create monitor
    monitor = TAR1090Monitor(args.server, args.interval)
    
    if args.test:
        print(f"Testing connection to {args.server}...")
        if monitor.fetch_aircraft_data():
            print("✅ Connection successful!")
            status = monitor.get_status()
            print(f"Found {status['total_aircraft']} aircraft")
        else:
            print("❌ Connection failed!")
            sys.exit(1)
        return
    
    if args.web:
        # Run with web interface
        import threading
        
        # Start monitoring in background thread
        monitor_thread = threading.Thread(target=monitor.run, daemon=True)
        monitor_thread.start()
        
        # Create and run Flask app
        app = create_flask_app(monitor)
        print(f"Starting web interface on http://0.0.0.0:{args.web_port}")
        print(f"Monitoring TAR1090 at {args.server}")
        app.run(host='0.0.0.0', port=args.web_port, debug=False)
    else:
        # Run monitoring only
        try:
            monitor.run()
        except KeyboardInterrupt:
            print("\nStopping monitor...")


if __name__ == '__main__':
    main()