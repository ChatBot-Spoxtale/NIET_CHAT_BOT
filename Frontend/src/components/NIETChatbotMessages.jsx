"use client"

import { useState, useEffect, useRef } from "react"
import baseKnowledge from "../../../../Json_Format_Data/base_knowledge.json"


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

function extractLinkFromText(text) {
  if (!text || typeof text !== 'string') {
    return { cleanText: text, link: null }
  }

  // Regular expression to match URLs
  const urlRegex = /(https?:\/\/[^\s]+)/g
  const matches = text.match(urlRegex)

  if (matches && matches.length > 0) {
    const cleanText = text.replace(urlRegex, '').trim()
    return { cleanText: cleanText || null, link: matches[0] }
  }

  return { cleanText: text, link: null }
}

function ImageSlideshow({ images }) {
  const [currentIndex, setCurrentIndex] = useState(0)
  const autoSlideTimer = useRef(null)

  useEffect(() => {
    autoSlideTimer.current = setInterval(() => {
      setCurrentIndex((prev) => (prev + 1) % images.length)
    }, 5000)

    return () => clearInterval(autoSlideTimer.current)
  }, [images.length])

  const handlePrev = () => {
    setCurrentIndex((prev) => (prev - 1 + images.length) % images.length)
    clearInterval(autoSlideTimer.current)
    autoSlideTimer.current = setInterval(() => {
      setCurrentIndex((prev) => (prev + 1) % images.length)
    }, 5000)
  }

  const handleNext = () => {
    setCurrentIndex((prev) => (prev + 1) % images.length)
    clearInterval(autoSlideTimer.current)
    autoSlideTimer.current = setInterval(() => {
      setCurrentIndex((prev) => (prev + 1) % images.length)
    }, 5000)
  }

  return (
    <div className="relative w-full bg-slate-100 rounded-lg overflow-hidden mt-2">
      <div className="relative h-[320px] sm:h-[380px] md:h-[420px] lg:h-[480px] flex items-center justify-center bg-slate-200">
        <img
          src={images[currentIndex] || "/placeholder.svg"}
          alt={`Image ${currentIndex + 1} of ${images.length}`}
          className="w-full h-full object-cover"
        />
      </div>

      {images.length > 1 && (
        <>
          <button
            onClick={handlePrev}
            className="absolute left-2 top-1/2 -translate-y-1/2 bg-black/50 hover:bg-black/70 text-white rounded-full p-2 transition-all duration-200 z-10"
            aria-label="Previous image"
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
            </svg>
          </button>
          <button
            onClick={handleNext}
            className="absolute right-2 top-1/2 -translate-y-1/2 bg-black/50 hover:bg-black/70 text-white rounded-full p-2 transition-all duration-200 z-10"
            aria-label="Next image"
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
            </svg>
          </button>
          <div className="absolute bottom-2 left-1/2 -translate-x-1/2 flex gap-1.5">
            {images.map((_, idx) => (
              <button
                key={idx}
                onClick={() => {
                  setCurrentIndex(idx)
                  clearInterval(autoSlideTimer.current)
                  autoSlideTimer.current = setInterval(() => {
                    setCurrentIndex((prev) => (prev + 1) % images.length)
                  }, 5000)
                }}
                className={`w-2 h-2 rounded-full transition-all duration-300 ${idx === currentIndex ? "bg-white w-6" : "bg-white/50"
                  }`}
                aria-label={`Go to image ${idx + 1}`}
              />
            ))}
          </div>
        </>
      )}
    </div>
  )
}

function parseMessageContent(text) {
  if (typeof text !== "string") return { type: "plain", content: text }

  const hasCourseDetails =
    text.includes("*Course Details*") ||
    text.includes("*Placements*") ||
    text.includes("*Why Choose*") ||
    (text.includes("*Overview*") && text.includes("*"))

  const hasBulletPoints = /^[\s]*[-•*]/m.test(text)
  const hasMultipleSections = (text.match(/\n/g) || []).length > 3 && hasBulletPoints
  const isGreeting = text.length < 150 && !hasBulletPoints && !hasCourseDetails

  if (hasCourseDetails) return { type: "courseDetails", content: text }
  if (hasMultipleSections) return { type: "structured", content: text }
  if (hasBulletPoints) return { type: "bulletList", content: text }
  return { type: "greeting", content: text }
}

