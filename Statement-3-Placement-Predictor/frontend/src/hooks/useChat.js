import { useState, useCallback } from 'react'
import { sendChat, getExperiences, uploadResume } from '../api/client'

export function useChat() {
  const [messages, setMessages]       = useState([])
  const [step, setStep]               = useState(1)   // 1=chat, 2=profile, 3=score, 4=experiences
  const [profile, setProfile]         = useState(null)
  const [score, setScore]             = useState(null)
  const [experiences, setExperiences] = useState([])
  const [loading, setLoading]         = useState(false)

  async function sendMessage(userText) {
    const newMessages = [...messages, { role: 'user', content: userText }]
    setMessages(newMessages)
    setLoading(true)

    try {
      const { data } = await sendChat(newMessages)
      const updatedMessages = [...newMessages, { role: 'assistant', content: data.reply }]
      setMessages(updatedMessages)

      if (data.profile_complete && data.profile) {
        setProfile(data.profile)
        setStep(2)

        if (data.prediction) {
          setScore(data.prediction)
          setStep(3)
        }

        const techStack = data.profile.tech_stack || []
        if (techStack.length > 0) {
          try {
            const { data: ragData } = await getExperiences(techStack)
            setExperiences(ragData.experiences || [])
          } catch {
            setExperiences([])
          }
        }
        setStep(4)
      }
    } catch (e) {
      console.error('Chat error:', e)
    } finally {
      setLoading(false)
    }
  }

  function reset() {
    setMessages([])
    setStep(1)
    setProfile(null)
    setScore(null)
    setExperiences([])
  }

  return { messages, step, profile, score, experiences, loading, sendMessage, reset }
}


export function useResumeUpload() {
  const [phase, setPhase]             = useState('idle')  // idle | uploading | done | error
  const [profile, setProfile]         = useState(null)
  const [score, setScore]             = useState(null)
  const [experiences, setExperiences] = useState([])
  const [error, setError]             = useState(null)
  const [fileName, setFileName]       = useState(null)

  const upload = useCallback(async (file) => {
    setPhase('uploading')
    setError(null)
    setFileName(file.name)

    try {
      const { data } = await uploadResume(file, 3)

      setProfile(data.profile)
      setScore({
        score:        data.score,
        ml_score:     data.ml_score,
        rule_score:   data.rule_score,
        tier:         data.tier,
        reasons:      data.reasons,
        improvements: data.improvements,
        advice:       data.advice,
        confidence:   data.confidence,
        what_if:      data.what_if,
        feature_importance: data.feature_importance || {},
      })
      setExperiences(data.recommended_experiences || [])
      setPhase('done')
    } catch (err) {
      const msg = err?.response?.data?.detail || err.message || 'Upload failed'
      setError(msg)
      setPhase('error')
    }
  }, [])

  const reset = useCallback(() => {
    setPhase('idle')
    setProfile(null)
    setScore(null)
    setExperiences([])
    setError(null)
    setFileName(null)
  }, [])

  return { phase, profile, score, experiences, error, fileName, upload, reset }
}
