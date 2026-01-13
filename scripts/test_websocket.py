import asyncio
import websockets
import json
import sys

async def test_websocket():
    uri = "ws://localhost:8000/ws"
    print(f"Connecting to {uri}...")
    try:
        async with websockets.connect(uri) as websocket:
            print("Connected!")
            
            # Wait for initial system state or just listen
            while True:
                try:
                    message = await asyncio.wait_for(websocket.recv(), timeout=10)
                    data = json.loads(message)
                    print(f"Received: {json.dumps(data, indent=2)}")
                    
                    if data.get("type") == "CONTROL_UPDATE":
                        print("Control update received! Test Passed.")
                        break
                        
                except asyncio.TimeoutError:
                    print("Timeout waiting for message.")
                    break
                except Exception as e:
                    print(f"Error: {e}")
                    break
                    
    except Exception as e:
        print(f"Connection failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(test_websocket())
