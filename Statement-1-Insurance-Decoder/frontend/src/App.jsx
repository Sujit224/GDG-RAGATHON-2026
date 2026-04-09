import { useState } from 'react'
import ChatBox from './ChatBox'
import './App.css'

function App() {
  return (
    <div className="app-container centered-layout">
      <div className="main-content">
        <h1 className="main-title">Insurance Decoder ChatBot</h1>
        <ChatBox />
      </div>
      <div className="decorative-blur centered-blur-1"></div>
      <div className="decorative-blur-2 centered-blur-2"></div>
    </div>
  )
}

export default App
