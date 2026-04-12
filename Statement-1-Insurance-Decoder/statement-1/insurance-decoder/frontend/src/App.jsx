import { useState, useRef, useEffect } from 'react';
import axios from 'axios';
import { Upload, FileText, Send, User, Bot, AlertTriangle, ShieldCheck, ShieldAlert, Cpu } from 'lucide-react';
import './index.css';

const API_URL = 'http://localhost:8000';

function App() {
  const [file, setFile] = useState(null);
  const [uploadStatus, setUploadStatus] = useState({ uploading: false, success: false, error: null });
  const [messages, setMessages] = useState([
    { id: 1, type: 'ai', text: 'Hello! I am your Insurance Decoder. Upload your policy PDF and ask me anything about it.',
      badge: null, keyword: null }
  ]);
  const [query, setQuery] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isTyping]);

  const handleFileUpload = async (e) => {
    const selectedFile = e.target.files[0];
    if (!selectedFile) return;
    
    if (selectedFile.type !== 'application/pdf') {
      setUploadStatus({ uploading: false, success: false, error: 'Only PDF files are supported.' });
      return;
    }

    setFile(selectedFile);
    setUploadStatus({ uploading: true, success: false, error: null });

    const formData = new FormData();
    formData.append('file', selectedFile);

    try {
      await axios.post(`${API_URL}/upload`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      setUploadStatus({ uploading: false, success: true, error: null });
    } catch (err) {
      setUploadStatus({ uploading: false, success: false, error: err.response?.data?.detail || 'Error uploading file' });
    }
  };

  const handleAsk = async (question) => {
    if (!question.trim()) return;

    // Add user message
    const newMessages = [...messages, { id: Date.now(), type: 'user', text: question }];
    setMessages(newMessages);
    setQuery('');
    setIsTyping(true);

    try {
      const response = await axios.post(`${API_URL}/ask`, { query: question });
      const { explanation, highlight, is_covered } = response.data;
      
      setMessages([...newMessages, { 
        id: Date.now() + 1, 
        type: 'ai', 
        text: explanation,
        badge: is_covered,
        keyword: highlight
      }]);
    } catch (err) {
      setMessages([...newMessages, { 
        id: Date.now() + 1, 
        type: 'ai', 
        text: err.response?.data?.detail || 'Sorry, there was an error processing your question. Ensure you uploaded a PDF first!',
        badge: '❌ Not Covered',
        keyword: 'Error'
      }]);
    } finally {
      setIsTyping(false);
    }
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    handleAsk(query);
  };

  const predefinedQuestions = [
    "Is MRI covered?",
    "What is deductible?",
    "What is not covered?",
    "Is skydiving covered?"
  ];

  return (
    <div>
      <header className="app-header">
        <h1 className="app-title"><ShieldCheck size={36} style={{display: 'inline', verticalAlign: 'middle', marginRight: '10px'}}/> Insurance Decoder</h1>
        <p className="app-subtitle">Making sense of policies using AI</p>
      </header>

      <div className="main-layout">
        <aside className="sidebar glass-panel">
          <div className="upload-section">
            <h3>Document</h3>
            <div className="upload-btn-wrapper">
              <button className="btn btn-primary" disabled={uploadStatus.uploading}>
                <Upload size={18} />
                {uploadStatus.uploading ? 'Processing...' : 'Upload PDF'}
              </button>
              <input type="file" name="file" accept=".pdf" onChange={handleFileUpload} />
            </div>
            
            {file && !uploadStatus.uploading && uploadStatus.success && (
              <div className="file-status">
                <FileText size={16} /> {file.name} loaded
              </div>
            )}
            
            {uploadStatus.error && (
              <div className="file-status error">
                <AlertTriangle size={16} /> {uploadStatus.error}
              </div>
            )}
          </div>

          <div className="quick-questions">
            <h3>Quick Questions</h3>
            {predefinedQuestions.map((q, idx) => (
              <button key={idx} className="question-btn" onClick={() => handleAsk(q)}>
                {q}
              </button>
            ))}
          </div>
          
          <div className="quick-questions" style={{ marginTop: 'auto' }}>
            <h3>Risk Analyzer</h3>
            <p style={{fontSize: '0.8rem', color: 'var(--text-secondary)', marginBottom: '0.5rem'}}>Enter a scenario below to check coverage.</p>
            <button className="question-btn" style={{borderStyle: 'dashed', borderColor: 'var(--primary)'}} 
                    onClick={() => handleAsk("Analyze this scenario based on the policy and determine coverage, risk, and conditions: I got admitted for standard procedure without prior info")}>
              Try: Admitted without info
            </button>
          </div>
        </aside>

        <main className="chat-container glass-panel">
          <div className="chat-messages">
            {messages.map((msg) => (
              <div key={msg.id} className={`message ${msg.type}`}>
                <div className={`avatar ${msg.type}-avatar`}>
                  {msg.type === 'user' ? <User size={20} color="white" /> : <Bot size={20} color="white" />}
                </div>
                <div className="message-content">
                  {msg.type === 'ai' && msg.badge && (
                    <div>
                      <span className={`badge ${
                        msg.badge.includes('Covered') && !msg.badge.includes('Not') ? 'badge-covered' : 
                        msg.badge.includes('Not') ? 'badge-not-covered' : 'badge-conditions'
                      }`}>
                        {msg.badge}
                      </span>
                      {msg.keyword && <span className="highlight-keyword">{msg.keyword}</span>}
                    </div>
                  )}
                  <p>{msg.text}</p>
                </div>
              </div>
            ))}
            
            {isTyping && (
              <div className="message ai">
                <div className="avatar ai-avatar">
                  <Cpu size={20} color="white" />
                </div>
                <div className="message-content">
                  <div className="typing-indicator">
                    <div className="typing-dot"></div>
                    <div className="typing-dot"></div>
                    <div className="typing-dot"></div>
                  </div>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          <form className="chat-input-area" onSubmit={handleSubmit}>
            <div className="input-wrapper">
              <input
                type="text"
                className="chat-input"
                placeholder="Ask a question or describe a scenario..."
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                disabled={uploadStatus.uploading}
              />
              <button 
                type="submit" 
                className="send-btn" 
                disabled={!query.trim() || uploadStatus.uploading}
              >
                <Send size={18} />
              </button>
            </div>
          </form>
        </main>
      </div>
    </div>
  );
}

export default App;
