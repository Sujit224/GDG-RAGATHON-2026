import axios from 'axios'

const api = axios.create({ baseURL: 'http://localhost:8000/api' })

// ── Existing ──────────────────────────────────────────────────────────────────
export const sendChat       = (messages)    => api.post('/chat', { messages })
export const getPrediction  = (profile)     => api.post('/predict', profile)
export const getExperiences = (tech_stack)  => api.post('/rag', { tech_stack, top_k: 3 })

// ── Resume Pipeline ───────────────────────────────────────────────────────────

/** Upload PDF/DOCX → full pipeline (parse + predict + match) */
export const uploadResume = (file, top_k = 3) => {
  const form = new FormData()
  form.append('file', file)
  return api.post(`/upload_resume?top_k=${top_k}`, form, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
}

/** Upload PDF/DOCX → parsed profile JSON only */
export const extractProfile = (file) => {
  const form = new FormData()
  form.append('file', file)
  return api.post('/extract', form, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
}

/** POST profile JSON → cosine-matched experiences */
export const matchExperiences = (profile, top_k = 3) =>
  api.post('/match', { ...profile, top_k })

/** POST profile JSON → full pipeline (no file, manual input) */
export const analyzeProfile = (profile, top_k = 3) =>
  api.post('/analyze', { ...profile, top_k })
