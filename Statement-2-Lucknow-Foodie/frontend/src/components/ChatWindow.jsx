import React, { useRef, useEffect, useState } from 'react';
import { Send, Trash2 } from 'lucide-react';
import { MessageBubble } from './MessageBubble';
import { QuickChips } from './QuickChips';

export const ChatWindow = ({ messages, loading, onSendMessage, onClear, onViewMap }) => {
    const endRef = useRef(null);
    const [input, setInput] = useState('');

    useEffect(() => {
        endRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, [messages, loading]);

    const handleSubmit = (e) => {
        e.preventDefault();
        if (input.trim() && !loading) {
            onSendMessage(input.trim());
            setInput('');
        }
    };

    const handleChip = (text) => {
        if (!loading) {
            onSendMessage(text);
        }
    };

    return (
        <div className="flex flex-col h-full bg-[#f8f9fa] rounded-2xl border border-gray-200 overflow-hidden shadow-sm">
            {/* Header */}
            <div className="bg-white border-b border-gray-200 px-4 py-3 flex justify-between items-center z-10">
                <div className="flex items-center gap-2">
                    <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
                    <h2 className="font-semibold text-gray-800 text-sm">Lucknow Foodie AI</h2>
                </div>
                <button 
                    onClick={onClear}
                    className="text-gray-400 hover:text-red-500 transition-colors flex items-center gap-1 text-xs font-medium"
                    title="Clear Chat History"
                >
                    <Trash2 size={14} /> Clear
                </button>
            </div>

            {/* Chat Area */}
            <div className="flex-1 overflow-y-auto p-4 custom-scrollbar relative">
                {messages.length <= 1 && (
                    <div className="mb-6">
                        <QuickChips onSelect={handleChip} />
                    </div>
                )}
                
                {messages.map((m, idx) => (
                    <MessageBubble key={idx} message={m} onViewMap={onViewMap} />
                ))}

                {loading && (
                    <div className="flex justify-start mb-4">
                        <div className="bg-white px-4 py-3 rounded-2xl rounded-tl-sm border border-gray-100 shadow-sm flex items-center gap-1.5 w-16">
                            <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{animationDelay: '0ms'}}></div>
                            <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{animationDelay: '150ms'}}></div>
                            <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{animationDelay: '300ms'}}></div>
                        </div>
                    </div>
                )}
                <div ref={endRef} className="pb-2"></div>
            </div>

            {/* Input Form */}
            <div className="p-3 bg-white border-t border-gray-200">
                <form onSubmit={handleSubmit} className="flex flex-nowrap items-center gap-2">
                    <input
                        type="text"
                        value={input}
                        onChange={(e) => setInput(e.target.value)}
                        placeholder="Ask about food, vibes, budget..."
                        disabled={loading}
                        className="flex-1 bg-gray-50 border border-gray-200 rounded-full px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary transition-all disabled:opacity-50 disabled:bg-gray-100"
                    />
                    <button 
                        type="submit"
                        disabled={!input.trim() || loading}
                        className="bg-primary hover:bg-orange-600 disabled:bg-gray-300 disabled:cursor-not-allowed text-white p-2.5 rounded-full transition-colors w-10 h-10 flex items-center justify-center flex-shrink-0 shadow-sm"
                    >
                        <Send size={18} className="ml-1" />
                    </button>
                </form>
            </div>
        </div>
    );
};
