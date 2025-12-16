import React, { useState, useEffect, useRef } from "react";
import baseKnowledge from "../../../RAG/data/base_knowledge.json";

function now() {
  return new Date().toLocaleTimeString([], {
    hour: "2-digit",
    minute: "2-digit",
  });
}

function delay(ms) {
  return new Promise((res) => setTimeout(res, ms));
}

const getCoursesByLevel = (level) => {
  const courses = Object.values(baseKnowledge.courses || {});

  if (level === "UG") {
    return courses.filter(
      (c) =>
        c.course_name.startsWith("B.") ||
        c.course_name.startsWith("Bachelor")
    );
  }

  if (level === "PG") {
    return courses.filter(
      (c) =>
        c.course_name.startsWith("M.") ||
        c.course_name.startsWith("Master") ||
        c.course_name === "MBA"
    );
  }

  if (level === "TWINNING") {
    return courses.filter((c) =>
      c.course_name.toLowerCase().includes("twinning")
    );
  }

  return [];
};

export default function NIETChatbotMessages({ initialMessages = [] }) {
  const [messages, setMessages] = useState(() => {
    if (initialMessages.length) return initialMessages;
    return [
      {
        id: 1,
        from: "bot",
        text: "Hello! I'm the NIET Assistant — how can I help you today?",
        time: now(),
      },
    ];
  });

  const [input, setInput] = useState("");
  const [typing, setTyping] = useState(false);
  const [isSending, setIsSending] = useState(false);

  const [options, setOptions] = useState([]);
  const [breadcrumb, setBreadcrumb] = useState(["Home"]);

  const messagesRef = useRef(null);

  useEffect(() => {
    setOptions([
      "About NIET",
      "Courses Offered",
      "Admission",
      "Placement Records",
      "Activities",
      "Other",
    ]);
  }, []);

  useEffect(() => {
    if (messagesRef.current) {
      messagesRef.current.scrollTop = messagesRef.current.scrollHeight;
    }
  }, [messages, typing, options]);

  const pushBot = (text) =>
    setMessages((m) => [
      ...m,
      { id: Date.now() + Math.random(), from: "bot", text, time: now() },
    ]);

  const pushUser = (text) =>
    setMessages((m) => [
      ...m,
      { id: Date.now() + Math.random(), from: "user", text, time: now() },
    ]);

  const handleBreadcrumbClick = (index) => {
    const path = breadcrumb.slice(0, index + 1);
    setBreadcrumb(path);
    setOptions([]);

    if (path.length === 1) {
      setOptions([
        "About NIET",
        "Courses Offered",
        "Admission",
        "Placement Records",
        "Activities",
        "Other",
      ]);
    }

    if (path.includes("Courses")) {
      setOptions([
        "Undergraduate Programs",
        "Postgraduate Programs",
        "Twinning Programs",
      ]);
    }

    if (path.includes("UG")) {
      setOptions(getCoursesByLevel("UG").map((c) => c.course_name));
    }

    if (path.includes("PG")) {
      setOptions(getCoursesByLevel("PG").map((c) => c.course_name));
    }
  };

  /*OPTION HANDLER*/
  const handleOptionClick = (opt) => {
    pushUser(opt);
    setOptions([]);

    if (opt === "Courses Offered") {
      setBreadcrumb(["Home", "Courses"]);
      setOptions([
        "Undergraduate Programs",
        "Postgraduate Programs",
        "Twinning Programs",
      ]);
      return;
    }

    if (opt === "Undergraduate Programs") {
      setBreadcrumb(["Home", "Courses", "UG"]);
      setOptions(getCoursesByLevel("UG").map((c) => c.course_name));
      return;
    }

    if (opt === "Postgraduate Programs") {
      setBreadcrumb(["Home", "Courses", "PG"]);
      setOptions(getCoursesByLevel("PG").map((c) => c.course_name));
      return;
    }

    if (opt === "Twinning Programs") {
      setBreadcrumb(["Home", "Courses", "Twinning"]);
      setOptions(getCoursesByLevel("TWINNING").map((c) => c.course_name));
      return;
    }

    if (breadcrumb.includes("UG") || breadcrumb.includes("PG")) {
      setBreadcrumb((b) => [...b, opt]);
      pushBot(
        `You selected ${opt}. Ask me about eligibility, fees, admission, or placements.`
      );
      return;
    }

    if (opt === "Admission") {
      setBreadcrumb(["Home", "Admission"]);
      setOptions(["Eligibility", "Direct Admission", "Indirect Admission"]);
      return;
    }

    if (opt === "Eligibility") {
      pushBot("Eligibility varies by course. Please specify a program.");
      return;
    }

    if (opt === "Direct Admission") {
      pushBot("Direct admission is available via management quota.");
      return;
    }

    if (opt === "Indirect Admission") {
      pushBot("Admission through entrance exams and counseling.");
      return;
    }

    if (opt === "Other") {
      pushBot("Please type your query below.");
    }
  };

  const sendMessage = async (text) => {
    if (!text.trim()) return;

    pushUser(text);
    setInput("");
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
      pushBot("Error contacting server.");
    } finally {
      setTyping(false);
      setIsSending(false);
    }
  };

  return (
    <div className="h-full w-full flex flex-col bg-white">
      {/*HEADER WITH MAIN LOGO*/}
      <div className="shrink-0 px-4 py-3 bg-gradient-to-r from-[#e2111f] to-[#551023] text-white flex items-center gap-3">
        <div className="w-10 h-10 rounded-full bg-white flex items-center justify-center overflow-hidden shrink-0">
          <img
            src="/niet-logo.svg"
            alt="NIET"
            className="w-7 h-7 object-contain"
          />
        </div>

        <div className="leading-tight">
          <div className="font-semibold text-sm">NIET Virtual Assistant</div>
          <div className="text-xs opacity-90">
            Admissions & College Queries
          </div>
        </div>
      </div>

      {/*BREADCRUMB*/}
      <div className="shrink-0 px-4 py-1 text-xs text-gray-500 border-b">
        {breadcrumb.map((b, i) => (
          <span
            key={i}
            onClick={() => handleBreadcrumbClick(i)}
            className="cursor-pointer hover:underline"
          >
            {b}
            {i < breadcrumb.length - 1 && " > "}
          </span>
        ))}
      </div>

      {/*CHAT AREA*/}
      <div
        ref={messagesRef}
        className="flex-1 overflow-y-auto px-4 py-3 bg-gray-50 flex flex-col gap-4"
      >
        {messages.map((m) => (
          <div
            key={m.id}
            className={`flex items-end gap-3 ${
              m.from === "user" ? "justify-end" : "justify-start"
            }`}
          >
            {/*BOT AVATAR*/}
            {m.from === "bot" && (
              <div className="w-9 h-9 rounded-full border bg-white flex items-center justify-center shrink-0 overflow-hidden">
                <img
                  src="/niet-logo.svg"
                  alt="NIET"
                  className="w-6 h-6 object-contain"
                />
              </div>
            )}

            {/*MESSAGE*/}
            <div
              className={`max-w-[70%] px-4 py-3 rounded-xl shadow-sm text-sm ${
                m.from === "user"
                  ? "bg-gradient-to-b from-[#e2111f] to-[#551023] text-white"
                  : "bg-white text-[#551023]"
              }`}
            >
              {m.text}
              <div className="text-xs text-gray-400 text-right mt-1">
                {m.time}
              </div>
            </div>

            {/*USER AVATAR*/}
            {m.from === "user" && (
              <div className="w-9 h-9 rounded-full bg-[#e2111f] text-white flex items-center justify-center shrink-0 font-semibold">
                U
              </div>
            )}
          </div>
        ))}

        {/*OPTIONS*/}
        {options.length > 0 && (
          <div className="self-start max-w-[85%] bg-white border rounded-xl shadow-sm p-3">
            <div className="text-sm font-medium text-[#551023] mb-2">
              Select an option
            </div>

            <div className="max-h-48 overflow-y-auto divide-y">
              {options.map((opt) => (
                <div
                  key={opt}
                  onClick={() => handleOptionClick(opt)}
                  className="px-2 py-2 cursor-pointer text-sm text-[#551023] hover:bg-gray-50 transition"
                >
                  {opt}
                </div>
              ))}
            </div>
          </div>
        )}

        {typing && (
          <div className="bg-white px-3 py-2 rounded-xl shadow-sm w-fit">
            <span className="animate-bounce inline-block w-2 h-2 bg-gray-400 rounded-full" />
            <span className="animate-bounce inline-block w-2 h-2 bg-gray-400 rounded-full ml-2" />
            <span className="animate-bounce inline-block w-2 h-2 bg-gray-400 rounded-full ml-2" />
          </div>
        )}
      </div>

      {/* INPUT */}
      <form
        onSubmit={(e) => {
          e.preventDefault();
          sendMessage(input);
        }}
        className="shrink-0 flex items-center gap-2 px-3 py-3 border-t bg-white"
      >
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Ask about admissions, courses, placements..."
          className="flex-1 border rounded-full px-3 py-2 outline-none"
        />
        <button
          type="submit"
          disabled={isSending}
          className="bg-[#e2111f] text-white px-4 py-2 rounded-full"
        >
          Send
        </button>
      </form>
    </div>
  );
}
