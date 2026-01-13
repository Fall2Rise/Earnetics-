import React, { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Send, Mic, MicOff, Terminal, X, Maximize2, Minimize2 } from 'lucide-react';
import { useAgentStore } from '../../stores/agentStore';

interface Message {
    id: string;
    text: string;
    sender: 'user' | 'atom';
    timestamp: Date;
}

export const AssistantConsole: React.FC = () => {
    const [isOpen, setIsOpen] = useState(false);
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
                }
            } catch (err) {
                console.error('Failed to parse WS message in console:', err);
            }
        };

        socket.addEventListener('message', handleMessage);
        return () => socket.removeEventListener('message', handleMessage);
    }, [socket]);

    const addMessage = (text: string, sender: 'user' | 'atom') => {
        const newMessage: Message = {
            id: Math.random().toString(36).substr(2, 9),
            text,
            sender,
            timestamp: new Date(),
        };
        setMessages((prev) => [...prev, newMessage]);
    };

    const handleSend = async () => {
        if (!input.trim()) return;

        const userMessage = input.trim();
        setInput('');
        addMessage(userMessage, 'user');
        setIsTyping(true);

        try {
            const apiUrl = import.meta.env?.VITE_API_BASE_URL || 'http://localhost:8000';
            const response = await fetch(`${apiUrl}/api/atom/chat`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message: userMessage }),
            });

            const data = await response.json();
            if (data.status === 'ok') {
                // Response will also come via WebSocket, but we can handle it here too if needed
                // For now, let's rely on the WebSocket broadcast for consistency
            } else {
                addMessage(`Error: ${data.message || 'Failed to reach ATOM'}`, 'atom');
            }
        } catch (err) {
            addMessage('System Error: ATOM core is unreachable.', 'atom');
        } finally {
            setIsTyping(false);
        }
    };

    return (
        <div className={`fixed bottom-6 left-6 z-50 transition-all duration-500 ${isMaximized ? 'w-[600px] h-[800px]' : 'w-96 h-[500px]'} ${!isOpen && 'h-12 w-48'}`}>
            <AnimatePresence>
                {!isOpen ? (
                    <motion.button
                        initial={{ y: 20, opacity: 0 }}
                        animate={{ y: 0, opacity: 1 }}
                        onClick={() => setIsOpen(true)}
                        className="w-full h-full bg-cyan-500/20 backdrop-blur-xl border border-cyan-500/50 rounded-xl flex items-center justify-center gap-2 text-cyan-400 font-bold hover:bg-cyan-500/30 transition-all shadow-lg shadow-cyan-500/20"
                    >
                        <Terminal size={18} />
                        <span>ATOM CONSOLE</span>
                    </motion.button>
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
                                <button onClick={() => setIsMaximized(!isMaximized)} className="text-gray-400 hover:text-white transition-colors">
                                    {isMaximized ? <Minimize2 size={16} /> : <Maximize2 size={16} />}
                                </button>
                                <button onClick={() => setIsOpen(false)} className="text-gray-400 hover:text-white transition-colors">
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
                                    placeholder="Enter directive for ATOM..."
                                    className="w-full bg-slate-900/50 border border-cyan-500/20 rounded-xl py-3 pl-4 pr-12 text-sm text-white focus:outline-none focus:border-cyan-500/50 transition-all"
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
                                    <button className="hover:text-cyan-400 transition-colors flex items-center gap-1">
                                        <Mic size={10} />
                                        VOICE MODE
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
