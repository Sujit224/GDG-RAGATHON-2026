import { useEffect, useState } from 'react'
import './ScoreGauge.css'

export default function ScoreGauge({ result }) {
  const [animatedScore, setAnimatedScore] = useState(0)
  
  const score = result.readiness_score || 0
  const verdict = result.verdict || 'Unknown'
  const message = result.message || ''
  const breakdown = result.breakdown || []

  // SVG Gauge calculations
  const radius = 100
  const circumference = 2 * Math.PI * radius
  const strokeDashoffset = circumference - (animatedScore / 100) * circumference

  useEffect(() => {
    // Animate score from 0 to target
    const timer = setTimeout(() => {
      setAnimatedScore(score)
    }, 300)
    return () => clearTimeout(timer)
  }, [score])

  // Determine colors based on score
  let strokeColor = 'url(#gradient-high)'
  let verdictClass = 'verdict-improvement'
  
  if (score >= 80) {
    strokeColor = 'url(#gradient-high)'
    verdictClass = 'verdict-excellent'
  } else if (score >= 65) {
    strokeColor = 'url(#gradient-mid)'
    verdictClass = 'verdict-good'
  } else if (score >= 50) {
    strokeColor = 'url(#gradient-warn)'
    verdictClass = 'verdict-moderate'
  } else {
    strokeColor = 'url(#gradient-low)'
    verdictClass = 'verdict-improvement'
  }

  return (
    <div className="glass-card" style={{ padding: 'var(--space-xl)' }} id="score-gauge">
      <div className="score-container">
        
        <div className="gauge-wrapper">
          <svg className="gauge-svg" viewBox="0 0 240 240">
            <defs>
              <linearGradient id="gradient-high" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" stopColor="#34d399" />
                <stop offset="100%" stopColor="#6ee7b7" />
              </linearGradient>
              <linearGradient id="gradient-mid" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" stopColor="#8b5cf6" />
                <stop offset="100%" stopColor="#3b82f6" />
              </linearGradient>
              <linearGradient id="gradient-warn" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" stopColor="#fbbf24" />
                <stop offset="100%" stopColor="#f59e0b" />
              </linearGradient>
              <linearGradient id="gradient-low" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" stopColor="#f87171" />
                <stop offset="100%" stopColor="#ef4444" />
              </linearGradient>
            </defs>
            <circle className="gauge-track" cx="120" cy="120" r={radius} />
            <circle 
              className="gauge-fill" 
              cx="120" cy="120" r={radius} 
              strokeDasharray={circumference}
              strokeDashoffset={strokeDashoffset}
              stroke={strokeColor}
            />
          </svg>
          <div className="gauge-content">
            <div className="score-value">{score}</div>
            <div className="score-label">Readiness</div>
          </div>
        </div>

        <div className={`verdict-badge ${verdictClass}`}>
          {verdict}
        </div>
        
        <p className="score-message">{message}</p>
        
      </div>

      <div className="breakdown-list" id="feature-breakdown">
        <h4 style={{ marginBottom: 'var(--space-xs)', color: 'var(--color-text-secondary)' }}>
          Profile Breakdown
        </h4>
        {breakdown.map((item, i) => (
          <div key={i} className="breakdown-item">
            <div className="breakdown-header">
              <span className="breakdown-name">{item.name}</span>
              <span className="breakdown-val">{item.value} <span style={{color: 'var(--color-text-muted)'}}>/ {item.max}</span></span>
            </div>
            <div className="breakdown-bar-bg">
              <div 
                className="breakdown-bar-fill" 
                style={{ 
                  width: animatedScore > 0 ? `${item.percentage}%` : '0%',
                  background: item.percentage >= 80 ? 'var(--gradient-score-high)' : 
                              item.percentage >= 50 ? 'var(--gradient-score-mid)' : 'var(--gradient-score-low)'
                }}
              ></div>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
