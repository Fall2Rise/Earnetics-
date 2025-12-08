import sys
import urllib.request
import urllib.error
import socket
import time

def check_server(url):
    print(f"Checking {url}...")
    try:
        start_time = time.time()
        with urllib.request.urlopen(url, timeout=5) as response:
            status = response.getcode()
            content = response.read().decode('utf-8')
            print(f"✅ Success! Status: {status}")
            print(f"Response: {content[:100]}...")
            print(f"Time: {time.time() - start_time:.2f}s")
            return True
    except urllib.error.URLError as e:
        print(f"❌ Connection failed: {e}")
        if isinstance(e.reason, socket.timeout):
            print("   (Timed out)")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def check_port(host, port):
    print(f"Checking port {host}:{port}...")
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(2)
    try:
        result = s.connect_ex((host, port))
        if result == 0:
            print(f"✅ Port {port} is OPEN on {host}")
            s.close()
            return True
        else:
            print(f"❌ Port {port} is CLOSED/UNREACHABLE on {host} (Code: {result})")
            s.close()
            return False
    except Exception as e:
        print(f"❌ Port check error: {e}")
        return False

if __name__ == "__main__":
    print("--- DIAGNOSTIC START ---")
    
    # 1. Check TCP Port
    port_open = check_port("localhost", 8000)
    if not port_open:
        print("   Trying 127.0.0.1...")
        check_port("127.0.0.1", 8000)
    
    # 2. Check HTTP Endpoint
    if port_open:
        check_server("http://localhost:8000/api/system/status")
        check_server("http://127.0.0.1:8000/api/system/status")
    
    print("--- DIAGNOSTIC END ---")
