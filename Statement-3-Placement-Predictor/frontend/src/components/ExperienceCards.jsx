export default function ExperienceCards({ experiences }) {
  return (
    <div className="animate-in fade-in duration-500">
      <h2 className="text-sm font-semibold text-white/60 mb-4">
        Relevant Senior Interview Experiences
      </h2>
      <div className="grid md:grid-cols-3 gap-4">
        {experiences.map((exp, i) => (
          <div key={i} className="bg-white/5 border border-white/10 rounded-2xl p-4 hover:border-indigo-500/40 transition">
            <div className="flex items-start justify-between mb-3">
              <div>
                <div className="text-sm font-semibold text-white">{exp.company || 'Company'}</div>
                <div className="text-xs text-white/40 mt-0.5">{exp.role || 'Software Engineer'}</div>
              </div>
              <div className="text-xs bg-indigo-500/20 text-indigo-300 px-2 py-0.5 rounded-full">
                #{i + 1}
              </div>
            </div>
            <p className="text-xs text-white/60 leading-relaxed line-clamp-5">
              {exp.text}
            </p>
            {exp.tech_stack && exp.tech_stack.length > 0 && (
              <div className="mt-3 flex flex-wrap gap-1">
                {exp.tech_stack.slice(0, 4).map((t, j) => (
                  <span key={j} className="text-xs bg-white/10 text-white/50 px-2 py-0.5 rounded-full">{t}</span>
                ))}
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  )
}
