import requests
import sys
import time

def check_url(url, description):
    print(f"Checking {description} at {url}...")
    try:
        response = requests.get(url, timeout=5)
        print(f"Status Code: {response.status_code}")
        print(f"Headers: {response.headers}")
        print(f"Content Length: {len(response.content)}")
        print(f"Preview: {response.text[:200]}...")
        return True
    except requests.exceptions.ConnectionError:
        print(f"Failed to connect to {url}")
        return False
    except Exception as e:
        print(f"Error checking {url}: {e}")
        return False

def main():
    print("Verifying Dashboard Connectivity...")
    
    # Check localhost:8000 (Docker mapped port)
    docker_url = "http://localhost:8000"
    check_url(docker_url, "Docker Mapped Port")
    
    # Check /ping endpoint
    ping_url = "http://localhost:8000/ping"
    check_url(ping_url, "Ping Endpoint")

    # Check /health endpoint
    health_url = "http://localhost:8000/health"
    check_url(health_url, "Health Endpoint")

if __name__ == "__main__":
    main()
