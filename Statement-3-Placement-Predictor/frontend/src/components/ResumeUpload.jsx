import { useRef, useState } from 'react'

const PHASES = {
  idle:      { icon: '📄', title: 'Upload Your Resume', subtitle: 'Drag & drop or click to browse' },
  uploading: { icon: '⚡', title: 'Analyzing Resume…',  subtitle: 'Parsing → Predicting → Matching' },
  done:      { icon: '✅', title: 'Analysis Complete',   subtitle: 'Your full report is ready below' },
  error:     { icon: '❌', title: 'Upload Failed',       subtitle: 'Please try again' },
}

export default function ResumeUpload({ phase, fileName, error, onUpload, onReset }) {
  const inputRef = useRef(null)
  const [isDragging, setIsDragging] = useState(false)

  const meta = PHASES[phase] || PHASES.idle

  const handleFile = (file) => {
    if (!file) return
    const ext = file.name.split('.').pop().toLowerCase()
    if (!['pdf', 'docx', 'doc'].includes(ext)) {
      alert('Please upload a PDF or DOCX file.')
      return
    }
    if (file.size > 10 * 1024 * 1024) {
      alert('File too large (max 10 MB).')
      return
    }
    onUpload(file)
  }

  const onDrop = (e) => {
    e.preventDefault()
    setIsDragging(false)
    const file = e.dataTransfer?.files?.[0]
    handleFile(file)
  }

  const onChange = (e) => {
    handleFile(e.target.files?.[0])
    e.target.value = ''
  }

  if (phase === 'done') {
    return (
      <div className="bg-emerald-500/10 border border-emerald-500/30 rounded-2xl p-5 animate-in fade-in duration-500">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-emerald-500/20 flex items-center justify-center text-lg">✅</div>
            <div>
              <div className="text-sm font-semibold text-emerald-300">Analysis Complete</div>
              <div className="text-xs text-white/40 mt-0.5">{fileName}</div>
            </div>
          </div>
          <button
            onClick={onReset}
            className="text-xs text-white/50 hover:text-white border border-white/20 px-3 py-1 rounded-full transition"
          >
            Upload Another
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className="animate-in fade-in duration-500">
      {/* Drop zone */}
      <div
        onDragOver={(e) => { e.preventDefault(); setIsDragging(true) }}
        onDragLeave={() => setIsDragging(false)}
        onDrop={onDrop}
        onClick={() => phase === 'idle' && inputRef.current?.click()}
        className={`
          relative overflow-hidden rounded-2xl border-2 border-dashed p-8
          flex flex-col items-center justify-center gap-4 cursor-pointer
          transition-all duration-300
          ${isDragging
            ? 'border-indigo-400 bg-indigo-500/10 scale-[1.01]'
            : phase === 'error'
              ? 'border-red-500/40 bg-red-500/5'
              : phase === 'uploading'
                ? 'border-indigo-500/40 bg-indigo-500/5 cursor-wait'
                : 'border-white/15 bg-white/5 hover:border-indigo-500/40 hover:bg-white/[0.07]'
          }
        `}
      >
        {/* Shimmer bar for uploading */}
        {phase === 'uploading' && (
          <div className="absolute inset-x-0 top-0 h-1">
            <div className="h-full w-1/3 bg-gradient-to-r from-transparent via-indigo-400 to-transparent animate-shimmer rounded-full" />
          </div>
        )}

        {/* Icon */}
        <div className={`
          w-16 h-16 rounded-2xl flex items-center justify-center text-2xl
          ${phase === 'uploading'
            ? 'bg-indigo-500/20 animate-pulse'
            : phase === 'error'
              ? 'bg-red-500/20'
              : 'bg-white/10'}
        `}>
          {meta.icon}
        </div>

        {/* Text */}
        <div className="text-center">
          <div className="text-base font-semibold text-white/90">{meta.title}</div>
          <div className="text-sm text-white/40 mt-1">{meta.subtitle}</div>
        </div>

        {/* File info */}
        {fileName && phase === 'uploading' && (
          <div className="flex items-center gap-2 bg-white/5 rounded-xl px-4 py-2">
            <svg className="w-4 h-4 text-indigo-400 animate-spin" viewBox="0 0 24 24" fill="none">
              <circle cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="3" strokeDasharray="30 60" />
            </svg>
            <span className="text-xs text-white/60">{fileName}</span>
          </div>
        )}

        {/* Error detail */}
        {phase === 'error' && error && (
          <div className="bg-red-500/10 border border-red-500/30 rounded-xl px-4 py-2 text-xs text-red-300 max-w-md text-center">
            {error}
          </div>
        )}

        {/* Reset on error */}
        {phase === 'error' && (
          <button
            onClick={(e) => { e.stopPropagation(); onReset() }}
            className="text-xs bg-white/10 hover:bg-white/20 px-4 py-1.5 rounded-lg transition"
          >
            Try Again
          </button>
        )}

        {/* Accepted formats badge */}
        {phase === 'idle' && (
          <div className="flex gap-2 mt-1">
            {['PDF', 'DOCX'].map(fmt => (
              <span key={fmt} className="text-xs bg-white/10 text-white/40 px-2.5 py-0.5 rounded-full">
                .{fmt.toLowerCase()}
              </span>
            ))}
            <span className="text-xs text-white/25">Max 10 MB</span>
          </div>
        )}

        <input
          ref={inputRef}
          type="file"
          accept=".pdf,.docx,.doc"
          onChange={onChange}
          className="hidden"
        />
      </div>
    </div>
  )
}
