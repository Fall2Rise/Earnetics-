import sys
from pathlib import Path

file_path = Path(r"c:\AI_Projects\Fallat_CrewAI\fallat_crewai_dashboard\src\styles\index.css")
content = file_path.read_text(encoding="utf-8").splitlines()

# Keep lines 1-10 (0-9 index)
new_content = content[:10]

# Insert missing blocks and fix structure
new_content.extend([
    "    --color-iris: #5b4bff;",
    "    --color-aqua: #2cf7f4;",
    "    --color-ink: #0b101f;",
    "    --color-muted: rgba(255, 255, 255, 0.55);",
    "  }",
    "",
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
    "}",
    "",
    ".header-frame {",
    "  @apply sticky top-0 z-50 mx-auto mt-6 flex w-[92%] items-center justify-between rounded-3xl border border-white/10 bg-white/5 px-10 py-4 backdrop-blur-2xl shadow-[0_25px_60px_rgba(3, 7, 20, 0.45)];",
    "}",
    "",
    ".header-brand {",
    "  @apply flex items-center gap-4;",
    "}",
    "",
    ".brand-glyph {",
    "  @apply flex h-12 w-12 items-center justify-center rounded-2xl bg-gradient-to-br from-indigo-500 to-cyan-400 font-orbitron text-lg font-semibold text-white shadow-[0_10px_25px_rgba(44, 247, 244, 0.35)];",
    "}",
    "",
    ".header-brand h1 {",
    "  @apply text-base font-semibold uppercase tracking-[0.3em];",
    "}",
    "",
    ".header-brand p {",
    "  @apply text-xs uppercase text-white/50 tracking-widest;",
    "}",
    ""
])

# Find the line where .header-nav starts (without extra indentation)
start_index = -1
for i, line in enumerate(content):
    if line.strip() == ".header-nav {":
        start_index = i
        break

if start_index != -1:
    new_content.extend(content[start_index:])
else:
    print("Could not find .header-nav, appending rest of file from line 65")
    new_content.extend(content[64:])

file_path.write_text("\n".join(new_content), encoding="utf-8")
print("File restored successfully.")
