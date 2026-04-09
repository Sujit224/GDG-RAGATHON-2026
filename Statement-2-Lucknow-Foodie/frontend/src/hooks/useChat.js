import { useState, useEffect } from 'react';
import { chatWithBot } from '../api/client';

export const useChat = () => {
    const [messages, setMessages] = useState(() => {
        const saved = localStorage.getItem('lucknowFoodieChatHistory');
        if (saved) {
            try {
                return JSON.parse(saved);
            } catch (e) {
                console.error("Could not parse saved chat history.");
            }
        }
        return [{ role: "assistant", content: "Hi! I'm Lucknow Foodie, your AI food buddy near IIIT Lucknow.\n\nI can help you find the best places to eat based on diet, budget, location, and vibes. What are you craving today?" }];
    });
    const [loading, setLoading] = useState(false);

    useEffect(() => {
        localStorage.setItem('lucknowFoodieChatHistory', JSON.stringify(messages));
    }, [messages]);

    const sendMessage = async (text) => {
        const userMsg = { role: "user", content: text };
        const updatedHistory = [...messages, userMsg];
        setMessages(updatedHistory);
        setLoading(true);

        try {
            // Send previously accumulated messages (excluding the new one which is sent as message param)
            // Wait, we should probably pass all, but let's see. The backend handles the current one separately. 
            // `history` is past messages.
            const historyForApi = messages.map(m => ({
                role: m.role,
                content: m.content || ""
            }));
            
            const data = await chatWithBot(text, historyForApi);
            setMessages(prev => [...prev, {
                role: "assistant",
                content: data.reply,
                restaurants: data.restaurants
            }]);
        } catch (error) {
            console.error(error);
            setMessages(prev => [...prev, {
                role: "assistant",
                content: "Oops! Something went wrong. Try again.",
                isError: true
            }]);
        } finally {
            setLoading(false);
        }
    };

    const clearChat = () => {
        const initMsg = [{ role: "assistant", content: "Hi! I'm Lucknow Foodie, your AI food buddy near IIIT Lucknow.\n\nI can help you find the best places to eat based on diet, budget, location, and vibes. What are you craving today?" }];
        setMessages(initMsg);
        localStorage.removeItem('lucknowFoodieChatHistory');
    };

    return { messages, sendMessage, loading, clearChat };
};
