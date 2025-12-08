from pathlib import Path
text = Path("backend/fallat_corporate_hierarchy.py").read_text(encoding="utf-8")
start = text.index("\"recent_activities\"")
end = text.index("    }")
print(text[start:end])
