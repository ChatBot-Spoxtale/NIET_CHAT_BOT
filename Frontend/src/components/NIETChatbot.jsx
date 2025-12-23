import { useState } from "react";
import NIETChatbotMessages from "./NIETChatbotMessages";

export default function NIETChatbot() {
  const [open, setOpen] = useState(false);

  return (
    <>
      {/*CHAT LAUNCHER*/}
      <button
        onClick={() => setOpen(prev => !prev)}
        className="
          fixed bottom-5 right-5 z-50
          w-14 h-14 rounded-full
          bg-[#e2111f] shadow-xl
          flex items-center justify-center
        "
        aria-label="Open NIET Chatbot"
      >
        <div className="w-9 h-9 rounded-full bg-white flex items-center justify-center overflow-hidden">
          <img
            src="/niet-logo.svg"
            alt="NIET"
            className="w-6 h-6 object-contain"
          />
        </div>
      </button>

      {/*CHAT CONTAINER*/}
      {open && (
        <div
          className="
            fixed inset-0 z-40
            flex items-center justify-center
            sm:items-end sm:justify-end
            sm:bottom-24 sm:right-5
            pointer-events-none
          "
        >
          <div
            className="
              pointer-events-auto
              w-[92vw] sm:w-[26rem] lg:w-[28rem]
              h-[80vh] max-h-[720px]
              bg-white rounded-xl
              shadow-2xl overflow-hidden
            "
          >
            <NIETChatbotMessages />
          </div>
        </div>
      )}
    </>
  );
}
