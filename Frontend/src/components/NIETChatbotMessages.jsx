"use client"

import { useState, useEffect, useRef } from "react"
import baseKnowledge from "../../../RAG/data/base_knowledge.json"
import placement from "../../../RAG/index_store/placement_chunks.json"

function now() {
  return new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })
}

function delay(ms) {
  return new Promise((res) => setTimeout(res, ms))
}

const INITIAL_OPTIONS = ["About NIET", "Courses Offered", "Admission", "Placement Records", "Activities", "Other"]

const getCoursesByLevel = (level) => {
  const courses = Object.values(baseKnowledge.courses || {})
  if (level === "UG") return courses.filter((c) => c.course_name?.toLowerCase().startsWith("b"))
  if (level === "PG") return courses.filter((c) => c.course_name?.toLowerCase().startsWith("m"))
  if (level === "TWINNING") return courses.filter((c) => c.course_name?.toLowerCase().includes("twinning"))
  return []
}

const getPlacement = () => {
  const seen = new Set()

  return placement
    .filter((item) => {
      if (seen.has(item.department)) return false
      seen.add(item.department)
      return true
    })
    .map((item) => item.department)
}

function renderWithLinks(text) {
  const urlRegex = /(https?:\/\/[^\s]+)/g
  return text.split(urlRegex).map((part, i) =>
    part.match(urlRegex) ? (
      <a key={i} href={part} target="_blank" rel="noreferrer" className="text-blue-600 underline">
        {part}
      </a>
    ) : (
      <span key={i}>{part}</span>
    ),
  )
}

