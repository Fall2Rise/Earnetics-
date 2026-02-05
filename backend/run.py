# backend/run.py
import os
import sys
import socket
import time
import uvicorn

def _test_port_bindable(host: str, port: int, max_retries: int = 24) -> bool:
    """Test if we can actually bind to the port. Retries to handle zombie sockets.
    
    On Windows, we test WITHOUT SO_REUSEADDR to accurately detect if port is truly free.
    If it's in TIME_WAIT, the bind will fail, which is what we want to detect.
    """
    for attempt in range(max_retries):
        try:
            # Test WITHOUT SO_REUSEADDR to see if port is truly free
            # (Windows TIME_WAIT sockets will block this)
            test_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            test_sock.bind((host, port))
            test_sock.close()
            if attempt > 0:
                print(f"Port {port} is now bindable after {attempt} retries ({attempt * 0.5:.1f}s)")
            return True
        except OSError as e:
            if attempt < max_retries - 1:
                if attempt % 4 == 0:  # Print every 2 seconds
                    print(f"Port {port} still in use, waiting... ({attempt * 0.5:.1f}s / {max_retries * 0.5:.1f}s)")
                time.sleep(0.5)  # Wait 500ms between retries
            else:
                print(f"Port {port} bind test failed: {e}")
                return False
    return False

def main() -> None:
    host = os.getenv("HOST", "127.0.0.1")
    port = int(os.getenv("PORT", "8000"))
    log_level = os.getenv("LOG_LEVEL", "info").lower()
    reload_enabled = os.getenv("RELOAD", "0") == "1"
    workers = int(os.getenv("WORKERS", "1"))

    # Test if port is actually bindable (handles zombie sockets with retries)
    print(f"Testing if port {port} is bindable (waiting up to 12 seconds for zombie sockets to clear)...")
    if not _test_port_bindable(host, port, max_retries=24):
        print(f"\n❌ ERROR: Port {port} is not bindable after 12 seconds of retries.")
        print(f"\nThis usually means:")
        print(f"  1. Another process is actively using port {port}")
        print(f"  2. Windows zombie sockets (TIME_WAIT) haven't cleared yet")
        print(f"\nSolutions:")
        print(f"  Option 1: Wait longer (Windows TIME_WAIT can take 30-120 seconds)")
        print(f"  Option 2: Restart your computer (clears all zombie sockets)")
        print(f"  Option 3: Use a different port: set PORT=8001 in .env")
        print(f"\nTo check what's using the port:")
        print(f"  netstat -ano | findstr :8000")
        sys.exit(1)
    
    print(f"✅ Port {port} is bindable - starting server...")

    # IMPORTANT: app lives at backend.app.py (single import location)
    # Use main_server:app directly (app.py wraps it)
    # uvicorn already sets SO_REUSEADDR in bind_socket()
    uvicorn.run(
        "backend.main_server:app",
        host=host,
        port=port,
        log_level=log_level,
        reload=reload_enabled,
        workers=workers,
    )

if __name__ == "__main__":
    main()
