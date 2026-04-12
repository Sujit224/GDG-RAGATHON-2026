import { useState, useRef } from 'react'
import './ResumeUpload.css'

const API = 'http://localhost:8001'

export default function ResumeUpload({ onProfileReady }) {
  const [isDragging, setIsDragging] = useState(false)
  const [isProcessing, setIsProcessing] = useState(false)
  const [error, setError] = useState(null)
  const fileInputRef = useRef(null)

  const handleDrag = (e) => {
    e.preventDefault()
    e.stopPropagation()
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setIsDragging(true)
    } else if (e.type === 'dragleave') {
      setIsDragging(false)
    }
  }

  const handleDrop = (e) => {
    e.preventDefault()
    e.stopPropagation()
    setIsDragging(false)
    
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFile(e.dataTransfer.files[0])
    }
  }

  const handleChange = (e) => {
    e.preventDefault()
    if (e.target.files && e.target.files[0]) {
      handleFile(e.target.files[0])
    }
  }

  const handleFile = async (file) => {
    setError(null)
    const validTypes = ['application/pdf', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document']
    
    if (!validTypes.includes(file.type)) {
      setError("Please upload a PDF or DOCX file.")
      return
    }

    setIsProcessing(true)
    const formData = new FormData()
    formData.append('file', file)

    try {
      const res = await fetch(`${API}/upload-resume`, {
        method: 'POST',
        body: formData,
      })
      
      const data = await res.json()
      
      if (!res.ok) {
        throw new Error(data.detail || "Failed to process resume")
      }

      // Briefly show processing success before moving on
      setTimeout(() => {
        onProfileReady(data.profile)
      }, 1000)
      
    } catch (err) {
      setError(err.message)
      setIsProcessing(false)
    }
  }

  return (
    <div className="upload-container" id="resume-upload">
      <div className="section-title">Resume Parser</div>
      <p className="section-subtitle">
        Upload your resume and our Gemini AI will automatically extract your profile details to predict your score.
      </p>

      {isProcessing ? (
        <div className="glass-card upload-processing">
          <div className="upload-loader"></div>
          <h3 className="upload-title">Analyzing Your Resume...</h3>
          <p className="upload-subtitle">Gemini is extracting your skills, CGPA, and experience.</p>
        </div>
      ) : (
        <div 
          className={`upload-zone ${isDragging ? 'active' : ''}`}
          onDragEnter={handleDrag}
          onDragLeave={handleDrag}
          onDragOver={handleDrag}
          onDrop={handleDrop}
          onClick={() => fileInputRef.current?.click()}
        >
          <input 
            type="file" 
            ref={fileInputRef} 
            onChange={handleChange} 
            className="file-input" 
            accept=".pdf,.docx"
          />
          
          <div className="upload-icon">📄</div>
          <h3 className="upload-title">Drag & Drop Resume</h3>
          <p className="upload-subtitle">Supports PDF and Word Documents (.docx)</p>
          
          <div className="upload-btn">Browse Files</div>
          
          {error && (
            <p style={{ color: 'var(--color-accent-danger)', marginTop: 'var(--space-md)', fontSize: '0.9rem' }}>
              ⚠️ {error}
            </p>
          )}
        </div>
      )}

      {!isProcessing && (
        <div className="glass-card" style={{ padding: 'var(--space-md)' }}>
          <div style={{ display: 'flex', gap: '12px', alignItems: 'flex-start' }}>
            <div style={{ fontSize: '1.5rem' }}>💡</div>
            <div>
              <h4 style={{ color: 'var(--color-text-primary)', marginBottom: '4px' }}>Bonus Feature Active</h4>
              <p style={{ color: 'var(--color-text-secondary)', fontSize: '0.85rem', lineHeight: '1.5' }}>
                This feature uses Gemini 2.0 Flash to act as a structured data extraction agent, 
                converting unstructured PDF text immediately into the 7 numeric parameters required by our 
                Gradient Boosting model.
              </p>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
