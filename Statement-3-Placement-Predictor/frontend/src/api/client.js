import axios from 'axios'

const api = axios.create({ baseURL: 'http://localhost:8000/api' })

export const sendChat = (messages) => api.post('/chat', { messages })
export const getPrediction = (profile) => api.post('/predict', profile)
export const getExperiences = (tech_stack) => api.post('/rag', { tech_stack, top_k: 3 })
