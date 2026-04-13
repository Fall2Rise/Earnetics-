import React, { useState, useCallback } from 'react';
import { X, Upload, FileText, Database, Shield, Zap, CheckCircle, Loader } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

interface KnowledgeVaultModalProps {
  onClose: () => void;
}

export const KnowledgeVaultModal: React.FC<KnowledgeVaultModalProps> = ({ onClose }) => {
  const [dragActive, setDragActive] = useState(false);
  const [files, setFiles] = useState<File[]>([]);
  const [processing, setProcessing] = useState(false);
  const [results, setResults] = useState<Array<{ name: string; type: string; destination: string }>>([]);

  const handleDrag = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  }, []);

  const simulateProcessing = async (fileList: File[]) => {
    setProcessing(true);
    // Simulate AI analysis time
    await new Promise(resolve => setTimeout(resolve, 2500));
    
    const newResults = fileList.map(file => {
      // Mock logic for "determining information type"
      let type = "General Knowledge";
      let destination = "Corporate Archive";
      
      const name = file.name.toLowerCase();
      if (name.includes('revenue') || name.includes('strategy') || name.includes('plan')) {
        type = "Revenue Strategy";
        destination = "Executive Directives DB";
      } else if (name.includes('agent') || name.includes('bot') || name.includes('prompt')) {
        type = "Agent Protocol";
        destination = "Agent DNA Registry";
      } else if (name.includes('lead') || name.includes('list') || name.includes('data')) {
        type = "Raw Intelligence";
        destination = "Data Monetization Engine";
      }

      return { name: file.name, type, destination };
    });

    setResults(newResults);
    setProcessing(false);
  };

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      const fileList = Array.from(e.dataTransfer.files);
      setFiles(fileList);
      simulateProcessing(fileList);
    }
  }, []);

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm p-4">
      <motion.div 
        initial={{ scale: 0.9, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        exit={{ scale: 0.9, opacity: 0 }}
        className="w-full max-w-2xl bg-[#0a0510] border border-purple-900/50 rounded-2xl overflow-hidden shadow-[0_0_50px_rgba(75,0,130,0.3)]"
      >
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-purple-900/30 bg-gradient-to-r from-[#1a0b2e] to-[#0a0510]">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-purple-900/20 rounded-lg border border-purple-500/30">
              <Database className="w-6 h-6 text-purple-400" />
            </div>
            <div>
              <h2 className="text-xl font-bold text-white tracking-wider">KNOWLEDGE VAULT</h2>
              <p className="text-xs text-purple-400/60 font-mono">SECURE ARCHIVE // OBSIDIAN PROTOCOL</p>
            </div>
          </div>
          <button onClick={onClose} className="text-gray-400 hover:text-white transition-colors">
            <X className="w-6 h-6" />
          </button>
        </div>

        {/* Body */}
        <div className="p-8">
          
          {!files.length && (
            <div 
              className={`relative border-2 border-dashed rounded-xl p-12 flex flex-col items-center justify-center transition-all ${
                dragActive ? 'border-purple-400 bg-purple-900/20' : 'border-purple-900/30 hover:border-purple-700/50 hover:bg-purple-900/5'
              }`}
              onDragEnter={handleDrag}
              onDragLeave={handleDrag}
              onDragOver={handleDrag}
              onDrop={handleDrop}
            >
              <div className="w-20 h-20 mb-6 rounded-full bg-[#1a0b2e] flex items-center justify-center border border-purple-500/20 shadow-[0_0_30px_rgba(168,85,247,0.15)] group-hover:scale-110 transition-transform duration-300">
                <Upload className="w-10 h-10 text-purple-400" />
              </div>
              <h3 className="text-lg font-semibold text-white mb-2">Inject Knowledge Artifacts</h3>
              <p className="text-purple-300/50 text-center max-w-sm">
                Drag and drop documents, strategies, or datasets here. 
                The Obsidian Core will analyze and route them to the neural network.
              </p>
            </div>
          )}

          {/* Processing State */}
          <AnimatePresence>
            {processing && (
              <motion.div 
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className="flex flex-col items-center py-12"
              >
                <div className="relative w-24 h-24 mb-6">
                  <div className="absolute inset-0 border-4 border-purple-900 rounded-full"></div>
                  <div className="absolute inset-0 border-t-4 border-purple-500 rounded-full animate-spin"></div>
                  <div className="absolute inset-0 flex items-center justify-center">
                    <Zap className="w-8 h-8 text-yellow-400 animate-pulse" />
                  </div>
                </div>
                <h3 className="text-xl font-mono text-purple-200 animate-pulse">ANALYZING CONTENT STRUCTURE...</h3>
                <p className="text-sm text-purple-500 mt-2">Determining optimal neural pathways</p>
              </motion.div>
            )}
          </AnimatePresence>

          {/* Results State */}
          {results.length > 0 && !processing && (
            <div className="space-y-4">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-sm font-bold text-white uppercase tracking-wider">Ingestion Report</h3>
                <span className="text-xs text-green-400 font-mono flex items-center gap-1">
                  <CheckCircle className="w-3 h-3" /> SYSTEM SYNCED
                </span>
              </div>
              
              <div className="space-y-3">
                {results.map((res, idx) => (
                  <motion.div 
                    key={idx}
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: idx * 0.1 }}
                    className="flex items-center justify-between p-4 bg-[#130820] border border-purple-900/30 rounded-lg group hover:border-purple-500/50 transition-colors"
                  >
                    <div className="flex items-center gap-4">
                      <div className="p-2 bg-purple-500/10 rounded">
                        <FileText className="w-5 h-5 text-purple-300" />
                      </div>
                      <div>
                        <p className="text-white font-medium">{res.name}</p>
                        <p className="text-xs text-purple-400/60 font-mono">DETECTED: {res.type}</p>
                      </div>
                    </div>
                    <div className="text-right">
                      <div className="text-[10px] text-purple-500 uppercase font-bold tracking-wider mb-1">ROUTED TO</div>
                      <div className="inline-flex items-center gap-1.5 px-3 py-1 bg-purple-900/40 rounded border border-purple-500/20 text-purple-200 text-xs">
                        <Shield className="w-3 h-3" />
                        {res.destination}
                      </div>
                    </div>
                  </motion.div>
                ))}
              </div>

              <div className="mt-8 flex justify-end">
                <button 
                  onClick={() => { setFiles([]); setResults([]); }}
                  className="px-6 py-2 bg-purple-600 hover:bg-purple-500 text-white font-bold rounded-lg transition-colors shadow-lg shadow-purple-900/20"
                >
                  PROCESS MORE
                </button>
              </div>
            </div>
          )}

        </div>
      </motion.div>
    </div>
  );
};
