import React, { useState, useEffect, useRef } from "react";
import baseKnowledge from "../../../RAG/data/base_knowledge.json";

/* ---------------- helpers ---------------- */

function now() {
  return new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
}

function delay(ms) {
  return new Promise((res) => setTimeout(res, ms));
}

const INITIAL_OPTIONS = [
  "About NIET",
  "Courses Offered",
  "Admission",
  "Placement Records",
  "Activities",
  "Other",
];

const getCoursesByLevel = (level) => {
  const courses = Object.values(baseKnowledge.courses || {});
  if (level === "UG") return courses.filter(c => c.course_name?.toLowerCase().startsWith("b"));
  if (level === "PG") return courses.filter(c => c.course_name?.toLowerCase().startsWith("m"));
  if (level === "TWINNING") return courses.filter(c => c.course_name?.toLowerCase().includes("twinning"));
  return [];
};

function renderWithLinks(text) {
  const urlRegex = /(https?:\/\/[^\s]+)/g;
  return text.split(urlRegex).map((part, i) =>
    part.match(urlRegex) ? (
      <a key={i} href={part} target="_blank" rel="noreferrer" className="text-blue-600 underline">
        {part}
      </a>
    ) : (
      <span key={i}>{part}</span>
    )
  );
}

/* ---------------- component ---------------- */

export default function NIETChatbotMessages() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [typing, setTyping] = useState(false);
  const [isSending, setIsSending] = useState(false);
  const messagesRef = useRef(null);

  /* ---------- restore session ---------- */
  useEffect(() => {
    const saved = sessionStorage.getItem("niet_chat_messages");
    if (saved) {
      try {
        const parsed = JSON.parse(saved);
        if (Array.isArray(parsed)) {
          setMessages(parsed);
          return;
        }
      } catch {}
    }

    // first load
    pushBot("Hello! I'm the NIET Assistant — how can I help you today?");
    pushOptions(INITIAL_OPTIONS, false);
  }, []);

  /* ---------- persist session ---------- */
  useEffect(() => {
    sessionStorage.setItem("niet_chat_messages", JSON.stringify(messages));
  }, [messages]);

  /* ---------- auto scroll ---------- */
  useEffect(() => {
    messagesRef.current?.scrollTo({
      top: messagesRef.current.scrollHeight,
      behavior: "smooth",
    });
  }, [messages, typing]);

  /* ---------- message helpers ---------- */

  const pushBot = (text) =>
    setMessages((m) => [
      ...m,
      { id: crypto.randomUUID(), from: "bot", type: "text", text, time: now() },
    ]);

  const pushUser = (text) =>
    setMessages((m) => [
      ...m,
      { id: crypto.randomUUID(), from: "user", type: "text", text, time: now() },
    ]);

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
    ]);

  /* ---------- option click ---------- */

  const handleOptionClick = (opt) => {
    pushUser(opt);

    if (opt === "Courses Offered") {
      pushOptions(
        ["Undergraduate Programs", "Postgraduate Programs", "Twinning Programs"],
        true
      );
      return;
    }

    if (opt === "About NIET") {
      pushOptions(["Institute", "Research", "Facilities"], true);
      return;
    }

    if (opt === "Undergraduate Programs") {
      pushOptions(getCoursesByLevel("UG").map(c => c.course_name), true);
      return;
    }

    if (opt === "Postgraduate Programs") {
      pushOptions(getCoursesByLevel("PG").map(c => c.course_name), true);
      return;
    }

    if (opt === "Twinning Programs") {
      pushOptions(getCoursesByLevel("TWINNING").map(c => c.course_name), true);
      return;
    }

    if (opt === "Institute") {
      pushBot("NIET is a premier institute focused on academic excellence.");
      return;
    }

    if (opt === "Research") {
      pushBot("NIET actively promotes research and innovation.");
      return;
    }

    if (opt === "Facilities") {
      sendMessage("Facilities available at NIET");
      return;
    }

    sendMessage(`Tell me about ${opt} in NIET`);
  };

  /* ---------- backend ---------- */

  const sendMessage = async (text) => {
    pushUser(text);
    setTyping(true);
    setIsSending(true);

    try {
      const res = await fetch("http://localhost:8000/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question: text }),
      });
      const data = await res.json();
      await delay(600);
      pushBot(data.answer || "Sorry, I could not generate a reply.");
    } catch {
      pushBot("Server error. Please try again.");
    } finally {
      setTyping(false);
      setIsSending(false);
    }
  };

  /* ---------------- render ---------------- */

  return (
    <div className="h-full flex flex-col bg-white">
      {/* HEADER */}
      <div className="px-4 py-3 bg-gradient-to-r from-[#e2111f] to-[#551023] text-white flex gap-3">
        <div className="w-10 h-10 bg-white rounded-full flex items-center justify-center">
          <img src="/niet-logo.svg" alt="NIET" className="w-7 h-7" />
        </div>
        <div>
          <div className="font-semibold text-sm">NIET Virtual Assistant</div>
          <div className="text-xs opacity-90">Admissions & College Queries</div>
        </div>
      </div>

      {/* CHAT */}
      <div ref={messagesRef} className="flex-1 overflow-y-auto px-4 py-3 bg-gray-50 flex flex-col gap-4">
        {messages.map((m) => (
          <div key={m.id} className={`flex gap-3 ${m.from === "user" ? "justify-end" : ""}`}>
            {m.from === "bot" && (
              <div className="w-9 h-9 bg-white rounded-full border flex items-center justify-center">
                <img src="/niet-logo.svg" className="w-6 h-6" />
              </div>
            )}

            <div className={`max-w-[70%] px-4 py-3 rounded-xl shadow-sm text-sm ${
              m.from === "user"
                ? "bg-gradient-to-b from-[#e2111f] to-[#551023] text-white"
                : "bg-white text-[#551023]"
            }`}>
              {m.type === "options" ? (
                <>
                  <div className="flex justify-between mb-2 font-medium">
                    Select an option
                    {m.showBack && (
                      <button
                        onClick={() => pushOptions(INITIAL_OPTIONS, false)}
                        className="text-xs bg-gray-100 px-2 py-1 rounded"
                      >
                        ← Back
                      </button>
                    )}
                  </div>

                  <div className="max-h-40 overflow-y-auto divide-y">
                    {m.options.map((opt) => (
                      <div
                        key={opt}
                        onClick={() => handleOptionClick(opt)}
                        className="px-2 py-2 cursor-pointer hover:bg-gray-50"
                      >
                        {opt}
                      </div>
                    ))}
                  </div>
                </>
              ) : (
                <>
                  {renderWithLinks(m.text)}
                  <div className="text-xs text-gray-400 text-right mt-1">{m.time}</div>
                </>
              )}
            </div>

            {m.from === "user" && (
              <div className="w-9 h-9 rounded-full bg-[#e2111f] text-white flex items-center justify-center">
                U
              </div>
            )}
          </div>
        ))}

        {typing && <div className="text-sm text-gray-500">Typing…</div>}
      </div>

      {/* INPUT */}
      <form
        onSubmit={(e) => {
          e.preventDefault();
          sendMessage(input);
          setInput("");
        }}
        className="border-t px-3 py-3 flex gap-2"
      >
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          className="flex-1 border rounded-full px-3 py-2"
          placeholder="Ask about admissions, courses, placements..."
        />
        <button disabled={isSending} className="bg-[#e2111f] text-white px-4 py-2 rounded-full">
          Send
        </button>
      </form>
    </div>
  );
}
