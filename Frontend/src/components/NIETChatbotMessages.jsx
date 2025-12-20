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
  const courses = Object.values(baseKnowledge.courses || {}).filter(
    (c) => c && typeof c.course_name === "string"
  );

  if (level === "UG") {
    return courses.filter((c) => {
      const name = c.course_name.toLowerCase();
      return (
        name.startsWith("b") &&
        !name.includes("international twinning") &&
        !name.includes("twinning program")
      );
    });
  }

  if (level === "PG") {
    return courses.filter((c) => {
      const name = c.course_name.toLowerCase();
      return name.startsWith("m");
    });
  }

  if (level === "TWINNING") {
    return courses.filter((c) => {
      const name = c.course_name.toLowerCase();
      return (
        name.includes("international twinning") ||
        name.includes("twinning program")
      );
    });
  }

  return [];
};


function renderWithLinks(text) {
  const urlRegex = /(https?:\/\/[^\s]+)/g;

  return text.split(urlRegex).map((part, i) => {
    if (part.match(urlRegex)) {
      return (
        <a
          key={i}
          href={part}
          target="_blank"
          rel="noopener noreferrer"
          className="text-blue-600 underline break-all"
        >
          {part}
        </a>
      );
    }
    return <span key={i}>{part}</span>;
  });
}

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

    if (path.includes("Activities")) {
      setOptions([
        "Events",
        "Club",
      ]);
      return;
    }

    if (path.includes("UG")) {
      setOptions(getCoursesByLevel("UG").map((c) => c.course_name));
    }

    if (path.includes("PG")) {
      setOptions(getCoursesByLevel("PG").map((c) => c.course_name));
    }

     if (path.includes("TWINNING")) {
      setOptions(getCoursesByLevel("TWINNING").map((c) => c.course_name));
    }

    if (path.includes("Placement Records")) {
      setOptions([
        "Undergraduate Programs",
        "Postgraduate Programs",
        "Twinning Programs",
      ]);
      return;
    }

    if (path.includes("About NIET")) {
      setOptions([
        "Institute",
        "Research",
        "Facilities",
      ]);
      return;
    }
  };

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

    if (opt === "About NIET") {
      setBreadcrumb(["Home", "About NIET"]);
      setOptions([
        "Institute",
        "Research",
        "Facilities",
      ]);
      return;
    }

    if (opt === "Institute") {
      pushBot(
        `You selected ${opt}. What do you want to know about the ${opt} (overview, rankings, awards, or international_alliances.)`
      );      

      return;
    }

    
    if (opt === "Research") {
      pushBot(
        `You selected ${opt}. What do you want to know about the ${opt} (overview, areas, publications,journals or projects.)`
      );      

      return;
    }

     if (opt === "Facilities") {
     sendMessage(` ${opt}`);
      return;
    }

    if (opt === "Undergraduate Programs") {
      if (breadcrumb.includes("Placement Records")) {
        setBreadcrumb(["Home", "Placement Records", "UG"]);
      } else {
        setBreadcrumb(["Home", "Courses", "UG"]);
      }

      setOptions(getCoursesByLevel("UG").map(c => c.course_name));
      return;
    }

    if (opt === "Postgraduate Programs") {
      if (breadcrumb.includes("Placement Records")) {
        setBreadcrumb(["Home", "Placement Records", "PG"]);
      } else {
        setBreadcrumb(["Home", "Courses", "PG"]);
      }

      setOptions(getCoursesByLevel("PG").map(c => c.course_name));
      return;
    }

    if (opt === "Twinning Programs") {
      if (breadcrumb.includes("Placement Records")) {
        setBreadcrumb(["Home", "Placement Records", "Twinning"]);
      } else {
        setBreadcrumb(["Home", "Courses", "Twinning"]);
      }

      setOptions(getCoursesByLevel("TWINNING").map(c => c.course_name));
      return;
    }

    if (opt === "Admission") {
      setBreadcrumb(["Home", "Admission"]);
      setOptions(["Direct Admission", " Counselling"]);
      return;
    }

    if (opt === "Direct Admission") {
      pushBot("Direct admission is available via management quota.");
      return;
    }

    if (opt === "Counselling") {
      pushBot("Admission through entrance exams and counseling.");
      return;
    }

    if (opt === "Placement Records") {
      setBreadcrumb(["Home", "Placement Records"]);
      setOptions([
        "Undergraduate Programs",
        "Postgraduate Programs",
        "Twinning Programs",
      ]);
      return;
    }

    if (
      breadcrumb.includes("Courses") &&
      (breadcrumb.includes("UG") || breadcrumb.includes("PG") || breadcrumb.includes("Twinning"))
    ) {
      setBreadcrumb(b => [...b, opt]);
      sendMessage(`Tell me full details about ${opt} in NIET`);
      return;
    }

    if (
      breadcrumb.includes("Placement Records") &&
      (breadcrumb.includes("UG") || breadcrumb.includes("PG") || breadcrumb.includes("Twinning"))
    ) {
      setBreadcrumb(b => [...b, opt]);
      sendMessage(`placement record  ${opt} in NIET`);
    }

    if (opt === "Activities") {
      setBreadcrumb(["Home", "Activities"]);
      setOptions([
        "Events",
        "Club",
      ]);
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
function renderLines(text) {
  if (!text) return null;

  return text
    .split(/\. |\n/)        
    .filter(line => line.trim().length > 0)
    .map((line, i) => (
      <div key={i} className="leading-relaxed">
        • {line.trim()}
      </div>
    ));
}

function renderMessageText(text) {
  if (!text) return null;

  return text.split("\n").map((line, i) => (
    <div key={i} className="leading-relaxed">
      {renderWithLinks(line)}
    </div>
  ));
}

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
            className={`flex items-end gap-3 ${m.from === "user" ? "justify-end" : "justify-start"
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
              className={`max-w-[70%] px-4 py-3 rounded-xl shadow-sm text-sm ${m.from === "user"
                  ? "bg-gradient-to-b from-[#e2111f] to-[#551023] text-white"
                  : "bg-white text-[#551023]"
                }`}
            >
              {renderMessageText(m.text)}
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

