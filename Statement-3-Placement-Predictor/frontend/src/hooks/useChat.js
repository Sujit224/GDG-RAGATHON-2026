import { useState } from 'react'
import { sendChat, getPrediction, getExperiences } from '../api/client'

export function useChat() {
  const [messages, setMessages] = useState([])          // chat history
  const [step, setStep] = useState(1)                   // 1=chat, 2=profile, 3=score, 4=experiences
  const [profile, setProfile] = useState(null)
  const [score, setScore] = useState(null)
  const [experiences, setExperiences] = useState([])
  const [loading, setLoading] = useState(false)

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

        // Step 3: Get ML score
        const { data: scoreData } = await getPrediction(data.profile)
        setScore(scoreData)
        setStep(3)

        // Step 4: Get RAG experiences
        const { data: ragData } = await getExperiences(data.profile.tech_stack)
        setExperiences(ragData.experiences)
        setStep(4)
      }
    } catch (e) {
      console.error(e)
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
