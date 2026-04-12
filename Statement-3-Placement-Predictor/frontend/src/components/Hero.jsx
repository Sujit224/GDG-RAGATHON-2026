import './Hero.css'

export default function Hero({ onStartChat, onUploadResume }) {
  return (
    <section className="hero" id="hero">
      <div className="hero-badge">
        <span className="hero-badge-dot"></span>
        Powered by Gemini AI + Gradient Boosting
      </div>

      <h1>
        Know Your <span className="gradient-text">Placement Readiness</span>
        <br />Before the Interview
      </h1>

      <p className="hero-subtitle">
        Chat with our AI mentor, upload your resume, or fill in your profile — 
        get an instant readiness score backed by data from 1500+ student placements 
        and matched with real interview experiences.
      </p>

      <div className="hero-actions">
        <button className="btn-primary" onClick={onStartChat} id="start-chat-btn">
          💬 Start Chat Assessment
        </button>
        <button className="btn-secondary" onClick={onUploadResume} id="upload-resume-btn">
          📄 Upload Resume
        </button>
      </div>

      <div className="features-grid">
        <div className="glass-card feature-card">
          <div className="feature-icon">🤖</div>
          <h3>AI Chat Profiling</h3>
          <p>Have a natural conversation with our AI mentor who extracts your profile and assesses your readiness.</p>
        </div>
        <div className="glass-card feature-card">
          <div className="feature-icon">📊</div>
          <h3>ML Score Prediction</h3>
          <p>Gradient Boosting model trained on 1000+ profiles predicts your placement readiness (R² = 0.91).</p>
        </div>
        <div className="glass-card feature-card">
          <div className="feature-icon">🎯</div>
          <h3>Experience Matching</h3>
          <p>RAG-powered search finds the most relevant senior interview experiences matching your tech stack.</p>
        </div>
      </div>

      <div className="stats-row">
        <div className="stat-item">
          <div className="stat-value">1500+</div>
          <div className="stat-label">Student Profiles</div>
        </div>
        <div className="stat-item">
          <div className="stat-value">91%</div>
          <div className="stat-label">Model Accuracy (R²)</div>
        </div>
        <div className="stat-item">
          <div className="stat-value">969</div>
          <div className="stat-label">Interview Experiences</div>
        </div>
        <div className="stat-item">
          <div className="stat-value">7</div>
          <div className="stat-label">Profile Features</div>
        </div>
      </div>
    </section>
  )
}
