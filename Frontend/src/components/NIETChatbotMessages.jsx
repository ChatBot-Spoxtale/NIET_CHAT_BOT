"use client"

import { useState, useEffect, useRef } from "react"
import baseKnowledge from "../../../RAG/Json_Format_Data/base_knowledge.json"
import placement from "../../../RAG/Json_Format_Data/base_knowledge.json"

function now() {
  return new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })
}

function delay(ms) {
  return new Promise((res) => setTimeout(res, ms))
}

function truncateWithDots(text, limit = 28) {
  if (!text || text.length <= limit) return text
  return text.slice(0, limit) + "...."
}

const INITIAL_OPTIONS = [
  "Apply Now",
  "About NIET",
  "Courses Offered",
  "Admission",
  "Placement Records",
  "Events",
  "Clubs",
  "Request Callback",
  "Research",
  "Hostel Facility",
  "Academic Facility"
]

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
      <div key={i} className="my-2">
        <a
          href={part}
          target="_blank"
          rel="noreferrer"
          className="inline-flex items-center gap-2 px-4 py-2 rounded-full border border-[#e2111f] text-[#e2111f] font-semibold text-[11px] hover:bg-[#e2111f] hover:text-white transition-all duration-300 shadow-sm bg-white"
        >
          <span>{part.length > 30 ? "Visit Official Link" : part}</span>
          <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2.5}
              d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14"
            />
          </svg>
        </a>
      </div>
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
  const [selectedOptions, setSelectedOptions] = useState(new Set())
  const [activeDropdown, setActiveDropdown] = useState(null)
  const [callbackStep, setCallbackStep] = useState(null)
  const [callbackData, setCallbackData] = useState({ name: "", phone: "" })
  const messagesRef = useRef(null)

  useEffect(() => {
    sessionStorage.removeItem("niet_chat_messages")
    pushBot("Hello! I'm the NIET Assistant — how can I help you today?")
    pushOptions(INITIAL_OPTIONS, false)

    return () => {
      sessionStorage.removeItem("niet_chat_messages")
    }
  }, [])

  useEffect(() => {
    messagesRef.current?.scrollTo({
      top: messagesRef.current.scrollHeight,
      behavior: "smooth",
    })
    setActiveDropdown(null)
  }, [messages, typing])

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
        selectedValue: null,
      },
    ])

  const handleOptionClick = (opt, messageId) => {
    if (opt === "Apply Now") {
      window.open("https://applynow.niet.co.in/", "_blank")
      return
    }

    pushUser(opt)
    setMessages((prev) => prev.map((m) => (m.id === messageId ? { ...m, selectedValue: opt } : m)))
    setSelectedOptions((prev) => new Set(prev).add(opt))

    if (opt === "Request Callback") {
      setCallbackStep("name")
      pushBot("Please provide your name.")
      return
    }

    if (opt === "Courses Offered") {
      pushOptions(["Undergraduate Programs", "Postgraduate Programs", "Twinning Programs"], true)
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
    
    if (placement.some((p) => p.department === opt)) {
      sendMessage(`placement record of ${opt}`)
      return
    }

    if (opt === "Admission") {
      pushOptions(["Direct Admission", "Counselling", "Twinning"], true)
      return
    }
  }

  const sendMessage = async (text) => {
    if (callbackStep === "name") {
      setCallbackData((prev) => ({ ...prev, name: text }))
      pushUser(text)
      setCallbackStep("phone")
      pushBot("Great! Now kindly provide your mobile number so that our counsellor can contact you.")
      return
    }

    if (callbackStep === "phone") {
      setCallbackData((prev) => ({ ...prev, phone: text }))
      pushUser(text)
      setCallbackStep(null)
      const newRequest = { ...callbackData, phone: text, timestamp: new Date().toISOString() }
      const existing = JSON.parse(localStorage.getItem("niet_callback_requests") || "[]")
      localStorage.setItem("niet_callback_requests", JSON.stringify([...existing, newRequest]))
      console.log("[v0] Callback request stored:", newRequest)
      pushBot("Thank you! Our counsellor will get back to you shortly.")
      return
    }

    pushUser(text)
    setTyping(true)
    setIsSending(true)

    try {
      const res = await fetch("https://niet-chat-bot-rag.onrender.com/chat", {
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
    <div className="h-full flex flex-col bg-white overflow-hidden relative transform-gpu">
      <div className="chat-mesh-bg" />

      <div className="px-5 py-5 bg-gradient-to-br from-[#e2111f] via-[#d00f1c] to-[#9a0b15] flex items-center gap-3 shrink-0 shadow-lg relative z-10 border-b border-white/10 overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/5 to-transparent -translate-x-full animate-[shimmer_3s_infinite]" />

        <div className="relative">
          <div className="w-12 h-12 bg-white rounded-xl flex items-center justify-center shadow-inner overflow-hidden border border-white/20">
            <img src="/niet-logo.svg" alt="NIET" className="w-full h-full object-contain p-1.5" />
          </div>
        </div>

        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2">
            <h2 className="font-extrabold text-white text-xl tracking-tight truncate drop-shadow-sm">NIET Assistant</h2>
          </div>
          <div className="flex items-center gap-1.5">
            <span className="flex h-1.5 w-1.5 rounded-full bg-green-400 animate-pulse shadow-[0_0_8px_rgba(74,222,128,0.6)]" />
            <span className="text-[11px] font-bold text-white/80 uppercase tracking-widest">Online Support</span>
          </div>
        </div>

        <button
          onClick={() => {
            setMessages([])
            setSelectedOptions(new Set())
            setCallbackStep(null)
            setCallbackData({ name: "", phone: "" })
            sessionStorage.removeItem("niet_chat_messages")
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

      <div
        ref={messagesRef}
        className="flex-1 overflow-y-auto px-3 py-5 flex flex-col gap-6 no-overscroll relative z-0"
      >
        {messages.map((m, idx) => (
          <div
            key={m.id}
            className={`flex gap-2 items-start animate-in fade-in slide-in-from-bottom-2 duration-500 relative ${
              activeDropdown === m.id ? "z-50" : "z-0"
            } ${m.from === "user" ? "flex-row-reverse" : ""}`}
            style={{ animationDelay: `${idx * 0.05}s` }}
          >
            {m.from === "bot" && (
              <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-[#E30B5D] to-[#B00848] flex items-center justify-center border border-white/20 shrink-0 mt-1 shadow-md">
                <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z"
                  />
                </svg>
              </div>
            )}

            <div className={`flex flex-col gap-1 ${m.from === "user" ? "items-end" : "items-start"} max-w-[88%]`}>
              <div
                className={`px-3 py-2 text-[13px] leading-relaxed whitespace-pre-line ${m.from === "user" ? "organic-user" : "organic-bot overflow-visible"}`}
              >
                {m.type === "options" ? (
                  <div className="w-full">
                    <div className="text-[11px] font-bold text-[#e2111f] uppercase mb-3 border-b border-[#e2111f]/10 pb-1 font-[Arial,sans-serif]">
                      Quick Actions
                    </div>
                    {m.options.some(
                      (opt) => opt.match(/^[BM]\./i) || opt.toLowerCase().includes("twinning program in"),
                    ) ? (
                      <div className="relative group">
                        <button
                          onClick={() => setActiveDropdown(activeDropdown === m.id ? null : m.id)}
                          className="w-full min-w-[200px] bg-white border-2 border-[#e2111f]/20 rounded-xl px-4 py-2.5 text-[12px] font-bold text-slate-700 flex items-center justify-between hover:border-[#e2111f]/40 transition-all cursor-pointer shadow-sm"
                        >
                          <span className="truncate">
                            {m.selectedValue ? truncateWithDots(m.selectedValue) : "Select an option..."}
                          </span>
                          <svg
                            className={`w-4 h-4 text-[#e2111f] transition-transform duration-200 shrink-0 ${activeDropdown === m.id ? "rotate-180" : ""}`}
                            fill="none"
                            stroke="currentColor"
                            viewBox="0 0 24 24"
                          >
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M19 9l-7 7-7-7" />
                          </svg>
                        </button>

                        {activeDropdown === m.id && (
                          <div className="relative z-[60] mt-1 bg-white border border-slate-200 rounded-xl shadow-lg overflow-hidden animate-in fade-in slide-in-from-top-2 duration-200 w-full">
                            <div className="max-h-60 overflow-y-auto py-1 custom-scrollbar">
                              {m.options.map((opt) => (
                                <button
                                  key={opt}
                                  onClick={() => {
                                    handleOptionClick(opt, m.id)
                                    setActiveDropdown(null)
                                  }}
                                  className="w-full text-left px-4 py-2.5 text-[12px] font-medium text-slate-600 hover:bg-[#e2111f]/5 hover:text-[#e2111f] transition-colors border-b border-slate-50 last:border-0"
                                >
                                  {opt}
                                </button>
                              ))}
                            </div>
                          </div>
                        )}
                      </div>
                    ) : (
                      <div className="flex flex-wrap gap-2">
                        {m.options.map((opt) => (
                          <button
                            key={opt}
                            disabled={m.selectedValue !== null}
                            onClick={() => handleOptionClick(opt, m.id)}
                            className={`action-pill ${m.selectedValue === opt ? "action-pill-active" : ""}`}
                          >
                            {opt}
                            {opt === "Apply Now" && (
                              <svg className="ml-1.5 w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path
                                  strokeLinecap="round"
                                  strokeLinejoin="round"
                                  strokeWidth={2.5}
                                  d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14"
                                />
                              </svg>
                            )}
                          </button>
                        ))}
                      </div>
                    )}
                  </div>
                ) : (
                  renderWithLinks(m.text)
                )}
              </div>
              <div className="w-full mt-1">
                <span
                  className={`text-[9px] text-slate-400 font-bold uppercase tracking-widest px-1 opacity-50 ${m.from === "user" ? "float-right mr-1" : "float-left ml-1"}`}
                >
                  {m.time}
                </span>
              </div>
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

      <div className="p-4 pb-4 bg-white border-t border-slate-100 shadow-[0_-10px_20px_rgba(0,0,0,0.02)]">
        <form
          onSubmit={(e) => {
            e.preventDefault()
            if (!input.trim()) return
            sendMessage(input)
            setInput("")
          }}
          className="relative flex items-center group"
        >
          <input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            className="w-full bg-white border border-slate-300 rounded-[24px] px-6 py-[10px] pr-14 text-[14px] text-slate-700 focus:outline-none focus:ring-2 focus:ring-[#e2111f]/20 focus:border-[#e2111f] transition-all duration-300 placeholder:text-slate-400 font-medium h-[46px] shadow-sm"
            placeholder={callbackStep ? `Enter your ${callbackStep}...` : "Type your message..."}
          />
          <button
            disabled={isSending || !input.trim()}
            className="absolute right-1 w-9 h-9 rounded-full bg-[#e2111f] flex items-center justify-center text-white shadow-[0_4px_12px_rgba(226,17,31,0.3)] transition-all duration-300 hover:bg-[#b00d18] hover:scale-105 active:scale-95 disabled:opacity-30 disabled:scale-100"
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M5 12h14M12 5l7 7-7 7" />
            </svg>
          </button>
        </form>
      </div>
    </div>
  )
}
