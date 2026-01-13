import os

try:
    with open(r'c:\AI_Projects\Fallat_CrewAI\backend\prime_directive.py', 'rb') as f:
        content = f.read()
    
    print(repr(content))
except Exception as e:
    print(f"Error: {e}")
