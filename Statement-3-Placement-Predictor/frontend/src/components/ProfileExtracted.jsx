const FIELD_LABELS = {
  cgpa: 'CGPA',
  tech_stack: 'Tech Stack',
  num_projects: 'Projects',
  num_internships: 'Internships',
  communication: 'Communication',
  opensource: 'Open Source Contributions'
}

export default function ProfileExtracted({ profile }) {
  return (
    <div className="bg-white/5 border border-white/10 rounded-2xl p-5 animate-in fade-in duration-500">
      <div className="flex items-center gap-2 mb-4">
        <div className="w-5 h-5 rounded-full bg-emerald-500 flex items-center justify-center text-xs">✓</div>
        <h2 className="text-sm font-semibold text-white/80">Profile Extracted</h2>
        <span className="ml-auto text-xs text-white/30 font-mono">JSON</span>
      </div>
      <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
        {Object.entries(FIELD_LABELS).map(([key, label]) => (
          <div key={key} className="bg-white/5 rounded-xl p-3">
            <div className="text-xs text-white/40 mb-1">{label}</div>
            <div className="text-sm font-medium text-white">
              {Array.isArray(profile[key])
                ? profile[key].join(', ') || '—'
                : profile[key] ?? '—'}
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
