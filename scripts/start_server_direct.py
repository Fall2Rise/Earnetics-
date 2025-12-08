        import uvicorn
import os
import sys

if __name__ == "__main__":
    print("Starting server directly...")
    sys.path.append(os.getcwd())
    uvicorn.run("backend.main_server:app", host="0.0.0.0", port=8000, workers=4)
