import React, { useRef, useMemo, useState } from 'react';
import * as THREE from 'three';
import { useFrame } from '@react-three/fiber';
import { Float, Html } from '@react-three/drei';

// Custom shader for the "Cosmic Symbiote"
const InternalEnergyShader = {
  uniforms: {
    uTime: { value: 0 },
    uColor1: { value: new THREE.Color('#4c1d95') }, // Deep Cosmic Purple
    uColor2: { value: new THREE.Color('#fbbf24') }, // Bright Gold
  },
  vertexShader: `
    varying vec2 vUv;
    varying vec3 vNormal;
    varying vec3 vPosition;
    uniform float uTime;
    
    // ... (noise functions) ...
    vec3 mod289(vec3 x) { return x - floor(x * (1.0 / 289.0)) * 289.0; }
    vec4 mod289(vec4 x) { return x - floor(x * (1.0 / 289.0)) * 289.0; }
    vec4 permute(vec4 x) { return mod289(((x*34.0)+1.0)*x); }
    vec4 taylorInvSqrt(vec4 r) { return 1.79284291400159 - 0.85373472095314 * r; }
    float snoise(vec3 v) {
      const vec2  C = vec2(1.0/6.0, 1.0/3.0) ;
      const vec4  D = vec4(0.0, 0.5, 1.0, 2.0);
      vec3 i  = floor(v + dot(v, C.yyy) );
      vec3 x0 = v - i + dot(i, C.xxx) ;
      vec3 g = step(x0.yzx, x0.xyz);
      vec3 l = 1.0 - g;
      vec3 i1 = min( g.xyz, l.zxy );
      vec3 i2 = max( g.xyz, l.zxy );
      vec3 x1 = x0 - i1 + C.xxx;
      vec3 x2 = x0 - i2 + C.yyy;
      vec3 x3 = x0 - D.yyy;
      i = mod289(i);
      vec4 p = permute( permute( permute( 
                 i.z + vec4(0.0, i1.z, i2.z, 1.0 ))
               + i.y + vec4(0.0, i1.y, i2.y, 1.0 )) 
               + i.x + vec4(0.0, i1.x, i2.x, 1.0 ));
      float n_ = 0.142857142857;
      vec3  ns = n_ * D.wyz - D.xzx;
      vec4 j = p - 49.0 * floor(p * ns.z * ns.z);
      vec4 x_ = floor(j * ns.z);
      vec4 y_ = floor(j - 7.0 * x_ );
      vec4 x = x_ *ns.x + ns.yyyy;
      vec4 y = y_ *ns.x + ns.yyyy;
      vec4 h = 1.0 - abs(x) - abs(y);
      vec4 b0 = vec4( x.xy, y.xy );
      vec4 b1 = vec4( x.zw, y.zw );
      vec4 s0 = floor(b0)*2.0 + 1.0;
      vec4 s1 = floor(b1)*2.0 + 1.0;
      vec4 sh = -step(h, vec4(0.0));
      vec4 a0 = b0.xzyw + s0.xzyw*sh.xxyy ;
      vec4 a1 = b1.xzyw + s1.xzyw*sh.zzww ;
      vec3 p0 = vec3(a0.xy,h.x);
      vec3 p1 = vec3(a0.zw,h.y);
      vec3 p2 = vec3(a1.xy,h.z);
      vec3 p3 = vec3(a1.zw,h.w);
      vec4 norm = taylorInvSqrt(vec4(dot(p0,p0), dot(p1,p1), dot(p2, p2), dot(p3,p3)));
      p0 *= norm.x;
      p1 *= norm.y;
      p2 *= norm.z;
      p3 *= norm.w;
      vec4 m = max(0.6 - vec4(dot(x0,x0), dot(x1,x1), dot(x2,x2), dot(x3,x3)), 0.0);
      m = m * m;
      return 42.0 * dot( m*m, vec4( dot(p0,x0), dot(p1,x1), 
                                    dot(p2,x2), dot(p3,x3) ) );
    }

    void main() {
      vUv = uv;
      vNormal = normal;
      vPosition = position;
      
      // Gentle, organic pulse of the shape itself
      // Much subtler than before to avoid "wobbling jelly" look
      float pulse = snoise(position * 0.5 + uTime * 0.2) * 0.03;
      vec3 newPosition = position + normal * pulse;
      
      gl_Position = projectionMatrix * modelViewMatrix * vec4(newPosition, 1.0);
    }
  `,
  fragmentShader: `
    uniform float uTime;
    uniform vec3 uColor1;
    uniform vec3 uColor2;
    varying vec2 vUv;
    varying vec3 vPosition;
    
    // Simplex noise import
    vec3 mod289(vec3 x) { return x - floor(x * (1.0 / 289.0)) * 289.0; }
    vec4 mod289(vec4 x) { return x - floor(x * (1.0 / 289.0)) * 289.0; }
    vec4 permute(vec4 x) { return mod289(((x*34.0)+1.0)*x); }
    vec4 taylorInvSqrt(vec4 r) { return 1.79284291400159 - 0.85373472095314 * r; }
    float snoise(vec3 v) {
      const vec2  C = vec2(1.0/6.0, 1.0/3.0) ;
      const vec4  D = vec4(0.0, 0.5, 1.0, 2.0);
      vec3 i  = floor(v + dot(v, C.yyy) );
      vec3 x0 = v - i + dot(i, C.xxx) ;
      vec3 g = step(x0.yzx, x0.xyz);
      vec3 l = 1.0 - g;
      vec3 i1 = min( g.xyz, l.zxy );
      vec3 i2 = max( g.xyz, l.zxy );
      vec3 x1 = x0 - i1 + C.xxx;
      vec3 x2 = x0 - i2 + C.yyy;
      vec3 x3 = x0 - D.yyy;
      i = mod289(i);
      vec4 p = permute( permute( permute( 
                 i.z + vec4(0.0, i1.z, i2.z, 1.0 ))
               + i.y + vec4(0.0, i1.y, i2.y, 1.0 )) 
               + i.x + vec4(0.0, i1.x, i2.x, 1.0 ));
      float n_ = 0.142857142857;
      vec3  ns = n_ * D.wyz - D.xzx;
      vec4 j = p - 49.0 * floor(p * ns.z * ns.z);
      vec4 x_ = floor(j * ns.z);
      vec4 y_ = floor(j - 7.0 * x_ );
      vec4 x = x_ *ns.x + ns.yyyy;
      vec4 y = y_ *ns.x + ns.yyyy;
      vec4 h = 1.0 - abs(x) - abs(y);
      vec4 b0 = vec4( x.xy, y.xy );
      vec4 b1 = vec4( x.zw, y.zw );
      vec4 s0 = floor(b0)*2.0 + 1.0;
      vec4 s1 = floor(b1)*2.0 + 1.0;
      vec4 sh = -step(h, vec4(0.0));
      vec4 a0 = b0.xzyw + s0.xzyw*sh.xxyy ;
      vec4 a1 = b1.xzyw + s1.xzyw*sh.zzww ;
      vec3 p0 = vec3(a0.xy,h.x);
      vec3 p1 = vec3(a0.zw,h.y);
      vec3 p2 = vec3(a1.xy,h.z);
      vec3 p3 = vec3(a1.zw,h.w);
      vec4 norm = taylorInvSqrt(vec4(dot(p0,p0), dot(p1,p1), dot(p2, p2), dot(p3,p3)));
      p0 *= norm.x;
      p1 *= norm.y;
      p2 *= norm.z;
      p3 *= norm.w;
      vec4 m = max(0.6 - vec4(dot(x0,x0), dot(x1,x1), dot(x2,x2), dot(x3,x3)), 0.0);
      m = m * m;
      return 42.0 * dot( m*m, vec4( dot(p0,x0), dot(p1,x1), 
                                    dot(p2,x2), dot(p3,x3) ) );
    }

    void main() {
      // COORDINATE SYSTEM: 
      // We need a rotational field (polar coordinates) for the "Galaxy" effect
      
      // Center the coordinates roughly
      vec3 pos = vPosition;
      
      // 1. Create the Swirl (Galaxy Arms)
      // Angle of the point around the Y axis
      float angle = atan(pos.z, pos.x);
      float dist = length(pos.xz);
      
      // Twisting factor: Modifies angle based on distance from center + time
      // This creates the "spiral" motion
      float spiral = angle + dist * 2.0 - uTime * 1.5;
      
      // 2. Galaxy Noise
      // We map the noise to this spiral coordinate system
      vec3 noiseCoord = vec3(cos(spiral) * dist, pos.y, sin(spiral) * dist);
      
      // Base Nebula (Purple clouds)
      float nebulaNoise = snoise(noiseCoord * 1.5 + vec3(uTime * 0.1));
      
      // Detail Stars/Sparkles (Gold specs)
      float starNoise = snoise(pos * 8.0 + vec3(uTime * 0.5)); // High frequency
      
      // 3. Symbiotic Tendrils
      // Veins that run through the galaxy
      float tendrilNoise = snoise(pos * 3.0 + vec3(uTime * 0.2));
      float tendrils = 1.0 - abs(tendrilNoise); // Sharp lines
      tendrils = pow(tendrils, 4.0); // Make them very thin
      
      // COLOR MIXING
      
      // Deep Space Void
      vec3 voidColor = vec3(0.0, 0.0, 0.02); 
      
      // Purple Nebula
      vec3 nebulaColor = uColor1;
      float nebulaMask = smoothstep(0.2, 0.8, nebulaNoise);
      
      // Gold Energy (Stars + Tendrils)
      vec3 goldColor = uColor2;
      
      // Star mask (only show stars in the "arms" of the galaxy)
      float starMask = smoothstep(0.7, 1.0, starNoise) * nebulaMask;
      
      // Tendril mask
      float tendrilMask = smoothstep(0.6, 0.9, tendrils);
      
      // Composite
      vec3 finalColor = mix(voidColor, nebulaColor, nebulaMask * 0.6); // Nebula is semi-transparent fog
      finalColor += goldColor * starMask * 2.0; // Add sparkling stars (bright!)
      finalColor += goldColor * tendrilMask * 1.5; // Add gold tendrils
      
      // Add a central core glow
      float coreGlow = 1.0 / (dist * 2.0 + 0.5);
      finalColor += uColor1 * coreGlow * 0.5;

      gl_FragColor = vec4(finalColor, 1.0);
    }
  `
};

