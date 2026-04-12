import { useState, useCallback, useMemo } from "react";
import axios from "axios";
import { motion as Motion, AnimatePresence } from "framer-motion";

const API_BASE = import.meta.env.VITE_API_URL ?? "http://127.0.0.1:8000";

const client = axios.create({ baseURL: API_BASE, timeout: 120000 });

function cn(...parts) {
  return parts.filter(Boolean).join(" ");
}

function ScoreRing({ score, size = 160, stroke = 10 }) {
  const r = (size - stroke) / 2;
  const c = 2 * Math.PI * r;
  const pct = Math.min(100, Math.max(0, score)) / 100;
  const offset = c * (1 - pct);

  const hue =
    score >= 75 ? 175 : score >= 50 ? 200 : 280;

  return (
    <div className="relative shrink-0" style={{ width: size, height: size }}>
      <svg width={size} height={size} className="-rotate-90">
        <circle
          cx={size / 2}
          cy={size / 2}
          r={r}
          fill="none"
          stroke="oklch(0.25 0.02 260)"
          strokeWidth={stroke}
        />
        <Motion.circle
          cx={size / 2}
          cy={size / 2}
          r={r}
          fill="none"
          stroke={`oklch(0.72 0.14 ${hue})`}
          strokeWidth={stroke}
          strokeLinecap="round"
          strokeDasharray={c}
          initial={{ strokeDashoffset: c }}
          animate={{ strokeDashoffset: offset }}
          transition={{ duration: 1.1, ease: [0.22, 1, 0.36, 1] }}
        />
      </svg>
      <div className="absolute inset-0 flex flex-col items-center justify-center">
        <span className="font-mono text-3xl font-semibold tabular-nums tracking-tight text-white">
          {Number(score).toFixed(1)}
        </span>
        <span className="text-[11px] uppercase tracking-[0.2em] text-zinc-500">
          readiness
        </span>
      </div>
    </div>
  );
}

function Pill({ children, tone = "neutral" }) {
  const tones = {
    neutral: "bg-white/5 text-zinc-300 border-white/10",
    good: "bg-emerald-500/15 text-emerald-200 border-emerald-500/25",
    warn: "bg-amber-500/15 text-amber-200 border-amber-500/25",
    bad: "bg-rose-500/12 text-rose-200 border-rose-500/22",
    accent: "bg-cyan-500/12 text-cyan-200 border-cyan-500/25",
  };
  return (
    <span
      className={cn(
        "inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-medium",
        tones[tone] ?? tones.neutral
      )}
    >
      {children}
    </span>
  );
}

const tabs = [
  { id: "overview", label: "Overview" },
  { id: "analysis", label: "AI analysis" },
  { id: "interviews", label: "Interview prep" },
  { id: "plan", label: "Roadmap" },
];

