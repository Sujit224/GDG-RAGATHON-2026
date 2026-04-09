import { useState, useEffect } from 'react'
import './App.css'
import Navbar from './components/Navbar'
import Footer from './components/Footer'
import Hero from './components/Hero'
import ChatInterface from './components/ChatInterface'
import ResumeUpload from './components/ResumeUpload'
import ScoreGauge from './components/ScoreGauge'
import ExperienceCards from './components/ExperienceCards'

const API = 'http://localhost:8001'

function App() {
  const [activeTab, setActiveTab] = useState('chat') // 'chat' | 'resume'
  const [predictionResult, setPredictionResult] = useState(null)
  const [experienceMatches, setExperienceMatches] = useState(null)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState(null)

  // Smooth scroll to element
  const scrollTo = (id) => {
    const el = document.getElementById(id)
    if (el) el.scrollIntoView({ behavior: 'smooth', block: 'start' })
  }

  // Handle extracted profile from Chat or Resume
  const handleProfileReady = async (profile) => {
    setIsLoading(true)
    setError(null)
    
    try {
      // 1. Get prediction score
      const predRes = await fetch(`${API}/predict`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(profile)
      })
      if (!predRes.ok) throw new Error('Prediction API failed')
      const predData = await predRes.json()
      setPredictionResult(predData)

      // 2. Get experience matches (Bonus feature)
      // Extract a summary string from the profile to use for RAG
      const techStackCount = profile.tech_stack_score || 5
      const profileSummaryStr = `Student with ${profile.academic_score || 7} CGPA, DSA level ${profile.dsa_skill || 5}/10. Looking for roles requiring ${techStackCount} technologies.`
      
      const expRes = await fetch(`${API}/match-experiences`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text: profileSummaryStr })
      })
      
      if (expRes.ok) {
        const expData = await expRes.json()
        setExperienceMatches(expData.matches)
      }
      
      // Scroll to results
      setTimeout(() => scrollTo('results-section'), 100)
      
    } catch (err) {
      console.error(err)
      setError("Failed to generate prediction. Is the backend running on port 8001?")
    } finally {
      setIsLoading(false)
    }
  }

  // Reset all state
  const resetApp = () => {
    setPredictionResult(null)
    setExperienceMatches(null)
    setError(null)
    scrollTo('hero')
  }

  return (
    <div className="app-container">
      <Navbar />
      
      <main className="app-main">
        {/* State 1: Landing */}
        {!predictionResult && !isLoading && (
          <>
            <Hero 
              onStartChat={() => { setActiveTab('chat'); scrollTo('assessment-section'); }} 
              onUploadResume={() => { setActiveTab('resume'); scrollTo('assessment-section'); }} 
            />
            
            <div id="assessment-section" style={{ paddingTop: 'var(--space-2xl)' }}>
              <div className="tab-nav">
                <button 
                  className={`tab-btn ${activeTab === 'chat' ? 'active' : ''}`}
                  onClick={() => setActiveTab('chat')}
                >
                  💬 Chat & Form Profiling
                </button>
                <button 
                  className={`tab-btn ${activeTab === 'resume' ? 'active' : ''}`}
                  onClick={() => setActiveTab('resume')}
                >
                  📄 Resume Upload Scanner (Bonus)
                </button>
              </div>

              {activeTab === 'chat' ? (
                <ChatInterface onProfileReady={handleProfileReady} />
              ) : (
                <ResumeUpload onProfileReady={handleProfileReady} />
              )}
            </div>
          </>
        )}

        {/* State 2: Loading Analysis */}
        {isLoading && (
          <div className="spinner-overlay" id="loading-state">
            <div className="spinner"></div>
            <h2 className="section-title">Analyzing Your Profile</h2>
            <div className="spinner-text">Running Gradient Boosting Regression & Vector Search...</div>
          </div>
        )}

        {/* State 3: Results Dashboard */}
        {predictionResult && !isLoading && (
          <div id="results-section" className="animate-fade-in-up">
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 'var(--space-xl)' }}>
              <h2 className="section-title" style={{ margin: 0, textAlign: 'left' }}>Your Placement Dashboard</h2>
              <button className="btn-secondary" onClick={resetApp}>↺ Start Over</button>
            </div>
            
            <div className="result-area">
              <div>
                <h3 style={{ marginBottom: 'var(--space-md)', fontFamily: 'var(--font-display)', color: 'var(--color-text-secondary)' }}>
                  Readiness Prediction
                </h3>
                <ScoreGauge result={predictionResult} />
              </div>
              
              <div>
                <h3 style={{ marginBottom: 'var(--space-md)', fontFamily: 'var(--font-display)', color: 'var(--color-text-secondary)', display: 'flex', justifyContent: 'space-between' }}>
                  <span>Matching Experiences</span>
                  <span style={{ fontSize: '0.8rem', padding: '2px 10px', background: 'rgba(108,99,255,0.1)', color: 'var(--color-text-accent)', borderRadius: '12px' }}>Bonus Active</span>
                </h3>
                <ExperienceCards experiences={experienceMatches} />
              </div>
            </div>
          </div>
        )}

        {/* Error State */}
        {error && (
          <div className="glass-card" style={{ marginTop: 'var(--space-xl)', padding: 'var(--space-lg)', borderLeft: '4px solid var(--color-accent-danger)' }}>
            <h3 style={{ color: 'var(--color-accent-danger)', marginBottom: '8px' }}>Analysis Failed</h3>
            <p>{error}</p>
            <button className="btn-secondary" style={{ marginTop: '16px' }} onClick={() => setError(null)}>Try Again</button>
          </div>
        )}
      </main>

      <Footer />
    </div>
  )
}

export default App
