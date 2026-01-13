// fallat_crewai_dashboard/src/components/3d/environment/DeckMaterials.ts
import * as THREE from "three";

export type DeckMaterials = {
  darkMetal: THREE.MeshStandardMaterial;
  holoGlass: THREE.MeshPhysicalMaterial;
  emissiveLine: THREE.MeshStandardMaterial;
  softPanel: THREE.MeshStandardMaterial;
};

export function createDeckMaterials(): DeckMaterials {
  const darkMetal = new THREE.MeshStandardMaterial({
    color: new THREE.Color("#07101c"),
    metalness: 0.8,
    roughness: 0.35,
  });

  const softPanel = new THREE.MeshStandardMaterial({
    color: new THREE.Color("#09162a"),
    metalness: 0.4,
    roughness: 0.55,
  });

  // "Holo glass" for subtle translucent panels
  const holoGlass = new THREE.MeshPhysicalMaterial({
    color: new THREE.Color("#0b2a3d"),
    metalness: 0.0,
    roughness: 0.2,
    transmission: 0.65,
    thickness: 0.9,
    transparent: true,
    opacity: 0.35,
    clearcoat: 0.6,
    clearcoatRoughness: 0.2,
  });

  // Emissive material that will bloom nicely
  const emissiveLine = new THREE.MeshStandardMaterial({
    color: new THREE.Color("#0ee7ff"),
    emissive: new THREE.Color("#0ee7ff"),
    emissiveIntensity: 1.1,
    metalness: 0.1,
    roughness: 0.35,
  });

  return { darkMetal, holoGlass, emissiveLine, softPanel };
}
