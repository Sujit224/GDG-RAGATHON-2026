import { useState } from 'react'
import { useChat, useResumeUpload } from './hooks/useChat'
import ChatInterface from './components/ChatInterface'
import ProfileExtracted from './components/ProfileExtracted'
import ScoreGauge from './components/ScoreGauge'
import ExperienceCards from './components/ExperienceCards'
import StepProgress from './components/StepProgress'
import ResumeUpload from './components/ResumeUpload'

export default function App() {
  const [mode, setMode] = useState('chat') // 'chat' | 'resume'

  // Chat mode state
  const chat = useChat()

  // Resume mode state
  const resume = useResumeUpload()

  const isActive = mode === 'chat'
    ? chat.step > 1
    : resume.phase !== 'idle'

  const handleReset = () => {
    if (mode === 'chat') chat.reset()
    else resume.reset()
  }

  // Pick which data to display based on mode
  const profile     = mode === 'chat' ? chat.profile     : resume.profile
  const score       = mode === 'chat' ? chat.score        : resume.score
  const experiences = mode === 'chat' ? chat.experiences   : resume.experiences

  // Compute current step for progress indicator
  const currentStep = mode === 'resume'
    ? resume.phase === 'idle' ? 1
      : resume.phase === 'uploading' ? 1
      : resume.profile ? (resume.score ? (resume.experiences?.length > 0 ? 4 : 3) : 2)
      : 1
    : chat.step

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-indigo-950 to-slate-900 text-white">
      {/* ── Header ─────────────────────────────────────────────────── */}
      <header className="border-b border-white/10 px-6 py-4 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-lg bg-indigo-500 flex items-center justify-center text-sm font-bold shadow-lg shadow-indigo-500/40">P</div>
          <span className="text-lg font-semibold tracking-tight">PlaceIQ</span>
          <span className="text-xs text-white/40 ml-1 hidden sm:inline">Placement Predictor & Mentor</span>
        </div>
        <div className="flex items-center gap-3">
          {isActive && (
            <button onClick={handleReset} className="text-xs text-white/50 hover:text-white border border-white/20 px-3 py-1 rounded-full transition">
              Start Over
            </button>
          )}
        </div>
      </header>

      <main className="max-w-4xl mx-auto px-4 py-8 space-y-6">
        {/* ── Mode Switcher ── */}
        <div className="flex justify-center">
          <div className="inline-flex bg-white/5 border border-white/10 rounded-2xl p-1 gap-1">
            {[
              { id: 'chat',   icon: '💬', label: 'Chat Profiling' },
              { id: 'resume', icon: '📄', label: 'Upload Resume' },
            ].map(m => (
              <button
                key={m.id}
                onClick={() => setMode(m.id)}
                className={`
                  flex items-center gap-2 px-5 py-2.5 rounded-xl text-sm font-medium transition-all duration-300
                  ${mode === m.id
                    ? 'bg-indigo-500 text-white shadow-lg shadow-indigo-500/30'
                    : 'text-white/50 hover:text-white/80 hover:bg-white/5'
                  }
                `}
              >
                <span>{m.icon}</span>
                <span className="hidden sm:inline">{m.label}</span>
              </button>
            ))}
          </div>
        </div>

        {/* ── Step Progress ── */}
        <StepProgress currentStep={currentStep} mode={mode} />

        {/* ── Chat Mode ── */}
        {mode === 'chat' && (
          <ChatInterface
            messages={chat.messages}
            loading={chat.loading}
            onSend={chat.sendMessage}
            disabled={chat.step > 1}
          />
        )}

        {/* ── Resume Mode ── */}
        {mode === 'resume' && (
          <ResumeUpload
            phase={resume.phase}
            fileName={resume.fileName}
            error={resume.error}
            onUpload={resume.upload}
            onReset={resume.reset}
          />
        )}

        {/* ── Extracted Profile ── */}
        {profile && <ProfileExtracted profile={profile} />}

        {/* ── Full Prediction Output ── */}
        {score && (
          <ScoreGauge
            score={score.score}
            tier={score.tier}
            advice={score.advice}
            reasons={score.reasons}
            improvements={score.improvements}
            what_if={score.what_if}
            confidence={score.confidence}
            ml_score={score.ml_score}
            rule_score={score.rule_score}
          />
        )}

        {/* ── Recommended Interview Experiences ── */}
        {experiences && experiences.length > 0 && (
          <ExperienceCards experiences={experiences} />
        )}
      </main>

      {/* ── Footer ── */}
      <footer className="border-t border-white/5 py-6 text-center">
        <p className="text-xs text-white/20">
          PlaceIQ v2 • Hybrid ML + Domain Logic + Cosine Similarity Matching
        </p>
      </footer>
    </div>
  )
}
