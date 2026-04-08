const STEPS = [
  { id: 1, label: 'Chat Profiling' },
  { id: 2, label: 'Profile Extracted' },
  { id: 3, label: 'Score Generated' },
  { id: 4, label: 'Experiences Found' }
]

export default function StepProgress({ currentStep }) {
  return (
    <div className="flex items-center justify-center gap-0">
      {STEPS.map((s, i) => (
        <div key={s.id} className="flex items-center">
          <div className={`flex flex-col items-center gap-1`}>
            <div className={`w-8 h-8 rounded-full flex items-center justify-center text-xs font-bold transition-all duration-500
              ${currentStep >= s.id ? 'bg-indigo-500 text-white shadow-lg shadow-indigo-500/40' : 'bg-white/10 text-white/30'}`}>
              {currentStep > s.id ? '✓' : s.id}
            </div>
            <span className={`text-xs whitespace-nowrap ${currentStep >= s.id ? 'text-white/80' : 'text-white/30'}`}>
              {s.label}
            </span>
          </div>
          {i < STEPS.length - 1 && (
            <div className={`h-0.5 w-16 mb-5 mx-1 transition-all duration-700 ${currentStep > s.id ? 'bg-indigo-500' : 'bg-white/10'}`} />
          )}
        </div>
      ))}
    </div>
  )
}
