"use client"

import { useState } from "react"

export default function NIETChatbotUI({ children }) {
  const [isOpen, setIsOpen] = useState(false)

  const onToggle = () => setIsOpen((prev) => !prev)
  return (
    <>
      {/*Floating launcher*/}
      <button
        onClick={onToggle}
        aria-label={isOpen ? "Close chat" : "Open chat"}
        className="fixed right-8 bottom-5 w-14 h-14 rounded-full bg-[#e2111f] shadow-lg flex items-center justify-center z-50 cursor-pointer"
      >
        {isOpen ? (
          <span className="text-white text-2xl font-bold leading-none">×</span>
        ) : (
          <div className="w-10 h-10 rounded-full bg-white p-1 flex items-center justify-center overflow-hidden">
            <img
              src="/niet-logo.svg"
              alt="NIET"
              className="w-full h-full object-contain rounded-full"
              onError={(e) => (e.target.src = "/niet-logo.png")}
            />
          </div>
        )}
      </button>

      {/*Chat window*/}
      <div
        className={`${
          isOpen ? "translate-y-0 opacity-100" : "translate-y-6 opacity-0 pointer-events-none"
        } fixed right-12 bottom-24 w-[22rem] md:w-[34rem] z-40 transition-all`}
        style={{ display: "block" }}
      >
        <div className="bg-white rounded-xl shadow-xl overflow-hidden flex flex-col">
          <div className="flex items-center justify-between px-4 py-3 bg-gradient-to-r from-[#e2111f] to-[#551023] text-white">
            <div className="flex items-center gap-3">
              <div className="w-11 h-11 rounded-full bg-white/20 p-1 flex items-center justify-center overflow-hidden">
                <img
                  src="/niet-logo.svg"
                  alt="logo"
                  className="w-full h-full object-contain rounded-full"
                  onError={(e) => (e.target.src = "/niet-logo.png")}
                />
              </div>
              <div>
                <div className="font-semibold">NIET Virtual Assistant</div>
                <div className="text-xs opacity-90">Official - NIET</div>
              </div>
            </div>
          </div>

          <div className="h-full flex flex-col">{children}</div>
        </div>
      </div>
    </>
  )
}