function renderCourseDetails(text) {
  const sections = text.split(/(\*[^*]+\*)/g).filter(Boolean)

  const sectionIcons = {
    "*Course Details*": "",
    "*Placements*": "",
    "*Why Choose This Course?*": "",
    "*Overview*": ""
  }

  const contentGroups = []
  let currentGroup = { title: null, items: [] }

  sections.forEach((section) => {
    if (section.startsWith("*") && section.endsWith("*")) {
      if (currentGroup.items.length > 0) {
        contentGroups.push(currentGroup)
      }
      currentGroup = { title: section, items: [] }
    } else {
      const lines = section.split("\n").filter((l) => l.trim())
      lines.forEach((line) => {
        const match = line.match(/^[\s]*[-•*]\s*(.*)/)
        if (match) {
          currentGroup.items.push(match[1])
        } else if (line.trim()) {
          currentGroup.items.push(line.trim())
        }
      })
    }
  })

  if (currentGroup.items.length > 0) {
    contentGroups.push(currentGroup)
  }

  return (
    <div className="space-y-3 w-full">
      {contentGroups.filter(group => {
        if (!group.title) return false
        const hasMeaningfulText = group.items.some(
          item => item.replace(/[^\w\s]/g, "").trim().length > 0
        )
        return hasMeaningfulText
      }).map((group, groupIdx) => {
        const title = group.title?.slice(1, -1)
        const icon = sectionIcons[group.title] || ""

        return (
          <div key={groupIdx} className="course-detail-card">
            <div className="flex items-center gap-2 mb-2 pb-2 border-b-2 border-red-300">
              {icon && <span className="text-xl">{icon}</span>}
              <h3 className="font-bold text-red-600 text-sm uppercase tracking-wide">{title}</h3>
            </div>
            <div className="space-y-2 ml-1">
              {group.items.map((item, itemIdx) => (
                <div key={itemIdx} className="flex gap-3 items-start">
                  <div className="w-2 h-2 bg-gradient-to-r from-red-500 to-red-400 rounded-full mt-1.5 shrink-0" />
                  <p className="text-sm text-slate-700 leading-relaxed">{renderTextWithLinks(item)}</p>
                </div>
              ))}
            </div>
          </div>
        )
      })}
    </div>
  )
}

const renderTextWithLinks = (text) => {
  if (!text) return null

  const urlRegex = /(https?:\/\/[^\s]+)/g

  return text.split(urlRegex).map((part, i) =>
    part.match(urlRegex) ? (
      <a
        key={i}
        href={part}
        target="_blank"
        rel="noopener noreferrer"
        className="relative z-20 text-[#e2111f] font-semibold underline underline-offset-2 pointer-events-auto"
      >
        Visit Official Link
      </a>
    ) : (
      <span key={i}>{part}</span>
    )
  )
}

