import { useEffect, useState } from 'react'

const TIER_META = {
  'Placement Ready 🏆':   { color: '#22c55e', bg: '#22c55e18', label: 'Placement Ready' },
  'Almost There 🎯':       { color: '#f59e0b', bg: '#f59e0b18', label: 'Almost There' },
  'Needs Improvement 📈': { color: '#f97316', bg: '#f9731618', label: 'Needs Improvement' },
  'Work In Progress 🔧':  { color: '#a78bfa', bg: '#a78bfa18', label: 'Work In Progress' },
  'Early Stage 🌱':        { color: '#ef4444', bg: '#ef444418', label: 'Early Stage' },
}

function AnimatedScore({ target }) {
  const [val, setVal] = useState(0)
  useEffect(() => {
    let cur = 0
    const t = setInterval(() => {
      cur += 1.5
      if (cur >= target) { setVal(target); clearInterval(t) }
      else setVal(Math.round(cur))
    }, 16)
    return () => clearInterval(t)
  }, [target])
  return val
}

export default function ScoreGauge({ score, tier, advice, reasons, improvements, what_if, confidence, ml_score, rule_score }) {
  const [animScore, setAnimScore] = useState(0)
  const meta = TIER_META[tier] || { color: '#6366f1', bg: '#6366f118', label: tier }

  useEffect(() => {
    let cur = 0
    const t = setInterval(() => {
      cur += 1.5
      if (cur >= score) { setAnimScore(score); clearInterval(t) }
      else setAnimScore(Math.round(cur))
    }, 16)
    return () => clearInterval(t)
  }, [score])

  // SVG gauge
  const R = 70, CX = 100, CY = 90
  const toRad = d => (d * Math.PI) / 180
  const arcX = a => CX + R * Math.cos(toRad(a))
  const arcY = a => CY + R * Math.sin(toRad(a))
  const startAngle = -180, endAngle = 0
  const scoreAngle = startAngle + (animScore / 100) * (endAngle - startAngle)
  const largeArc = scoreAngle - startAngle > 180 ? 1 : 0

  const confidenceColor = { High: '#22c55e', Medium: '#f59e0b', Low: '#ef4444' }[confidence] || '#6366f1'

  return (
    <div className="space-y-4 animate-in fade-in duration-500">

      {/* ── Main Score Card ── */}
      <div className="bg-white/5 border border-white/10 rounded-2xl p-6">
        <div className="flex items-center justify-between mb-5">
          <h2 className="text-sm font-semibold text-white/60">Placement Readiness Score</h2>
          {confidence && (
            <span className="text-xs px-2 py-0.5 rounded-full border font-medium"
              style={{ borderColor: confidenceColor + '60', color: confidenceColor, background: confidenceColor + '15' }}>
              {confidence} Confidence
            </span>
          )}
        </div>

        <div className="flex flex-col md:flex-row items-center gap-8">
          {/* Gauge */}
          <div className="flex-shrink-0">
            <svg viewBox="0 0 200 110" width="220" height="120">
              <path d={`M ${arcX(startAngle)} ${arcY(startAngle)} A ${R} ${R} 0 1 1 ${arcX(endAngle)} ${arcY(endAngle)}`}
                fill="none" stroke="rgba(255,255,255,0.08)" strokeWidth="12" strokeLinecap="round" />
              {animScore > 0 && (
                <path d={`M ${arcX(startAngle)} ${arcY(startAngle)} A ${R} ${R} 0 ${largeArc} 1 ${arcX(scoreAngle)} ${arcY(scoreAngle)}`}
                  fill="none" stroke={meta.color} strokeWidth="12" strokeLinecap="round"
                  style={{ filter: `drop-shadow(0 0 10px ${meta.color}80)` }} />
              )}
              <text x={CX} y={CY - 5} textAnchor="middle" fill="white" fontSize="30" fontWeight="bold">{animScore}</text>
              <text x={CX} y={CY + 14} textAnchor="middle" fill="rgba(255,255,255,0.35)" fontSize="10">out of 100</text>
            </svg>
            {/* ML vs Rule breakdown */}
            {ml_score !== undefined && (
              <div className="flex gap-3 justify-center mt-1 text-xs text-white/40">
                <span>ML: <span className="text-white/70">{ml_score}</span></span>
                <span>·</span>
                <span>Rules: <span className="text-white/70">{rule_score}</span></span>
              </div>
            )}
          </div>

          {/* Tier + Advice */}
          <div className="flex-1 space-y-3">
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full border text-sm font-semibold"
              style={{ borderColor: meta.color + '60', color: meta.color, background: meta.bg }}>
              {tier}
            </div>
            <p className="text-white/70 text-sm leading-relaxed whitespace-pre-line">{advice}</p>
          </div>
        </div>
      </div>

      {/* ── Reasons ── */}
      {reasons && reasons.length > 0 && (
        <div className="bg-white/5 border border-white/10 rounded-2xl p-5">
          <h3 className="text-sm font-semibold text-white/60 mb-3">Why this score?</h3>
          <ul className="space-y-2">
            {reasons.map((r, i) => (
              <li key={i} className="flex items-start gap-2 text-sm text-white/75 leading-snug">
                <span className="mt-0.5 shrink-0 text-base">{r.split(' ')[0]}</span>
                <span>{r.split(' ').slice(1).join(' ')}</span>
              </li>
            ))}
          </ul>
        </div>
      )}

      <div className="grid md:grid-cols-2 gap-4">
        {/* ── What-If Analysis ── */}
        {what_if && (
          <div className="bg-white/5 border border-white/10 rounded-2xl p-5">
            <h3 className="text-sm font-semibold text-white/60 mb-3">What-If Analysis 🔮</h3>
            <div className="space-y-3">
              {[
                { label: '+1 Internship', newScore: what_if.plus_1_internship, gain: what_if.score_gain_internship },
                { label: '+1 Project',    newScore: what_if.plus_1_project,    gain: what_if.score_gain_project },
              ].map(({ label, newScore, gain }) => (
                <div key={label} className="flex items-center justify-between bg-white/5 rounded-xl px-4 py-2.5">
                  <span className="text-sm text-white/70">{label}</span>
                  <div className="text-right">
                    <span className="text-sm font-bold text-white">{newScore}</span>
                    <span className={`ml-2 text-xs font-semibold ${gain > 0 ? 'text-emerald-400' : 'text-red-400'}`}>
                      {gain > 0 ? '+' : ''}{gain}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* ── Improvements ── */}
        {improvements && improvements.length > 0 && (
          <div className="bg-white/5 border border-white/10 rounded-2xl p-5">
            <h3 className="text-sm font-semibold text-white/60 mb-3">Actionable Improvements 🎯</h3>
            <ul className="space-y-2">
              {improvements.map((imp, i) => (
                <li key={i} className="flex items-start gap-2 text-sm text-white/75 leading-snug">
                  <span className="text-emerald-400 shrink-0 mt-0.5">→</span>
                  <span>{imp}</span>
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>
    </div>
  )
}
