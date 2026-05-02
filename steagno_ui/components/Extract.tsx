// //update 3
// "use client"

// import React, { useState } from "react"
// import {
//   SearchCode,
//   FileSearch,
//   ShieldCheck,
//   Copy,
//   RefreshCcw,
//   Terminal,
//   AlertCircle,
//   Clock,
//   Waves,
// } from "lucide-react"
// import {
//   useEchoExtracting,
//   useExtracting,
//   useVideoExtraction,
// } from "@/hooks/useExtract"

// const ALGORITHMS = [
//   // { id: "auto", label: "Auto-detect", desc: "Scan all domains" },
//   { id: "LSB", label: "LSB", desc: "Images/png" },
//   { id: "DCT", label: "DCT", desc: "Images/png" },
//   { id: "EchoHiding", label: "Echo Hiding", desc: "Audio Domain (wav)" },
//   { id: "DWT", label: "DWT", desc: "Videos" },
// ]

// const Extract = () => {
//   const [selectedAlgo, setSelectedAlgo] = useState("auto")
//   const [selectedFile, setSelectedFile] = useState<File | null>(null)
//   const [error, setError] = useState<string | null>(null)
//   const [activeResult, setActiveResult] = useState<any>(null)

//   const { mutate: runExtracting, isPending: isImageScanning } = useExtracting()
//   const { mutate: runEchoExtracting, isPending: isEchoScanning } =
//     useEchoExtracting()

//   const { mutate: runVideoExtraction, isPending: isVideoScanning } =
//     useVideoExtraction()

//   const isScanning = isImageScanning || isEchoScanning || isVideoScanning

//   const handleExtract = () => {
//     if (!selectedFile) {
//       setError("Please upload a stego-object first.")
//       return
//     }
//     setError(null)
//     setActiveResult(null)

//     const formData = new FormData()
//     // The backend for Echo Hiding expects 'audio', others expect 'file'
//     if (selectedAlgo === "EchoHiding") {
//       formData.append("audio", selectedFile)
//       runEchoExtracting(
//         { formData },
//         {
//           onSuccess: (data) => {
//             if (data.success) {
//               setActiveResult(data)
//             } else {
//               setError(data.message || "Extraction failed.")
//             }
//           },
//           onError: () =>
//             setError("System failed to isolate payload from audio carrier."),
//         },
//       )
//     } else if (selectedAlgo === "DWT") {
//       formData.append("file", selectedFile)
//       runEchoExtracting(
//         { formData },
//         {
//           onSuccess: (data) => {
//             if (data.success) {
//               setActiveResult(data)
//             } else {
//               setError(data.message || "Extraction failed.")
//             }
//           },
//           onError: () =>
//             setError("System failed to isolate payload from audio carrier."),
//         },
//       )
//     } else {
//       formData.append("file", selectedFile)
//       formData.append("algorithm", selectedAlgo)
//       runExtracting(
//         { formData },
//         {
//           onSuccess: (data) => {
//             if (data.success) {
//               setActiveResult(data)
//             } else {
//               setError(data.message || "Extraction failed.")
//             }
//           },
//           onError: () =>
//             setError("System failed to isolate payload from image carrier."),
//         },
//       )
//     }
//   }

//   const copyToClipboard = () => {
//     if (activeResult?.secret) {
//       navigator.clipboard.writeText(activeResult.secret)
//     }
//   }

//   return (
//     <div className="max-w-6xl mx-auto p-4 lg:p-8 space-y-8 animate-in fade-in duration-700 lg:pt-36 lg:pl-40">
//       {/* Header */}
//       <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
//         <div>
//           <h1 className="text-[28px] font-black text-slate-900 flex items-center gap-3">
//             <SearchCode className="text-indigo-600" size={32} />
//             Forensic Extraction
//           </h1>
//           <p className="text-slate-500 text-[16px] mt-1">
//             Reverse-engineer media files to recover hidden payloads.
//           </p>
//         </div>
//         <div className="flex items-center gap-2 px-4 py-2 bg-indigo-50 rounded-2xl border border-indigo-100">
//           <ShieldCheck size={18} className="text-indigo-600" />
//           <span className="text-[13px] font-bold text-indigo-700 uppercase tracking-wider">
//             Integrity Check Active
//           </span>
//         </div>
//       </div>

