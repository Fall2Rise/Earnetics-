// Optional 3D scene placeholder using react-three-fiber; fallback to 2D if not present.
export function AgentScene3D() {
  return (
    <div className="p-4 rounded-hud border border-white/10 text-white/70">
      3D scene placeholder (react-three-fiber). Use AgentScene2D if WebGL is unavailable.
    </div>
  );
}
