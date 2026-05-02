"use client"

import React, { useState } from "react"
import {
  BarChart3,
  Image as ImageIcon,
  ArrowRightLeft,
  Zap,
  CheckCircle2,
  ShieldAlert,
  Download,
  AlertCircle,
} from "lucide-react"
import { useAnalyze } from "@/hooks/useAnlyze"

const Quality = () => {
  const [originalFile, setOriginalFile] = useState<File | null>(null)
  const [modifiedFile, setModifiedFile] = useState<File | null>(null)
  const [previews, setPreviews] = useState<{
    original: string
    modified: string
  }>({
    original: "",
    modified: "",
  })
  const [error, setError] = useState<string | null>(null)

  const {
    mutate: runAnalysis,
    data: result,
    isPending: isAnalyzing,
  } = useAnalyze()

  const handleFileChange = (
    e: React.ChangeEvent<HTMLInputElement>,
    type: "original" | "modified",
  ) => {
    const file = e.target.files?.[0]
    if (!file) return

    const url = URL.createObjectURL(file)
    if (type === "original") {
      setOriginalFile(file)
      setPreviews((prev) => ({ ...prev, original: url }))
    } else {
      setModifiedFile(file)
      setPreviews((prev) => ({ ...prev, modified: url }))
    }
    setError(null)
  }

  const handleAnalyze = () => {
    if (!originalFile || !modifiedFile) {
      setError(
        "Both original and modified files are required for benchmarking.",
      )
      return
    }

    const formData = new FormData()
    formData.append("original_file", originalFile)
    formData.append("modified_file", modifiedFile)

    runAnalysis(
      { formData },
      {
        onError: (err) => {
          console.error("Analysis failed:", err)
          setError("Forensic analysis failed. Ensure file formats match.")
        },
      },
    )
  }

  const reportGenerated = result?.success

  return (
    <div className="max-w-7xl mx-auto p-6 lg:p-10 animate-in fade-in slide-in-from-bottom-4 duration-700 lg:pt-36">
      {/* Header */}
      <div className="mb-10 flex flex-col md:flex-row md:items-end justify-between gap-6">
        <div>
          <h1 className="text-[32px] font-black text-slate-900 flex items-center gap-4">
            <div className="p-2 bg-emerald-600 rounded-xl text-white shadow-lg shadow-emerald-100">
              <BarChart3 size={28} />
            </div>
            Visual Quality Benchmarking
          </h1>
          <p className="text-slate-500 text-[17px] mt-2 max-w-2xl">
            Compare the Original and Stego-Object to calculate structural
            similarity (SSIM) and peak signal-to-noise ratios (PSNR).
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 xl:grid-cols-12 gap-8">
        {/* Left: Forensic Inputs */}
        <div className="xl:col-span-4 space-y-6">
          <div className="bg-white rounded-[32px] p-8 shadow-xl shadow-slate-200/50 border border-slate-100 h-full">
            <h3 className="text-[18px] font-bold text-slate-800 mb-8 flex items-center gap-2">
              <Zap size={18} className="text-emerald-600" /> Comparison Engine
            </h3>

            <div className="space-y-6">
              {/* Original File */}
              <div className="group space-y-3">
                <label className="text-[13px] font-black text-slate-400 uppercase tracking-widest ml-1">
                  Original Reference
                </label>
                <div
                  className={`relative border-2 border-dashed rounded-2xl p-6 text-center transition-all cursor-pointer ${originalFile ? "border-emerald-500 bg-emerald-50/30" : "border-slate-200 bg-slate-50/50 hover:border-indigo-500"}`}
                >
                  <ImageIcon
                    size={24}
                    className={`mx-auto mb-2 ${originalFile ? "text-emerald-600" : "text-slate-300"}`}
                  />
                  <p className="text-[14px] font-bold text-slate-600 truncate px-2">
                    {originalFile ? originalFile.name : "Select Original"}
                  </p>
                  <input
                    type="file"
                    className="absolute inset-0 opacity-0 cursor-pointer"
                    onChange={(e) => handleFileChange(e, "original")}
                  />
                </div>
              </div>

              <div className="flex justify-center -my-3 relative z-10">
                <div className="bg-white p-2 rounded-full border border-slate-100 shadow-md">
                  <ArrowRightLeft
                    size={16}
                    className="text-slate-400 rotate-90"
                  />
                </div>
              </div>

              {/* Modified File */}
              <div className="group space-y-3">
                <label className="text-[13px] font-black text-slate-400 uppercase tracking-widest ml-1">
                  Stego-Object (Modified)
                </label>
                <div
                  className={`relative border-2 border-dashed rounded-2xl p-6 text-center transition-all cursor-pointer ${modifiedFile ? "border-emerald-500 bg-emerald-50/30" : "border-slate-200 bg-slate-50/50 hover:border-indigo-500"}`}
                >
                  <ImageIcon
                    size={24}
                    className={`mx-auto mb-2 ${modifiedFile ? "text-emerald-600" : "text-slate-300"}`}
                  />
                  <p className="text-[14px] font-bold text-slate-600 truncate px-2">
                    {modifiedFile ? modifiedFile.name : "Select Modified"}
                  </p>
                  <input
                    type="file"
                    className="absolute inset-0 opacity-0 cursor-pointer"
                    onChange={(e) => handleFileChange(e, "modified")}
                  />
                </div>
              </div>

              <button
                onClick={handleAnalyze}
                disabled={isAnalyzing || !originalFile || !modifiedFile}
                className="w-full mt-4 py-5 rounded-2xl bg-emerald-600 text-white text-[17px] font-bold shadow-xl shadow-emerald-100 hover:bg-emerald-700 transition-all active:scale-[0.98] disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {isAnalyzing
                  ? "Calculating Differentials..."
                  : "Run Quality Metrics"}
              </button>

              {error && (
                <div className="flex items-center gap-2 text-red-500 text-[12px] font-bold justify-center">
                  <AlertCircle size={14} /> {error}
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Right: Comparative Analysis */}
        <div className="xl:col-span-8">
          {reportGenerated ? (
            <div className="space-y-6 animate-in fade-in slide-in-from-right-4 duration-500">
              {/* Visual Compare Card */}
              <div className="bg-white rounded-[32px] p-2 shadow-xl border border-slate-100 overflow-hidden">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-2 md:h-[350px]">
                  <div className="bg-slate-100 rounded-[24px] flex items-center justify-center relative min-h-[200px] overflow-hidden">
                    <span className="absolute top-4 left-4 z-10 bg-black/60 backdrop-blur px-3 py-1 rounded-full text-white text-[11px] font-bold">
                      ORIGINAL
                    </span>
                    {previews.original ? (
                      <img
                        src={previews.original}
                        className="w-full h-full object-cover"
                        alt="Original"
                      />
                    ) : (
                      <ImageIcon size={48} className="text-slate-300" />
                    )}
                  </div>
                  <div className="bg-slate-100 rounded-[24px] flex items-center justify-center relative min-h-[200px] overflow-hidden">
                    <span className="absolute top-4 left-4 z-10 bg-emerald-600 px-3 py-1 rounded-full text-white text-[11px] font-bold uppercase">
                      STEGO OBJECT
                    </span>
                    {previews.modified ? (
                      <img
                        src={previews.modified}
                        className="w-full h-full object-cover"
                        alt="Modified"
                      />
                    ) : (
                      <ImageIcon size={48} className="text-slate-300" />
                    )}
                  </div>
                </div>
              </div>

              {/* Metrics Grid */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <MetricCard
                  label="PSNR"
                  value={result.metrics.psnr.toFixed(2)}
                  unit="dB"
                  status={result.metrics.psnr > 40 ? "Excellent" : "Good"}
                  desc="Peak Signal-to-Noise Ratio."
                  color="emerald"
                />
                <MetricCard
                  label="SSIM"
                  value={result.metrics.ssim.toFixed(4)}
                  unit=""
                  status={result.metrics.ssim > 0.99 ? "Optimal" : "Stable"}
                  desc="Structural Similarity Index."
                  color="indigo"
                />
                <MetricCard
                  label="MSE"
                  value={result.metrics.mse.toExponential(2)}
                  unit=""
                  status="Verified"
                  desc="Mean Squared Error rate."
                  color="blue"
                />
              </div>

              {/* Integrity Badge */}
              <div className="flex items-center gap-4 bg-emerald-50 border border-emerald-100 p-6 rounded-[24px]">
                <div className="w-12 h-12 bg-emerald-100 rounded-full flex items-center justify-center text-emerald-600 shrink-0">
                  <CheckCircle2 size={24} />
                </div>
                <div>
                  <h4 className="font-bold text-emerald-900">
                    {result.assessment}
                  </h4>
                  <p className="text-emerald-700/70 text-[14px]">
                    The payload has a Signal-to-Noise ratio of{" "}
                    {result.metrics.snr.toFixed(2)} dB, confirming high
                    perceptual transparency.
                  </p>
                </div>
              </div>
            </div>
          ) : (
            <div className="h-full min-h-[500px] border-2 border-dashed border-slate-200 rounded-[40px] flex flex-col items-center justify-center text-center p-12 bg-white/50">
              <div
                className={`w-20 h-20 rounded-3xl flex items-center justify-center mb-6 transition-all ${isAnalyzing ? "bg-emerald-100 text-emerald-600 animate-pulse" : "bg-slate-100 text-slate-300"}`}
              >
                <ShieldAlert size={40} />
              </div>
              <h3 className="text-[20px] font-bold text-slate-400">
                {isAnalyzing
                  ? "Forensic Calculation in Progress"
                  : "Awaiting Data Comparison"}
              </h3>
              <p className="text-slate-400 max-w-xs mt-2">
                {isAnalyzing
                  ? "Running pixel-by-pixel differential analysis across color channels..."
                  : "Upload the original and stego-modified files to begin forensic quality analysis."}
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

type MetricCardProps = {
  label: string
  value: string | number
  unit: string
  status: string
  desc: string
  color: "emerald" | "indigo" | "blue"
}

function MetricCard({
  label,
  value,
  unit,
  status,
  desc,
  color,
}: MetricCardProps) {
  const colorMap = {
    emerald: "text-emerald-600 bg-emerald-50 border-emerald-100",
    indigo: "text-indigo-600 bg-indigo-50 border-indigo-100",
    blue: "text-blue-600 bg-blue-50 border-blue-100",
  }

  return (
    <div className="bg-white p-6 rounded-[28px] border border-slate-100 shadow-sm hover:shadow-md transition-shadow">
      <div className="flex justify-between items-start mb-4">
        <p className="text-[13px] font-black text-slate-400 uppercase tracking-widest">
          {label}
        </p>
        <span
          className={`text-[10px] font-bold px-2 py-1 rounded-lg uppercase ${colorMap[color]}`}
        >
          {status}
        </span>
      </div>
      <div className="flex items-baseline gap-1 mb-2">
        <p className="text-[28px] font-black text-slate-900 tracking-tight">
          {value}
        </p>
        <span className="text-slate-400 font-bold text-[14px]">{unit}</span>
      </div>
      <p className="text-[13px] text-slate-500 leading-relaxed font-medium">
        {desc}
      </p>
    </div>
  )
}

export default Quality