//       <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
//         {/* Left: Input Panel */}
//         <div className="lg:col-span-5 space-y-6">
//           <div className="bg-white rounded-[32px] p-8 shadow-xl shadow-slate-200/60 border border-slate-100">
//             <h3 className="text-[18px] font-bold text-slate-800 mb-6">
//               Extraction Parameters
//             </h3>

//             <div className="group relative border-2 border-dashed border-slate-200 rounded-[24px] p-10 text-center hover:border-indigo-500 hover:bg-indigo-50/50 transition-all duration-300 mb-6 overflow-hidden">
//               <div className="w-16 h-16 bg-slate-50 rounded-2xl flex items-center justify-center mx-auto mb-4 group-hover:rotate-12 transition-transform">
//                 <FileSearch
//                   size={32}
//                   className={
//                     selectedFile ? "text-indigo-600" : "text-slate-400"
//                   }
//                 />
//               </div>
//               <p className="text-[16px] font-bold text-slate-700 truncate px-2">
//                 {selectedFile ? selectedFile.name : "Upload Stego-Object"}
//               </p>
//               <input
//                 type="file"
//                 onChange={(e) => setSelectedFile(e.target.files?.[0] || null)}
//                 className="absolute inset-0 opacity-0 cursor-pointer"
//                 accept={selectedAlgo === "EchoHiding" ? ".wav" : "image/*"}
//               />
//             </div>

//             <div className="space-y-3 mb-8">
//               <label className="text-[13px] font-black text-slate-400 uppercase tracking-widest ml-1">
//                 Detection Method
//               </label>
//               <div className="grid grid-cols-1 gap-3">
//                 {ALGORITHMS.map((algo) => (
//                   <button
//                     key={algo.id}
//                     onClick={() => setSelectedAlgo(algo.id)}
//                     className={`flex items-center justify-between p-4 rounded-2xl border transition-all text-left ${
//                       selectedAlgo === algo.id
//                         ? "border-indigo-500 bg-indigo-50/30"
//                         : "border-slate-100 bg-slate-50/50"
//                     }`}
//                   >
//                     <div>
//                       <p
//                         className={`text-[15px] font-bold ${selectedAlgo === algo.id ? "text-indigo-600" : "text-slate-700"}`}
//                       >
//                         {algo.label}
//                       </p>
//                       <p className="text-[12px] text-slate-400">{algo.desc}</p>
//                     </div>
//                     <div
//                       className={`w-5 h-5 rounded-full border-2 flex items-center justify-center ${selectedAlgo === algo.id ? "border-indigo-500" : "border-slate-200"}`}
//                     >
//                       {selectedAlgo === algo.id && (
//                         <div className="w-2.5 h-2.5 rounded-full bg-indigo-500" />
//                       )}
//                     </div>
//                   </button>
//                 ))}
//               </div>
//             </div>

//             <button
//               onClick={handleExtract}
//               disabled={isScanning || !selectedFile}
//               className="w-full py-5 rounded-2xl bg-slate-900 text-white text-[17px] font-bold shadow-2xl hover:bg-indigo-600 transition-all disabled:opacity-50 flex items-center justify-center gap-3"
//             >
//               {isScanning ? (
//                 <>
//                   <RefreshCcw size={20} className="animate-spin" /> Scanning
//                   Bits...
//                 </>
//               ) : (
//                 <>
//                   <SearchCode size={20} /> Initiate Extraction
//                 </>
//               )}
//             </button>
//             {error && (
//               <p className="text-red-500 text-[12px] mt-4 text-center font-bold">
//                 !! {error}
//               </p>
//             )}
//           </div>
//         </div>

//         {/* Right: Forensic Result Terminal */}
//         <div className="lg:col-span-7">
//           <div className="bg-[#0B0F1A] rounded-[32px] shadow-2xl overflow-hidden h-full flex flex-col min-h-[500px]">
//             <div className="bg-white/5 px-6 py-4 flex items-center justify-between border-b border-white/10">
//               <div className="flex items-center gap-2">
//                 <div className="flex gap-1.5">
//                   <div className="w-3 h-3 rounded-full bg-red-500/80" />
//                   <div className="w-3 h-3 rounded-full bg-amber-500/80" />
//                   <div className="w-3 h-3 rounded-full bg-emerald-500/80" />
//                 </div>
//                 <span className="ml-4 text-[12px] font-mono text-white/40 flex items-center gap-2">
//                   <Terminal size={14} /> steganography_analyzer.exe
//                 </span>
//               </div>
//               {activeResult?.success && (
//                 <button
//                   onClick={copyToClipboard}
//                   className="text-white/40 hover:text-white transition-colors p-2 bg-white/5 rounded-lg"
//                 >
//                   <Copy size={16} />
//                 </button>
//               )}
//             </div>

