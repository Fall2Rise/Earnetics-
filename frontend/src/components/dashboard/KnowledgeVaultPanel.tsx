import React, { useState } from 'react';
import { Canvas } from '@react-three/fiber';
import { Environment, Grid } from '@react-three/drei';
import { createLibraryItem, fetchLibraryItems, LibraryItem } from '../../api/libraryApi';
import { logAuditReason } from '../../api/auditApi';
import { ObsidianVault } from '../3d/ObsidianVault';
import { KnowledgeVaultModal } from './KnowledgeVaultModal';
import { Zap, Database, Search } from 'lucide-react';

export const KnowledgeVaultPanel: React.FC = () => {
  const [items, setItems] = React.useState<LibraryItem[]>([]);
  const [error, setError] = React.useState<string | null>(null);
  const [showUploadModal, setShowUploadModal] = useState(false);
  const [loading, setLoading] = useState(true);

  const loadItems = React.useCallback(async () => {
    try {
      setLoading(true);
      const response = await fetchLibraryItems('Knowledge');
      setItems(response.items || []);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load knowledge vault');
    } finally {
      setLoading(false);
    }
  }, []);

  React.useEffect(() => {
    void loadItems();
  }, [loadItems]);

  return (
    <div className="flex flex-col h-full bg-[#030305] rounded-2xl overflow-hidden relative">
      {/* 3D Header Section - The Living Artifact */}
      <div className="relative w-full h-[400px] bg-[#050505] border-b border-purple-900/30">
        <div className="absolute inset-0 z-0">
            <Canvas camera={{ position: [0, 2, 14], fov: 45 }}>
                <color attach="background" args={['#050505']} />
                <fog attach="fog" args={['#050505', 10, 30]} />
                
                <ambientLight intensity={0.5} />
                <pointLight position={[10, 10, 10]} intensity={1} color="#a855f7" />
                <pointLight position={[-10, -10, -10]} intensity={0.5} color="#ffd700" />
                
                <Environment preset="studio" />
                
                {/* Tech Grid Floor */}
                <Grid 
                    position={[0, -6, 0]} 
                    args={[100, 100]} 
                    cellColor="#333" 
                    sectionColor="#444" 
                    fadeDistance={30} 
                    fadeStrength={1}
                />
                
                <ObsidianVault 
                    position={[0, 0, 0]} 
                    onClick={() => setShowUploadModal(true)}
                />
            </Canvas>
        </div>
        
        {/* Overlay UI */}
        <div className="absolute inset-0 pointer-events-none flex flex-col justify-between p-8 z-10">
            <div>
                <h1 className="text-4xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-purple-400 to-amber-200 tracking-wider">KNOWLEDGE VAULT</h1>
                <p className="text-purple-300/60 font-mono text-sm mt-2 max-w-md">
                    SECURE ARCHIVE // NEURAL STORAGE PROTOCOL
                    <br/>
                    Interact with the Obsidian Core to inject new intelligence.
                </p>
            </div>
            
            <div className="flex justify-center pointer-events-auto">
                <button 
                    onClick={() => setShowUploadModal(true)}
                    className="flex items-center gap-2 px-6 py-3 bg-purple-600/20 hover:bg-purple-600/40 border border-purple-500/50 hover:border-purple-400 rounded-full text-purple-200 font-bold tracking-wide transition-all backdrop-blur-md shadow-[0_0_20px_rgba(168,85,247,0.3)] hover:shadow-[0_0_30px_rgba(168,85,247,0.5)] group"
                >
                    <Zap className="w-5 h-5 text-amber-300 group-hover:animate-pulse" />
                    INJECT DATA ARTIFACT
                </button>
            </div>
        </div>
      </div>

      {/* Content Section - The Database */}
      <div className="flex-1 p-6 overflow-hidden flex flex-col">
        <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-2 text-slate-400">
                <Database className="w-4 h-4" />
                <span className="text-xs font-mono uppercase tracking-wider">Stored Knowledge Assets ({items.length})</span>
            </div>
            <div className="relative">
                <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-slate-500" />
                <input 
                    type="text" 
                    placeholder="Search neural archives..." 
                    className="bg-black/30 border border-white/10 rounded-lg pl-9 pr-4 py-1.5 text-sm text-slate-300 focus:border-purple-500/50 focus:outline-none w-64"
                />
            </div>
        </div>

        <div className="flex-1 overflow-y-auto space-y-2 pr-2">
            {loading ? (
                <div className="text-center py-12 text-slate-500 font-mono animate-pulse">Establishing neural link...</div>
            ) : items.length === 0 ? (
                <div className="text-center py-12 border border-dashed border-white/10 rounded-xl bg-white/5">
                    <p className="text-slate-400">The vault is empty.</p>
                    <p className="text-slate-600 text-sm mt-1">Upload files to begin populating the knowledge graph.</p>
                </div>
            ) : (
                items.map((item) => (
                    <div key={item.id} className="flex items-center justify-between p-4 bg-[#0f0a16] border border-purple-900/20 rounded-xl hover:border-purple-500/30 transition-all group">
                        <div className="flex items-start gap-4">
                            <div className="p-3 bg-purple-900/20 rounded-lg text-purple-400 group-hover:text-purple-300 group-hover:bg-purple-900/30 transition-colors">
                                <Database className="w-5 h-5" />
                            </div>
                            <div>
                                <h4 className="text-slate-200 font-medium group-hover:text-white transition-colors">{item.title}</h4>
                                {item.description && <p className="text-sm text-slate-500 mt-0.5 line-clamp-1">{item.description}</p>}
                                <div className="flex gap-2 mt-2">
                                    <span className="text-[10px] px-2 py-0.5 rounded bg-white/5 text-slate-400 border border-white/5">
                                        {item.category || 'General'}
                                    </span>
                                    <span className="text-[10px] px-2 py-0.5 rounded bg-white/5 text-slate-400 border border-white/5">
                                        {new Date(item.last_updated || Date.now()).toLocaleDateString()}
                                    </span>
                                </div>
                            </div>
                        </div>
                        <button className="px-3 py-1.5 text-xs font-medium text-slate-400 hover:text-white border border-white/10 hover:border-white/30 rounded-lg transition-all">
                            ACCESS
                        </button>
                    </div>
                ))
            )}
        </div>
      </div>

      {showUploadModal && (
        <KnowledgeVaultModal onClose={() => setShowUploadModal(false)} />
      )}
    </div>
  );
};
