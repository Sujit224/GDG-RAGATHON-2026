import React, { useState } from 'react';
import { Bot, User, CheckCircle2, Copy } from 'lucide-react';
import { RestaurantCard } from './RestaurantCard';

export const MessageBubble = ({ message, onViewMap }) => {
    const isBot = message.role === "assistant";
    const [copied, setCopied] = useState(false);

    const handleCopy = () => {
        navigator.clipboard.writeText(message.content);
        setCopied(true);
        setTimeout(() => setCopied(false), 2000);
    };

    return (
        <div className={`flex w-full mb-6 ${isBot ? 'justify-start' : 'justify-end'}`}>
            {isBot && (
                <div className="flex-shrink-0 mr-3 mt-1">
                    <div className="w-8 h-8 bg-gradient-to-tr from-primary to-orange-400 rounded-full flex items-center justify-center shadow-md">
                        <Bot size={16} className="text-white" />
                    </div>
                </div>
            )}
            
            <div className={`max-w-[85%] ${isBot ? '' : 'flex flex-col items-end'}`}>
                {/* Bubble Text */}
                <div className={`relative px-4 py-3 shadow-sm text-sm group ${
                    isBot 
                    ? 'bg-white text-gray-800 rounded-2xl rounded-tl-sm border border-gray-100 markdown-content' 
                    : 'bg-primary text-white rounded-2xl rounded-tr-sm'
                }`}>
                    <div className="whitespace-pre-wrap">{message.content}</div>
                    
                    {isBot && !message.isError && (
                        <button 
                            onClick={handleCopy}
                            className="absolute -right-8 top-2 text-gray-400 hover:text-gray-600 opacity-0 group-hover:opacity-100 transition-opacity"
                            title="Copy reply"
                        >
                            {copied ? <CheckCircle2 size={16} className="text-green-500" /> : <Copy size={16} />}
                        </button>
                    )}
                </div>

                {/* Inline Restaurant Cards */}
                {isBot && message.restaurants && message.restaurants.length > 0 && (
                    <div className="mt-3 overflow-x-auto pb-2 -mx-1 px-1 custom-scrollbar">
                        <div className="flex gap-3 w-max">
                            {message.restaurants.map((r, i) => (
                                <div key={i} className="w-64 flex-shrink-0">
                                    <RestaurantCard restaurant={r} onViewMap={onViewMap} className="h-full" />
                                </div>
                            ))}
                        </div>
                    </div>
                )}
            </div>

            {!isBot && (
                <div className="flex-shrink-0 ml-3 mt-1">
                    <div className="w-8 h-8 bg-gray-200 rounded-full flex items-center justify-center shadow-inner">
                        <User size={16} className="text-gray-500" />
                    </div>
                </div>
            )}
        </div>
    );
};
