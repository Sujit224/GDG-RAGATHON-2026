import { useState, useRef, useEffect } from 'react'
import './ChatInterface.css'

const API = 'http://localhost:8001'

export default function ChatInterface({ onProfileReady }) {
  const [mode, setMode] = useState('choose') // 'choose' | 'chat' | 'form'
  const [messages, setMessages] = useState([])
  const [history, setHistory] = useState([])
  const [input, setInput] = useState('')
  const [isTyping, setIsTyping] = useState(false)
  const [formData, setFormData] = useState({
    academic_score: '', dsa_skill: '', project_quality: '',
    experience_score: '', opensource_value: '1', soft_skills: '', tech_stack_score: ''
  })
  const messagesEndRef = useRef(null)

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, isTyping])

  // Start chat mode
  const startChat = () => {
    setMode('chat')
    setMessages([{
      role: 'bot',
      content: "Hey there! 👋 I'm PlaceMentor, your placement readiness guide. I'll help you understand how prepared you are for campus placements.\n\nLet's start with the basics — what's your current CGPA, and what branch/year are you in?"
    }])
  }

  // Send chat message
  const sendMessage = async () => {
    if (!input.trim() || isTyping) return
    const userMsg = input.trim()
    setInput('')
    setMessages(prev => [...prev, { role: 'user', content: userMsg }])
    setIsTyping(true)

    try {
      const res = await fetch(`${API}/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: userMsg, history })
      })
      const data = await res.json()

      setMessages(prev => [...prev, { role: 'bot', content: data.reply }])
      setHistory(prev => [
        ...prev,
        { role: 'user', content: userMsg },
        { role: 'assistant', content: data.reply }
      ])

      if (data.profile_complete && data.profile) {
        setTimeout(() => onProfileReady(data.profile), 1000)
      }
    } catch (err) {
      setMessages(prev => [...prev, {
        role: 'bot',
        content: "Sorry, I'm having trouble connecting to the server. Please make sure the backend is running on port 8001."
      }])
    }
    setIsTyping(false)
  }

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      sendMessage()
    }
  }

  // Manual form submit
  const submitForm = async () => {
    const profile = {
      academic_score: parseFloat(formData.academic_score) || 7.0,
      dsa_skill: parseInt(formData.dsa_skill) || 5,
      project_quality: parseInt(formData.project_quality) || 5,
      experience_score: parseInt(formData.experience_score) || 3,
      opensource_value: parseInt(formData.opensource_value) || 1,
      soft_skills: parseInt(formData.soft_skills) || 5,
      tech_stack_score: parseInt(formData.tech_stack_score) || 5,
    }
    onProfileReady(profile)
  }

  const updateForm = (field, value) => {
    setFormData(prev => ({ ...prev, [field]: value }))
  }

  // ── Choose mode ─────────────────────────────────────────────────
  if (mode === 'choose') {
    return (
      <div className="chat-container" id="chat">
        <div className="section-title">Assess Your Profile</div>
        <p className="section-subtitle">
          Choose how you'd like to share your profile details
        </p>
        <div style={{ display: 'flex', gap: '1rem', justifyContent: 'center', flexWrap: 'wrap' }}>
          <button className="btn-primary" onClick={startChat} id="chat-mode-btn">
            💬 Chat with AI Mentor
          </button>
          <button className="btn-secondary" onClick={() => setMode('form')} id="form-mode-btn">
            📝 Fill Manual Form
          </button>
        </div>
      </div>
    )
  }

  // ── Chat mode ───────────────────────────────────────────────────
  if (mode === 'chat') {
    return (
      <div className="chat-container" id="chat-interface">
        <div className="chat-header">
          <div className="chat-avatar">🤖</div>
          <div className="chat-header-info">
            <h3>PlaceMentor AI</h3>
            <p>Powered by Gemini &middot; Assessing your profile</p>
          </div>
        </div>

        <div className="glass-card chat-messages" id="chat-messages">
          {messages.map((msg, i) => (
            <div key={i} className={`chat-msg ${msg.role}`}>
              <div className="chat-msg-avatar">
                {msg.role === 'bot' ? '🤖' : '👤'}
              </div>
              <div className="chat-msg-bubble">
                {msg.content.split('\n').map((line, j) => (
                  <span key={j}>{line}<br /></span>
                ))}
              </div>
            </div>
          ))}
          {isTyping && (
            <div className="typing-indicator">
              <span className="typing-dot"></span>
              <span className="typing-dot"></span>
              <span className="typing-dot"></span>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        <div className="chat-input-area">
          <input
            className="chat-input"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Tell me about yourself..."
            disabled={isTyping}
            id="chat-input"
          />
          <button
            className="chat-send-btn"
            onClick={sendMessage}
            disabled={!input.trim() || isTyping}
            id="chat-send"
          >
            Send →
          </button>
        </div>
      </div>
    )
  }

  // ── Manual form mode ────────────────────────────────────────────
  return (
    <div className="manual-form" id="manual-form">
      <div className="section-title">Your Profile</div>
      <p className="section-subtitle">
        Fill in your details to get your placement readiness score
      </p>

      <div className="glass-card" style={{ padding: 'var(--space-xl)' }}>
        <div className="form-grid">
          <div className="form-group">
            <label className="form-label">
              🎓 CGPA <span className="form-label-hint">(0-10)</span>
            </label>
            <input className="form-input" type="number" step="0.1" min="0" max="10"
              placeholder="e.g., 8.5" value={formData.academic_score}
              onChange={(e) => updateForm('academic_score', e.target.value)} id="form-cgpa" />
          </div>

          <div className="form-group">
            <label className="form-label">
              💻 DSA Skill <span className="form-label-hint">(1-10)</span>
            </label>
            <input className="form-input" type="number" min="1" max="10"
              placeholder="e.g., 7" value={formData.dsa_skill}
              onChange={(e) => updateForm('dsa_skill', e.target.value)} id="form-dsa" />
          </div>

          <div className="form-group">
            <label className="form-label">
              🔧 Project Quality <span className="form-label-hint">(1-10)</span>
            </label>
            <input className="form-input" type="number" min="1" max="10"
              placeholder="e.g., 6" value={formData.project_quality}
              onChange={(e) => updateForm('project_quality', e.target.value)} id="form-projects" />
          </div>

          <div className="form-group">
            <label className="form-label">
              💼 Experience <span className="form-label-hint">(0-10)</span>
            </label>
            <input className="form-input" type="number" min="0" max="10"
              placeholder="e.g., 4" value={formData.experience_score}
              onChange={(e) => updateForm('experience_score', e.target.value)} id="form-experience" />
          </div>

          <div className="form-group">
            <label className="form-label">
              🌐 Open Source <span className="form-label-hint">(1=No, 10=Active)</span>
            </label>
            <select className="form-input" value={formData.opensource_value}
              onChange={(e) => updateForm('opensource_value', e.target.value)} id="form-opensource">
              <option value="1">No contributions</option>
              <option value="10">Active contributor</option>
            </select>
          </div>

          <div className="form-group">
            <label className="form-label">
              🗣️ Soft Skills <span className="form-label-hint">(1-10)</span>
            </label>
            <input className="form-input" type="number" min="1" max="10"
              placeholder="e.g., 7" value={formData.soft_skills}
              onChange={(e) => updateForm('soft_skills', e.target.value)} id="form-softskills" />
          </div>

          <div className="form-group full-width">
            <label className="form-label">
              ⚙️ Tech Stack Score <span className="form-label-hint">(1-10, number of technologies)</span>
            </label>
            <input className="form-input" type="number" min="1" max="10"
              placeholder="e.g., 5" value={formData.tech_stack_score}
              onChange={(e) => updateForm('tech_stack_score', e.target.value)} id="form-techstack" />
          </div>
        </div>

        <button className="btn-primary form-submit" onClick={submitForm} id="form-submit">
          🚀 Predict My Readiness Score
        </button>
      </div>
    </div>
  )
}
