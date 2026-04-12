const FIELD_MAP = [
  { key: 'cgpa',          label: 'CGPA',           icon: '🎓' },
  { key: 'tech_stack',    label: 'Tech Stack',     icon: '⚡' },
  { key: 'projects',      alt: 'num_projects',     label: 'Projects',     icon: '🚀' },
  { key: 'internships',   alt: 'num_internships',  label: 'Internships',  icon: '💼' },
  { key: 'communication', label: 'Communication',  icon: '🗣️' },
  { key: 'open_source',   alt: 'opensource',       label: 'Open Source',  icon: '🌐' },
]

export default function ProfileExtracted({ profile }) {
  return (
    <div className="bg-white/5 border border-white/10 rounded-2xl p-5 animate-in fade-in duration-500">
      <div className="flex items-center gap-2 mb-4">
        <div className="w-5 h-5 rounded-full bg-emerald-500 flex items-center justify-center text-xs">✓</div>
        <h2 className="text-sm font-semibold text-white/80">Extracted Profile</h2>
        <span className="ml-auto text-xs text-white/30 font-mono">JSON</span>
      </div>
      <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
        {FIELD_MAP.map(({ key, alt, label, icon }) => {
          const val = profile[key] ?? (alt ? profile[alt] : undefined) ?? '—'
          const display = Array.isArray(val)
            ? (val.length > 0 ? val.join(', ') : '—')
            : val

          return (
            <div key={key} className="bg-white/5 rounded-xl p-3 hover:bg-white/[0.07] transition">
              <div className="text-xs text-white/40 mb-1 flex items-center gap-1">
                <span>{icon}</span> {label}
              </div>
              <div className="text-sm font-medium text-white truncate" title={String(display)}>
                {String(display)}
              </div>
            </div>
          )
        })}
      </div>
    </div>
  )
}
