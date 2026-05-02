"use client"

import React, { useState, useEffect } from "react"
import {
  Grid,
  Activity,
  MessageSquare,
  Shield,
  Zap,
  HomeIcon,
  LogIn,
  Lock,
} from "lucide-react"
import Link from "next/link"
import { usePathname, useRouter } from "next/navigation"

type NavItem = {
  id: string
  label: string
  icon: React.ReactNode
  requiresAuth: boolean
}

const NAV_ITEMS: NavItem[] = [
  { id: "", label: "Home", icon: <HomeIcon size={20} />, requiresAuth: false },
  {
    id: "embed",
    label: "Embed Data",
    icon: <Zap size={20} />,
    requiresAuth: true,
  },
  {
    id: "extract",
    label: "Extract Data",
    icon: <Grid size={20} />,
    requiresAuth: true,
  },
  {
    id: "quality",
    label: "Forensics",
    icon: <Activity size={20} />,
    requiresAuth: true,
  },
  {
    id: "chat",
    label: "AI Assistant",
    icon: <MessageSquare size={20} />,
    requiresAuth: true,
  },
]

const Sidebar = () => {
  const [expanded, setExpanded] = useState(false)
  const [active, setActive] = useState("")
  const [token, setToken] = useState<string | null>(null)
  const [mounted, setMounted] = useState(false)

  const pathname = usePathname()
  const router = useRouter()

  // Safe localStorage access and auth state initialization
  useEffect(() => {
    setMounted(true)
    const storedToken = localStorage.getItem("steagno_access_token")
    setToken(storedToken)

    // Set active based on current path
    const currentPath = pathname.split("/")[1] || ""
    setActive(currentPath)
  }, [pathname])

  // Protected route guard
  useEffect(() => {
    if (!mounted) return

    const currentPath = pathname
    const isProtectedRoute = NAV_ITEMS.some(
      (item) => item.requiresAuth && `/${item.id}` === currentPath,
    )

    if (isProtectedRoute && !token) {
      // Redirect to login with return URL
      router.push(`/login?redirect=${encodeURIComponent(currentPath)}`)
    }
  }, [token, pathname, mounted, router])

  const handleNavigation = (
    itemId: string,
    requiresAuth: boolean,
    e: React.MouseEvent,
  ) => {
    if (requiresAuth && !token) {
      e.preventDefault()
      router.push(`/login?redirect=/${itemId}`)
      return
    }
    setActive(itemId)
  }

  // Don't render until mounted to prevent hydration mismatch
  if (!mounted) return null

  return (
    <>
      {/* ── DESKTOP FLOATING SIDEBAR ── */}
      <nav
        onMouseEnter={() => setExpanded(true)}
        onMouseLeave={() => setExpanded(false)}
        className={`
          fixed left-6 top-1/2 -translate-y-1/2 z-50
          hidden lg:flex flex-col items-center
          max-h-[650px] h-[75vh]
          bg-white/70 backdrop-blur-xl border border-white/40
          rounded-[32px] shadow-[0_20px_50px_rgba(0,0,0,0.1)]
          py-6 transition-all duration-500 ease-[cubic-bezier(0.34,1.56,0.64,1)]
          ${expanded ? "w-64 items-start px-4" : "w-20 items-center px-0"}
        `}
      >
        {/* Brand Identity */}
        <div
          className={`flex items-center mb-10 transition-all duration-500 ${expanded ? "pl-2 w-full" : "justify-center"}`}
        >
          <div className="shrink-0 w-11 h-11 rounded-2xl bg-indigo-600 flex items-center justify-center text-white shadow-lg shadow-indigo-200">
            <Shield size={24} strokeWidth={2.5} />
          </div>
          <div
            className={`ml-4 overflow-hidden transition-all duration-500 ${expanded ? "opacity-100 w-auto" : "opacity-0 w-0"}`}
          >
            <p className="text-[13px] font-black text-slate-900 leading-tight uppercase tracking-tighter">
              AI-Powered
            </p>
            <p className="text-[11px] font-bold text-indigo-600 leading-tight uppercase tracking-widest">
              Stegano System
            </p>
          </div>
        </div>

        {/* Navigation Group */}
        <div className="flex-1 w-full space-y-2">
          {NAV_ITEMS.map((item) => {
            const isActive = active === item.id
            const isLocked = item.requiresAuth && !token

            return (
              <Link
                key={item.id}
                href={isLocked ? "#" : `/${item.id}`}
                onClick={(e) => handleNavigation(item.id, item.requiresAuth, e)}
                className={`
                  group relative flex items-center w-full rounded-2xl transition-all duration-300 border-none cursor-pointer
                  h-14 ${expanded ? "px-4 gap-4" : "justify-center px-0"}
                  ${isActive && !isLocked ? "text-indigo-600" : ""}
                  ${isLocked ? "opacity-50 cursor-not-allowed" : "hover:bg-slate-50/50"}
                  ${!isLocked && !isActive ? "text-slate-400 hover:text-slate-600" : ""}
                `}
              >
                {isActive && !isLocked && (
                  <>
                    <div className="absolute inset-0 bg-indigo-50 rounded-2xl ring-1 ring-indigo-100 shadow-sm" />
                    <div className="absolute left-0 w-1 h-6 bg-indigo-600 rounded-r-full shadow-[2px_0_8px_rgba(79,70,229,0.4)]" />
                  </>
                )}

                {/* Lock icon for protected items */}
                {isLocked && (
                  <div className="absolute -top-1 -right-1 z-20">
                    <div className="w-5 h-5 bg-amber-500 rounded-full flex items-center justify-center shadow-md">
                      <Lock size={10} className="text-white" />
                    </div>
                  </div>
                )}

                <span
                  className={`relative z-10 transition-transform duration-300 ${isActive && !isLocked ? "scale-110" : "group-hover:scale-110"}`}
                >
                  {item.icon}
                </span>

                <span
                  className={`relative z-10 text-[15px] font-bold whitespace-nowrap transition-all duration-500
                    ${expanded ? "opacity-100 translate-x-0" : "opacity-0 -translate-x-4 w-0"}
                    ${isActive && !isLocked ? "text-slate-900" : "text-inherit"}
                  `}
                >
                  {item.label}
                </span>

                {/* Tooltip for collapsed state */}
                {!expanded && (
                  <div className="absolute left-20 px-3 py-2 bg-slate-900 text-white text-[12px] font-bold rounded-xl opacity-0 group-hover:opacity-100 pointer-events-none translate-x-4 group-hover:translate-x-0 transition-all shadow-xl whitespace-nowrap z-50">
                    {isLocked ? `Sign in to use ${item.label}` : item.label}
                  </div>
                )}
              </Link>
            )
          })}
        </div>

        {/* Footer: Auth Conditional UI */}
        <div
          className={`mt-auto w-full pt-6 border-t border-slate-100 transition-all ${expanded ? "px-2" : "flex flex-col items-center"}`}
        >
          {token ? (
            /* AUTHENTICATED: Show User Menu */
            <div className="w-full space-y-3">
              <div
                className={`flex items-center gap-3 transition-all ${expanded ? "" : "justify-center"}`}
              >
                <div className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse shadow-[0_0_8px_rgba(16,185,129,0.6)]" />
                <span
                  className={`text-[11px] font-bold text-slate-400 uppercase tracking-widest transition-all ${expanded ? "opacity-100" : "opacity-0 w-0"}`}
                >
                  Engine Online
                </span>
              </div>

              {expanded && (
                <button
                  onClick={() => {
                    localStorage.removeItem("steagno_access_token")
                    localStorage.removeItem("steagno_user")
                    setToken(null)
                    router.push("/")
                  }}
                  className="w-full px-3 py-2 text-xs font-bold text-red-600 hover:bg-red-50 rounded-xl transition-colors"
                >
                  Sign Out
                </button>
              )}
            </div>
          ) : (
            /* UNAUTHENTICATED: Call to Action */
            <Link
              href="/login"
              className={`flex items-center transition-all duration-300 group
                ${
                  expanded
                    ? "w-full gap-3 px-4 py-3 bg-gradient-to-r from-indigo-600 to-indigo-700 rounded-2xl text-white shadow-lg shadow-indigo-200 hover:from-indigo-700 hover:to-indigo-800 active:scale-95"
                    : "justify-center text-indigo-600 hover:scale-110"
                }`}
            >
              <LogIn size={20} />
              <span
                className={`text-[13px] font-bold transition-all ${expanded ? "opacity-100 ml-1" : "opacity-0 w-0"}`}
              >
                Sign In
              </span>
            </Link>
          )}
        </div>
      </nav>

      {/* ── MOBILE TAB BAR ── */}
      <nav className="lg:hidden fixed bottom-6 left-6 right-6 bg-white/80 backdrop-blur-2xl border border-white/40 rounded-[24px] shadow-[0_20px_50px_rgba(0,0,0,0.15)] z-50">
        <div className="flex items-center justify-around px-2 h-16">
          {NAV_ITEMS.map((item) => {
            const isLocked = item.requiresAuth && !token
            const isActive = active === item.id

            return (
              <Link
                key={item.id}
                href={isLocked ? "/login" : `/${item.id}`}
                onClick={(e) => {
                  if (isLocked) {
                    e.preventDefault()
                    router.push(`/login?redirect=/${item.id}`)
                  } else {
                    setActive(item.id)
                  }
                }}
                className={`
                  relative flex flex-col items-center justify-center gap-1 flex-1 h-12 rounded-xl transition-all duration-300
                  ${isLocked ? "opacity-40" : ""}
                  ${isActive && !isLocked ? "text-indigo-600 -translate-y-1" : "text-slate-400"}
                `}
              >
                {isActive && !isLocked && (
                  <div className="absolute inset-0 bg-indigo-50/50 rounded-xl scale-90 -z-10" />
                )}
                <div className="relative">
                  {item.icon}
                  {isLocked && (
                    <Lock
                      size={10}
                      className="absolute -top-1 -right-2 text-amber-500"
                    />
                  )}
                </div>
                <span
                  className={`text-[9px] font-bold uppercase tracking-tighter ${isActive && !isLocked ? "text-slate-900" : "text-slate-400"}`}
                >
                  {item.label.split(" ")[0]}
                </span>
              </Link>
            )
          })}
        </div>

        {/* Mobile Auth Indicator */}
        {!token && (
          <div className="absolute -top-8 left-1/2 -translate-x-1/2 px-3 py-1.5 bg-indigo-500 rounded-full shadow-lg whitespace-nowrap">
            <p className="text-[9px] font-bold text-white">
              🔒 Sign in to unlock all features
            </p>
          </div>
        )}
      </nav>
    </>
  )
}

export default Sidebar
