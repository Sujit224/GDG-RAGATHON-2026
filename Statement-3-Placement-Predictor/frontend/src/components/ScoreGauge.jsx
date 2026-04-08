import { useEffect, useState } from 'react'

const TIER_COLORS = {
  'Placement Ready': '#22c55e',
  'Almost There': '#f59e0b',
  'Needs Improvement': '#f97316',
  'Early Stage': '#ef4444'
}

export default function ScoreGauge({ score, tier, advice }) {
  const [animatedScore, setAnimatedScore] = useState(0)

  useEffect(() => {
    let current = 0
    const timer = setInterval(() => {
      current += 2
      if (current >= score) { setAnimatedScore(score); clearInterval(timer) }
      else setAnimatedScore(current)
    }, 20)
    return () => clearInterval(timer)
  }, [score])

  // SVG arc math
  const R = 70, CX = 100, CY = 90
  const startAngle = -180
  const endAngle = 0
  const totalAngle = endAngle - startAngle
  const scoreAngle = startAngle + (animatedScore / 100) * totalAngle
  const toRad = deg => (deg * Math.PI) / 180
  const arcX = (angle) => CX + R * Math.cos(toRad(angle))
  const arcY = (angle) => CY + R * Math.sin(toRad(angle))
  const largeArc = scoreAngle - startAngle > 180 ? 1 : 0
  const color = TIER_COLORS[tier] || '#6366f1'

  return (
    <div className="bg-white/5 border border-white/10 rounded-2xl p-6 animate-in fade-in duration-500">
      <h2 className="text-sm font-semibold text-white/60 mb-6">Placement Readiness Score</h2>
      <div className="flex flex-col md:flex-row items-center gap-8">
        {/* Gauge SVG */}
        <div className="flex-shrink-0">
          <svg viewBox="0 0 200 110" width="220" height="120">
            {/* Background track */}
            <path
              d={`M ${arcX(startAngle)} ${arcY(startAngle)} A ${R} ${R} 0 1 1 ${arcX(endAngle)} ${arcY(endAngle)}`}
              fill="none" stroke="rgba(255,255,255,0.1)" strokeWidth="12" strokeLinecap="round"
            />
            {/* Score arc */}
            {animatedScore > 0 && (
              <path
                d={`M ${arcX(startAngle)} ${arcY(startAngle)} A ${R} ${R} 0 ${largeArc} 1 ${arcX(scoreAngle)} ${arcY(scoreAngle)}`}
                fill="none" stroke={color} strokeWidth="12" strokeLinecap="round"
                style={{ filter: `drop-shadow(0 0 8px ${color}60)` }}
              />
            )}
            {/* Score text */}
            <text x={CX} y={CY - 5} textAnchor="middle" fill="white" fontSize="28" fontWeight="bold">
              {animatedScore}
            </text>
            <text x={CX} y={CY + 14} textAnchor="middle" fill="rgba(255,255,255,0.4)" fontSize="10">
              out of 100
            </text>
          </svg>
        </div>

        {/* Tier and Advice */}
        <div className="flex-1 space-y-3">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full border text-sm font-medium"
            style={{ borderColor: color + '60', color, background: color + '15' }}>
            {tier}
          </div>
          <p className="text-white/70 text-sm leading-relaxed">{advice}</p>
        </div>
      </div>
    </div>
  )
}