//             <div className="flex-1 p-8 font-mono text-[15px] overflow-y-auto">
//               {isScanning ? (
//                 <div className="space-y-4">
//                   <p className="text-emerald-500 animate-pulse">
//                     {">"} INITIALIZING FORENSIC_SCAN
//                   </p>
//                   <p className="text-white/60">
//                     {">"} Isolating {selectedAlgo.toUpperCase()} domain
//                     coefficients...
//                   </p>
//                   {selectedAlgo === "EchoHiding" && (
//                     <p className="text-pink-400/60">
//                       {">"} Detecting acoustic echo patterns...
//                     </p>
//                   )}
//                 </div>
//               ) : activeResult?.success ? (
//                 <div className="space-y-6 animate-in slide-in-from-top-4">
//                   <div className="p-4 bg-emerald-500/10 border border-emerald-500/20 rounded-xl">
//                     <p className="text-emerald-400 font-bold flex items-center gap-2">
//                       <ShieldCheck size={18} /> {activeResult.message}
//                     </p>
//                   </div>

//                   <div className="space-y-2">
//                     <label className="text-white/30 text-[11px] uppercase font-bold tracking-widest">
//                       Recovered Payload
//                     </label>
//                     <div className="text-emerald-50/90 leading-relaxed bg-white/5 p-6 rounded-2xl border border-white/5 min-h-[100px] break-all">
//                       {activeResult.secret}
//                     </div>
//                   </div>

//                   {/* Dynamic Metadata Section */}
//                   <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
//                     {activeResult.details?.parameters_used && (
//                       <div className="col-span-2 bg-white/5 border border-white/10 rounded-xl p-4">
//                         <p className="text-white/40 text-[10px] font-bold uppercase mb-3 flex items-center gap-2">
//                           <Waves size={12} /> Detected Echo Parameters
//                         </p>
//                         <div className="grid grid-cols-4 gap-2 text-center">
//                           <div>
//                             <p className="text-white/30 text-[9px]">SPB</p>
//                             <p className="text-pink-400 text-[13px] font-bold">
//                               {activeResult.details.parameters_used.spb}
//                             </p>
//                           </div>
//                           <div>
//                             <p className="text-white/30 text-[9px]">D0</p>
//                             <p className="text-pink-400 text-[13px] font-bold">
//                               {activeResult.details.parameters_used.d0}
//                             </p>
//                           </div>
//                           <div>
//                             <p className="text-white/30 text-[9px]">D1</p>
//                             <p className="text-pink-400 text-[13px] font-bold">
//                               {activeResult.details.parameters_used.d1}
//                             </p>
//                           </div>
//                           <div>
//                             <p className="text-white/30 text-[9px]">Decay</p>
//                             <p className="text-pink-400 text-[13px] font-bold">
//                               {activeResult.details.parameters_used.decay}
//                             </p>
//                           </div>
//                         </div>
//                       </div>
//                     )}
//                   </div>

//                   <div className="grid grid-cols-2 gap-4 pt-4 text-[12px] border-t border-white/5">
//                     <div className="text-white/30 italic flex items-center gap-2">
//                       <Clock size={12} /> Scan Time:{" "}
//                       {activeResult.extraction_time.toFixed(4)}s
//                     </div>
//                     <div className="text-white/30 italic text-right uppercase">
//                       Method: {activeResult.details.algorithm}
//                     </div>
//                   </div>
//                 </div>
//               ) : (
//                 <div className="h-full flex flex-col items-center justify-center text-center space-y-4 opacity-20">
//                   <AlertCircle size={48} className="text-white" />
//                   <p className="text-white text-[16px]">
//                     Forensic Engine Idle. Upload stego-carrier to begin.
//                   </p>
//                 </div>
//               )}
//             </div>
//           </div>
//         </div>
//       </div>
//     </div>
//   )
// }

// export default Extract

"use client"