function renderBulletList(text) {
  const lines = text.split("\n")
  const elements = []
  let currentList = []

  lines.forEach((line) => {
    const trimmed = line.trim()

    if (/^[\s]*[-•*]/.test(trimmed)) {
      const content = trimmed.replace(/^[\s]*[-•*]\s*/, "")
      if (content.trim()) {
        currentList.push(content)
      }
    } else if (trimmed && currentList.length > 0) {
      elements.push({ type: "list", items: currentList })
      currentList = []
      elements.push({ type: "text", content: trimmed })
    } else if (trimmed) {
      if (currentList.length > 0) {
        elements.push({ type: "list", items: currentList })
        currentList = []
      }
      elements.push({ type: "text", content: trimmed })
    }
  })

  if (currentList.length > 0) {
    elements.push({ type: "list", items: currentList })
  }

  return (
    <div className="space-y-3 w-full">
      {elements.map((elem, idx) => {
        if (elem.type === "list") {
          return (
            <div key={idx} className="bullet-list-card">
              <ul className="space-y-3">
                {elem.items.map((item, itemIdx) => {
                  const { cleanText, link } = extractLinkFromText(item)

                  if (!cleanText && !link) return null

                  return (
                    <li key={itemIdx} className="flex flex-col gap-1">
                      {/* Bullet text */}
                      {cleanText && (
                        <div className="flex gap-3 items-start">
                          <span className="w-2 h-2 bg-red-500 rounded-full mt-1.5 shrink-0 shadow-sm" />
                          <span className="text-sm text-slate-700 leading-relaxed">
                            {cleanText}
                          </span>
                        </div>
                      )}

                      {/* Link outside bullet */}
                      {link && (
                        <button
                          onClick={() => window.open(link, "_blank")}
                          className="ml-5 relative z-[999] pointer-events-auto inline-flex items-center gap-2 px-5 py-2 rounded-full bg-[#e2111f] text-white font-semibold text-sm hover:bg-[#b00d18] transition-all shadow-md cursor-pointer"
                        >
                          <span>Visit Official Link</span>
                          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path
                              strokeLinecap="round"
                              strokeLinejoin="round"
                              strokeWidth={2}
                              d="M14 3h7m0 0v7m0-7L10 14"
                            />
                          </svg>
                        </button>
                      )}
                    </li>
                  )
                })}

              </ul>
            </div>
          )
        }

        return (
          <div
            key={idx}
            className="rounded-lg p-3 border-l-4 border-red-500 shadow-sm"
            style={{
              background: 'linear-gradient(to right, #fef2f2, #ffffff)',
            }}
          >
            {elem.content.match(/https?:\/\/[^\s]+/) ? (
              <div className="flex flex-col gap-2">
                <button
                  onClick={() => window.open(elem.content.match(/https?:\/\/[^\s]+/)[0], "_blank")}
                  className="relative z-[999] pointer-events-auto inline-flex items-center gap-2 px-5 py-2 rounded-full bg-[#e2111f] text-white font-semibold text-sm hover:bg-[#b00d18] transition-all shadow-md cursor-pointer"
                >
                  <span>Visit Official Link</span>
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M14 3h7m0 0v7m0-7L10 14"
                    />
                  </svg>
                </button>
              </div>
            ) : (
              renderWithLinks(elem.content)
            )}
          </div>
        )
      })}
    </div>
  )
}

export { renderBulletList }


function renderStructuredContent(text) {
  const lines = text.split("\n")
  const elements = []
  let currentList = []

  lines.forEach((line) => {
    const trimmed = line.trim()

    if (/^[\s]*[-•*]/.test(trimmed)) {
      const content = trimmed.replace(/^[\s]*[-•*]\s*/, "")
      if (content.trim()) {
        currentList.push(content)
      }
    } else if (trimmed && currentList.length > 0) {
      elements.push({ type: "list", items: currentList })
      currentList = []
      elements.push({ type: "text", content: trimmed })
    } else if (trimmed) {
      if (currentList.length > 0) {
        elements.push({ type: "list", items: currentList })
        currentList = []
      }
      elements.push({ type: "text", content: trimmed })
    }
  })

  if (currentList.length > 0) {
    elements.push({ type: "list", items: currentList })
  }

  return (
    <div className="space-y-3 w-full">
      {elements.map((elem, idx) => {
        if (elem.type === "list") {
          return (
            <div key={idx} className="mixed-content-card">
              <ul className="space-y-2">
                {elem.items.map((item, itemIdx) => (
                  <li key={itemIdx} className="flex gap-3 items-start">
                    <span className="w-2 h-2 bg-gradient-to-r from-red-500 to-pink-500 rounded-full mt-1.5 shrink-0" />
                    <span className="text-sm text-slate-700 leading-relaxed">{renderTextWithLinks(item)}</span>
                  </li>
                ))}
              </ul>
            </div>
          )
        }
        return (
          <div key={idx} className="text-sm text-slate-700 leading-relaxed px-3 py-2">
            {renderWithLinks(elem.content)}
          </div>
        )
      })}
    </div>
  )
}

function renderGreeting(text) {
  return (
    <div className="inline-block max-w-full">
      <p className="text-sm text-slate-700 leading-relaxed greeting-pill">{text}</p>
    </div>
  )
}

