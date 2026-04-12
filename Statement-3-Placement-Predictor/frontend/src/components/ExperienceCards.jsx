export default function ExperienceCards({ experiences }) {
  if (!experiences || experiences.length === 0) return null

  // Detect whether these are cosine-matched (have match_score) or legacy RAG results
  const isCosineMatched = experiences[0]?.match_score !== undefined

  return (
    <div className="animate-in fade-in duration-500">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-sm font-semibold text-white/60">
          {isCosineMatched ? '🎯 Recommended Interview Experiences' : 'Relevant Senior Interview Experiences'}
        </h2>
        {isCosineMatched && (
          <span className="text-xs bg-indigo-500/15 text-indigo-300 px-2.5 py-0.5 rounded-full border border-indigo-500/20">
            Cosine Similarity Match
          </span>
        )}
      </div>

      <div className="grid md:grid-cols-3 gap-4">
        {experiences.map((exp, i) => {
          const matchPct = exp.match_score != null ? Math.round(exp.match_score * 100) : null

          return (
            <div
              key={i}
              className="bg-white/5 border border-white/10 rounded-2xl p-5 hover:border-indigo-500/40 transition group relative overflow-hidden"
            >
              {/* Match score glow bar */}
              {matchPct !== null && (
                <div
                  className="absolute inset-x-0 top-0 h-0.5 rounded-full"
                  style={{
                    background: `linear-gradient(90deg, transparent, ${matchPct >= 70 ? '#22c55e' : matchPct >= 40 ? '#f59e0b' : '#6366f1'}, transparent)`,
                    width: `${matchPct}%`
                  }}
                />
              )}

              {/* Header */}
              <div className="flex items-start justify-between mb-3">
                <div>
                  <div className="text-sm font-semibold text-white group-hover:text-indigo-200 transition">
                    {exp.company || 'Company'}
                  </div>
                  <div className="text-xs text-white/40 mt-0.5">
                    {exp.role || 'Software Engineer'}
                  </div>
                </div>
                <div className={`
                  text-xs font-bold px-2.5 py-1 rounded-full
                  ${matchPct !== null
                    ? matchPct >= 70
                      ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/30'
                      : matchPct >= 40
                        ? 'bg-amber-500/20 text-amber-300 border border-amber-500/30'
                        : 'bg-indigo-500/20 text-indigo-300 border border-indigo-500/30'
                    : 'bg-indigo-500/20 text-indigo-300'
                  }
                `}>
                  {matchPct !== null ? `${matchPct}%` : `#${i + 1}`}
                </div>
              </div>

              {/* Why recommended */}
              {exp.why_recommended && (
                <div className="bg-indigo-500/10 border border-indigo-500/20 rounded-xl px-3 py-2 mb-3">
                  <p className="text-xs text-indigo-200/80 leading-relaxed">
                    💡 {exp.why_recommended}
                  </p>
                </div>
              )}

              {/* Summary / Text */}
              <p className="text-xs text-white/60 leading-relaxed line-clamp-4">
                {exp.summary || exp.text || 'Interview experience details'}
              </p>

              {/* Tech stack tags */}
              {exp.tech_stack && exp.tech_stack.length > 0 && (
                <div className="mt-3 flex flex-wrap gap-1.5">
                  {exp.tech_stack.slice(0, 5).map((t, j) => (
                    <span
                      key={j}
                      className="text-xs bg-white/10 text-white/50 px-2 py-0.5 rounded-full hover:bg-white/15 hover:text-white/70 transition"
                    >
                      {t}
                    </span>
                  ))}
                </div>
              )}
            </div>
          )
        })}
      </div>
    </div>
  )
}
