import os

try:
    with open(r'c:\AI_Projects\Fallat_CrewAI\backend\prime_directive.py', 'rb') as f:
        content = f.read()
    
    print(f"Read {len(content)} bytes.")
    
    with open(r'c:\AI_Projects\Fallat_CrewAI\prime_directive_dump.txt', 'wb') as f:
        f.write(content)
        
    print("Dumped to prime_directive_dump.txt")
except Exception as e:
    print(f"Error: {e}")
