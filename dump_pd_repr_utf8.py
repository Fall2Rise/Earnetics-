import os

try:
    with open(r'c:\AI_Projects\Fallat_CrewAI\backend\prime_directive.py', 'rb') as f:
        content = f.read()
    
    with open(r'c:\AI_Projects\Fallat_CrewAI\pd_repr_utf8.txt', 'w', encoding='utf-8') as f:
        f.write(repr(content))
        
    print("Done")
except Exception as e:
    print(f"Error: {e}")
