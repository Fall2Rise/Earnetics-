import re
from pathlib import Path

file_path = Path(r"c:\AI_Projects\Fallat_CrewAI\fallat_crewai_dashboard\src\styles\index.css")
content = file_path.read_text(encoding="utf-8")

# 1. Fix all rgba with spaces inside shadow-[...]
# Pattern: shadow-[...rgba(x, y, z, a)...]
def fix_rgba(match):
    return match.group(0).replace(", ", ",")

content = re.sub(r"shadow-\[.*?rgba\(.*?\).*?\]", fix_rgba, content)

# 2. Fix the corrupted holo-pulse keyframes and media query
# We'll look for the corrupted part and replace it with the correct one.
# The corruption starts around line 888 in the current file.

corrupted_pattern = r"@keyframes holo-pulse \{.*?@apply text-sm tracking-widest;.*?\}\s*\.header-nav \{"
replacement = """@keyframes holo-pulse {
  0% {
    opacity: 0.2;
  }

  50% {
    opacity: 0.4;
  }

  100% {
    opacity: 0.2;
  }
}

/* Mobile & Tablet Responsiveness */
@media (max-width: 1024px) {
.header-frame {
  @apply w-[96%] px-6 py-3 mt-4;
}

.header-brand h1 {
  @apply text-sm tracking-widest;
}

.header-nav {"""

content = re.sub(corrupted_pattern, replacement, content, flags=re.DOTALL)

file_path.write_text(content, encoding="utf-8")
print("CSS file fixed successfully.")
