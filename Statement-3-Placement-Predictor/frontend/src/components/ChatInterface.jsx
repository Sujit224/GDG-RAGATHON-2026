import { useState, useRef, useEffect } from 'react'

export default function ChatInterface({ messages, loading, onSend, disabled }) {
  const [input, setInput] = useState('')
  const bottomRef = useRef(null)

  useEffect(() => { bottomRef.current?.scrollIntoView({ behavior: 'smooth' }) }, [messages])

  const handleSend = () => {
    if (!input.trim() || loading || disabled) return
    onSend(input.trim())
    setInput('')
  }

  // Show welcome message if no messages yet
  const showWelcome = messages.length === 0

  return (
    <div className="bg-white/5 border border-white/10 rounded-2xl overflow-hidden">
      <div className="p-4 border-b border-white/10 flex items-center gap-2">
        <div className="w-2 h-2 rounded-full bg-green-400 animate-pulse" />
        <span className="text-sm text-white/60">AI Mentor — Online</span>
      </div>

      <div className="h-80 overflow-y-auto p-4 space-y-3 scroll-smooth">
        {showWelcome && (
          <div className="flex items-start gap-3">
            <div className="w-7 h-7 rounded-full bg-indigo-500 flex-shrink-0 flex items-center justify-center text-xs">AI</div>
            <div className="bg-indigo-500/20 border border-indigo-500/30 rounded-2xl rounded-tl-sm px-4 py-2.5 text-sm text-white/90 max-w-md">
              👋 Hi! I'm your PlaceIQ mentor. I'll help predict your placement readiness. Let's start — what's your current CGPA?
            </div>
          </div>
        )}

        {messages.map((m, i) => (
          <div key={i} className={`flex items-start gap-3 ${m.role === 'user' ? 'flex-row-reverse' : ''}`}>
            <div className={`w-7 h-7 rounded-full flex-shrink-0 flex items-center justify-center text-xs
              ${m.role === 'user' ? 'bg-slate-600' : 'bg-indigo-500'}`}>
              {m.role === 'user' ? 'You' : 'AI'}
            </div>
            <div className={`rounded-2xl px-4 py-2.5 text-sm max-w-sm
              ${m.role === 'user'
                ? 'bg-slate-700 text-white rounded-tr-sm'
                : 'bg-indigo-500/20 border border-indigo-500/30 text-white/90 rounded-tl-sm'}`}>
              {m.content}
            </div>
          </div>
        ))}

        {loading && (
          <div className="flex items-start gap-3">
            <div className="w-7 h-7 rounded-full bg-indigo-500 flex items-center justify-center text-xs">AI</div>
            <div className="bg-indigo-500/20 border border-indigo-500/30 rounded-2xl rounded-tl-sm px-4 py-2.5">
              <div className="flex gap-1">
                {[0,1,2].map(i => <div key={i} className="w-1.5 h-1.5 bg-indigo-400 rounded-full animate-bounce" style={{animationDelay:`${i*0.15}s`}} />)}
              </div>
            </div>
          </div>
        )}
        <div ref={bottomRef} />
      </div>

      {!disabled && (
        <div className="p-3 border-t border-white/10 flex gap-2">
          <input
            value={input}
            onChange={e => setInput(e.target.value)}
            onKeyDown={e => e.key === 'Enter' && handleSend()}
            placeholder="Type your answer..."
            className="flex-1 bg-white/5 border border-white/15 rounded-xl px-4 py-2.5 text-sm text-white placeholder-white/30 outline-none focus:border-indigo-500/60 transition"
          />
          <button
            onClick={handleSend}
            disabled={loading || !input.trim()}
            className="bg-indigo-500 hover:bg-indigo-400 disabled:opacity-40 px-5 py-2.5 rounded-xl text-sm font-medium transition"
          >
            Send
          </button>
        </div>
      )}
    </div>
  )
}
