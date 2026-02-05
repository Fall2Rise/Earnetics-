import React, { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Send, Mic, MicOff, Terminal, X, Maximize2, Minimize2 } from 'lucide-react';
import { useAgentStore } from '../../stores/agentStore';
import { API_BASE_URL } from '../../api/config';

interface Message {
    id: string;
    text: string;
    sender: 'user' | 'atom';
    timestamp: Date;
}

export const AssistantConsole: React.FC = () => {
    const [isOpen, setIsOpen] = useState(false);
    const [isMinimized, setIsMinimized] = useState(false);
    const [isMaximized, setIsMaximized] = useState(false);
    const [input, setInput] = useState('');
    const [messages, setMessages] = useState<Message[]>([
        {
            id: '1',
            text: 'Welcome to the ATOM Command Interface. I am ATOM, your Chief Architect. How can I assist you in optimizing the corporation today?',
            sender: 'atom',
            timestamp: new Date(),
        },
    ]);
    const [isTyping, setIsTyping] = useState(false);
    const scrollRef = useRef<HTMLDivElement>(null);
    const { socket } = useAgentStore();
    const [isListening, setIsListening] = useState(false);
    const [recognition, setRecognition] = useState<any>(null);

    useEffect(() => {
        if (scrollRef.current) {
            scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
        }
    }, [messages]);

    useEffect(() => {
        if (!socket) return;

        const handleMessage = (event: MessageEvent) => {
            try {
                const data = JSON.parse(event.data);
                if (data.type === 'atom_response') {
                    addMessage(data.message, 'atom');
                    // Play voice if audio URL is provided
                    if (data.audio_url) {
                        console.log('[ATOM] 🎤 Audio URL from WebSocket, attempting to play:', data.audio_url);
                        playAtomVoice(data.audio_url);
                    } else {
                        console.warn('[ATOM] ⚠️ No audio_url in WebSocket message');
                    }
                }
            } catch (err) {
                console.error('Failed to parse WS message in console:', err);
            }
        };

        socket.addEventListener('message', handleMessage);
        return () => socket.removeEventListener('message', handleMessage);
    }, [socket]);

    useEffect(() => {
        const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
        if (SpeechRecognition) {
            const recognitionInstance = new SpeechRecognition();
            recognitionInstance.continuous = false;
            recognitionInstance.interimResults = true;
            recognitionInstance.lang = 'en-US';

            recognitionInstance.onresult = (event: any) => {
                const transcript = event.results[0][0].transcript;
                setInput(transcript);
                if (event.results[0].isFinal) {
                    setIsListening(false);
                }
            };

            recognitionInstance.onerror = () => setIsListening(false);
            recognitionInstance.onend = () => setIsListening(false);
            setRecognition(recognitionInstance);
        }
    }, []);

    const toggleListening = () => {
        if (!recognition) return;
        if (isListening) {
            recognition.stop();
        } else {
            recognition.start();
            setIsListening(true);
        }
    };

    const addMessage = (text: string, sender: 'user' | 'atom') => {
        const newMessage: Message = {
            id: Math.random().toString(36).substr(2, 9),
            text,
            sender,
            timestamp: new Date(),
        };
        setMessages((prev) => [...prev, newMessage]);
    };

    const playAtomVoice = (audioUrl: string) => {
        try {
            // Use absolute URL if relative
            let url = audioUrl;
            if (!url.startsWith('http')) {
                const baseUrl = import.meta.env?.VITE_API_BASE_URL || 'http://127.0.0.1:8000';
                url = baseUrl + (url.startsWith('/') ? url : '/' + url);
            }
            
            console.log('[ATOM] 🎤 Playing voice from URL:', url);
            console.log('[ATOM] Original audioUrl:', audioUrl);
            
            const audio = new Audio(url);
            audio.volume = 0.8; // Slightly lower volume for comfortable listening
            
            // Add event listeners for debugging
            audio.addEventListener('loadstart', () => {
                console.log('[ATOM] ✅ Audio loading started');
            });
            audio.addEventListener('loadeddata', () => {
                console.log('[ATOM] ✅ Audio data loaded');
            });
            audio.addEventListener('canplay', () => {
                console.log('[ATOM] ✅ Audio can play - ready to start');
            });
            audio.addEventListener('play', () => {
                console.log('[ATOM] 🎵 Audio playback STARTED!');
            });
            audio.addEventListener('playing', () => {
                console.log('[ATOM] 🎵 Audio is currently playing!');
            });
            audio.addEventListener('pause', () => {
                console.log('[ATOM] ⏸️ Audio paused');
            });
            audio.addEventListener('ended', () => {
                console.log('[ATOM] ✅ Audio playback completed');
            });
            audio.addEventListener('error', (e) => {
                console.error('[ATOM] ❌ Audio error event:', e);
                console.error('[ATOM] Audio error code:', audio.error?.code);
                console.error('[ATOM] Audio error message:', audio.error?.message);
                console.error('[ATOM] Audio src:', audio.src);
            });
            
            // Preload audio
            audio.preload = 'auto';
            
            // Play audio - browsers require user interaction first
            const playPromise = audio.play();
            if (playPromise !== undefined) {
                playPromise
                    .then(() => {
                        console.log('[ATOM] ✅ Voice playback promise resolved - audio should be playing!');
                    })
                    .catch(err => {
                        console.error('[ATOM] ❌ Audio play promise rejected:', err);
                        console.error('[ATOM] Error name:', err.name);
                        console.error('[ATOM] Error message:', err.message);
                        if (err.name === 'NotAllowedError') {
                            console.warn('[ATOM] ⚠️ Browser blocked autoplay - user must interact with page first');
                            // Try to show a notification or button to play manually
                        } else if (err.name === 'NotSupportedError') {
                            console.error('[ATOM] ❌ Audio format not supported');
                        } else {
                            console.error('[ATOM] ❌ Unknown audio error:', err);
                        }
                    });
            } else {
                console.warn('[ATOM] ⚠️ audio.play() returned undefined');
            }
        } catch (err) {
            console.error('[ATOM] ❌ Error creating audio object:', err);
        }
    };

    const handleSend = async () => {
        if (!input.trim()) return;

        const userMessage = input.trim();
        setInput('');
        addMessage(userMessage, 'user');
        setIsTyping(true);

        try {
            // Use relative URL (Vite proxy handles it) or explicit VITE_API_BASE_URL
            const apiUrl = import.meta.env?.VITE_API_BASE_URL || API_BASE_URL || '';
            const url = apiUrl ? `${apiUrl}/api/atom/chat` : '/api/atom/chat';
            console.log('[ATOM] Sending message to:', url);
            
            const response = await fetch(url, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ 
                    message: userMessage,
                    enable_voice: true  // Explicitly enable voice
                }),
            });

            console.log('[ATOM] Response:', response.status, response.statusText);
            
            if (!response.ok) {
                const errorText = await response.text();
                console.error('[ATOM] Error response:', errorText);
                addMessage(`Error: ${errorText || 'Failed to reach ATOM'}`, 'atom');
                return;
            }

            const data = await response.json();
            console.log('[ATOM] Data received:', data);
            console.log('[ATOM] Audio URL in response:', data.audio_url);
            
            if (data.status === 'ok') {
                const responseText = data.response || '';
                addMessage(responseText, 'atom');
                
                // Play voice response if audio URL is provided
                if (data.audio_url) {
                    console.log('[ATOM] 🎤 Audio URL found, attempting to play:', data.audio_url);
                    playAtomVoice(data.audio_url);
                } else {
                    console.warn('[ATOM] ⚠️ No audio_url in response. Response keys:', Object.keys(data));
                }
            } else {
                addMessage(`Error: ${data.message || 'Failed to reach ATOM'}`, 'atom');
            }
        } catch (err) {
            console.error('[ATOM] Fetch error:', err);
            addMessage(`System Error: ATOM core is unreachable. ${err instanceof Error ? err.message : ''}`, 'atom');
        } finally {
            setIsTyping(false);
        }
    };

    return (
        <div className={`fixed bottom-6 left-6 z-50 transition-all duration-500 ${isMaximized ? 'w-[600px] h-[800px]' : isMinimized ? 'w-96 h-12' : 'w-96 h-[500px]'} ${!isOpen && 'h-12 w-48'}`}>
            <AnimatePresence>
                {!isOpen ? (
                    <motion.button
                        initial={{ y: 20, opacity: 0 }}
                        animate={{ y: 0, opacity: 1 }}
                        onClick={() => {
                            setIsOpen(true);
                            setIsMinimized(false);
                        }}
                        className="w-full h-full bg-cyan-500/20 backdrop-blur-xl border border-cyan-500/50 rounded-xl flex items-center justify-center gap-2 text-cyan-400 font-bold hover:bg-cyan-500/30 transition-all shadow-lg shadow-cyan-500/20"
                    >
                        <Terminal size={18} />
                        <span>ATOM CONSOLE</span>
                    </motion.button>
                ) : isMinimized ? (
                    <motion.div
                        initial={{ scale: 0.9, opacity: 0 }}
                        animate={{ scale: 1, opacity: 1 }}
                        exit={{ scale: 0.9, opacity: 0 }}
                        className="w-full h-full bg-slate-950/90 backdrop-blur-2xl border border-cyan-500/30 rounded-2xl flex items-center justify-between px-4 shadow-2xl shadow-black"
                    >
                        <div className="flex items-center gap-2">
                            <div className="w-2 h-2 rounded-full bg-cyan-500 animate-pulse" />
                            <span className="text-xs font-bold text-cyan-400 tracking-widest uppercase">Atom Master Interface</span>
                            {messages.length > 1 && (
                                <span className="text-xs text-gray-400">({messages.length - 1} messages)</span>
                            )}
                        </div>
                        <div className="flex items-center gap-2">
                            <button 
                                onClick={() => setIsMinimized(false)} 
                                className="text-gray-400 hover:text-white transition-colors"
                                title="Restore"
                            >
                                <Maximize2 size={16} />
                            </button>
                            <button 
                                onClick={() => setIsOpen(false)} 
                                className="text-gray-400 hover:text-white transition-colors"
                                title="Close"
                            >
                                <X size={16} />
                            </button>
                        </div>
                    </motion.div>
                ) : (
                    <motion.div
                        initial={{ scale: 0.9, opacity: 0 }}
                        animate={{ scale: 1, opacity: 1 }}
                        exit={{ scale: 0.9, opacity: 0 }}
                        className="w-full h-full bg-slate-950/90 backdrop-blur-2xl border border-cyan-500/30 rounded-2xl flex flex-col shadow-2xl shadow-black"
                    >
                        {/* Header */}
                        <div className="p-4 border-b border-cyan-500/20 flex items-center justify-between bg-cyan-500/5">
                            <div className="flex items-center gap-2">
                                <div className="w-2 h-2 rounded-full bg-cyan-500 animate-pulse" />
                                <span className="text-xs font-bold text-cyan-400 tracking-widest uppercase">Atom Master Interface</span>
                            </div>
                            <div className="flex items-center gap-2">
                                <button 
                                    onClick={() => setIsMinimized(true)} 
                                    className="text-gray-400 hover:text-white transition-colors"
                                    title="Minimize"
                                >
                                    <Minimize2 size={16} />
                                </button>
                                <button 
                                    onClick={() => setIsMaximized(!isMaximized)} 
                                    className="text-gray-400 hover:text-white transition-colors"
                                    title={isMaximized ? "Restore" : "Maximize"}
                                >
                                    {isMaximized ? <Minimize2 size={16} /> : <Maximize2 size={16} />}
                                </button>
                                <button 
                                    onClick={() => setIsOpen(false)} 
                                    className="text-gray-400 hover:text-white transition-colors"
                                    title="Close"
                                >
                                    <X size={16} />
                                </button>
                            </div>
                        </div>

                        {/* Messages */}
                        <div ref={scrollRef} className="flex-1 overflow-y-auto p-4 space-y-4 custom-scrollbar">
                            {messages.map((msg) => (
                                <motion.div
                                    key={msg.id}
                                    initial={{ x: msg.sender === 'user' ? 20 : -20, opacity: 0 }}
                                    animate={{ x: 0, opacity: 1 }}
                                    className={`flex ${msg.sender === 'user' ? 'justify-end' : 'justify-start'}`}
                                >
                                    <div className={`max-w-[85%] p-3 rounded-2xl text-sm ${msg.sender === 'user'
                                            ? 'bg-cyan-600/20 border border-cyan-500/30 text-white rounded-tr-none'
                                            : 'bg-slate-800/50 border border-slate-700 text-cyan-50 rounded-tl-none'
                                        }`}>
                                        {msg.text}
                                        <div className="text-[10px] opacity-40 mt-1">
                                            {msg.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                                        </div>
                                    </div>
                                </motion.div>
                            ))}
                            {isTyping && (
                                <div className="flex justify-start">
                                    <div className="bg-slate-800/50 border border-slate-700 p-3 rounded-2xl rounded-tl-none">
                                        <div className="flex gap-1">
                                            <div className="w-1.5 h-1.5 bg-cyan-500 rounded-full animate-bounce" />
                                            <div className="w-1.5 h-1.5 bg-cyan-500 rounded-full animate-bounce [animation-delay:0.2s]" />
                                            <div className="w-1.5 h-1.5 bg-cyan-500 rounded-full animate-bounce [animation-delay:0.4s]" />
                                        </div>
                                    </div>
                                </div>
                            )}
                        </div>

                        {/* Input */}
                        <div className="p-4 border-t border-cyan-500/20 bg-black/40">
                            <div className="relative flex items-center gap-2">
                                <input
                                    type="text"
                                    value={input}
                                    onChange={(e) => setInput(e.target.value)}
                                    onKeyPress={(e) => e.key === 'Enter' && handleSend()}
                                    placeholder={isListening ? "Listening..." : "Enter directive for ATOM..."}
                                    className={`w-full bg-slate-900/50 border rounded-xl py-3 pl-4 pr-12 text-sm text-white focus:outline-none transition-all ${isListening ? 'border-red-500/50 shadow-[0_0_10px_rgba(239,68,68,0.2)]' : 'border-cyan-500/20 focus:border-cyan-500/50'
                                        }`}
                                />
                                <button
                                    onClick={handleSend}
                                    className="absolute right-2 p-2 text-cyan-400 hover:text-cyan-300 transition-colors"
                                >
                                    <Send size={18} />
                                </button>
                            </div>
                            <div className="mt-2 flex items-center justify-between text-[10px] text-gray-500 uppercase tracking-tighter">
                                <span>Secure Presidential Link Active</span>
                                <div className="flex items-center gap-2">
                                    <button
                                        onClick={toggleListening}
                                        className={`transition-colors flex items-center gap-1 ${isListening ? 'text-red-400 animate-pulse' : 'hover:text-cyan-400'}`}
                                    >
                                        {isListening ? <MicOff size={10} /> : <Mic size={10} />}
                                        {isListening ? 'STOP LISTENING' : 'VOICE MODE'}
                                    </button>
                                </div>
                            </div>
                        </div>
                    </motion.div>
                )}
            </AnimatePresence>
        </div>
    );
};
