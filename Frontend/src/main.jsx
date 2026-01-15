import React from "react"
import { createRoot } from "react-dom/client"
import App from "./App"
import "./index.css"

if (window.self !== window.top) {
  document.body.classList.add("embed")
}

const root = createRoot(document.getElementById("root"))
root.render(<App />)
