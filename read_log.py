import sys

try:
    with open(r'c:\AI_Projects\Fallat_CrewAI\backend\logs\backend_boot_latest.log', 'r', encoding='utf-16le') as f:
        content = f.read()
    with open(r'c:\AI_Projects\Fallat_CrewAI\log_output.txt', 'w', encoding='utf-8') as f:
        f.write(content)
    print("Log written to log_output.txt")
except Exception as e:
    with open(r'c:\AI_Projects\Fallat_CrewAI\log_output.txt', 'w', encoding='utf-8') as f:
        f.write(f"Error: {e}")
    print(f"Error: {e}")
