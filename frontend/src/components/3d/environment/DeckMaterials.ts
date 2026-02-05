// fallat_crewai_dashboard/src/components/3d/environment/DeckMaterials.ts
import * as THREE from "three";

export type DeckMaterials = {
  darkMetal: THREE.MeshStandardMaterial;
  holoGlass: THREE.MeshStandardMaterial; // Changed from MeshPhysicalMaterial to avoid uniform issues
  emissiveLine: THREE.MeshStandardMaterial;
  softPanel: THREE.MeshStandardMaterial;
};

export function createDeckMaterials(): DeckMaterials {
  const darkMetal = new THREE.MeshStandardMaterial({
    color: new THREE.Color("#0a1424"),
    emissive: new THREE.Color("#050a12"),
    emissiveIntensity: 0.2,
    metalness: 0.7, // Reduced metalness to be less "black mirror"
    roughness: 0.4, // Increased roughness to catch more diffuse light
    envMapIntensity: 1.0,
  });
  darkMetal.needsUpdate = true;

  const softPanel = new THREE.MeshStandardMaterial({
    color: new THREE.Color("#0b1b31"),
    emissive: new THREE.Color("#061020"),
    emissiveIntensity: 0.2,
    metalness: 0.3,
    roughness: 0.6, // Matte finish for panels
    envMapIntensity: 0.8,
  });
  softPanel.needsUpdate = true;

  // "Holo glass" - Upgraded to MeshPhysicalMaterial for transmission
  const holoGlass = new THREE.MeshPhysicalMaterial({
    color: new THREE.Color("#4fd1ff"),
    metalness: 0.1,
    roughness: 0.05,
    transmission: 0.6, // Real glass effect
    thickness: 0.5,
    transparent: true,
    opacity: 0.4,
    emissive: new THREE.Color("#0f3a52"),
    emissiveIntensity: 0.8,
    clearcoat: 1.0,
    clearcoatRoughness: 0.0,
  }) as unknown as THREE.MeshStandardMaterial; // Cast to satisfy type signature
  holoGlass.needsUpdate = true;

  // Emissive material that will bloom nicely
  const emissiveLine = new THREE.MeshStandardMaterial({
    color: new THREE.Color("#00f2ff"),
    emissive: new THREE.Color("#00f2ff"),
    emissiveIntensity: 4.0, // Boosted for bloom
    metalness: 0.8,
    roughness: 0.1,
    toneMapped: false, // Critical for bright bloom
  });
  emissiveLine.needsUpdate = true;

  return { darkMetal, holoGlass, emissiveLine, softPanel };
}
