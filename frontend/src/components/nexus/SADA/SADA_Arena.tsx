import React, { useEffect } from 'react';
import { Canvas } from '@react-three/fiber';
import { OrbitControls, Stars } from '@react-three/drei';
import { AgentUnit } from './AgentUnit';
import { useAgentStore } from '../../../stores/agentStore';
import { SovereignHUD } from '../SovereignHUD';
import { EarneticsSigil } from './environment/EarneticsSigil';
import { FactoryFloor } from './environment/FactoryFloor';
import { FinanceZone } from './zones/FinanceZone';
import { LegalZone } from './zones/LegalZone';

export const SADA_Arena: React.FC = () => {
    const { agents, fetchAgents } = useAgentStore();

    useEffect(() => {
        void fetchAgents();
    }, [fetchAgents]);

    return (
        <div className="w-full h-screen bg-black relative">
            <SovereignHUD />
            <div className="absolute top-4 left-4 z-10 pointer-events-none">
                <h2 className="text-cyan-500 font-mono text-xl tracking-widest border-l-4 border-cyan-500 pl-4 bg-black/50 backdrop-blur-sm p-2">
                    S.A.D.A. // SPATIAL AGENT DEPLOYMENT ARENA
                </h2>
            </div>

            <Canvas camera={{ position: [0, 15, 25], fov: 45 }} shadows>
                <color attach="background" args={['#020202']} />
                <fog attach="fog" args={['#020202', 20, 80]} />

                {/* Factory Lighting - Dim & Dramatic */}
                <ambientLight intensity={0.2} />
                <pointLight position={[0, 10, 0]} intensity={1.5} color="#00ffff" distance={30} castShadow />
                <spotLight position={[30, 30, 20]} angle={0.3} penumbra={1} intensity={1} color="#ffd700" castShadow />
                <spotLight position={[-30, 30, -20]} angle={0.3} penumbra={1} intensity={0.5} color="#0044ff" castShadow />

                {/* Environment */}
                <Stars radius={100} depth={50} count={3000} factor={4} saturation={0} fade speed={0.5} />
                <FactoryFloor />
                <EarneticsSigil />

                {/* Department Zones */}
                <FinanceZone position={[15, 0, 5]} />
                <LegalZone position={[5, 0, -15]} />

                {/* Deploy Real Agents */}
                {agents.map((agent) => {
                    // Map store status to visual status
                    let visualStatus: 'active' | 'idle' | 'alert' = 'idle';
                    if (agent.status === 'active') visualStatus = 'active';
                    if (agent.status === 'error') visualStatus = 'alert';

                    return (
                        <AgentUnit
                            key={agent.id}
                            position={agent.position}
                            name={agent.name}
                            role={agent.role}
                            status={visualStatus}
                            onClick={() => console.log(`Selected ${agent.name}`)}
                        />
                    );
                })}

                <OrbitControls makeDefault maxPolarAngle={Math.PI / 2.1} minDistance={5} maxDistance={50} />
            </Canvas>
        </div>
    );
};
