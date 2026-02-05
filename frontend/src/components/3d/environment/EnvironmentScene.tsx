import React, { useRef } from 'react'
import { Canvas, useFrame, useLoader } from '@react-three/fiber'
import { TextureLoader } from 'three'
import * as THREE from 'three'

function RotatingSigil() {
  const meshRef = useRef<THREE.Mesh>(null!)
  const texture = useLoader(TextureLoader, '/favicon.png')

  useFrame(() => {
    if (meshRef.current) {
      meshRef.current.rotation.z += 0.003
    }
  })

  return (
    <mesh
      ref={meshRef}
      rotation={[-Math.PI / 2, 0, 0]}
      position={[0, 0.01, 0]}
    >
      <planeGeometry args={[5, 5]} />
      <meshStandardMaterial
        map={texture}
        emissive={'#00ffff'}
        emissiveIntensity={2}
        transparent
      />
    </mesh>
  )
}

export function EnvironmentScene() {
  return (
    <Canvas camera={{ position: [0, 5, 10], fov: 50 }}>
      <ambientLight intensity={0.5} />
      <pointLight position={[10, 10, 10]} />

      {/* Glowing rotating sigil */}
      <RotatingSigil />

      {/* Dark floor */}
      <mesh rotation={[-Math.PI / 2, 0, 0]} position={[0, 0, 0]}>
        <planeGeometry args={[100, 100]} />
        <meshStandardMaterial color={'#111111'} />
      </mesh>
    </Canvas>
  )
}
