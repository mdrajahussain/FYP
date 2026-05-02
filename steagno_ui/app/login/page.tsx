"use client"

import React, { useState } from "react"
import { Mail, Lock, ArrowRight, Eye, EyeOff } from "lucide-react"
import Link from "next/link"
import { useLogin } from "@/hooks/useAuth"
import { toast } from "sonner"
import { useRouter, useSearchParams } from "next/navigation"

const LoginPage = () => {
  const [showPassword, setShowPassword] = useState(false)
  const [formData, setFormData] = useState({
    email: "",
    password: "",
  })

  const searchParams = useSearchParams()

  const { mutate, isPending } = useLogin()

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()

    const payload = {
      email: formData.email,
      password: formData.password,
    }

    mutate(payload, {
      onSuccess: (response: {
        message?: string
        access_token: string
        data: unknown
      }) => {
        toast.success(response.message || "Login successful! Redirecting...")
        localStorage.setItem("steagno_access_token", response.access_token)
        localStorage.setItem("steagno_user", JSON.stringify(response.data))

        setTimeout(() => {
          window.location.href = searchParams.get("redirect") || "/"
        }, 1000)
      },
      onError: (error) => {
        console.error("Login error:", error)
        toast.error(
          error instanceof Error
            ? error.message
            : "Login failed. Please check your credentials and try again.",
        )
      },
    })
  }

  return (
    <div className="min-h-screen bg-[#fafafa] flex items-center justify-center p-6 relative overflow-hidden selection:bg-indigo-100">
      {/* --- AMBIENT BACKGROUND BLOBS --- */}
      <div className="absolute top-[-10%] left-[-10%] w-[40%] h-[40%] bg-indigo-200/30 rounded-full blur-[120px] animate-pulse" />
      <div className="absolute bottom-[-10%] right-[-10%] w-[40%] h-[40%] bg-emerald-100/40 rounded-full blur-[120px] animate-pulse delay-700" />

      {/* --- LOGIN CARD --- */}
      <div className="w-full max-w-[460px] bg-white/70 backdrop-blur-2xl rounded-[40px] border border-white shadow-[0_32px_64px_rgba(0,0,0,0.06)] p-8 md:p-12 relative z-10">
        {/* Header */}
        <div className="flex flex-col items-center text-center mb-10">
          <h2 className="text-3xl font-black text-slate-900 tracking-tight">
            Welcome Back
          </h2>
          <p className="text-slate-500 font-medium mt-2">
            Sign in to get access to use our features.
          </p>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} className="space-y-5">
          {/* Email Field */}
          <div className="space-y-2">
            <label className="text-[11px] font-black text-slate-400 uppercase tracking-widest ml-1">
              Email Address
            </label>
            <div className="relative group">
              <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none text-slate-400 group-focus-within:text-indigo-600 transition-colors">
                <Mail size={18} />
              </div>
              <input
                type="email"
                placeholder="user@gmail.com"
                value={formData.email}
                onChange={(e) =>
                  setFormData({ ...formData, email: e.target.value })
                }
                className="w-full pl-11 pr-4 py-4 bg-slate-50 border border-slate-100 rounded-2xl focus:ring-4 focus:ring-indigo-50 focus:border-indigo-500 outline-none transition-all font-medium text-slate-900 placeholder:text-slate-300"
                required
              />
            </div>
          </div>

          {/* Password Field */}
          <div className="space-y-2">
            <div className="flex justify-between items-center px-1">
              <label className="text-[11px] font-black text-slate-400 uppercase tracking-widest">
                Password
              </label>
              {/* <Link
                href="/forgot-password"
                className="text-[11px] font-bold text-indigo-600 hover:text-indigo-700 transition-colors"
              >
                Forgot Password?
              </Link> */}
            </div>
            <div className="relative group">
              <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none text-slate-400 group-focus-within:text-indigo-600 transition-colors">
                <Lock size={18} />
              </div>
              <input
                type={showPassword ? "text" : "password"}
                placeholder="••••••••"
                value={formData.password}
                onChange={(e) =>
                  setFormData({ ...formData, password: e.target.value })
                }
                className="w-full pl-11 pr-12 py-4 bg-slate-50 border border-slate-100 rounded-2xl focus:ring-4 focus:ring-indigo-50 focus:border-indigo-500 outline-none transition-all font-medium text-slate-900 placeholder:text-slate-300"
                required
              />
              <button
                type="button"
                onClick={() => setShowPassword(!showPassword)}
                className="absolute inset-y-0 right-0 pr-4 flex items-center text-slate-400 hover:text-indigo-600 transition-colors"
                tabIndex={-1}
              >
                {showPassword ? <EyeOff size={18} /> : <Eye size={18} />}
              </button>
            </div>
          </div>

          <button
            type="submit"
            disabled={isPending}
            className="w-full py-4 bg-indigo-600 hover:bg-indigo-700 text-white rounded-2xl font-bold shadow-xl shadow-indigo-100 flex items-center justify-center gap-2 transition-all active:scale-[0.98] disabled:opacity-70 mt-4"
          >
            {isPending ? (
              <div className="flex items-center gap-2">
                <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                Authenticating...
              </div>
            ) : (
              <>
                Sign In
                <ArrowRight size={18} />
              </>
            )}
          </button>
        </form>

        {/* Footer Link */}
        <p className="mt-10 text-center text-slate-500 font-medium text-sm">
          Don&apos;t have an account?{" "}
          <Link
            href="/register"
            className="text-indigo-600 font-black hover:underline underline-offset-4"
          >
            Register Now
          </Link>
        </p>
      </div>

      {/* System Status Decoration */}
      <div className="absolute bottom-8 flex items-center gap-2 opacity-40 select-none">
        <span className="text-[10px] font-black text-slate-400 uppercase tracking-[0.3em]">
          AI-Powered Multi-Media Steganography System
        </span>
      </div>
    </div>
  )
}

export default LoginPage
