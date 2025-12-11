import React, { useState, useEffect, useRef } from 'react';

export default function NIETChatbot() {
  const [open, setOpen] = useState(false);
  const [messages, setMessages] = useState([
    {
      id: 1,
      from: 'bot',
      text: "Hello! I'm the NIET Assistant — how can I help you today?",
      time: now(),
    },
  ]);

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
  }, [messages, open, typing]);

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

    // Append user's message immediately
    setMessages((m) => [...m, userMsg]);
    setInput('');
    setIsSending(true);

    // Simulate status progression locally
    setTimeout(
      () => setMessages((m) => m.map((msg) => (msg.id === id ? { ...msg, status: 'sent' } : msg))),
      400
    );
    setTimeout(
      () => setMessages((m) => m.map((msg) => (msg.id === id ? { ...msg, status: 'delivered' } : msg))),
      900
    );
    setTimeout(
      () => setMessages((m) => m.map((msg) => (msg.id === id ? { ...msg, status: 'read' } : msg))),
      1600
    );

    // Typing behaviour: show immediately, ensure a minimum visible time
    const minTyping = 600; // ms
    const typingStart = Date.now();
    setTyping(true);

    try {
      // Send request to backend
      const res = await fetch('/chatBot/message', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: newText, sessionId }),
      });

      // If response not ok, read body text (helps debugging)
      if (!res.ok) {
        const bodyText = await res.text().catch(() => '[unreadable body]');
        throw new Error(`Server error ${res.status}: ${bodyText}`);
      }

      // Try parse JSON — if backend returns non-JSON this will throw and go to catch
      const data = await res.json();

      // Collect possible reply fields
      const botTexts = [];
      if (data.reply) botTexts.push(data.reply);
      if (Array.isArray(data.replies)) botTexts.push(...data.replies);
      if (data.text) botTexts.push(data.text);
      if (botTexts.length === 0) botTexts.push('Sorry, I could not generate a reply.');

      // Ensure typing visible for at least minTyping ms for realism
      const elapsed = Date.now() - typingStart;
      if (elapsed < minTyping) {
        await delay(minTyping - elapsed);
      }

      // Hide typing and append bot replies
      setTyping(false);
      setMessages((m) => [
        ...m,
        ...botTexts.map((t) => ({
          id: Date.now() + Math.random(),
          from: 'bot',
          text: t,
          time: now(),
        })),
      ]);
    } catch (err) {
      console.error('Chat error:', err);

      // Clear typing (important) and show a helpful error to the user
      setTyping(false);
      setMessages((m) => [
        ...m,
        {
          id: Date.now() + 1,
          from: 'bot',
          // show short message including the error message (trimmed)
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

  const toggleOpen = () => setOpen((v) => !v);

  return (
    <>
      {/* Floating launcher — slightly moved left from the corner */}
      <button
        onClick={toggleOpen}
        aria-label="Open chat"
        className="fixed right-8 bottom-5 w-14 h-14 rounded-full bg-[#e2111f] shadow-lg flex items-center justify-center z-50"
      >
        {/* circular padded avatar so square images fit perfectly */}
        <div className="w-10 h-10 rounded-full bg-white p-1 flex items-center justify-center overflow-hidden">
          <img
            src="/niet-logo.svg"
            alt="NIET"
            className="w-full h-full object-contain rounded-full"
            onError={(e) => (e.target.src = '/niet-logo.png')}
          />
        </div>
      </button>

      {/* Chat window — shifted left a bit and wider */}
      <div
        className={`${
          open ? 'translate-y-0 opacity-100' : 'translate-y-6 opacity-0 pointer-events-none'
        } fixed right-12 bottom-24 w-[22rem] md:w-[34rem] z-40 transition-all`}
        style={{ display: 'block' }}
      >
        <div className="bg-white rounded-xl shadow-xl overflow-hidden flex flex-col">
          <div className="flex items-center justify-between px-4 py-3 bg-gradient-to-r from-[#e2111f] to-[#551023] text-white">
            <div className="flex items-center gap-3">
              <div className="w-11 h-11 rounded-full bg-white/20 p-1 flex items-center justify-center overflow-hidden">
                <img
                  src="/niet-logo.svg"
                  alt="logo"
                  className="w-full h-full object-contain rounded-full"
                  onError={(e) => (e.target.src = '/niet-logo.png')}
                />
              </div>
              <div>
                <div className="font-semibold">NIET Virtual Assistant</div>
                <div className="text-xs opacity-90">Official - NIET</div>
              </div>
            </div>
            {/* kept header compact — remove right-side text for a cleaner look */}
          </div>

          <div className="p-4 bg-gray-50">
            <div ref={messagesRef} className="h-80 overflow-auto flex flex-col gap-3 pr-2">
              {messages.map((m) => (
                <div key={m.id} className={`flex items-end gap-3 ${m.from === 'user' ? 'justify-end' : 'justify-start'}`}>
                  <div className="w-9 h-9 rounded-full bg-white flex items-center justify-center text-sm font-bold text-[#551023] overflow-hidden">
                    {m.from === 'bot' ? (
                      <img src="/niet-logo.svg" alt="NIET" className="w-full h-full object-cover" onError={(e) => (e.target.src = '/niet-logo.png')} />
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
                    <div className="text-xs text-gray-400 text-right mt-1">{m.time}</div>
                  </div>
                </div>
              ))}

              {/* Typing indicator */}
              {typing && (
                <div className="flex items-center gap-3">
                  <div className="w-9 h-9 rounded-full bg-white flex items-center justify-center text-sm font-bold text-[#551023] overflow-hidden">
                    <img src="/niet-logo.svg" alt="NIET" className="w-full h-full object-cover" onError={(e) => (e.target.src = '/niet-logo.png')} />
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
        </div>
      </div>
    </>
  );
}

function now() {
  return new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
}

function delay(ms) {
  return new Promise((res) => setTimeout(res, ms));
}
