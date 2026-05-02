"use client"

import React from "react"
import {
  Zap,
  ChevronRight,
  SearchCode,
  MessageSquareText,
  BarChart3,
  ArrowRight,
} from "lucide-react"
import { useRouter } from "next/navigation"
import { toast } from "sonner"

const LandingPage = () => {
  const authToken = localStorage.getItem("steagno_access_token")
  const authUser = localStorage.getItem("steagno_user")

  const router = useRouter()

  const handleLaunch = () => {
    if (!authToken || !authUser) {
      toast.warning("Please log in to access the workspace.")
    } else {
      router.push("/embed")
    }
  }

  return (
    <div className="min-h-screen bg-[#F8FAFC] overflow-x-hidden pt-24 lg:pl-32 pb-20 relative">
      {/* ── BACKGROUND AMBIENCE (Static Tailwind Blur) ── */}
      <div className="absolute inset-0 z-0 pointer-events-none">
        <div className="absolute top-[-10%] left-[-10%] w-[50%] h-[50%] bg-indigo-500/5 rounded-full blur-[120px]" />
        <div className="absolute bottom-[-10%] right-[-10%] w-[50%] h-[50%] bg-emerald-500/5 rounded-full blur-[120px]" />
      </div>

      {/* ── HERO SECTION ── */}
      <section className="relative z-10 max-w-7xl mx-auto px-6 py-12 md:py-24 text-center animate-in fade-in slide-in-from-bottom-4 duration-700">
        <h1 className="text-[44px] md:text-[80px] font-black text-slate-900 tracking-tighter leading-[1.05] mb-6">
          Secure Data. <br />
          <span className="text-transparent bg-clip-text bg-gradient-to-r from-indigo-600 to-emerald-600">
            Perfectly Hidden.
          </span>
        </h1>

        <p className="max-w-2xl mx-auto text-[18px] md:text-[21px] text-slate-500 leading-relaxed mb-10">
          An advanced forensic suite for hiding sensitive information within
          standard media using high-frequency domain transformations and
          AI-driven entropy analysis.
        </p>

        <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
          <button
            onClick={handleLaunch}
            className="w-full sm:w-auto px-10 py-5 bg-slate-900 text-white rounded-2xl font-bold text-[18px] shadow-2xl hover:bg-indigo-600 hover:scale-105 active:scale-95 transition-all flex items-center justify-center gap-3 cursor-pointer border-none"
          >
            Launch Workspace <ChevronRight size={20} />
          </button>
        </div>
      </section>

      {/* ── SYSTEM MODULES HUB ── */}
      <section className="relative z-10 max-w-7xl mx-auto px-6 py-10">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 animate-in fade-in slide-in-from-bottom-8 duration-1000 delay-300 fill-mode-both">
          <ModuleCard
            icon={Zap}
            title="Embedding"
            desc="Securely hide payloads using frequency domain modulation."
            color="indigo"
            redirectUrl="/embed"
            authToken={authToken}
            authUser={authUser}
          />
          <ModuleCard
            icon={SearchCode}
            title="Extraction"
            desc="Recover hidden data from carriers with bit-perfect accuracy."
            color="blue"
            redirectUrl="/extract"
            authToken={authToken}
            authUser={authUser}
          />
          <ModuleCard
            icon={BarChart3}
            title="Quality"
            desc="Benchmark integrity using PSNR, SSIM, and MSE metrics."
            color="emerald"
            redirectUrl="/quality"
            authToken={authToken}
            authUser={authUser}
          />
          <ModuleCard
            icon={MessageSquareText}
            title="Assistant"
            desc="AI-powered consultation on security and encoding methods."
            color="purple"
            redirectUrl="/chat"
            authToken={authToken}
            authUser={authUser}
          />
        </div>
      </section>
    </div>
  )
}

type ModuleColor = "indigo" | "blue" | "emerald" | "purple"

interface ModuleCardProps {
  icon: React.ComponentType<{ size?: number; className?: string }>
  title: string
  desc: string
  color: ModuleColor
  redirectUrl: string
  authToken?: string | null
  authUser?: string | null
}

function ModuleCard({
  icon: Icon,
  title,
  desc,
  color,
  redirectUrl,
  authToken,
  authUser,
}: ModuleCardProps) {
  const router = useRouter()

  const colorStyles: Record<ModuleColor, string> = {
    indigo: "hover:bg-indigo-600 hover:border-indigo-600",
    blue: "hover:bg-blue-600 hover:border-blue-600",
    emerald: "hover:bg-emerald-600 hover:border-emerald-600",
    purple: "hover:bg-purple-600 hover:border-purple-600",
  }

  const iconColors: Record<ModuleColor, string> = {
    indigo: "text-indigo-600 bg-indigo-50",
    blue: "text-blue-600 bg-blue-50",
    emerald: "text-emerald-600 bg-emerald-50",
    purple: "text-purple-600 bg-purple-50",
  }

  const iconHoverText: Record<ModuleColor, string> = {
    indigo: "group-hover:text-indigo-600",
    blue: "group-hover:text-blue-600",
    emerald: "group-hover:text-emerald-600",
    purple: "group-hover:text-purple-600",
  }

  const handleRedirect = () => {
    if (!authToken || !authUser) {
      toast.warning("Please log in to use this feature.")
    } else {
      router.push(redirectUrl)
    }
  }

  return (
    <div
      onClick={handleRedirect}
      className={`group bg-white p-8 rounded-[35px] border border-slate-100 shadow-xl shadow-slate-200/50 transition-all duration-300 flex flex-col h-full hover:-translate-y-2 cursor-pointer ${colorStyles[color]}`}
    >
      <div
        className={`w-12 h-12 rounded-xl flex items-center justify-center mb-6 transition-all duration-300 ${iconColors[color]} group-hover:bg-white ${iconHoverText[color]}`}
      >
        <Icon size={24} />
      </div>
      <div className="flex-1">
        <h4 className="text-[20px] font-black text-slate-900 mb-2 transition-colors duration-300 group-hover:text-white">
          {title}
        </h4>
        <p className="text-[14px] text-slate-500 leading-relaxed transition-colors duration-300 group-hover:text-white/80 mb-6">
          {desc}
        </p>
      </div>
    </div>
  )
}

export default LandingPage
