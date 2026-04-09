import './Footer.css'

export default function Footer() {
  return (
    <footer className="footer" id="footer">
      <div className="footer-inner">
        <div className="footer-brand">
          Built with AI by <span>&nbsp;Team PlaceMentor</span>
        </div>
        <div className="footer-tech">
          <span className="footer-chip">React</span>
          <span className="footer-chip">FastAPI</span>
          <span className="footer-chip">Gemini</span>
          <span className="footer-chip">ChromaDB</span>
          <span className="footer-chip">Scikit-learn</span>
        </div>
        <div className="footer-copy">
          GDG RAGATHON 2026 &middot; IIIT Lucknow &middot; Statement 3: Placement Predictor &amp; Mentor
        </div>
      </div>
    </footer>
  )
}
