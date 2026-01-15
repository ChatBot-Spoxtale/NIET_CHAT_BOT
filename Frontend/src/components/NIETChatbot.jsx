"use client"

import { useState } from "react"
import NIETChatbotMessages from "./NIETChatbotMessages"

export default function NIETChatbot(embed={embed}) {
  const [open, setOpen] = useState(false)

  return (
    <>
      {!open && (
        <button
          onClick={() => setOpen(true)}
          className="fixed bottom-6 right-6 z-[100] w-14 h-14 rounded-2xl bg-gradient-to-br from-[#e2111f] to-[#b00d18] flex items-center justify-center shadow-[0_10px_30px_rgba(226,17,31,0.4)] transition-all duration-300 hover:scale-110 active:scale-95 group overflow-hidden"
          aria-label="Open Chat"
        >
          <div className="relative w-full h-full flex items-center justify-center">
            <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z"
              />
            </svg>
          </div>
        </button>
      )}

      {open && (
        <div
  className={
    embed
      ? "fixed bottom-6 right-6 z-[90]"   // no fullscreen, no transparency
      : "fixed inset-0 z-[90] pointer-events-none flex flex-col items-end justify-end p-2 sm:p-6 animate-in fade-in duration-300"
          }
        >
          <div className="relative pointer-events-auto w-full sm:w-[380px] md:w-[480px] lg:w-[560px] h-full sm:h-[min(700px,calc(100vh-120px))] md:h-[min(800px,calc(100vh-100px))] lg:h-[min(850px,calc(100vh-80px))] bg-white border border-slate-100 shadow-[0_30px_100px_rgba(0,0,0,0.18)] flex flex-col animate-in slide-in-from-bottom-8 duration-500 rounded-[32px] transform-gpu">
            {/* Desktop Close Button */}
            <button
              onClick={() => setOpen(false)}
              className="absolute -top-3 -right-3 z-[101] w-7 h-7 rounded-full bg-[#e2111f] items-center justify-center shadow-lg transition-all duration-300 hover:scale-110 active:scale-95 hidden sm:flex border-2 border-white"
              aria-label="Close Chat"
            >
              <svg className="w-3.5 h-3.5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>

            {/* Mobile Close Button */}
            <button
              onClick={() => setOpen(false)}
              className="absolute -top-3 -right-3 z-[101] w-8 h-8 rounded-full bg-[#e2111f] items-center justify-center shadow-lg transition-all duration-300 active:scale-95 flex sm:hidden border-2 border-white"
              aria-label="Close Chat"
            >
              <svg className="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>

            <div className="flex-1 flex flex-col rounded-[32px] overflow-hidden">
              <NIETChatbotMessages embed={embed}/>
            </div>
          </div>
        </div>
      )}
    </>
  )
}
