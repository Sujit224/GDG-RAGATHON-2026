import './Navbar.css'

export default function Navbar() {
  return (
    <nav className="navbar" id="navbar">
      <div className="navbar-inner">
        <a href="/" className="navbar-brand">
          <div className="navbar-logo">P</div>
          <div className="navbar-title">
            Place<span>Mentor</span>
          </div>
        </a>
        <div className="navbar-links">
          <a href="#chat" className="navbar-link">Chat</a>
          <a href="#resume" className="navbar-link">Resume</a>
          <a href="https://github.com" target="_blank" rel="noreferrer" className="navbar-link">GitHub</a>
          <span className="navbar-badge">GDG RAGATHON</span>
        </div>
      </div>
    </nav>
  )
}
