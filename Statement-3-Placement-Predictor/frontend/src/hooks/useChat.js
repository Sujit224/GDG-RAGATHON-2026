import { useState } from 'react'
import { sendChat, getExperiences } from '../api/client'

export function useChat() {
  const [messages, setMessages]     = useState([])
  const [step, setStep]             = useState(1)   // 1=chat, 2=profile, 3=score, 4=experiences
  const [profile, setProfile]       = useState(null)
  const [score, setScore]           = useState(null)
  const [experiences, setExperiences] = useState([])
  const [loading, setLoading]       = useState(false)

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

        // Use prediction already computed by the backend (full pipeline)
        if (data.prediction) {
          setScore(data.prediction)
          setStep(3)
        }

        // Step 4: RAG experiences (still separate, lightweight)
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
