"use client"

import React, { useEffect, useState } from "react"
import {
  CpuIcon,
  LogIn,
  ShieldCheck,
  LogOut,
  User as UserIcon,
} from "lucide-react"
import { useHealth } from "@/hooks/useHealth"
import Link from "next/link"
import { useRouter } from "next/navigation"

// Define user type based on your localstorage structure
interface UserData {
  id: number
  full_name: string
  email: string
}

const Navbar = () => {
  const { data, isLoading } = useHealth()
  const router = useRouter()

  const [token, setToken] = useState<string | null>(null)
  const [user, setUser] = useState<UserData | null>(null)
  const [isDropdownOpen, setIsDropdownOpen] = useState(false)

  useEffect(() => {
    // 1. Safe access to localStorage after mount
    const myToken = localStorage.getItem("steagno_access_token")
    const myUser = localStorage.getItem("steagno_user")

    if (myToken) setToken(myToken)
    if (myUser) {
      try {
        setUser(JSON.parse(myUser))
      } catch (e) {
        console.error("Failed to parse user info")
      }
    }
  }, [])

  const handleLogout = () => {
    localStorage.removeItem("steagno_access_token")
    localStorage.removeItem("steagno_user")
    setToken(null)
    setUser(null)
    window.location.href = "/"
    router.refresh()
  }

  return (
    <nav className="fixed top-0 left-0 right-0 z-40 px-6 py-4 pointer-events-none lg:pl-32 hidden sm:flex">
      <div className="max-w-7xl w-full mx-auto flex items-center justify-between pointer-events-auto bg-white/60 backdrop-blur-xl border border-white/40 shadow-[0_8px_32px_rgba(0,0,0,0.05)] rounded-[24px] px-8 h-20 transition-all duration-300">
        {/* Left: Project Context */}
        <div className="flex items-center gap-6">
          <div className="flex flex-col">
            <div className="flex items-center gap-2">
              <span className="text-[10px] md:text-[12px] font-bold text-slate-400 uppercase tracking-[0.2em]">
                AI-Powered
              </span>
              <div className="h-1 w-1 rounded-full bg-slate-300" />
            </div>
            <h2 className="text-[16px] md:text-[18px] font-black text-slate-900 tracking-tight leading-none">
              Multi-media Steganography System
            </h2>
          </div>
        </div>

        {/* Right: Actions & Status */}
        <div className="flex items-center gap-3 md:gap-4 animate-in fade-in slide-in-from-right-4 duration-700">
          {!token ? (
            <Link
              href="/login"
              className="flex items-center gap-2 px-5 py-2.5 bg-indigo-600 hover:bg-indigo-700 text-white rounded-xl shadow-lg shadow-indigo-200 transition-all active:scale-95"
            >
              <LogIn size={18} />
              <span className="text-[13px] font-bold">Sign In</span>
            </Link>
          ) : (
            <>
              {/* Status: Server Health */}
              <div className="hidden lg:flex items-center gap-2.5 px-3 py-1.5 bg-slate-50 border border-slate-200 rounded-lg group hover:border-emerald-200 transition-colors">
                <div className="relative flex h-2 w-2">
                  <span
                    className={`animate-ping absolute inline-flex h-full w-full rounded-full ${data?.status === "healthy" ? "bg-emerald-400" : "bg-rose-400"} opacity-75`}
                  ></span>
                  <span
                    className={`relative inline-flex rounded-full h-2 w-2 ${data?.status === "healthy" ? "bg-emerald-400" : "bg-rose-400"}`}
                  ></span>
                </div>
                <span
                  className={`text-[11px] font-bold uppercase tracking-tight text-slate-500`}
                >
                  {data?.status === "healthy"
                    ? "Server: Online"
                    : "Server: Offline"}
                </span>
              </div>

              {/* Status: Ollama Engine */}
              <div className="hidden md:flex items-center gap-2.5 px-3 py-1.5 bg-white border border-slate-200 rounded-lg shadow-sm">
                <div
                  className={`w-2 h-2 rounded-full animate-pulse ${data?.ollama_running ? "bg-emerald-500" : "bg-rose-500"}`}
                />
                <span className="text-[11px] font-bold text-slate-600">
                  Ollama
                </span>
              </div>

              {/* Profile Card with Dropdown */}
              <div className="relative">
                <button
                  onClick={() => setIsDropdownOpen(!isDropdownOpen)}
                  className="flex items-center gap-3 pl-3 pr-1 py-1 bg-white border border-slate-200 rounded-full hover:border-indigo-300 transition-all hover:shadow-md"
                >
                  <div className="flex flex-col items-end leading-none">
                    <span className="text-[12px] font-black text-slate-900">
                      {user?.full_name || "Agent"}
                    </span>
                    <span className="text-[10px] font-bold text-slate-400">
                      {user?.email || "Encrypted"}
                    </span>
                  </div>
                  <div className="w-9 h-9 rounded-full bg-indigo-50 border border-indigo-100 flex items-center justify-center text-indigo-600">
                    <UserIcon size={18} />
                  </div>
                </button>

                {/* Dropdown Menu */}
                {isDropdownOpen && (
                  <>
                    <div
                      className="fixed inset-0 z-0"
                      onClick={() => setIsDropdownOpen(false)}
                    />
                    <div className="absolute right-0 mt-3 w-48 bg-white rounded-2xl border border-slate-200 shadow-xl py-2 z-10 animate-in fade-in zoom-in-95 duration-200">
                      <div className="px-4 py-2 border-b border-slate-50 mb-1">
                        <p className="text-[10px] font-black text-slate-400  tracking-widest">
                          {user?.email || "No email available"}
                        </p>
                      </div>
                      <button
                        onClick={handleLogout}
                        className="w-full flex items-center gap-3 px-4 py-2.5 text-rose-600 hover:bg-rose-50 transition-colors font-bold text-sm"
                      >
                        <LogOut size={16} />
                        Logout Session
                      </button>
                    </div>
                  </>
                )}
              </div>
            </>
          )}
        </div>
      </div>
    </nav>
  )
}

export default Navbar
