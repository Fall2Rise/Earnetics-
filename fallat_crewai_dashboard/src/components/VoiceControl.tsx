import React, { useState, useEffect, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Mic, MicOff } from 'lucide-react';
import { useAgentStore } from '../stores/agentStore';

interface VoiceControlProps {
  onCommand: (command: string, params?: any) => void;
}

export const VoiceControl: React.FC<VoiceControlProps> = ({ onCommand }) => {
  const [isListening, setIsListening] = useState(false);
  const [transcript, setTranscript] = useState('');
  const [recognition, setRecognition] = useState<any>(null);
  const [supported, setSupported] = useState(true);
  const { agents } = useAgentStore();

  useEffect(() => {
    const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
    
    if (!SpeechRecognition) {
      setSupported(false);
      return;
    }

    const recognitionInstance = new SpeechRecognition();
    recognitionInstance.continuous = true;
    recognitionInstance.interimResults = true;
    recognitionInstance.lang = 'en-US';

    recognitionInstance.onresult = (event: any) => {
      const current = event.resultIndex;
      const transcriptText = event.results[current][0].transcript;
      setTranscript(transcriptText);

      if (event.results[current].isFinal) {
        processCommand(transcriptText.toLowerCase());
      }
    };

    recognitionInstance.onerror = (event: any) => {
      console.error('Speech recognition error:', event.error);
      setIsListening(false);
    };

    recognitionInstance.onend = () => {
      if (isListening) {
        recognitionInstance.start();
      }
    };

    setRecognition(recognitionInstance);

    return () => {
      if (recognitionInstance) {
        recognitionInstance.stop();
      }
    };
  }, []);

  const processCommand = useCallback((command: string) => {
    if (command.includes('show agent')) {
      const agentName = command.replace('show agent', '').trim();
      const agent = agents.find(a => 
        a.name.toLowerCase().includes(agentName) || 
        a.id.toLowerCase().includes(agentName)
      );
      if (agent) {
        onCommand('focus_agent', { agent });
      }
    } else if (command.includes('pause all') && command.includes('finance')) {
      onCommand('pause_division', { division: 'Finance & Revenue' });
    } else if (command.includes('pause all')) {
      const division = command.replace('pause all', '').trim();
      onCommand('pause_division', { division });
    } else if (command.includes('status report')) {
      onCommand('status_report');
    } else if (command.includes('zoom in')) {
      onCommand('zoom_in');
    } else if (command.includes('zoom out')) {
      onCommand('zoom_out');
    } else if (command.includes('reset view')) {
      onCommand('reset_view');
    } else if (command.includes('show all agents')) {
      onCommand('show_all_agents');
    }
    
    setTranscript('');
  }, [agents, onCommand]);

  const toggleListening = () => {
    if (!recognition) return;

    if (isListening) {
      recognition.stop();
      setIsListening(false);
      setTranscript('');
    } else {
      recognition.start();
      setIsListening(true);
    }
  };

  if (!supported) {
    return null;
  }

  return (
    <div className="fixed bottom-24 right-6 z-20">
      <motion.button
        onClick={toggleListening}
        className={`relative p-4 rounded-full backdrop-blur-md border-2 transition-all ${
          isListening
            ? 'bg-red-500/20 border-red-500 shadow-lg shadow-red-500/50'
            : 'bg-cyan-500/20 border-cyan-500 hover:bg-cyan-500/30'
        }`}
        whileHover={{ scale: 1.1 }}
        whileTap={{ scale: 0.95 }}
      >
        {isListening ? (
          <MicOff className="w-6 h-6 text-red-400" />
        ) : (
          <Mic className="w-6 h-6 text-cyan-400" />
        )}
        
        {isListening && (
          <motion.div
            className="absolute inset-0 rounded-full border-2 border-red-500"
            animate={{
              scale: [1, 1.5, 1],
              opacity: [1, 0, 1],
            }}
            transition={{
              duration: 2,
              repeat: Infinity,
              ease: "easeInOut",
            }}
          />
        )}
      </motion.button>

      <AnimatePresence>
        {transcript && (
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: 10 }}
            className="absolute bottom-full right-0 mb-2 bg-black/90 backdrop-blur-md border border-cyan-500/30 rounded-lg px-4 py-2 min-w-[200px]"
          >
            <div className="text-xs text-gray-400 mb-1">Listening...</div>
            <div className="text-sm text-white">{transcript}</div>
          </motion.div>
        )}
      </AnimatePresence>

      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        className="absolute bottom-full right-0 mb-16 bg-black/80 backdrop-blur-md border border-cyan-500/20 rounded-lg p-3 w-64"
      >
        <div className="text-xs text-cyan-400 font-bold mb-2">Voice Commands:</div>
        <div className="space-y-1 text-xs text-gray-300">
          <div>• "Show agent [name]"</div>
          <div>• "Pause all [division]"</div>
          <div>• "Status report"</div>
          <div>• "Zoom in/out"</div>
          <div>• "Reset view"</div>
        </div>
      </motion.div>
    </div>
  );
};
