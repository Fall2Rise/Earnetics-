// fallat_crewai_dashboard/src/components/3d/environment/StarBackdrop.tsx
import React from "react";
import { Stars } from "@react-three/drei";

type Props = {
  enabled?: boolean;
  radius?: number;
  depth?: number;
  count?: number;
  factor?: number;
  fade?: boolean;
  saturation?: number;
};

export const StarBackdrop: React.FC<Props> = ({
  enabled = true,
  radius = 120,
  depth = 40,
  count = 800,
  factor = 1.4,
  fade = true,
  saturation = 0,
}) => {
  if (!enabled) return null;

  return (
    <>
      {/* Keep it subtle — this is "room + depth", not "space sim" */}
      <Stars
        radius={radius}
        depth={depth}
        count={count}
        factor={factor}
        fade={fade}
        saturation={saturation}
        speed={0.05}
      />
    </>
  );
};
