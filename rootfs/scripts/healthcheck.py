#!/usr/bin/env python3

import os
import sys
import json
import urllib.request
import urllib.error

def check_health():
    """Check the health of the go-around tracker service."""
    try:
        # Get the port from environment or use default
        port = os.environ.get('HEALTHCHECK_PORT', '8889')
        
        # Make request to health endpoint
        url = f'http://localhost:{port}/api/health'
        req = urllib.request.Request(url)
        
        with urllib.request.urlopen(req, timeout=5) as response:
            if response.status == 200:
                data = json.loads(response.read().decode())
                
                # Check if service is healthy
                if data.get('status') == 'healthy':
                    print(f"Service is healthy: {data.get('message', 'OK')}")
                    return 0
                else:
                    print(f"Service unhealthy: {data.get('message', 'Unknown error')}")
                    return 1
            else:
                print(f"Unexpected status code: {response.status}")
                return 1
                
    except urllib.error.URLError as e:
        print(f"Connection error: {e}")
        return 1
    except json.JSONDecodeError as e:
        print(f"Invalid JSON response: {e}")
        return 1
    except Exception as e:
        print(f"Unexpected error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(check_health())