import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

interface BootloaderProps {
    onComplete: () => void;
}

export const NexusBootloader: React.FC<BootloaderProps> = ({ onComplete }) => {
    const [step, setStep] = useState<number>(0);
    const [log, setLog] = useState<string[]>([]);

    const bootSequence = [
        "INITIALIZING SOVEREIGN KERNEL...",
        "VERIFYING FALLAT DYNASTY SIGNATURES...",
        "LOADING PRIME DIRECTIVE ENFORCER...",
        "ESTABLISHING SECURE MEMORY VAULT...",
        "CONNECTING TO SPATIAL AGENT ARENA...",
        "ACCESS GRANTED."
    ];

    useEffect(() => {
        let delay = 500;
        let currentStep = 0;

        const runSequence = async () => {
            for (const msg of bootSequence) {
                await new Promise(r => setTimeout(r, delay));
                setLog(prev => [...prev, msg]);
                delay = Math.max(100, delay - 50); // Speed up
                currentStep++;
                setStep(currentStep);
            }
            setTimeout(onComplete, 800);
        };

        runSequence();
    }, [onComplete]);

    return (
        <div className="fixed inset-0 bg-black text-cyan-500 font-mono flex flex-col items-center justify-center z-50 overflow-hidden">
            <div className="absolute inset-0 bg-[url('/grid.png')] opacity-10 pointer-events-none"></div>

            <div className="w-full max-w-2xl p-8 border border-cyan-900/50 bg-black/80 backdrop-blur-sm rounded-lg relative">
                <div className="absolute top-0 left-0 w-2 h-2 border-t border-l border-cyan-500"></div>
                <div className="absolute top-0 right-0 w-2 h-2 border-t border-r border-cyan-500"></div>
                <div className="absolute bottom-0 left-0 w-2 h-2 border-b border-l border-cyan-500"></div>
                <div className="absolute bottom-0 right-0 w-2 h-2 border-b border-r border-cyan-500"></div>

                {/* BOOT LOGO PLACEHOLDER */}
                <div className="mb-8 flex justify-center">
                    <div className="w-24 h-24 border-2 border-dashed border-cyan-900/50 rounded-full flex items-center justify-center animate-pulse">
                        <span className="text-[10px] text-cyan-700">LOGO_SLOT</span>
                    </div>
                </div>

                <h1 className="text-3xl font-bold mb-8 text-center tracking-[0.5em] text-white glow-text">
                    EARNETICS INTELLIGENCE ARENA
                </h1>

                <div className="space-y-2 font-xs h-64 overflow-y-auto scrollbar-hide">
                    <AnimatePresence>
                        {log.map((msg, i) => (
                            <motion.div
                                key={i}
                                initial={{ opacity: 0, x: -20 }}
                                animate={{ opacity: 1, x: 0 }}
                                className="flex items-center gap-3"
                            >
                                <span className="text-cyan-700">{`>`}</span>
                                <span className={i === log.length - 1 ? "text-white" : "text-cyan-400/70"}>
                                    {msg}
                                </span>
                                {i === log.length - 1 && (
                                    <span className="animate-pulse inline-block w-2 h-4 bg-cyan-500 ml-2" />
                                )}
                            </motion.div>
                        ))}
                    </AnimatePresence>
                </div>

                <div className="mt-8 border-t border-cyan-900/50 pt-4 flex justify-between items-center text-xs text-cyan-700 uppercase">
                    <span>Sovereign Mode: ACTIVE</span>
                    <span>Encryption: ED25519-GCM</span>
                </div>
            </div>
        </div>
    );
};
