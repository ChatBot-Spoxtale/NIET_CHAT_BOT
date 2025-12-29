"use client"

import { useState } from "react"
import NIETChatbotMessages from "./NIETChatbotMessages"

export default function NIETChatbot() {
  const [open, setOpen] = useState(false)

  return (
    <>
      <button
        onClick={() => setOpen((prev) => !prev)}
        className="fixed bottom-6 right-6 z-[100] w-11 h-11 rounded-2xl bg-gradient-to-br from-[#e2111f] to-[#b00d18] flex items-center justify-center shadow-[0_8px_25px_rgba(226,17,31,0.35)] transition-all hover:scale-105 active:scale-95 group"
        aria-label={open ? "Close Chat" : "Open Chat"}
      >
        <div className="relative w-full h-full flex items-center justify-center">
          {open ? (
            <svg
              className="w-8 h-8 text-white animate-in zoom-in duration-300"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M6 18L18 6M6 6l12 12" />
            </svg>
          ) : (
            <img
              src="/niet-logo.svg"
              alt="NIET"
              className="w-8 h-8 object-contain invert brightness-0 animate-in zoom-in duration-300"
            />
          )}
        </div>
      </button>

      {open && (
        <div className="fixed inset-0 z-[90] pointer-events-none flex flex-col items-end justify-end sm:p-6 animate-in fade-in duration-300">
          <div className="pointer-events-auto w-full sm:w-[400px] h-full sm:h-[min(680px,calc(100vh-140px))] bg-white border border-slate-100 shadow-[0_30px_90px_rgba(0,0,0,0.15)] overflow-hidden flex flex-col animate-in slide-in-from-bottom-12 duration-500 sm:rounded-[32px] rounded-none">
            <NIETChatbotMessages />
          </div>
        </div>
      )}
    </>
  )
}