export default function NIETChatbotMessages() {
  const [messages, setMessages] = useState([])
  const [input, setInput] = useState("")
  const [typing, setTyping] = useState(false)
  const [isSending, setIsSending] = useState(false)
  const messagesRef = useRef(null)

  /*restore session*/
  useEffect(() => {
    const saved = sessionStorage.getItem("niet_chat_messages")
    if (saved) {
      try {
        const parsed = JSON.parse(saved)
        if (Array.isArray(parsed)) {
          setMessages(parsed)
          return
        }
      } catch {}
    }

    pushBot("Hello! I'm the NIET Assistant — how can I help you today?")
    pushOptions(INITIAL_OPTIONS, false)
  }, [])

  /*session*/
  useEffect(() => {
    sessionStorage.setItem("niet_chat_messages", JSON.stringify(messages))
  }, [messages])

  /*auto scroll */
  useEffect(() => {
    messagesRef.current?.scrollTo({
      top: messagesRef.current.scrollHeight,
      behavior: "smooth",
    })
  }, [messages, typing])

  /*message helpers*/

  const pushBot = (text) =>
    setMessages((m) => [...m, { id: crypto.randomUUID(), from: "bot", type: "text", text, time: now() }])

  const pushUser = (text) =>
    setMessages((m) => [...m, { id: crypto.randomUUID(), from: "user", type: "text", text, time: now() }])

  const pushOptions = (options, showBack) =>
    setMessages((m) => [
      ...m,
      {
        id: crypto.randomUUID(),
        from: "bot",
        type: "options",
        options,
        showBack,
        time: now(),
      },
    ])

  /*option click*/

  const handleOptionClick = (opt) => {
    pushUser(opt)

    if (opt === "Courses Offered") {
      pushOptions(["Undergraduate Programs", "Postgraduate Programs", "Twinning Programs"], true)
      return
    }

    if (opt === "About NIET") {
      pushOptions(["Institute", "Research", "Facilities"], true)
      return
    }

    if (opt === "Undergraduate Programs") {
      pushOptions(
        getCoursesByLevel("UG").map((c) => c.course_name),
        true,
      )
      return
    }

    if (opt === "Postgraduate Programs") {
      pushOptions(
        getCoursesByLevel("PG").map((c) => c.course_name),
        true,
      )
      return
    }

    if (opt === "Twinning Programs") {
      pushOptions(
        getCoursesByLevel("TWINNING").map((c) => c.course_name),
        true,
      )
      return
    }
    if (opt === "Placement Records") {
      pushOptions(getPlacement(), true)
      return
    }
    if (placement.some((p) => p.department === opt)) {
      sendMessage(`placement record of ${opt}`)
      return
    }
    if (opt === "Institute") {
      pushBot(
        `You selected ${opt}. What do you want to know about the ${opt} (overview, rankings, awards, or international_alliances.)`,
      )
      return
    }

    if (opt === "Research") {
      pushBot(
        `You selected ${opt}. What do you want to know about the ${opt} (overview, areas, publications,journals or projects.)`,
      )
      return
    }

    if (opt === "Facilities") {
      sendMessage("Facilities available at NIET")
      return
    }
    if (opt === "Admission") {
      pushOptions(["Direct Admission", "Counselling", "Twinning"], true)
      return
    }

    if (opt === "Direct Admission") {
      sendMessage("How can I get direct admission?")
      return
    }
    if (opt === "Counselling") {
      sendMessage("What is the admission process for first year BTech through JEE Main?")
      return
    }
    if (opt === "Twinning") {
      sendMessage("Eligibility for twinning admission")
      return
    }

    if (opt === "Activities") {
      pushOptions(["Events", "Club"], true)
      return
    }
    if (opt === "Club") {
      sendMessage("list of clubs")
      return
    }
    sendMessage(`About ${opt} in NIET`)
  }

  /* ---------- backend ---------- */

  const sendMessage = async (text) => {
    pushUser(text)
    setTyping(true)
    setIsSending(true)

    try {
      const res = await fetch("http://localhost:8000/chat", {
        method: "POST",
        mode: "cors",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question: text }),
      })
      const data = await res.json()
      await delay(600)
      pushBot(data.final_answer || data.answer || "Server replied but no message found.")
    } catch {
      pushBot("Server error. Please try again.")
    } finally {
      setTyping(false)
      setIsSending(false)
    }
  }

  return (
    <div className="h-full flex flex-col bg-white overflow-hidden relative">
      <div className="chat-mesh-bg" />

      {/* HEADER */}
      <div className="px-6 py-5 bg-gradient-to-br from-[#e2111f] via-[#d00f1c] to-[#9a0b15] flex items-center gap-4 shrink-0 shadow-xl relative z-10 border-b border-white/5">
        <div className="relative">
          <div className="w-12 h-12 bg-white rounded-xl flex items-center justify-center shadow-lg transition-transform hover:rotate-6">
            <img src="/niet-logo.svg" alt="NIET" className="w-9 h-9 object-contain" />
          </div>
          <div className="absolute -bottom-0.5 -right-0.5 w-3.5 h-3.5 bg-green-500 rounded-full border-2 border-[#e2111f]" />
        </div>

        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2">
            <h2 className="font-bold text-white text-lg tracking-tight truncate">NIET Assistant</h2>
            <div className="w-1.5 h-1.5 bg-white/60 rounded-full animate-pulse" />
          </div>
          <span className="text-[10px] font-bold text-white/70 uppercase tracking-[0.15em] flex items-center gap-1.5">
            <span className="w-1 h-1 bg-white/40 rounded-full" />
            Active Intelligent Support
          </span>
        </div>

        <button
          onClick={() => {
            setMessages([])
            pushBot("Hello! I'm the NIET Assistant — how can I help you today?")
            pushOptions(INITIAL_OPTIONS, false)
          }}
          className="back-home-btn group"
          title="Reset View"
        >
          <svg
            className="w-4 h-4 group-hover:scale-110 transition-transform"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2.5}
              d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6"
            />
          </svg>
        </button>
      </div>

      {/* CHAT AREA */}
      <div
        ref={messagesRef}
        className="flex-1 overflow-y-auto px-5 py-6 flex flex-col gap-6 no-overscroll relative z-0"
      >
        {messages.map((m) => (
          <div
            key={m.id}
            className={`flex gap-3 items-start animate-fade-in ${m.from === "user" ? "flex-row-reverse" : ""}`}
          >
            {m.from === "bot" && (
              <div className="w-7 h-7 rounded-lg bg-white/80 backdrop-blur-sm flex items-center justify-center border border-slate-100 shrink-0 mt-1 shadow-sm">
                <img src="/niet-logo.svg" className="w-4 h-4 object-contain opacity-60" />
              </div>
            )}

            <div className={`flex flex-col gap-1.5 ${m.from === "user" ? "items-end" : "items-start"} max-w-[85%]`}>
              <div
                className={`px-4 py-3 text-[13px] leading-relaxed ${m.from === "user" ? "organic-user" : "organic-bot"}`}
              >
                {m.type === "options" ? (
                  <div className="w-full">
                    <div className="text-[9px] font-black text-slate-400 uppercase tracking-[0.15em] mb-3 opacity-70">
                      Suggestions
                    </div>
                    <div className="grid grid-cols-2 gap-2">
                      {m.options.map((opt) => (
                        <button key={opt} onClick={() => handleOptionClick(opt)} className="action-pill">
                          <span>{opt}</span>
                        </button>
                      ))}
                    </div>
                  </div>
                ) : (
                  renderWithLinks(m.text)
                )}
              </div>
              <span className="text-[9px] text-slate-400 font-bold uppercase tracking-widest px-1 opacity-60">
                {m.time}
              </span>
            </div>
          </div>
        ))}
        {typing && (
          <div className="flex gap-1.5 items-center animate-fade-in ml-1 mt-2">
            <div className="flex gap-1">
              <div className="w-1.5 h-1.5 bg-[#e2111f]/40 rounded-full animate-bounce [animation-delay:-0.3s]" />
              <div className="w-1.5 h-1.5 bg-[#e2111f]/40 rounded-full animate-bounce [animation-delay:-0.15s]" />
              <div className="w-1.5 h-1.5 bg-[#e2111f]/40 rounded-full animate-bounce" />
            </div>
          </div>
        )}
      </div>

      {/* INPUT AREA */}
      <div className="p-6 bg-white/50 backdrop-blur-md border-t border-slate-100/50">
        <form
          onSubmit={(e) => {
            e.preventDefault()
            if (!input.trim()) return
            sendMessage(input)
            setInput("")
          }}
          className="relative flex items-center mb-3"
        >
          <input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            className="w-full bg-slate-50 border border-slate-100 rounded-2xl px-5 py-4 pr-14 text-[13px] focus:outline-none focus:ring-2 focus:ring-[#e2111f]/5 transition-all placeholder:text-slate-400"
            placeholder="Ask anything about NIET..."
          />
          <button
            disabled={isSending || !input.trim()}
            className="absolute right-2 w-10 h-10 rounded-full bg-[#e2111f] flex items-center justify-center text-white shadow-lg shadow-[#e2111f]/20 hover:scale-105 active:scale-95 disabled:opacity-50 transition-all"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2.5}
                d="M5 12h14M12 5l7 7-7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6"
              />
            </svg>
          </button>
        </form>
        <div className="text-center text-[9px] font-black text-slate-300 tracking-[0.2em] uppercase">
          NIET DIGITAL HUB
        </div>
      </div>
    </div>
  )
}
