import React, { useState } from 'react';
import { Play, Pause, SkipBack, SkipForward } from 'lucide-react';

export const Timeline = () => {
    const [isPlaying, setIsPlaying] = useState(false);
    const [progress, setProgress] = useState(100);

    return (
        <div className="bg-gray-900 border-t border-gray-800 p-2 flex items-center gap-4">
            <div className="flex items-center gap-2">
                <button className="p-1 hover:bg-gray-800 rounded text-gray-400 hover:text-white">
                    <SkipBack size={16} />
                </button>
                <button
                    className="p-1 hover:bg-gray-800 rounded text-green-500 hover:text-green-400"
                    onClick={() => setIsPlaying(!isPlaying)}
                >
                    {isPlaying ? <Pause size={16} /> : <Play size={16} />}
                </button>
                <button className="p-1 hover:bg-gray-800 rounded text-gray-400 hover:text-white">
                    <SkipForward size={16} />
                </button>
            </div>

            <div className="flex-1 flex flex-col justify-center">
                <div className="flex justify-between text-[10px] text-gray-500 mb-1 uppercase tracking-wider">
                    <span>00:00:00</span>
                    <span>Live</span>
                </div>
                <input
                    type="range"
                    min="0"
                    max="100"
                    value={progress}
                    onChange={(e) => setProgress(Number(e.target.value))}
                    className="w-full h-1 bg-gray-800 rounded-lg appearance-none cursor-pointer accent-green-500"
                />
            </div>

            <div className="text-xs font-mono text-green-500 w-16 text-right">
                {progress === 100 ? 'LIVE' : `-${100 - progress}m`}
            </div>
        </div>
    );
};
