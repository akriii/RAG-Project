import { useState, useRef, useEffect } from 'react'
import './App.css'

const DEPARTMENTS = [
  { id: 'HR', label: 'HR' },
  { id: 'Engineering', label: 'Engineering' },
]

function formatTime(date) {
  return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
}

function SealIcon() {
  return (
    <svg className="seal-icon" width="22" height="22" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
      <circle cx="12" cy="12" r="9" stroke="currentColor" strokeWidth="1.4" />
      <path d="M12 7.5v9M8.5 9.5l7 5M15.5 9.5l-7 5" stroke="currentColor" strokeWidth="1.2" strokeLinecap="round" />
    </svg>
  )
}

function App() {
  const [messages, setMessages] = useState([])
  const [input, setInput] = useState('')
  const [department, setDepartment] = useState('HR')
  const [isLoading, setIsLoading] = useState(false)

  // Simple random session ID for this demo
  const [sessionId] = useState(() => Math.random().toString(36).substring(7))
  const scrollRef = useRef(null)

  useEffect(() => {
    scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight, behavior: 'smooth' })
  }, [messages, isLoading])

  const sendMessage = async (e) => {
    e.preventDefault()
    const question = input.trim()
    if (!question) return

    setMessages(prev => [...prev, { role: 'user', text: question, time: new Date() }])
    setInput('')
    setIsLoading(true)

    try {
      const response = await fetch(`${import.meta.env.VITE_API_URL}/api/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          session_id: sessionId,
          question,
          department,
        }),
      })

      const data = await response.json()

      setMessages(prev => [...prev, {
        role: 'ai',
        text: data.answer,
        // Optional: render citation pills if the backend includes a `sources` array.
        sources: Array.isArray(data.sources) ? data.sources : [],
        time: new Date(),
      }])
    } catch (error) {
      console.error('API Error:', error)
      setMessages(prev => [...prev, {
        role: 'ai',
        text: "Couldn't reach the policy index. Check the connection and try again.",
        error: true,
        time: new Date(),
      }])
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="chat-container">
      <header>
        <div className="brand">
          <span className="seal"><SealIcon /></span>
          <div className="brand-text">
            <h1>Policy Desk</h1>
            <p className="subtitle">Answers grounded in filed company policy</p>
          </div>
        </div>
        <span className="session-tag">session · {sessionId}</span>
      </header>

      <div className="dept-switch" role="tablist" aria-label="Acting as">
        {DEPARTMENTS.map(d => (
          <button
            key={d.id}
            type="button"
            role="tab"
            aria-selected={department === d.id}
            className={`dept-tab ${department === d.id ? 'active' : ''}`}
            onClick={() => setDepartment(d.id)}
          >
            {d.label}
          </button>
        ))}
      </div>

      <div className="chat-window" ref={scrollRef}>
        {messages.length === 0 && (
          <div className="placeholder">
            <p className="placeholder-title">No entries yet</p>
            <p>Ask about leave, benefits, or engineering process — answers cite the source document.</p>
          </div>
        )}

        {messages.map((msg, index) => (
          <div key={index} className={`message ${msg.role} ${msg.error ? 'error' : ''}`}>
            <div className="message-head">
              <span className="role-label">{msg.role === 'user' ? 'You' : 'Agent'}</span>
              <span className="time">{formatTime(msg.time)}</span>
            </div>
            <p>{msg.text}</p>
            {msg.sources && msg.sources.length > 0 && (
              <div className="sources">
                {msg.sources.map((s, i) => (
                  <span key={i} className="source-pill">§ {s}</span>
                ))}
              </div>
            )}
          </div>
        ))}

        {isLoading && (
          <div className="message ai typing">
            <div className="message-head">
              <span className="role-label">Agent</span>
            </div>
            <span className="dots" aria-label="Agent is typing"><i></i><i></i><i></i></span>
          </div>
        )}
      </div>

      <form onSubmit={sendMessage} className="input-area">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder={`Ask about ${department === 'HR' ? 'leave, benefits, conduct…' : 'process, tooling, on-call…'}`}
          disabled={isLoading}
          aria-label="Ask a policy question"
        />
        <button type="submit" disabled={isLoading || !input.trim()}>
          {isLoading ? 'Asking…' : 'Ask'}
        </button>
      </form>
    </div>
  )
}

export default App