import React, { useState, useEffect, useRef } from 'react';
import { findLinkForText } from './keywordLinker';

function now() {
  return new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
}
function delay(ms) {
  return new Promise((res) => setTimeout(res, ms));
}

export default function NIETChatbotMessages({ onSend, initialMessages = [] }) {
  const [messages, setMessages] = useState(() => {
    if (initialMessages && initialMessages.length) return initialMessages;
    return [
      {
        id: 1,
        from: 'bot',
        text: "Hello! I'm the NIET Assistant — how can I help you today?",
        time: now(),
      },
    ];
  });

  const [input, setInput] = useState('');
  const [isSending, setIsSending] = useState(false);
  const [sessionId, setSessionId] = useState(null);
  const [typing, setTyping] = useState(false);

  const messagesRef = useRef(null);

  useEffect(() => {
    let sid = localStorage.getItem('niet_chat_session');
    if (!sid) {
      sid = `s_${Math.random().toString(36).slice(2, 12)}`;
      localStorage.setItem('niet_chat_session', sid);
    }
    setSessionId(sid);
  }, []);

  useEffect(() => {
    if (messagesRef.current) {
      messagesRef.current.scrollTop = messagesRef.current.scrollHeight;
    }
  }, [messages, typing]);

  function parseRepliesFromText(text) {
    if (!text) return [];
    const separators = ['\n---\n', '\n;;;\n', '\r\n---\r\n', '---', ';;;', '\n\n'];
    for (const sep of separators) {
      if (text.includes(sep.replace(/\\n/g, '\n'))) {
        return text
          .split(sep.replace(/\\n/g, '\n'))
          .map((s) => s.trim())
          .filter(Boolean);
      }
    }
    const lines = text.split(/\r?\n/).map((l) => l.trim()).filter(Boolean);
    if (lines.length <= 3) {
      return [text.trim()];
    }
    return lines;
  }

  const sendMessage = async (newText) => {
    if (!newText || !newText.trim()) return;

    const id = Date.now();
    const userMsg = {
      id,
      from: 'user',
      text: newText,
      time: now(),
      status: 'sending',
    };

    setMessages((m) => [...m, userMsg]);
    setInput('');
    setIsSending(true);

    // status simulation
    setTimeout(() => setMessages((m) => m.map((msg) => (msg.id === id ? { ...msg, status: 'sent' } : msg))), 400);
    setTimeout(() => setMessages((m) => m.map((msg) => (msg.id === id ? { ...msg, status: 'delivered' } : msg))), 900);
    setTimeout(() => setMessages((m) => m.map((msg) => (msg.id === id ? { ...msg, status: 'read' } : msg))), 1600);

    const minTyping = 600;
    const typingStart = Date.now();
    setTyping(true);

    try {
      const res = await fetch('http://localhost:8000/chat', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    question: newText, 
  }),
});

if (!res.ok) {
  const bodyText = await res.text().catch(() => '[unreadable body]');
  throw new Error(`Server error ${res.status}: ${bodyText}`);
}

const data = await res.json();

let botTexts = [];
if (data.answer) {
  botTexts.push(data.answer);
}

if (botTexts.length === 0) {
  botTexts.push('Sorry, I could not generate a reply.');
}

      const elapsed = Date.now() - typingStart;
      if (elapsed < minTyping) {
        await delay(minTyping - elapsed);
      }

      setTyping(true);

      const repliesWithLinks = botTexts.map((t) => {
        const link = findLinkForText(t) || findLinkForText(newText);
        return { text: t, link: link || null };
      });

      setMessages((m) => [
        ...m,
        ...repliesWithLinks.map((r) => ({
          id: Date.now() + Math.random(),
          from: 'bot',
          text: r.text,
          link: r.link || undefined,
          time: now(),
        })),
      ]);
    } catch (err) {
      console.error('Chat error:', err);
      setTyping(false);
      setMessages((m) => [
        ...m,
        {
          id: Date.now() + 1,
          from: 'bot',
          text: `Error contacting server: ${err.message}`.slice(0, 300),
          time: now(),
        },
      ]);
    } finally {
      setIsSending(false);
    }
  };

  const handleSubmit = (e) => {
    e && e.preventDefault();
    sendMessage(input);
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage(input);
    }
  };

  return (
    <>
      <div className="p-4 bg-gray-50">
        <div ref={messagesRef} className="h-80 overflow-auto flex flex-col gap-3 pr-2">
          {messages.map((m) => (
            <div key={m.id} className={`flex items-end gap-3 ${m.from === 'user' ? 'justify-end' : 'justify-start'}`}>
              <div className="w-9 h-9 rounded-full bg-white flex items-center justify-center text-sm font-bold text-[#551023] overflow-hidden">
                {m.from === 'bot' ? (
                  <img src="/niet-logo.svg" alt="NIET" className="w-full h-full object-cover" onError={(e) => (e.target.src = '/niet-logo.svg')} />
                ) : (
                  'U'
                )}
              </div>

              <div
                className={`${
                  m.from === 'user' ? 'bg-gradient-to-b from-[#e2111f] to-[#551023] text-white' : 'bg-white text-[#551023]'
                } max-w-[75%] px-4 py-3 rounded-xl shadow-sm`}
              >
                <div className="text-sm leading-relaxed">{m.text}</div>

                {m.link && (
                  <div className="mt-2">
                    <a href={m.link} target="_blank" rel="noopener noreferrer" className="text-sm underline text-[#1d4ed8] break-all">
                      {m.link}
                    </a>
                  </div>
                )}

                <div className="text-xs text-gray-400 text-right mt-1">{m.time}</div>
              </div>
            </div>
          ))}

          {typing && (
            <div className="flex items-center gap-3">
              <div className="w-9 h-9 rounded-full bg-white flex items-center justify-center text-sm font-bold text-[#551023] overflow-hidden">
                <img src="/niet-logo.svg" alt="NIET" className="w-full h-full object-cover" onError={(e) => (e.target.src = '/niet-logo.svg')} />
              </div>

              <div className="bg-white px-3 py-2 rounded-xl shadow-sm flex items-center">
                <span className="inline-block bg-gray-400 w-2 h-2 rounded-full animate-bounce" style={{ animationDelay: '0s' }} />
                <span className="inline-block bg-gray-400 w-2 h-2 rounded-full animate-bounce ml-2" style={{ animationDelay: '.12s' }} />
                <span className="inline-block bg-gray-400 w-2 h-2 rounded-full animate-bounce ml-2" style={{ animationDelay: '.24s' }} />
              </div>
            </div>
          )}
        </div>
      </div>

      <form onSubmit={handleSubmit} className="flex items-center gap-2 px-3 py-3 bg-white border-t">
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Ask about admissions, departments, contacts..."
          className="flex-1 border rounded-full px-3 py-2 outline-none"
        />
        <button type="submit" disabled={isSending} className="bg-[#e2111f] text-white px-4 py-2 rounded-full">
          Send
        </button>
      </form>
    </>
  );
}
