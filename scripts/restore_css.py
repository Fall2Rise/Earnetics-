import sys
from pathlib import Path

file_path = Path(r"c:\AI_Projects\Fallat_CrewAI\fallat_crewai_dashboard\src\styles\index.css")
content = file_path.read_text(encoding="utf-8").splitlines()

# Keep lines 1-15 (0-14 index)
new_content = content[:15]

# Insert missing blocks
new_content.extend([
    "  body {",
    "    @apply min-h-screen text-white font-inter;",
    "    background: radial-gradient(120% 120% at 50% 0%, rgba(74, 0, 224, 0.4), transparent),",
    "      radial-gradient(100% 120% at 10% 80%, rgba(44, 247, 244, 0.25), transparent),",
    "      linear-gradient(180deg, #03040c 0%, #060714 40%, #03040c 100%);",
    "    overflow-x: hidden;",
    "  }",
    "",
    "  h1,",
    "  h2,",
    "  h3,",
    "  h4,",
    "  h5,",
    "  h6 {",
    "    @apply font-orbitron tracking-wide;",
    "  }",
    "}",
    "",
    "@layer components {",
    "  .glass-panel {",
    "    @apply bg-white/5 backdrop-blur-xl border border-white/10 rounded-3xl shadow-[0_20px_60px_rgba(5,5,45,0.45)];",
    "  }",
    "",
    "  .app-container {",
    "    @apply relative min-h-screen overflow-hidden pl-0 pr-0 pb-20;",
    "  }",
    "",
    "  .aurora-overlay {",
    "    @apply absolute inset-0 pointer-events-none;",
    "    background:",
    "      radial-gradient(40% 45% at 20% 20%, rgba(91, 75, 255, 0.35), transparent),",
    "      radial-gradient(35% 40% at 80% 10%, rgba(44, 247, 244, 0.25), transparent),",
    "      radial-gradient(30% 35% at 90% 90%, rgba(255, 81, 170, 0.2), transparent);",
    "    mix-blend-mode: screen;",
    "    animation: aurora-shift 18s ease-in-out infinite alternate;",
    "  }",
    "",
    "  @keyframes aurora-shift {",
    "    0% {",
    "      transform: translate3d(0, 0, 0) scale(1);",
    "    }",
    "",
    "    100% {",
    "      transform: translate3d(2%, -2%, 0) scale(1.05);",
    "    }",
    "  }",
    ""
])

# Append the rest of the file from line 25 (index 24) onwards, fixing indentation
# We need to remove 4 spaces of indentation from each line if it starts with spaces
for line in content[24:]:
    if line.startswith("    "):
        new_content.append(line[4:])
    elif line.startswith("  "):
        new_content.append(line[2:])
    else:
        new_content.append(line)

file_path.write_text("\n".join(new_content), encoding="utf-8")
print("File restored successfully.")
