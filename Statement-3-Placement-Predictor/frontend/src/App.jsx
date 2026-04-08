import { useEffect, useState } from 'react'
import { useChat } from './hooks/useChat'
import ChatInterface from './components/ChatInterface'
import ProfileExtracted from './components/ProfileExtracted'
import ScoreGauge from './components/ScoreGauge'
import ExperienceCards from './components/ExperienceCards'
import StepProgress from './components/StepProgress'

export default function App() {
  const { messages, step, profile, score, experiences, loading, sendMessage, reset } = useChat()

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-indigo-950 to-slate-900 text-white">
      <header className="border-b border-white/10 px-6 py-4 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-lg bg-indigo-500 flex items-center justify-center text-sm font-bold">P</div>
          <span className="text-lg font-semibold tracking-tight">PlaceIQ</span>
          <span className="text-xs text-white/40 ml-1">Placement Predictor & Mentor</span>
        </div>
        {step > 1 && (
          <button onClick={reset} className="text-xs text-white/50 hover:text-white border border-white/20 px-3 py-1 rounded-full transition">
            Start Over
          </button>
        )}
      </header>

      <main className="max-w-5xl mx-auto px-4 py-8 space-y-8">
        <StepProgress currentStep={step} />

        {/* Step 1: Chat */}
        <ChatInterface
          messages={messages}
          loading={loading}
          onSend={sendMessage}
          disabled={step > 1}
        />

        {/* Step 2: Profile */}
        {profile && <ProfileExtracted profile={profile} />}

        {/* Step 3: Score */}
        {score && <ScoreGauge score={score.score} tier={score.tier} advice={score.advice} />}

        {/* Step 4: RAG Experiences */}
        {experiences.length > 0 && <ExperienceCards experiences={experiences} />}
      </main>
    </div>
  )
}
