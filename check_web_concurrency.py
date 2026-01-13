import os

def check_web_concurrency():
    path = ".env"
    if not os.path.exists(path):
        print(".env not found")
        return

    try:
        with open(path, 'rb') as f:
            content = f.read().decode('utf-8', errors='ignore')
        
        if "WEB_CONCURRENCY" in content:
            print("WEB_CONCURRENCY: FOUND")
        else:
            print("WEB_CONCURRENCY: MISSING")
            
    except Exception as e:
        print(f"Error: {e}")

check_web_concurrency()
