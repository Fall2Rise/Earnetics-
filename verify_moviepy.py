
import sys
try:
    import moviepy.editor
    result = "SUCCESS: moviepy.editor imported successfully"
    print(result)
except Exception as e:
    result = f"FAILURE: {e}"
    print(result)

with open("verification_result.md", "w", encoding="utf-8") as f:
    f.write(result)