interface ObsidianVaultProps {
  position: [number, number, number];
  onClick?: () => void;
}

export const ObsidianVault: React.FC<ObsidianVaultProps> = ({ position, onClick }) => {
  const groupRef = useRef<THREE.Group>(null);
  const coreRef = useRef<THREE.Mesh>(null);
  const [hovered, setHovered] = useState(false);

  // Generate "Tooth" Geometry (Distorted Cone)
  const toothGeometry = useMemo(() => {
    // Create a cone
    const geometry = new THREE.ConeGeometry(3, 12, 64, 16, true);
    
    // Distort vertices to make it rugged and curved
    const posAttribute = geometry.attributes.position;
    const vertex = new THREE.Vector3();
    
    for (let i = 0; i < posAttribute.count; i++) {
      vertex.fromBufferAttribute(posAttribute, i);
      
      // Bend the tooth (Curve along X based on Y)
      const bendFactor = vertex.y * 0.3;
      vertex.x += Math.pow(bendFactor, 2);
      
      // Add "rugged" noise to surface
      if (vertex.y < 5) { 
        vertex.x += (Math.random() - 0.5) * 0.3;
        vertex.z += (Math.random() - 0.5) * 0.3;
      }
      
      posAttribute.setXYZ(i, vertex.x, vertex.y, vertex.z);
    }
    
    geometry.computeVertexNormals();
    return geometry;
  }, []);

  useFrame((state) => {
    if (groupRef.current) {
      // 1. Spin the Whole Object slowly
      groupRef.current.rotation.y += 0.002; 
    }
    
    if (coreRef.current) {
      // 2. Independent Galaxy Motion
      // The shader handles the heavy lifting, but we can slowly rotate the core mesh
      // to change the viewing angle of the shader's coordinate system
      coreRef.current.rotation.y -= 0.001; 
      
      // Update shader time
      const material = coreRef.current.material as THREE.ShaderMaterial;
      material.uniforms.uTime.value = state.clock.elapsedTime;
    }
  });

  return (
    <group position={position}>
        <Float speed={2} rotationIntensity={0.2} floatIntensity={0.5}>
            <group 
                ref={groupRef}
                onPointerOver={() => {
                    setHovered(true);
                    document.body.style.cursor = 'pointer';
                }}
                onPointerOut={() => {
                    setHovered(false);
                    document.body.style.cursor = 'default';
                }}
                onClick={onClick}
            >
                {/* 1. Inner Core (The Symbiotic Galaxy Entity) */}
                <mesh ref={coreRef} geometry={toothGeometry} scale={[0.9, 0.9, 0.9]} rotation={[Math.PI, 0, 0]}>
                    <shaderMaterial args={[InternalEnergyShader]} transparent opacity={1.0} side={THREE.DoubleSide} />
                </mesh>

                {/* 2. Outer Shell (The Obsidian Crystal Ball Glass) */}
                <mesh geometry={toothGeometry} rotation={[Math.PI, 0, 0]}>
                    <meshPhysicalMaterial 
                        color="#000000"
                        metalness={1}
                        roughness={0.0} // Perfectly smooth glass
                        transmission={0.9} // Extremely clear
                        thickness={1.0}
                        clearcoat={1}
                        clearcoatRoughness={0.0}
                        ior={1.5}
                        envMapIntensity={3} 
                        attenuationColor={new THREE.Color('#2e1065')} 
                        attenuationDistance={3}
                    />
                </mesh>

                {/* Label on Hover */}
                {hovered && (
                    <Html position={[0, 4, 0]} center>
                        <div className="px-4 py-2 bg-black/80 border border-purple-500/50 rounded-lg text-purple-200 text-sm font-bold backdrop-blur-md whitespace-nowrap shadow-[0_0_15px_rgba(168,85,247,0.5)]">
                            KNOWLEDGE VAULT
                        </div>
                    </Html>
                )}
            </group>
        </Float>
        
        {/* Ambient Purple Glow */}
        <pointLight position={[0, -2, 0]} color="#a855f7" intensity={3} distance={15} />
    </group>
  );
};