import React, { useState } from "react"
import {
  SearchCode,
  FileSearch,
  ShieldCheck,
  Copy,
  RefreshCcw,
  Terminal,
  AlertCircle,
  Clock,
  Waves,
  Video,
  Database,
} from "lucide-react"
import {
  useEchoExtracting,
  useExtracting,
  useVideoExtraction,
} from "@/hooks/useExtract"

const ALGORITHMS = [
  { id: "LSB", label: "LSB", desc: "Images (Raster Domain)" },
  { id: "DCT", label: "DCT", desc: "Images (Frequency Domain)" },
  { id: "EchoHiding", label: "Echo Hiding", desc: "Audio Domain (WAV)" },
  { id: "DWT", label: "DWT (Video)", desc: "Video Domain (AVI/MP4)" },
]

const Extract = () => {
  const [selectedAlgo, setSelectedAlgo] = useState("LSB")
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [activeResult, setActiveResult] = useState<any>(null)

  const { mutate: runExtracting, isPending: isImageScanning } = useExtracting()
  const { mutate: runEchoExtracting, isPending: isEchoScanning } =
    useEchoExtracting()
  const { mutate: runVideoExtraction, isPending: isVideoScanning } =
    useVideoExtraction()

  const isScanning = isImageScanning || isEchoScanning || isVideoScanning

  const handleExtract = () => {
    if (!selectedFile) {
      setError("Please upload a stego-object first.")
      return
    }
    setError(null)
    setActiveResult(null)

    const formData = new FormData()

    if (selectedAlgo === "EchoHiding") {
      formData.append("audio", selectedFile)
      runEchoExtracting(
        { formData },
        {
          onSuccess: (data) => {
            if (data.success) setActiveResult(data)
            else setError(data.message || "Extraction failed.")
          },
          onError: () =>
            setError("System failed to isolate payload from audio carrier."),
        },
      )
    } else if (selectedAlgo === "DWT") {
      formData.append("file", selectedFile)
      runVideoExtraction(
        { formData },
        {
          onSuccess: (data) => {
            if (data.success) setActiveResult(data)
            else setError(data.message || "Extraction failed.")
          },
          onError: () =>
            setError("System failed to process video stream frames."),
        },
      )
    } else {
      formData.append("file", selectedFile)
      formData.append("algorithm", selectedAlgo)
      runExtracting(
        { formData },
        {
          onSuccess: (data) => {
            if (data.success) setActiveResult(data)
            else setError(data.message || "Extraction failed.")
          },
          onError: () =>
            setError("System failed to isolate payload from image carrier."),
        },
      )
    }
  }

  const copyToClipboard = () => {
    if (activeResult?.secret) {
      navigator.clipboard.writeText(activeResult.secret)
    }
  }

  // Helper to determine display style based on algorithm
  const isVideoResult =
    activeResult?.algorithm === "DWT-Video" || selectedAlgo === "DWT"

  return (
    <div className="max-w-6xl mx-auto p-4 lg:p-8 space-y-8 animate-in fade-in duration-700 lg:pt-36 lg:pl-40">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-[28px] font-black text-slate-900 flex items-center gap-3">
            <SearchCode className="text-indigo-600" size={32} />
            Forensic Extraction
          </h1>
          <p className="text-slate-500 text-[16px] mt-1">
            Reverse-engineer media files to recover hidden payloads.
          </p>
        </div>
        <div className="flex items-center gap-2 px-4 py-2 bg-indigo-50 rounded-2xl border border-indigo-100">
          <ShieldCheck size={18} className="text-indigo-600" />
          <span className="text-[13px] font-bold text-indigo-700 uppercase tracking-wider">
            Integrity Check Active
          </span>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
        {/* Left: Input Panel */}
        <div className="lg:col-span-5 space-y-6">
          <div className="bg-white rounded-[32px] p-8 shadow-xl shadow-slate-200/60 border border-slate-100">
            <h3 className="text-[18px] font-bold text-slate-800 mb-6">
              Extraction Parameters
            </h3>

            <div className="group relative border-2 border-dashed border-slate-200 rounded-[24px] p-10 text-center hover:border-indigo-500 hover:bg-indigo-50/50 transition-all duration-300 mb-6 overflow-hidden">
              <div className="w-16 h-16 bg-slate-50 rounded-2xl flex items-center justify-center mx-auto mb-4 group-hover:rotate-12 transition-transform">
                {selectedAlgo === "DWT" ? (
                  <Video
                    size={32}
                    className={
                      selectedFile ? "text-indigo-600" : "text-slate-400"
                    }
                  />
                ) : (
                  <FileSearch
                    size={32}
                    className={
                      selectedFile ? "text-indigo-600" : "text-slate-400"
                    }
                  />
                )}
              </div>
              <p className="text-[16px] font-bold text-slate-700 truncate px-2">
                {selectedFile ? selectedFile.name : "Upload Stego-Object"}
              </p>
              <input
                type="file"
                key={selectedAlgo} // Crucial: Resets the input state when algorithm changes
                onChange={(e) => {
                  const file = e.target.files?.[0]
                  if (file) {
                    setSelectedFile(file)
                    setError(null) // Clear errors when a new file is successfully picked
                  }
                }}
                className="absolute inset-0 opacity-0 cursor-pointer"
                // Improved accept string for better compatibility
                accept={
                  selectedAlgo === "EchoHiding"
                    ? "audio/wav,audio/x-wav,.wav"
                    : selectedAlgo === "DWT"
                      ? "video/x-msvideo,video/avi,video/mp4,video/quicktime,.avi,.mp4,.mov"
                      : "image/*"
                }
              />
            </div>

            <div className="space-y-3 mb-8">
              <label className="text-[13px] font-black text-slate-400 uppercase tracking-widest ml-1">
                Detection Method
              </label>
              <div className="grid grid-cols-1 gap-3">
                {ALGORITHMS.map((algo) => (
                  <button
                    key={algo.id}
                    onClick={() => {
                      setSelectedAlgo(algo.id)
                      setSelectedFile(null)
                    }}
                    className={`flex items-center justify-between p-4 rounded-2xl border transition-all text-left ${
                      selectedAlgo === algo.id
                        ? "border-indigo-500 bg-indigo-50/30"
                        : "border-slate-100 bg-slate-50/50"
                    }`}
                  >
                    <div>
                      <p
                        className={`text-[15px] font-bold ${selectedAlgo === algo.id ? "text-indigo-600" : "text-slate-700"}`}
                      >
                        {algo.label}
                      </p>
                      <p className="text-[12px] text-slate-400">{algo.desc}</p>
                    </div>
                    <div
                      className={`w-5 h-5 rounded-full border-2 flex items-center justify-center ${selectedAlgo === algo.id ? "border-indigo-500" : "border-slate-200"}`}
                    >
                      {selectedAlgo === algo.id && (
                        <div className="w-2.5 h-2.5 rounded-full bg-indigo-500" />
                      )}
                    </div>
                  </button>
                ))}
              </div>
            </div>

            <button
              onClick={handleExtract}
              disabled={isScanning || !selectedFile}
              className="w-full py-5 rounded-2xl bg-slate-900 text-white text-[17px] font-bold shadow-2xl hover:bg-indigo-600 transition-all disabled:opacity-50 flex items-center justify-center gap-3"
            >
              {isScanning ? (
                <>
                  <RefreshCcw size={20} className="animate-spin" /> Scanning
                  Carrier...
                </>
              ) : (
                <>
                  <SearchCode size={20} /> Initiate Extraction
                </>
              )}
            </button>
            {error && (
              <p className="text-red-500 text-[12px] mt-4 text-center font-bold">
                !! {error}
              </p>
            )}
          </div>
        </div>

        {/* Right: Forensic Result Terminal */}
        <div className="lg:col-span-7">
          <div className="bg-[#0B0F1A] rounded-[32px] shadow-2xl overflow-hidden h-full flex flex-col min-h-[500px]">
            <div className="bg-white/5 px-6 py-4 flex items-center justify-between border-b border-white/10">
              <div className="flex items-center gap-2">
                <div className="flex gap-1.5">
                  <div className="w-3 h-3 rounded-full bg-red-500/80" />
                  <div className="w-3 h-3 rounded-full bg-amber-500/80" />
                  <div className="w-3 h-3 rounded-full bg-emerald-500/80" />
                </div>
                <span className="ml-4 text-[12px] font-mono text-white/40 flex items-center gap-2">
                  <Terminal size={14} /> forensic_analyzer.py
                </span>
              </div>
              {activeResult?.success && (
                <button
                  onClick={copyToClipboard}
                  className="text-white/40 hover:text-white transition-colors p-2 bg-white/5 rounded-lg"
                  title="Copy Result"
                >
                  <Copy size={16} />
                </button>
              )}
            </div>

            <div className="flex-1 p-8 font-mono text-[15px] overflow-y-auto">
              {isScanning ? (
                <div className="space-y-4">
                  <p className="text-emerald-500 animate-pulse">
                    {">"} INITIALIZING FORENSIC_SCAN
                  </p>
                  <p className="text-white/60">
                    {">"} Analyzing {selectedAlgo.toUpperCase()} subbands...
                  </p>
                  {selectedAlgo === "DWT" && (
                    <p className="text-indigo-400/60">
                      {">"} Reading video frames into discrete wavelet buffer...
                    </p>
                  )}
                  {selectedAlgo === "EchoHiding" && (
                    <p className="text-pink-400/60">
                      {">"} Detecting acoustic echo patterns...
                    </p>
                  )}
                </div>
              ) : activeResult?.success ? (
                <div className="space-y-6 animate-in slide-in-from-top-4">
                  <div className="p-4 bg-emerald-500/10 border border-emerald-500/20 rounded-xl">
                    <p className="text-emerald-400 font-bold flex items-center gap-2">
                      <ShieldCheck size={18} /> {activeResult.message}
                    </p>
                  </div>

                  <div className="space-y-2">
                    <label className="text-white/30 text-[11px] uppercase font-bold tracking-widest">
                      Recovered Payload
                    </label>
                    <div className="text-emerald-50/90 leading-relaxed bg-white/5 p-6 rounded-2xl border border-white/5 min-h-[100px] break-all">
                      {activeResult.secret}
                    </div>
                  </div>

                  {/* Metadata Sections */}
                  <div className="grid grid-cols-1 gap-4">
                    {/* Video DWT Specific Details */}
                    {activeResult.algorithm === "DWT-Video" && (
                      <div className="bg-white/5 border border-white/10 rounded-xl p-4 flex items-center justify-between">
                        <div>
                          <p className="text-white/30 text-[10px] font-bold uppercase">
                            Quantization Step
                          </p>
                          <p className="text-indigo-400 text-[18px] font-bold">
                            {activeResult.details?.quantisation_step}
                          </p>
                        </div>
                        <Video size={24} className="text-white/10" />
                      </div>
                    )}

                    {/* Echo Specific Details */}
                    {activeResult.details?.parameters_used && (
                      <div className="bg-white/5 border border-white/10 rounded-xl p-4">
                        <p className="text-white/40 text-[10px] font-bold uppercase mb-3 flex items-center gap-2">
                          <Waves size={12} /> Detected Echo Parameters
                        </p>
                        <div className="grid grid-cols-4 gap-2 text-center">
                          <div>
                            <p className="text-white/30 text-[9px]">SPB</p>
                            <p className="text-pink-400 text-[13px] font-bold">
                              {activeResult.details.parameters_used.spb}
                            </p>
                          </div>
                          <div>
                            <p className="text-white/30 text-[9px]">D0</p>
                            <p className="text-pink-400 text-[13px] font-bold">
                              {activeResult.details.parameters_used.d0}
                            </p>
                          </div>
                          <div>
                            <p className="text-white/30 text-[9px]">D1</p>
                            <p className="text-pink-400 text-[13px] font-bold">
                              {activeResult.details.parameters_used.d1}
                            </p>
                          </div>
                          <div>
                            <p className="text-white/30 text-[9px]">Decay</p>
                            <p className="text-pink-400 text-[13px] font-bold">
                              {activeResult.details.parameters_used.decay}
                            </p>
                          </div>
                        </div>
                      </div>
                    )}
                  </div>

                  <div className="grid grid-cols-2 gap-4 pt-4 text-[12px] border-t border-white/5">
                    <div className="text-white/30 italic flex items-center gap-2">
                      <Clock size={12} /> Processed by Engine
                    </div>
                    <div className="text-white/30 italic text-right uppercase">
                      Method:{" "}
                      {activeResult.algorithm ||
                        activeResult.details?.algorithm}
                    </div>
                  </div>
                </div>
              ) : (
                <div className="h-full flex flex-col items-center justify-center text-center space-y-4 opacity-20">
                  <AlertCircle size={48} className="text-white" />
                  <p className="text-white text-[16px]">
                    Forensic Engine Idle. Upload stego-carrier to begin.
                  </p>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default Extract
