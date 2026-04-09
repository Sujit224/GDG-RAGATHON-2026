import { useState, useRef, useEffect } from 'react';
import './ChatBox.css';

const API_CHAT = 'http://localhost:8000/api/chat';
const API_UPLOAD = 'http://localhost:8000/api/upload';

export default function ChatBox() {
  const [messages, setMessages] = useState([
    { role: 'system', content: 'Hello! I am the Insurance Decoder. Upload your policy PDF above and ask me anything about its coverage, penalties, or exclusions.' }
  ]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadStatus, setUploadStatus] = useState('');
  const [typedMessage, setTypedMessage] = useState('');
  const [isTypingEffect, setIsTypingEffect] = useState(false);

  const messagesEndRef = useRef(null);
  const fileInputRef = useRef(null);

  const typeEffect = (text) => {
    setIsTypingEffect(true);
    setTypedMessage('');
    let i = 0;
    const interval = setInterval(() => {
      setTypedMessage(prev => prev + text.charAt(i));
      i++;
      if (i >= text.length) {
        clearInterval(interval);
        setMessages(prev => [...prev, { role: 'system', content: text }]);
        setTypedMessage('');
        setIsTypingEffect(false);
      }
    }, 5);
  };

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isLoading, typedMessage]);

  const handleFileUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    if (file.type !== 'application/pdf') {
      setUploadStatus('Please upload a valid PDF file.');
      return;
    }

    setIsUploading(true);
    setUploadStatus('Uploading and parsing document...');

    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await fetch(API_UPLOAD, {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        throw new Error('Upload failed');
      }

      const data = await response.json();
      setUploadStatus('Upload successful! Document is ready for questions.');
      setMessages(prev => [...prev, { role: 'system', content: `Successfully loaded context from: ${file.name}` }]);
    } catch (error) {
      setUploadStatus('Failed to upload document. Is the backend running?');
    } finally {
      setIsUploading(false);
      if (fileInputRef.current) fileInputRef.current.value = ''; // Reset input
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;

    const userMsg = input.trim();
    setMessages(prev => [...prev, { role: 'user', content: userMsg }]);
    setInput('');
    setIsLoading(true);

    try {
      const response = await fetch(API_CHAT, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query: userMsg })
      });

      if (!response.ok) {
        throw new Error('Failed to fetch from API');
      }

      const data = await response.json();
      typeEffect(data.response);
    } catch (error) {
      setMessages(prev => [...prev, { role: 'system', content: 'Connection error. Ensure the FastAPI backend is running and GROQ_API_KEY is configured.' }]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="chatbox-wrapper">
      <div className="upload-zone">
        <div style={{display: 'flex', flexDirection: 'column'}}>
          <h4 style={{marginBottom: '4px'}}>Insurance Policy Sync</h4>
          <span className="upload-status">{uploadStatus || 'Select a PDF policy document to decode.'}</span>
        </div>
        <div>
          <input
            type="file"
            accept=".pdf"
            ref={fileInputRef}
            onChange={handleFileUpload}
            style={{ display: 'none' }}
            id="pdf-upload"
          />
          <label htmlFor="pdf-upload" className={`upload-button ${isUploading ? 'loading' : ''}`}>
            {isUploading ? '⌛ Processing...' : '📤 Upload PDF Policy'}
          </label>
        </div>
      </div>

      <div className="centered-chat">
        <div className="chat-header">
          <div className="ai-icon"></div>
          <div>
            <h3>Policy Decoder Pro</h3>
            <p>Smart RAG Insurance Analysis • ELI5 Enabled</p>
          </div>
        </div>

        <div className="messages-area">
          {messages.map((msg, i) => (
            <div key={i} className={`message-wrapper ${msg.role}`}>
              <div className={`message-bubble ${msg.role}`} 
                dangerouslySetInnerHTML={{ __html: msg.content.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>').replace(/\n/g, '<br>') }}>
              </div>
            </div>
          ))}
          {isTypingEffect && (
            <div className="message-wrapper system">
              <div className="message-bubble system" 
                dangerouslySetInnerHTML={{ __html: typedMessage.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>').replace(/\n/g, '<br>') }}>
              </div>
            </div>
          )}
          {isLoading && (
            <div className="message-wrapper system">
              <div className="message-bubble system typing">
                <span className="dot"></span>
                <span className="dot"></span>
                <span className="dot"></span>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        <form className="input-area" onSubmit={handleSubmit}>
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="E.g., Does this policy cover injuries from extreme sports?"
          />
          <button type="submit" disabled={!input.trim() || isLoading}>
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M22 2L11 13" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
              <path d="M22 2L15 22L11 13L2 9L22 2Z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
            </svg>
          </button>
        </form>
      </div>
      
      <div className="upload-zone">
        <input
          type="file"
          accept=".pdf"
          ref={fileInputRef}
          onChange={handleFileUpload}
          style={{ display: 'none' }}
          id="pdf-upload"
        />
        <label htmlFor="pdf-upload" className={`upload-button ${isUploading ? 'loading' : ''}`}>
          {isUploading ? '⏳ Processing...' : '📤 Upload PDF Policy'}
        </label>
        {uploadStatus && <span className="upload-status">{uploadStatus}</span>}
      </div>
    </div>
  );
}
