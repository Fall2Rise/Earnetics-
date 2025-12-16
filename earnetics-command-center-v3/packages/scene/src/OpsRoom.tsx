import React, { useRef } from 'react';
import { Canvas, useFrame } from '@react-three/fiber';
import { OrbitControls, PerspectiveCamera, Stars, Grid } from '@react-three/drei';
import * as THREE from 'three';

const HoloTable = () => {
    const meshRef = useRef<THREE.Mesh>(null);
    const [departments, setDepartments] = React.useState<string[]>([]);

    React.useEffect(() => {
        // @ts-ignore
        window.api?.getDepartments().then(setDepartments);

        // Listen for updates
        // @ts-ignore
        const cleanup = window.api?.onNewEvent((event: any) => {
            if (event.type === 'SYSTEM_READY') {
                // @ts-ignore
                window.api?.getDepartments().then(setDepartments);
            }
        });
        return cleanup;
    }, []);

    useFrame((state, delta) => {
        if (meshRef.current) {
            meshRef.current.rotation.y += delta * 0.1;
        }
    });

    return (
        <group position={[0, 0, 0]}>
            {/* Table Base */}
            <mesh position={[0, -0.5, 0]}>
                <cylinderGeometry args={[4, 4, 0.5, 32]} />
                <meshStandardMaterial color="#1a1a1a" metalness={0.8} roughness={0.2} />
            </mesh>

            {/* Holographic Projection */}
            <mesh ref={meshRef} position={[0, 1, 0]}>
                <sphereGeometry args={[1.5, 32, 32]} />
                <meshStandardMaterial color="#00ff88" wireframe transparent opacity={0.3} />
            </mesh>

            {/* Department Orbs */}
            {departments.map((dept, i) => {
                const angle = (i / departments.length) * Math.PI * 2;
                const x = Math.cos(angle) * 3;
                const z = Math.sin(angle) * 3;
                return (
                    <mesh key={dept} position={[x, 0.5, z]}>
                        <sphereGeometry args={[0.3, 16, 16]} />
                        <meshStandardMaterial color="#0080ff" emissive="#0080ff" emissiveIntensity={0.5} />
                    </mesh>
                );
            })}
        </group>
    );
};

export const OpsRoom = () => {
    return (
        <div className="w-full h-full bg-black">
            <Canvas>
                <PerspectiveCamera makeDefault position={[0, 5, 10]} />
                <OrbitControls enablePan={false} maxPolarAngle={Math.PI / 2} />

                <ambientLight intensity={0.2} />
                <pointLight position={[10, 10, 10]} intensity={1} />
                <spotLight position={[0, 10, 0]} angle={0.5} penumbra={1} intensity={2} castShadow />

                <Stars radius={100} depth={50} count={5000} factor={4} saturation={0} fade speed={1} />
                <Grid infiniteGrid fadeDistance={30} sectionColor="#00ff88" cellColor="#1a1a1a" />

                <HoloTable />
            </Canvas>
        </div>
    );
};
