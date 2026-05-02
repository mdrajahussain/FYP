"use client"

import React, { useState, useRef, useEffect } from "react"
import { Send, Bot, User, Sparkles, BrainCircuit } from "lucide-react"
import ReactMarkdown from "react-markdown"
import rehypeHighlight from "rehype-highlight"

import { useChatAI } from "@/hooks/useChat"

const SUGGESTIONS = [
  "DCT embedding?",
  "PSNR value?",
  "RS Analysis?",
  "Capacity tips?",
]

const Chat = () => {
  const [messages, setMessages] = useState([
    {
      role: "assistant",
      content:
        "System initialized. I am your AI-Powered Multi-Media Steganography System Specialist. How can I assist with your forensic analysis today?",
    },
  ])

  const { mutate, isPending } = useChatAI()

  const [input, setInput] = useState("")
  const scrollRef = useRef<HTMLDivElement>(null)

  // Auto-scroll
  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight
    }
  }, [messages, isPending])

  const handleSend = () => {
    if (!input.trim()) return

    const userMessage = { role: "user", content: input }

    // Add user message
    setMessages((prev) => [...prev, userMessage])

    mutate(
      { query: input },
      {
        onSuccess: (data) => {
          setMessages((prev) => [
            ...prev,
            {
              role: "assistant",
              content: data?.response || "No response received.",
            },
          ])
        },
        onError: () => {
          setMessages((prev) => [
            ...prev,
            {
              role: "assistant",
              content: "⚠️ AI service unavailable.",
            },
          ])
        },
      },
    )

    setInput("")
  }

  return (
    /* lg:pl-32 accounts for your sidebar; pt-6 for mobile, pt-32 for desktop */
    // <div className="max-w-5xl mx-auto h-[100dvh] lg:h-[calc(100vh-40px)] flex flex-col pt-6 lg:pt-28 px-4 lg:pl-32">
    <div className="max-w-5xl mx-auto h-[100dvh] lg:h-[calc(100vh-40px)] flex flex-col pt-6 lg:pt-28 px-4 lg:pl-32 pb-72 lg:pb-0">
      {/* Chat Area - Flexible height */}
      <div
        ref={scrollRef}
        className="flex-1 overflow-y-auto space-y-6 scroll-smooth pr-2 scrollbar-hide"
      >
        {messages.map((msg, idx) => (
          <div
            key={idx}
            className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"} animate-in fade-in slide-in-from-bottom-2`}
          >
            <div
              className={`flex gap-3 max-w-[90%] md:max-w-[80%] ${
                msg.role === "user" ? "flex-row-reverse" : "flex-row"
              }`}
            >
              {/* Avatar - Hidden on very small mobile to save space */}
              <div
                className={`hidden xs:flex shrink-0 w-8 h-8 md:w-10 md:h-10 rounded-xl items-center justify-center shadow-sm ${
                  msg.role === "user"
                    ? "bg-white border border-slate-200 text-slate-600"
                    : "bg-indigo-600 text-white"
                }`}
              >
                {msg.role === "user" ? (
                  <User size={18} />
                ) : (
                  <BrainCircuit size={18} />
                )}
              </div>

              {/* Message Bubble */}
              <div
                className={`p-4 md:p-5 rounded-[20px] text-[14px] md:text-[15px] leading-relaxed shadow-sm break-words whitespace-pre-wrap ${
                  msg.role === "user"
                    ? "bg-indigo-600 text-white rounded-tr-none"
                    : "bg-white border border-slate-100 text-slate-700 rounded-tl-none"
                }`}
              >
                {msg.role === "assistant" ? (
                  <ReactMarkdown rehypePlugins={[rehypeHighlight]}>
                    {msg.content}
                  </ReactMarkdown>
                ) : (
                  msg.content
                )}
              </div>
            </div>
          </div>
        ))}

        {isPending && (
          <div className="flex justify-start">
            <div className="bg-slate-100 px-4 py-2 rounded-full text-[11px] font-bold text-slate-500 animate-pulse border border-slate-200">
              Generating response...
            </div>
          </div>
        )}
      </div>

      {/* Input Area - Fixed at bottom */}
      {/* <div className="py-6  bg-red-400 lg:mb-0 sm:mb-60"> */}
      {/* Input Area */}
      <div className="fixed bottom-24 left-0 right-0 px-4 py-4 bg-white sm:static sm:px-0 sm:py-6">
        {/* Quick Suggestions - Scrollable horizontally */}
        <div className="flex gap-2 overflow-x-auto pb-4 scrollbar-hide no-scrollbar">
          {SUGGESTIONS.map((s, i) => (
            <button
              key={i}
              onClick={() => setInput(s)}
              className="whitespace-nowrap px-4 py-1.5 bg-white border border-slate-200 rounded-full text-[12px] font-bold text-slate-500 hover:border-indigo-500 hover:text-indigo-600 transition-all cursor-pointer shadow-sm active:scale-95"
            >
              {s}
            </button>
          ))}
        </div>

        {/* Text Input Container */}
        <div className="relative group ">
          <div className="absolute inset-0 bg-indigo-500/5 blur-2xl group-focus-within:bg-indigo-500/10 transition-all rounded-[32px]" />
          <div className="relative bg-white border border-slate-200 rounded-[24px] md:rounded-[32px] p-1.5 md:p-2 flex items-center gap-2 shadow-2xl shadow-slate-200/60">
            <div className="hidden sm:block pl-4 text-indigo-500">
              <Sparkles size={20} />
            </div>
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && handleSend()}
              placeholder="Ask about DCT or security..."
              className="flex-1 bg-transparent border-none py-3 md:py-4 px-3 text-[15px] md:text-[16px] text-slate-800 placeholder-slate-400 outline-none w-full"
            />
            <button
              onClick={handleSend}
              disabled={isPending}
              className="bg-indigo-600 text-white p-3 md:p-4 rounded-[18px] md:rounded-[24px] hover:bg-indigo-700 hover:scale-105 active:scale-95 transition-all shadow-lg shadow-indigo-200 border-none cursor-pointer flex shrink-0"
            >
              <Send size={18} />
            </button>
          </div>
        </div>

        <p className=" xs:block text-center text-[9px] text-slate-400 font-bold uppercase tracking-[0.2em] mt-4">
          AI-Powered Multi-Media Steganography System - Powered by Ollama
        </p>
      </div>
    </div>
  )
}

export default Chat