const renderWithLinks = (text) => {

  if (text.startsWith("LINK::")) {
    const [, payload] = text.split("LINK::")
    const [label, url] = payload.split("||")

    return (
      <button
        type="button"
        onClick={(e) => {
          e.stopPropagation()
          window.open(url, "_blank", "noopener,noreferrer")
        }}
        className="relative z-[999] pointer-events-auto inline-flex items-center gap-2 px-5 py-2 rounded-full bg-[#e2111f] text-white font-semibold text-sm hover:bg-[#b00d18] transition-all shadow-md cursor-pointer"
      >
        <span>{label}</span>
        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M14 3h7m0 0v7m0-7L10 14"
          />
        </svg>
      </button>
    )
  }

  if (typeof text !== "string") {
    return <span>{""}</span>
  }

  const { type, content } = parseMessageContent(text)

  if (type === "courseDetails") {
    return renderCourseDetails(content)
  } else if (type === "structured") {
    return renderStructuredContent(content)
  } else if (type === "bulletList") {
    return renderBulletList(content)
  } else {
    const urlRegex = /(https?:\/\/[^\s]+)/g
    const parts = content.split(urlRegex)
    const hasLinks = parts.some((p) => p.match(urlRegex))

    if (hasLinks) {
      return (
        <div className="flex flex-col gap-2 bg-transparent items-start">
          {parts.map((part, i) =>
            part.match(urlRegex) ? (
              <button
                key={i}
                onClick={() => {
                  console.log("Button clicked!")
                  window.open(part, "_blank")
                }}
                className="relative z-[999] pointer-events-auto inline-flex items-center gap-2 px-5 py-2 rounded-full bg-[#e2111f] text-white font-semibold text-sm hover:bg-[#b00d18] transition-all shadow-md cursor-pointer"
              >
                <span>Visit Official Link</span>
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M14 3h7m0 0v7m0-7L10 14"
                  />
                </svg>
              </button>
            ) : part.trim() && !part.toLowerCase().includes('visit official link') ? (
              <span key={i} className="text-sm text-slate-700 leading-relaxed">
                {part.trim()}
              </span>
            ) : null,
          )}
        </div>
      )
    }

    return renderGreeting(content)
  }
}

export { renderWithLinks }

const isValidName = (name) => {
  if (!name) return false
  const cleaned = name.trim()
  return /^[A-Za-z\s]{2,40}$/.test(cleaned)
}

const isValidIndianPhone = (phone) => {
  if (!phone) return false
  const cleaned = phone.replace(/\s|-/g, "").replace(/^(\+91)/, "")
  return /^[6-9]\d{9}$/.test(cleaned)
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
  "Academic Facility",
]

const getCoursesByLevel = (level) => {
  const courses = Object.values(baseKnowledge.courses || {})
  if (level === "Undergraduate (UG)") return courses.filter((c) => c.course_name?.toLowerCase().startsWith("b"))
  if (level === "Postgraduate (PG)") return courses.filter((c) => c.course_name?.toLowerCase().startsWith("m"))
  if (level === "TWINNING") return courses.filter((c) => c.course_name?.toLowerCase().includes("twinning"))
  return []
}