export default function App() {
  const [text, setText] = useState("");
  const [file, setFile] = useState(null);
  const [role, setRole] = useState("SDE");
  const [result, setResult] = useState(null);
  const [simulateResult, setSimulateResult] = useState(null);
  const [loading, setLoading] = useState({ predict: false, upload: false, simulate: false });
  const [error, setError] = useState(null);
  const [activeTab, setActiveTab] = useState("overview");
  const [inputMode, setInputMode] = useState("paste");

  const [simProjects, setSimProjects] = useState(3);
  const [simExperience, setSimExperience] = useState(2);
  const [simDsa, setSimDsa] = useState(7);

  const onDrag = useCallback((e) => {
    e.preventDefault();
    e.stopPropagation();
  }, []);

  const onDrop = useCallback((e) => {
    e.preventDefault();
    e.stopPropagation();
    const f = e.dataTransfer.files?.[0];
    if (f?.type === "application/pdf") setFile(f);
  }, []);

  const handlePredict = async () => {
    setError(null);
    setLoading((s) => ({ ...s, predict: true }));
    try {
      const res = await client.post("/predict", { text, role });
      setResult(res.data);
      setSimulateResult(null);
      setActiveTab("overview");
    } catch (e) {
      setError(e.response?.data?.detail ?? e.message ?? "Prediction failed");
    } finally {
      setLoading((s) => ({ ...s, predict: false }));
    }
  };

  const handleUpload = async () => {
    if (!file) {
      setError("Choose a PDF resume first.");
      return;
    }
    setError(null);
    setLoading((s) => ({ ...s, upload: true }));
    const formData = new FormData();
    formData.append("file", file);
    try {
      const res = await client.post("/upload-resume", formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });
      setResult(res.data);
      setSimulateResult(null);
      setActiveTab("overview");
    } catch (e) {
      setError(e.response?.data?.detail ?? e.message ?? "Upload failed");
    } finally {
      setLoading((s) => ({ ...s, upload: false }));
    }
  };

  const handleSimulate = async () => {
    const hasText = Boolean(text.trim());
    const hasProfile = Boolean(result?.profile);
    if (!hasText && !hasProfile) {
      setError("Run analysis first (paste text or upload PDF), then simulate.");
      return;
    }
    setError(null);
    setLoading((s) => ({ ...s, simulate: true }));
    try {
      const res = await client.post("/simulate", {
        text: hasText ? text : undefined,
        profile: !hasText ? result?.profile : undefined,
        changes: {
          projects: simProjects,
          experience: simExperience,
          dsa: simDsa,
        },
      });
      setSimulateResult(res.data);
    } catch (e) {
      setError(e.response?.data?.detail ?? e.message ?? "Simulation failed");
    } finally {
      setLoading((s) => ({ ...s, simulate: false }));
    }
  };

  const levelTone = useMemo(() => {
    if (!result?.level) return "neutral";
    if (result.level.includes("High")) return "good";
    if (result.level.includes("Moderate")) return "warn";
    return "bad";
  }, [result]);

  return (
    <div className="relative min-h-screen overflow-x-hidden">
      <div className="pointer-events-none fixed inset-0 grid-bg opacity-40" />
      <div className="pointer-events-none fixed inset-0 bg-[radial-gradient(ellipse_60%_40%_at_50%_0%,oklch(0.4_0.12_280/0.15),transparent)]" />

      <div className="relative z-10 mx-auto max-w-6xl px-4 pb-24 pt-12 sm:px-6 lg:px-8">
        <Motion.header
          className="mb-12 text-center"
          initial={{ opacity: 0, y: -12 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
        >
          <p className="mb-3 font-mono text-xs uppercase tracking-[0.35em] text-cyan-400/90">
            GDG · RAGATHON 2026
          </p>
          <h1 className="text-4xl font-bold tracking-tight sm:text-5xl md:text-6xl">
            <span className="text-gradient">Placement Predictor</span>
          </h1>
          <p className="mx-auto mt-4 max-w-2xl text-base text-zinc-400 sm:text-lg">
            Upload a resume or paste text. Get a readiness score, skill gaps, company
            suggestions, and interview snippets grounded in your profile.
          </p>
        </Motion.header>

        <div className="grid gap-8 lg:grid-cols-5">
          {/* Input column */}
          <Motion.section
            className="glass rounded-2xl p-6 lg:col-span-2"
            initial={{ opacity: 0, y: 16 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.08 }}
          >
            <div className="mb-5 flex rounded-xl bg-black/30 p-1">
              {["paste", "pdf"].map((m) => (
                <button
                  key={m}
                  type="button"
                  onClick={() => setInputMode(m)}
                  className={cn(
                    "flex-1 rounded-lg py-2 text-sm font-medium transition-colors",
                    inputMode === m
                      ? "bg-white/10 text-white shadow-sm"
                      : "text-zinc-500 hover:text-zinc-300"
                  )}
                >
                  {m === "paste" ? "Paste text" : "PDF upload"}
                </button>
              ))}
            </div>

            <label className="mb-2 block text-xs font-medium uppercase tracking-wider text-zinc-500">
              Target role
            </label>
            <div className="mb-5 flex gap-2">
              {["SDE", "ML"].map((r) => (
                <button
                  key={r}
                  type="button"
                  onClick={() => setRole(r)}
                  className={cn(
                    "rounded-lg border px-4 py-2 text-sm font-medium transition-all",
                    role === r
                      ? "border-cyan-500/50 bg-cyan-500/15 text-cyan-100"
                      : "border-white/10 bg-transparent text-zinc-400 hover:border-white/20"
                  )}
                >
                  {r}
                </button>
              ))}
              <span className="ml-auto self-center text-[11px] text-zinc-600">
                PDF path uses SDE on server
              </span>
            </div>

            <AnimatePresence mode="wait">
              {inputMode === "paste" ? (
                <Motion.div
                  key="paste"
                  initial={{ opacity: 0, x: -8 }}
                  animate={{ opacity: 1, x: 0 }}
                  exit={{ opacity: 0, x: 8 }}
                >
                  <textarea
                    className="mb-4 min-h-[200px] w-full resize-y rounded-xl border border-white/10 bg-black/40 px-4 py-3 text-sm text-zinc-100 placeholder:text-zinc-600 focus:border-cyan-500/40 focus:outline-none focus:ring-2 focus:ring-cyan-500/20"
                    placeholder="Paste your resume or LinkedIn-style summary…"
                    value={text}
                    onChange={(e) => setText(e.target.value)}
                  />
                  <button
                    type="button"
                    onClick={handlePredict}
                    disabled={loading.predict || !text.trim()}
                    className="flex w-full items-center justify-center gap-2 rounded-xl bg-gradient-to-r from-cyan-600 to-sky-600 py-3 text-sm font-semibold text-white shadow-lg shadow-cyan-900/30 transition hover:brightness-110 disabled:cursor-not-allowed disabled:opacity-40"
                  >
                    {loading.predict ? (
                      <span className="inline-block h-4 w-4 animate-spin rounded-full border-2 border-white/30 border-t-white" />
                    ) : null}
                    Analyze profile
                  </button>
                </Motion.div>
              ) : (
                <Motion.div
                  key="pdf"
                  initial={{ opacity: 0, x: 8 }}
                  animate={{ opacity: 1, x: 0 }}
                  exit={{ opacity: 0, x: -8 }}
                >
                  <div
                    role="button"
                    tabIndex={0}
                    onKeyDown={(e) => e.key === "Enter" && document.getElementById("pdf-input")?.click()}
                    onDragEnter={onDrag}
                    onDragOver={onDrag}
                    onDrop={onDrop}
                    onClick={() => document.getElementById("pdf-input")?.click()}
                    className="mb-4 flex cursor-pointer flex-col items-center justify-center rounded-xl border-2 border-dashed border-white/15 bg-black/25 px-6 py-14 transition hover:border-cyan-500/35 hover:bg-black/35"
                  >
                    <span className="mb-2 text-3xl opacity-80">📄</span>
                    <p className="text-center text-sm text-zinc-300">
                      Drop a PDF here or{" "}
                      <span className="text-cyan-400 underline-offset-4 hover:underline">browse</span>
                    </p>
                    {file && (
                      <p className="mt-3 font-mono text-xs text-emerald-400/90">{file.name}</p>
                    )}
                    <input
                      id="pdf-input"
                      type="file"
                      accept="application/pdf"
                      className="hidden"
                      onChange={(e) => setFile(e.target.files?.[0] ?? null)}
                    />
                  </div>
                  <button
                    type="button"
                    onClick={handleUpload}
                    disabled={loading.upload || !file}
                    className="flex w-full items-center justify-center gap-2 rounded-xl border border-emerald-500/40 bg-emerald-500/15 py-3 text-sm font-semibold text-emerald-100 transition hover:bg-emerald-500/25 disabled:cursor-not-allowed disabled:opacity-40"
                  >
                    {loading.upload ? (
                      <span className="inline-block h-4 w-4 animate-spin rounded-full border-2 border-emerald-400/30 border-t-emerald-200" />
                    ) : null}
                    Extract &amp; score
                  </button>
                </Motion.div>
              )}
            </AnimatePresence>

            {error && (
              <Motion.p
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                className="mt-4 rounded-lg border border-rose-500/30 bg-rose-500/10 px-3 py-2 text-sm text-rose-200"
              >
                {error}
              </Motion.p>
            )}
          </Motion.section>

          {/* Results column */}
          <section className="lg:col-span-3">
            <AnimatePresence mode="wait">
              {!result ? (
                <Motion.div
                  key="empty"
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  exit={{ opacity: 0 }}
                  className="glass flex min-h-[420px] flex-col items-center justify-center rounded-2xl p-10 text-center"
                >
                  <div className="mb-4 h-px w-24 bg-gradient-to-r from-transparent via-cyan-500/50 to-transparent" />
                  <p className="max-w-md text-zinc-500">
                    Results appear here: score ring, confidence, recommended companies, weaknesses,
                    and RAG-backed interview notes—once you run an analysis.
                  </p>
                </Motion.div>
              ) : (
                <Motion.div
                  key="has-result"
                  initial={{ opacity: 0, y: 12 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="glass overflow-hidden rounded-2xl"
                >
                  <div className="border-b border-white/10 p-6 sm:p-8">
                    <div className="flex flex-col gap-8 sm:flex-row sm:items-start sm:justify-between">
                      <div className="flex flex-col items-center gap-6 sm:flex-row sm:items-start">
                        <ScoreRing score={result.score} />
                        <div className="text-center sm:text-left">
                          <div className="mb-2 flex flex-wrap items-center justify-center gap-2 sm:justify-start">
                            <Pill tone={levelTone}>{result.level}</Pill>
                            <Pill tone="accent">{result.profile_type}</Pill>
                          </div>
                          <h2 className="text-xl font-semibold text-white">Your readiness snapshot</h2>
                          <p className="mt-1 text-sm text-zinc-400">
                            Confidence signal:{" "}
                            <span className="font-mono text-zinc-200">{result.confidence}</span>
                            <span className="text-zinc-600"> / 100</span>
                          </p>
                          <div className="mt-3 h-2 max-w-xs overflow-hidden rounded-full bg-white/10">
                            <Motion.div
                              className="h-full rounded-full bg-gradient-to-r from-cyan-500 to-violet-500"
                              initial={{ width: 0 }}
                              animate={{ width: `${Math.min(100, result.confidence)}%` }}
                              transition={{ duration: 0.8, ease: "easeOut" }}
                            />
                          </div>
                        </div>
                      </div>
                      <div className="w-full sm:max-w-[220px]">
                        <p className="mb-2 text-xs font-medium uppercase tracking-wider text-zinc-500">
                          Companies
                        </p>
                        <div className="flex flex-wrap gap-2">
                          {result.recommended_companies?.map((c) => (
                            <Pill key={c} tone="good">
                              {c}
                            </Pill>
                          ))}
                        </div>
                      </div>
                    </div>
                  </div>

                  <div className="flex flex-wrap gap-1 border-b border-white/10 px-4 pt-2">
                    {tabs.map((t) => (
                      <button
                        key={t.id}
                        type="button"
                        onClick={() => setActiveTab(t.id)}
                        className={cn(
                          "relative rounded-t-lg px-4 py-2.5 text-sm font-medium transition-colors",
                          activeTab === t.id ? "text-white" : "text-zinc-500 hover:text-zinc-300"
                        )}
                      >
                        {t.label}
                        {activeTab === t.id && (
                          <Motion.span
                            layoutId="tab"
                            className="absolute inset-x-2 bottom-0 h-0.5 rounded-full bg-cyan-400"
                          />
                        )}
                      </button>
                    ))}
                  </div>

                  <div className="p-6 sm:p-8">
                    {activeTab === "overview" && (
                      <Motion.div
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        className="space-y-6"
                      >
                        <div>
                          <h3 className="mb-2 text-sm font-semibold text-zinc-300">Detected skills</h3>
                          <div className="flex flex-wrap gap-2">
                            {result.profile?.skills?.map((s) => (
                              <span
                                key={s}
                                className="rounded-md border border-white/10 bg-white/5 px-2 py-1 text-xs text-zinc-300"
                              >
                                {s}
                              </span>
                            ))}
                          </div>
                        </div>
                        <div className="grid gap-4 sm:grid-cols-2">
                          <div className="rounded-xl border border-rose-500/20 bg-rose-500/5 p-4">
                            <h3 className="mb-2 text-sm font-semibold text-rose-200/90">Weaknesses</h3>
                            <ul className="space-y-1.5 text-sm text-zinc-400">
                              {result.weaknesses?.map((w, i) => (
                                <li key={i} className="flex gap-2">
                                  <span className="text-rose-400/80">—</span>
                                  {w}
                                </li>
                              ))}
                            </ul>
                          </div>
                          <div className="rounded-xl border border-amber-500/20 bg-amber-500/5 p-4">
                            <h3 className="mb-2 text-sm font-semibold text-amber-200/90">Skill gaps</h3>
                            <ul className="space-y-1.5 text-sm text-zinc-400">
                              {result.skill_gaps?.map((g, i) => (
                                <li key={i} className="flex gap-2">
                                  <span className="text-amber-400/80">→</span>
                                  {g}
                                </li>
                              ))}
                            </ul>
                          </div>
                        </div>
                      </Motion.div>
                    )}

                    {activeTab === "analysis" && (
                      <Motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
                        <div className="prose prose-invert prose-sm max-w-none">
                          <p className="whitespace-pre-wrap leading-relaxed text-zinc-300">
                            {result.analysis}
                          </p>
                        </div>
                      </Motion.div>
                    )}

                    {activeTab === "interviews" && (
                      <Motion.div
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        className="space-y-4"
                      >
                        {result.interviews?.length ? (
                          result.interviews.map((chunk, i) => (
                            <div
                              key={i}
                              className="rounded-xl border border-violet-500/20 bg-violet-500/5 p-4"
                            >
                              <p className="mb-2 font-mono text-[10px] uppercase tracking-widest text-violet-400/80">
                                Match {i + 1}
                              </p>
                              <p className="text-sm leading-relaxed text-zinc-300 whitespace-pre-wrap">
                                {chunk}
                              </p>
                            </div>
                          ))
                        ) : (
                          <p className="text-zinc-500">No interview snippets returned.</p>
                        )}
                      </Motion.div>
                    )}

                    {activeTab === "plan" && (
                      <Motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
                        <ol className="space-y-3">
                          {result.roadmap?.map((step, i) => (
                            <li
                              key={i}
                              className="flex gap-4 rounded-xl border border-cyan-500/15 bg-cyan-500/5 px-4 py-3"
                            >
                              <span className="font-mono text-sm text-cyan-400/90">
                                {(i + 1).toString().padStart(2, "0")}
                              </span>
                              <span className="text-sm text-zinc-300">{step}</span>
                            </li>
                          ))}
                        </ol>
                      </Motion.div>
                    )}
                  </div>
                </Motion.div>
              )}
            </AnimatePresence>

            {/* Simulator */}
            <Motion.section
              className="glass mt-8 rounded-2xl p-6 sm:p-8"
              initial={{ opacity: 0, y: 12 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.15 }}
            >
              <div className="mb-6 flex flex-col gap-2 sm:flex-row sm:items-end sm:justify-between">
                <div>
                  <h2 className="text-lg font-semibold text-white">What-if simulator</h2>
                  <p className="text-sm text-zinc-500">
                    Adjust levers and see how your score could move—uses the same text you pasted.
                  </p>
                </div>
                <button
                  type="button"
                  onClick={handleSimulate}
                  disabled={loading.simulate || (!text.trim() && !result?.profile)}
                  className="shrink-0 rounded-xl border border-violet-500/40 bg-violet-500/15 px-5 py-2.5 text-sm font-semibold text-violet-100 transition hover:bg-violet-500/25 disabled:cursor-not-allowed disabled:opacity-40"
                >
                  {loading.simulate ? "Running…" : "Run simulation"}
                </button>
              </div>

              <div className="grid gap-6 sm:grid-cols-3">
                {[
                  { label: "Projects", value: simProjects, set: setSimProjects, max: 10 },
                  { label: "Experience (yrs)", value: simExperience, set: setSimExperience, max: 5 },
                  { label: "DSA level", value: simDsa, set: setSimDsa, max: 10 },
                ].map((s) => (
                  <div key={s.label}>
                    <div className="mb-2 flex justify-between text-xs text-zinc-500">
                      <span>{s.label}</span>
                      <span className="font-mono text-zinc-300">{s.value}</span>
                    </div>
                    <input
                      type="range"
                      min={0}
                      max={s.max}
                      step={1}
                      value={s.value}
                      onChange={(e) => s.set(Number(e.target.value))}
                      className="h-2 w-full cursor-pointer appearance-none rounded-full bg-white/10 accent-violet-500"
                    />
                  </div>
                ))}
              </div>

              <AnimatePresence>
                {simulateResult && (
                  <Motion.div
                    initial={{ opacity: 0, height: 0 }}
                    animate={{ opacity: 1, height: "auto" }}
                    exit={{ opacity: 0 }}
                    className="mt-8 overflow-hidden rounded-xl border border-violet-500/25 bg-gradient-to-br from-violet-500/10 to-transparent p-5"
                  >
                    <div className="flex flex-wrap items-end gap-6">
                      <div>
                        <p className="text-xs uppercase tracking-wider text-zinc-500">Current</p>
                        <p className="font-mono text-2xl text-zinc-200">
                          {simulateResult.current_score?.toFixed(2)}
                        </p>
                      </div>
                      <div className="text-2xl text-zinc-600">→</div>
                      <div>
                        <p className="text-xs uppercase tracking-wider text-zinc-500">After changes</p>
                        <p className="font-mono text-2xl text-emerald-300">
                          {simulateResult.improved_score?.toFixed(2)}
                        </p>
                      </div>
                      <Pill tone="good">Impact +{simulateResult.impact}</Pill>
                    </div>
                    <p className="mt-4 text-sm text-violet-200/90">{simulateResult.message}</p>
                  </Motion.div>
                )}
              </AnimatePresence>
            </Motion.section>
          </section>
        </div>

        <footer className="mt-16 text-center text-xs text-zinc-600">
          API: <span className="font-mono text-zinc-500">{API_BASE}</span>
          {" · "}
          Set <code className="rounded bg-white/5 px-1 py-0.5 font-mono text-zinc-400">VITE_API_URL</code> to point
          your backend.
        </footer>
      </div>
    </div>
  );
}
