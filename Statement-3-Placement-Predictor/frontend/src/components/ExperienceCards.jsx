import './ExperienceCards.css'

export default function ExperienceCards({ experiences = [] }) {
  if (!experiences || experiences.length === 0) {
    return (
      <div className="glass-card exp-empty">
        <div className="exp-empty-icon">🔍</div>
        <h3>No Exact Matches Found</h3>
        <p>Complete your profile to see relevant senior interview experiences based on your tech stack.</p>
      </div>
    )
  }

  return (
    <div className="experiences-container" id="experience-cards">
      {experiences.map((exp, idx) => {
        // Handle PDF source vs XLSX source metadata mapping
        const isPdf = exp.metadata.source === 'interview_experiences_pdf'
        
        // Try to extract company name. If PDF, might not have it in metadata cleanly.
        let companyName = exp.metadata.company || 'Tech Company'
        if (companyName === 'nan' || companyName.trim() === '') companyName = 'Top Tech Corp'
        
        let roleName = exp.metadata.role || 'Software Engineer'
        if (roleName === 'nan' || roleName.trim() === '') roleName = 'SDE Interview Experience'
        
        const initial = companyName.charAt(0).toUpperCase()
        
        // Create tags from metadata
        const tags = []
        if (exp.metadata.tech_stack && exp.metadata.tech_stack !== 'nan') {
          const techArr = exp.metadata.tech_stack.split(',').slice(0, 3)
          tags.push(...techArr.map(t => t.trim()))
        }
        if (exp.metadata.package_lpa > 0) {
          tags.push(`${exp.metadata.package_lpa} LPA`)
        }
        if (isPdf) {
          tags.push('Senior Review')
        }

        return (
          <div key={idx} className="glass-card experience-card">
            {exp.similarity_pct && (
              <div className="exp-match-badge">
                🎯 {exp.similarity_pct}% Match
              </div>
            )}
            
            <div className="exp-header">
              <div className="exp-company-logo">
                {initial}
              </div>
              <div>
                <div className="exp-role">{roleName}</div>
                <div className="exp-company">{companyName}</div>
              </div>
            </div>
            
            {tags.length > 0 && (
              <div className="exp-tags">
                {tags.map((tag, i) => tag && (
                  <span key={i} className="exp-tag">{tag}</span>
                ))}
            </div>
            )}
            
            <div className="exp-content">
              {exp.content.length > 250 
                ? exp.content.substring(0, 250) + '...' 
                : exp.content}
            </div>
          </div>
        )
      })}
    </div>
  )
}