export default function NIETChatbotMessages({ embed = false }) {
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

  useEffect(() => {
    const savedProfile = JSON.parse(localStorage.getItem("CALLBACK_STORAGE_KEY"))
    if (savedProfile) {
      setCallbackData(savedProfile)
    }
  }, [])

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
  const fetchPlacementRecords = async () => {
    try {
      pushBot("NIET Placement Records")

      const res = await fetch("http://localhost:8000/placement-records")
      const data = await res.json()

      if (data.images?.length) {
        pushImages(data.images)
      }
    } catch (e) {
      pushBot("Unable to load placement records right now.")
    }
  }
  const pushImages = (images) =>
    setMessages((m) => [...m, { id: crypto.randomUUID(), from: "bot", type: "images", images, time: now() }])

  const sendCallbackToBackend = async (data) => {
    try {
      await fetch("http://localhost:8000/api/save-callback", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          name: data.name,
          phone: data.phone,
        }),
      })
    } catch (error) {
      console.error("Failed to save callback:", error)
    }
  }

  const handleOptionClick = (opt, messageId) => {
    if (opt === "Apply Now") {
      window.open("https://applynow.niet.co.in/", "_blank")
      return
    }

    setMessages((prev) => prev.map((m) => (m.id === messageId ? { ...m, selectedValue: opt } : m)))
    setSelectedOptions((prev) => new Set(prev).add(opt))

    if (opt === "Request Callback") {
      setCallbackStep("name")
      setCallbackData({ name: "", phone: "" })
      pushBot("Please provide your name.")
      return
    }

    if (opt === "About NIET") {
      sendMessage("About NIET")
      return
    }

    if (opt === "Clubs") {
      sendMessage("List Of Clubs")
      return
    }

    if (opt === "Admission") {
      sendMessage("Admission Prcoess At NIET")
      return
    }

    if (opt === "Academic Facility") {
      sendMessage("Academic Facility")
      return
    }

    if (opt === "Hostel Facility") {
      sendMessage("Hostel Facility")
      return
    }

    if (opt === "Research") {
      sendMessage("Research At NIET")
      return
    }

    if (opt === "Placement Records") {
      fetchPlacementRecords()
      return
    }

    if (opt === "Events") {
      sendMessage("Events At NIET")
      return
    }

    if (opt === "Courses Offered") {
      pushOptions(["Undergraduate (UG)", "Postgraduate (PG)", "TWINNING PROGRAM (International) "], true)
      return
    }

    if (["Undergraduate (UG)", "Postgraduate (PG)", "TWINNING PROGRAM (International) "].includes(opt)) {
      const level =
        opt === "Undergraduate (UG)" ? "Undergraduate (UG)" :
          opt === "Postgraduate (PG)" ? "Postgraduate (PG)" :
            "TWINNING"

      const courses = getCoursesByLevel(level)

      if (courses.length > 0) {
        pushBot("Which course would you like to know more about?")
        pushOptions(
          courses.map((c) => c.course_name),
          true
        )
      } else {
        pushBot(`Sorry, no ${opt} courses found.`)
        pushOptions(INITIAL_OPTIONS, true)
      }
      return
    }

    const allCourses = [
      ...getCoursesByLevel("Undergraduate (UG)"),
      ...getCoursesByLevel("Postgraduate (PG)"),
      ...getCoursesByLevel("TWINNING"),
    ]

    const selectedCourse = allCourses.find(
      (c) => c.course_name === opt
    )

    if (selectedCourse) {
      sendMessage(` ${selectedCourse.course_name}`)
      return
    }
  }
  const CALLBACK_STORAGE_KEY = "niet_user_profile"
  const CALLBACK_MAX_CLICKS = 5

  const CALLBACK_INTENT_KEYWORDS = [
    "fee",
    "fees",
    "apply",
    "application",
    "enquiry",
    "inquiry",
    "registration",
    "join",
    "amount",
    "cash",
  ]

  const PLACEMENT_KEYWORDS = [
  "overall "
]

  const getCallbackCount = () => {
    return Number(localStorage.getItem(CALLBACK_RATE_LIMIT_KEY) || 0)
  }

  const incrementCallbackCount = () => {
    const current = getCallbackCount()
    localStorage.setItem(CALLBACK_RATE_LIMIT_KEY, current + 1)
  }

  const isCallbackLimitReached = () => {
    return getCallbackCount() >= CALLBACK_MAX_CLICKS
  }

  const shouldTriggerCallback = (text) => {
    if (!text) return false
    const lower = text.toLowerCase()
    return CALLBACK_INTENT_KEYWORDS.some((k) => lower.includes(k))
  }

  const sendMessage = async (text) => {
    if (!text.trim()) return

    const lower = text.toLowerCase()

  if (PLACEMENT_KEYWORDS.some(k => lower.includes(k))) {
    pushUser(text)
    pushBot("Here are NIET placement details ")
    pushOptions(["Placement Records"], false)
    setInput("")
    return
  }
    if (!callbackStep && shouldTriggerCallback(text)) {
      pushUser(text)
      setCallbackStep("name")
      pushBot("I can help you with fees and admission details. May I know your name?")
      setInput("")
      return
    }
    if (callbackStep === "name") {
      if (!isValidName(text)) {
        pushBot("Please enter a valid name (only letters, min 2 characters).")
        setInput("")
        return
      }

      setCallbackData((prev) => ({ ...prev, name: text.trim() }))
      localStorage.setItem(
        CALLBACK_STORAGE_KEY,
        JSON.stringify({ ...callbackData, name: text.trim() })
      )

      pushUser(text)
      setCallbackStep("phone")
      pushBot("Please provide your 10-digit mobile number.")
      setInput("")
      return
    }

    if (callbackStep === "phone") {
      if (!isValidIndianPhone(text)) {
        pushBot("Please enter a valid Indian mobile number.")
        setInput("")
        return
      }

      const cleanedPhone = text.replace(/\s|-/g, "").replace(/^(\+91)/, "")

      const updatedData = { ...callbackData, phone: cleanedPhone }
      setCallbackData(updatedData)
      localStorage.setItem(CALLBACK_STORAGE_KEY, JSON.stringify(updatedData))

      pushUser(cleanedPhone)
      setCallbackStep(null)

      await sendCallbackToBackend(updatedData)

      pushBot("Thank you! Our counsellor will contact you shortly.")
      pushOptions(INITIAL_OPTIONS, false)
      setInput("")
      return
    }

    pushUser(text)
    setInput("")
    setTyping(true)
    setIsSending(true)

    try {
      const res = await fetch("http://localhost:8000/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question: text }),
      })

      const data = await res.json()
      await delay(600)

      if (data.images?.length) pushImages(data.images)
      if (data.type === "positive_sensitive") {
        if (data.text) {
          pushBot(data.text)
        }

        if (Array.isArray(data.details)) {
          const bulletText = data.details.map(d => `- ${d}`).join("\n")
          pushBot(bulletText)
        }

        if (Array.isArray(data.actions)) {
          data.actions.forEach(action => {
            if (action.type === "callback") {
              if (isCallbackLimitReached()) {
                pushBot(
                  "You have reached the maximum number of callback requests. "
                  + "Please wait or contact NIET directly through the official website."
                )
              } else {
                incrementCallbackCount()
                pushBot("Would you like our counsellor to contact you?")
                pushOptions(["Request Callback"], false)
              }
            }


            if (action.type === "link" && action.url) {
              pushBot(`LINK::${action.label}||${action.url}`)
            }
          })
        }
        setTyping(false)
        setIsSending(false)
        return
      }

      if (data.type === "sensitive_redirect") {
        if (data.text) {
          pushBot(data.text)
        }

        if (Array.isArray(data.actions)) {
          data.actions.forEach(action => {
            if (action.type === "callback") {
              pushBot("Would you like our counsellor to contact you?")
              pushOptions(["Request Callback"], false)
            }

            if (action.type === "link" && action.url) {
              pushBot(`LINK::${action.label}||${action.url}`)
            }
          })
        }
        setTyping(false)
        setIsSending(false)
        return
      }

      if (data.text || data.link) {
        if (data.text) pushBot(data.text)
        if (data.link?.url) {
          pushBot(`LINK::${data.link.label}||${data.link.url}`)
        }
        return
      }

      if (data.final_answer || data.answer)
        pushBot(data.final_answer || data.answer)
    } catch {
      pushBot("Server error. Please try again.")
    } finally {
      setTyping(false)
      setIsSending(false)
    }
  }


  return (
    <div
      className={`h-full flex flex-col overflow-hidden relative transform-gpu ${embed ? "" : "bg-white"
        }`}
    >
      {!embed && <div className="chat-mesh-bg" />}

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
            className={`flex gap-2 items-start animate-in fade-in slide-in-from-bottom-2 duration-500 relative ${activeDropdown === m.id ? "z-50" : "z-0"
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
              {m.type === "images" && (
                <div className="w-full">
                  <ImageSlideshow images={m.images} />
                </div>
              )}

              <div
                className={`relative z-10 pointer-events-auto leading-relaxed whitespace-pre-line ${m.from === "user"
                  ? " text-white rounded-full shadow-lg font-medium "
                  : "bg-white rounded-2xl rounded-tl-none text-slate-700 shadow-sm p-4"
                  }`}
              >
                {m.type === "options" ? (
                  <div className="w-full">
                    <div className="text-[11px] font-bold text-[#e2111f] uppercase mb-3 border-b border-[#e2111f]/10 pb-1 font-[Arial,sans-serif]">
                      Quick Actions
                    </div>
                    {m.options.some(
                      (opt) => opt.match(/^[BM]\./i) || opt.toLowerCase().includes("TWINNING PROGRAM (International)  in"),
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
                ) : m.type === "text" ? (
                  renderWithLinks(m.text)
                ) : null}
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

      <div className={`p-4 pb-4 ${embed ? "" : "bg-white border-t border-slate-100 shadow-[0_-10px_20px_rgba(0,0,0,0.02)]"}`}>
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
            className={`w-full ${embed ? "bg-transparent border-slate-400/50" : "bg-white border-slate-300"} rounded-[24px] px-6 py-[10px] pr-14 text-[14px] text-slate-700 focus:outline-none focus:ring-2 focus:ring-[#e2111f]/20 focus:border-[#e2111f] transition-all duration-300 placeholder:text-slate-400 font-medium h-[46px] shadow-sm`}
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