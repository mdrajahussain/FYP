// "use client"

// import React, { useState } from "react"
// import {
//   Upload,
//   Activity,
//   Database,
//   Zap,
//   ShieldCheck,
//   Download,
//   Info,
//   AlertTriangle,
//   Waves,
//   BarChart3,
//   Clock,
//   FileJson,
// } from "lucide-react"
// import {
//   useEchoEmbedding,
//   useEmbedding,
//   useVideoEmbedding,
// } from "@/hooks/useEmbedding"

// const ALGORITHMS = [
//   { id: "LSB", label: "LSB", tag: "Image/png" },
//   { id: "DCT", label: "DCT", tag: "Image/png" },
//   {
//     id: "EchoHiding",
//     label: "Echo Hiding",
//     tag: "audio/wav",
//   },
//   { id: "DWT", label: "DWT", tag: "Videos" },
// ]

// type Preview = {
//   url: string
//   type: string
// }

// const Embedding = () => {
//   const [selectedAlgo, setSelectedAlgo] = useState("LSB")
//   const [message, setMessage] = useState("")
//   const [selectedFile, setSelectedFile] = useState<File | null>(null)
//   const [preview, setPreview] = useState<Preview | null>(null)
//   const [showResult, setShowResult] = useState(false)
//   const [customError, setCustomError] = useState("")
//   const [downloadLoading, setDownloadLoading] = useState(false)

//   // Local state to hold the most recent successful API response
//   const [activeResult, setActiveResult] = useState<any>(null)

//   const { mutate: runEmbedding, isPending: isImagePending } = useEmbedding()
//   const { mutate: runEchoEmbedding, isPending: isEchoPending } =
//     useEchoEmbedding()
//   const { mutate: runVideoEmbedding, isPending: isVideoPending } =
//     useVideoEmbedding()

//   const isPending = isImagePending || isEchoPending || isVideoPending

//   const handleEmbed = () => {
//     setCustomError("")
//     setActiveResult(null)

//     if (!selectedFile)
//       return setCustomError("Please select a carrier file first!")
//     if (!message.trim()) return setCustomError("Please enter a secret message!")

//     if (selectedAlgo === "EchoHiding" && !selectedFile.type.includes("audio")) {
//       return setCustomError("Echo Hiding requires an audio (WAV) file.")
//     }

//     const formData = new FormData()
//     formData.append("file", selectedFile)
//     formData.append("secret", message)
//     formData.append("algorithm", selectedAlgo)

//     if (selectedAlgo === "EchoHiding") {
//       const echoFormData = new FormData()
//       echoFormData.append("audio", selectedFile)
//       echoFormData.append("secret", message)
//       runEchoEmbedding(
//         { formData: echoFormData },
//         {
//           onSuccess: (data) => {
//             if (data.success) {
//               setActiveResult(data)
//               setShowResult(true)
//             } else {
//               setCustomError(data.message || "Embedding failed.")
//             }
//           },
//           onError: () =>
//             setCustomError("Server error: Failed to process audio."),
//         },
//       )
//     } else if (selectedAlgo === "DWT") {
//       const videoFormData = new FormData()
//       videoFormData.append("file", selectedFile)
//       videoFormData.append("secret", message)
//       runVideoEmbedding(
//         { formData: videoFormData },
//         {
//           onSuccess: (data) => {
//             if (data.success) {
//               setActiveResult(data)
//               setShowResult(true)
//             } else {
//               setCustomError(data.message || "Embedding failed.")
//             }
//           },
//           onError: () =>
//             setCustomError("Server error: Failed to process audio."),
//         },
//       )
//     } else {
//       runEmbedding(
//         { formData },
//         {
//           onSuccess: (data) => {
//             if (data.success) {
//               setActiveResult(data)
//               setShowResult(true)
//             } else {
//               setCustomError(data.message || "Embedding failed.")
//             }
//           },
//           onError: () =>
//             setCustomError("Server error: Failed to process image."),
//         },
//       )
//     }
//   }

//   const downloadFile = async (fileName?: string) => {
//     if (!fileName) return
//     setDownloadLoading(true)
//     try {
//       const fileUrl = `${process.env.NEXT_PUBLIC_API_URL}/stego/download/${fileName}`
//       const link = document.createElement("a")
//       link.href = fileUrl
//       link.download = fileName
//       document.body.appendChild(link)
//       link.click()
//       document.body.removeChild(link)
//     } catch (err) {
//       setCustomError("Download failed.")
//     } finally {
//       setDownloadLoading(false)
//     }
//   }

//   const isAudioResult = activeResult?.algorithm === "EchoHiding"

//   return (
//     <div className="min-h-screen bg-[#F8FAFC] text-slate-900 p-8 lg:pt-36 lg:pl-40">
//       <div className="max-w-6xl mx-auto mb-10">
//         <div className="flex items-center gap-3 mb-2">
//           <div className="p-2 bg-indigo-600 rounded-lg text-white">
//             <ShieldCheck size={28} />
//           </div>
//           <h1 className="text-[28px] font-bold tracking-tight">
//             Embed Secret Payload
//           </h1>
//         </div>
//         <p className="text-[16px] text-slate-500 max-w-xl">
//           Upload a media carrier and hide your secret message using advanced
//           steganography.
//         </p>
//       </div>

//       <div className="max-w-6xl mx-auto grid grid-cols-1 lg:grid-cols-12 gap-8">
//         {/* Left Column */}
//         <div className="lg:col-span-7 space-y-6">
//           <div className="bg-white rounded-[24px] shadow-xl border border-slate-200 p-8">
//             <h2 className="text-[18px] font-bold mb-6 flex items-center gap-2 text-indigo-600">
//               <Zap size={18} /> Configuration
//             </h2>

//             {customError && (
//               <div className="mb-6 bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg flex items-center gap-2">
//                 <AlertTriangle size={16} />
//                 <span className="text-sm font-medium">{customError}</span>
//               </div>
//             )}

//             <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
//               <div className="group relative border-2 border-dashed border-slate-200 rounded-2xl p-8 text-center hover:border-indigo-500 hover:bg-indigo-50/30 transition-all cursor-pointer">
//                 <Upload
//                   size={32}
//                   className="text-slate-400 group-hover:text-indigo-600 mx-auto mb-2"
//                 />
//                 <p className="text-[14px] font-semibold text-slate-700">
//                   Select Carrier
//                 </p>
//                 <input
//                   type="file"
//                   className="absolute inset-0 opacity-0 cursor-pointer"
//                   accept={
//                     selectedAlgo === "EchoHiding"
//                       ? "audio/wav,audio/x-wav"
//                       : "image/*"
//                   }
//                   onChange={(e) => {
//                     const file = e.target.files?.[0]
//                     if (!file) return
//                     setSelectedFile(file)
//                     setPreview({
//                       url: URL.createObjectURL(file),
//                       type: file.type,
//                     })
//                     setShowResult(false)
//                   }}
//                 />
//               </div>

//               <div className="bg-slate-50 rounded-2xl flex items-center justify-center overflow-hidden border border-slate-100 p-4">
//                 {preview ? (
//                   preview.type.includes("image") ? (
//                     <img
//                       src={preview.url}
//                       alt="Preview"
//                       className="h-32 object-contain"
//                     />
//                   ) : (
//                     <div className="flex flex-col items-center gap-2">
//                       <Waves size={40} className="text-pink-500" />
//                       <span className="text-[10px] font-mono text-slate-500 truncate w-32 text-center">
//                         {selectedFile?.name}
//                       </span>
//                     </div>
//                   )
//                 ) : (
//                   <p className="text-slate-400 text-[13px]">
//                     No preview available
//                   </p>
//                 )}
//               </div>
//             </div>

//             <div className="space-y-3 mb-6">
//               <label className="text-[13px] font-bold text-slate-500 uppercase tracking-widest ml-1">
//                 Secret Message
//               </label>
//               <textarea
//                 rows={3}
//                 value={message}
//                 onChange={(e) => setMessage(e.target.value)}
//                 placeholder="Enter sensitive data..."
//                 className="w-full bg-slate-50 border border-slate-200 rounded-xl px-4 py-3 text-[15px] outline-none focus:border-indigo-500 transition-all"
//               />
//             </div>

//             {selectedAlgo === "EchoHiding" && (
//               <div className="mb-6 p-4 bg-yellow-50 border border-yellow-200 rounded-lg text-yellow-700 text-sm flex items-center gap-2">
//                 <Info size={16} className="text-yellow-500" />
//                 Echo Hiding requires an audio file in WAV format with a minimum
//                 duration of 30 seconds for optimal results.
//               </div>
//             )}

//             <div className="grid grid-cols-3 gap-3 mb-8">
//               {ALGORITHMS.map((algo) => (
//                 <button
//                   key={algo.id}
//                   onClick={() => setSelectedAlgo(algo.id)}
//                   className={`p-4 rounded-xl border-2 text-left transition-all ${
//                     selectedAlgo === algo.id
//                       ? "border-indigo-600 bg-indigo-50"
//                       : "border-slate-100 bg-white"
//                   }`}
//                 >
//                   <span
//                     className={`text-[14px] font-bold block ${selectedAlgo === algo.id ? "text-indigo-700" : "text-slate-700"}`}
//                   >
//                     {algo.label}
//                   </span>
//                   <span className="text-[10px] text-slate-400 whitespace-nowrap">
//                     {algo.tag}
//                   </span>
//                 </button>
//               ))}
//             </div>

//             <button
//               onClick={handleEmbed}
//               disabled={isPending}
//               className="w-full py-4 rounded-xl bg-indigo-600 text-white font-bold hover:bg-indigo-700 transition-all disabled:opacity-50"
//             >
//               {isPending
//                 ? "Processing Transformation..."
//                 : "Generate Stego-Object"}
//             </button>
//           </div>
//         </div>

//         {/* Right Column: Results */}
//         <div className="lg:col-span-5">
//           <div className="bg-slate-900 rounded-[24px] p-8 min-h-[500px] flex flex-col shadow-2xl relative overflow-hidden">
//             <h3 className="text-white/40 text-[11px] font-bold uppercase tracking-[0.2em] mb-8 flex items-center gap-2">
//               <div
//                 className={`w-2 h-2 rounded-full ${showResult ? "bg-emerald-500 animate-pulse" : "bg-white/20"}`}
//               />
//               {isAudioResult ? "Acoustic Analysis" : "Forensic Analysis"}
//             </h3>

//             {showResult && activeResult ? (
//               <div className="space-y-6 animate-in fade-in slide-in-from-right-4 duration-500">
//                 <div className="bg-white/5 border border-white/10 p-4 rounded-xl flex items-center gap-4">
//                   <div
//                     className={`p-2 rounded-lg ${isAudioResult ? "bg-pink-500/20" : "bg-indigo-500/20"}`}
//                   >
//                     {isAudioResult ? (
//                       <Waves size={20} className="text-pink-400" />
//                     ) : (
//                       <Database size={20} className="text-indigo-400" />
//                     )}
//                   </div>
//                   <div className="flex-1 overflow-hidden">
//                     <p className="text-white text-[14px] font-bold truncate">
//                       {activeResult.output_file}
//                     </p>
//                     <p className="text-white/40 text-[11px] uppercase">
//                       {isAudioResult ? "Audio (WAV)" : "Image (Raster)"} •{" "}
//                       {activeResult.algorithm}
//                     </p>
//                   </div>
//                 </div>

//                 <div className="grid grid-cols-2 gap-3">
//                   {isAudioResult ? (
//                     <>
//                       <MetricBox
//                         label="SNR"
//                         value={
//                           activeResult.metrics?.snr
//                             ? `${activeResult.metrics.snr.toFixed(2)} dB`
//                             : "Inaudible"
//                         }
//                         color="text-yellow-400"
//                         icon={<BarChart3 size={12} />}
//                       />
//                       <MetricBox
//                         label="Sample Rate"
//                         value={`${activeResult.details?.sample_rate || 0} Hz`}
//                         color="text-emerald-400"
//                         icon={<Activity size={12} />}
//                       />
//                       <MetricBox
//                         label="Duration"
//                         value={`${activeResult.details?.duration_s?.toFixed(2) || 0}s`}
//                         color="text-blue-400"
//                         icon={<Clock size={12} />}
//                       />
//                       <MetricBox
//                         label="Capacity"
//                         value={
//                           activeResult.details?.capacity_used
//                             ?.split("(")[1]
//                             ?.replace(")", "") || "N/A"
//                         }
//                         color="text-purple-400"
//                         icon={<Database size={12} />}
//                       />
//                       <MetricBox
//                         label="Bits Hidden"
//                         value={activeResult.details?.bits_used || 0}
//                         color="text-indigo-400"
//                         icon={<Zap size={12} />}
//                       />
//                       <MetricBox
//                         label="Execution"
//                         value={`${activeResult.embedding_time?.toFixed(3)}s`}
//                         color="text-slate-400"
//                         icon={<Clock size={12} />}
//                       />
//                     </>
//                   ) : (
//                     <>
//                       <MetricBox
//                         label="PSNR"
//                         value={`${activeResult.metrics?.psnr?.toFixed(2) || "0"} dB`}
//                         color="text-emerald-400"
//                       />
//                       <MetricBox
//                         label="SSIM"
//                         value={activeResult.metrics?.ssim?.toFixed(4) || "0"}
//                         color="text-blue-400"
//                       />
//                       <MetricBox
//                         label="Capacity"
//                         value={
//                           activeResult.details?.capacity_used?.split(" ")[1] ||
//                           "N/A"
//                         }
//                         color="text-amber-400"
//                       />
//                       <MetricBox
//                         label="Time"
//                         value={`${activeResult.embedding_time?.toFixed(3)}s`}
//                         color="text-slate-400"
//                       />
//                     </>
//                   )}
//                 </div>

//                 {isAudioResult && activeResult.details?.parameters && (
//                   <div className="bg-white/5 border border-white/10 rounded-xl p-4">
//                     <p className="text-white/40 text-[10px] font-bold uppercase mb-3 flex items-center gap-2">
//                       <Waves size={12} /> Echo Kernel Parameters
//                     </p>
//                     <div className="grid grid-cols-4 gap-2">
//                       <div className="text-center">
//                         <p className="text-white/30 text-[9px]">SPB</p>
//                         <p className="text-pink-400 text-[14px] font-bold">
//                           {activeResult.details.parameters.spb}
//                         </p>
//                       </div>
//                       <div className="text-center">
//                         <p className="text-white/30 text-[9px]">D0</p>
//                         <p className="text-pink-400 text-[14px] font-bold">
//                           {activeResult.details.parameters.d0}
//                         </p>
//                       </div>
//                       <div className="text-center">
//                         <p className="text-white/30 text-[9px]">D1</p>
//                         <p className="text-pink-400 text-[14px] font-bold">
//                           {activeResult.details.parameters.d1}
//                         </p>
//                       </div>
//                       <div className="text-center">
//                         <p className="text-white/30 text-[9px]">Decay</p>
//                         <p className="text-pink-400 text-[14px] font-bold">
//                           {activeResult.details.parameters.decay}
//                         </p>
//                       </div>
//                     </div>
//                   </div>
//                 )}

//                 <div className="pt-4 border-t border-white/10">
//                   <p className="text-white/30 text-[11px] font-bold mb-3 uppercase tracking-widest">
//                     Integrity Notes
//                   </p>
//                   <div className="p-3 bg-amber-500/10 border border-amber-500/20 rounded-lg flex gap-3">
//                     <Info
//                       size={14}
//                       className="text-amber-500 shrink-0 mt-0.5"
//                     />
//                     <p className="text-[11px] text-amber-200/80 leading-relaxed">
//                       {activeResult.note ||
//                         "Process complete. Secure your stego-object locally."}
//                     </p>
//                   </div>
//                 </div>

//                 <button
//                   onClick={() => downloadFile(activeResult?.output_file)}
//                   disabled={downloadLoading}
//                   className="w-full py-4 rounded-xl bg-white text-slate-900 font-bold hover:bg-indigo-50 flex items-center justify-center gap-2 transition-all shadow-lg shadow-white/5"
//                 >
//                   <Download size={18} />
//                   {downloadLoading ? "Downloading..." : "Download Result"}
//                 </button>
//               </div>
//             ) : (
//               <div className="flex-1 flex flex-col items-center justify-center text-center">
//                 <div className="w-16 h-16 rounded-full border-2 border-dashed border-white/10 flex items-center justify-center mb-4">
//                   <Activity size={32} className="text-white/10" />
//                 </div>
//                 <p className="text-white/30 text-[14px] max-w-[240px]">
//                   {isPending
//                     ? "Analyzing frequencies & carrier integrity..."
//                     : "Awaiting transmission to generate stego-object"}
//                 </p>
//               </div>
//             )}
//           </div>
//         </div>
//       </div>
//     </div>
//   )
// }

// function MetricBox({
//   label,
//   value,
//   color,
//   icon,
// }: {
//   label: string
//   value: string | number
//   color: string
//   icon?: React.ReactNode
// }) {
//   return (
//     <div className="bg-white/5 border border-white/10 rounded-xl p-4">
//       <div className="flex items-center justify-between mb-1">
//         <p className="text-white/30 text-[10px] font-bold uppercase">{label}</p>
//         {icon && <div className="text-white/20">{icon}</div>}
//       </div>
//       <p className={`${color} text-[18px] font-black tracking-tight`}>
//         {value}
//       </p>
//     </div>
//   )
// }

// export default Embedding

//update -4
"use client"

import React, { useState } from "react"
import {
  Upload,
  Activity,
  Database,
  Zap,
  ShieldCheck,
  Download,
  Info,
  AlertTriangle,
  Waves,
  BarChart3,
  Clock,
  Video,
  Play,
  Layers,
} from "lucide-react"
import {
  useEchoEmbedding,
  useEmbedding,
  useVideoEmbedding,
} from "@/hooks/useEmbedding"

const ALGORITHMS = [
  { id: "LSB", label: "LSB", tag: "Image/png" },
  { id: "DCT", label: "DCT", tag: "Image/png" },
  { id: "EchoHiding", label: "Echo Hiding", tag: "audio/wav" },
  { id: "DWT", label: "DWT (Video)", tag: "video/mp4" },
]

type Preview = {
  url: string
  type: string
}

const Embedding = () => {
  const [selectedAlgo, setSelectedAlgo] = useState("LSB")
  const [message, setMessage] = useState("")
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [preview, setPreview] = useState<Preview | null>(null)
  const [showResult, setShowResult] = useState(false)
  const [customError, setCustomError] = useState("")
  const [downloadLoading, setDownloadLoading] = useState(false)
  const [activeResult, setActiveResult] = useState<any>(null)

  const { mutate: runEmbedding, isPending: isImagePending } = useEmbedding()
  const { mutate: runEchoEmbedding, isPending: isEchoPending } =
    useEchoEmbedding()
  const { mutate: runVideoEmbedding, isPending: isVideoPending } =
    useVideoEmbedding()

  const isPending = isImagePending || isEchoPending || isVideoPending

  const handleEmbed = () => {
    setCustomError("")
    setActiveResult(null)

    if (!selectedFile)
      return setCustomError("Please select a carrier file first!")
    if (!message.trim()) return setCustomError("Please enter a secret message!")

    if (selectedAlgo === "EchoHiding" && !selectedFile.type.includes("audio")) {
      return setCustomError("Echo Hiding requires an audio (WAV) file.")
    }

    if (selectedAlgo === "DWT" && !selectedFile.type.includes("video")) {
      return setCustomError("Video DWT requires a video file.")
    }

    const formData = new FormData()
    formData.append("file", selectedFile)
    formData.append("secret", message)
    formData.append("algorithm", selectedAlgo)

    if (selectedAlgo === "EchoHiding") {
      const echoFormData = new FormData()
      echoFormData.append("audio", selectedFile)
      echoFormData.append("secret", message)
      runEchoEmbedding(
        { formData: echoFormData },
        {
          onSuccess: (data) => {
            if (data.success) {
              setActiveResult(data)
              setShowResult(true)
            } else {
              setCustomError(data.message || "Embedding failed.")
            }
          },
          onError: () =>
            setCustomError("Server error: Failed to process audio."),
        },
      )
    } else if (selectedAlgo === "DWT") {
      runVideoEmbedding(
        { formData },
        {
          onSuccess: (data) => {
            if (data.success) {
              setActiveResult(data)
              setShowResult(true)
            } else {
              setCustomError(data.message || "Embedding failed.")
            }
          },
          onError: () =>
            setCustomError("Server error: Failed to process video."),
        },
      )
    } else {
      runEmbedding(
        { formData },
        {
          onSuccess: (data) => {
            if (data.success) {
              setActiveResult(data)
              setShowResult(true)
            } else {
              setCustomError(data.message || "Embedding failed.")
            }
          },
          onError: () =>
            setCustomError("Server error: Failed to process image."),
        },
      )
    }
  }

  const downloadFile = async (fileName?: string) => {
    if (!fileName) return
    setDownloadLoading(true)
    try {
      const fileUrl = `${process.env.NEXT_PUBLIC_API_URL}/stego/download/${fileName}`
      const link = document.createElement("a")
      link.href = fileUrl
      link.download = fileName
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
    } catch (err) {
      setCustomError("Download failed.")
    } finally {
      setDownloadLoading(false)
    }
  }

  // Determine media type for result UI
  const resultType =
    activeResult?.algorithm?.toLowerCase().includes("video") ||
    activeResult?.algorithm === "DWT"
      ? "video"
      : activeResult?.algorithm === "EchoHiding"
        ? "audio"
        : "image"

  return (
    <div className="min-h-screen bg-[#F8FAFC] text-slate-900 p-8 lg:pt-36 lg:pl-40">
      <div className="max-w-6xl mx-auto mb-10">
        <div className="flex items-center gap-3 mb-2">
          <div className="p-2 bg-indigo-600 rounded-lg text-white">
            <ShieldCheck size={28} />
          </div>
          <h1 className="text-[28px] font-bold tracking-tight">
            Embed Secret Payload
          </h1>
        </div>
        <p className="text-[16px] text-slate-500 max-w-xl">
          Upload a media carrier and hide your secret message using advanced
          steganography.
        </p>
      </div>

      <div className="max-w-6xl mx-auto grid grid-cols-1 lg:grid-cols-12 gap-8">
        {/* Left Column */}
        <div className="lg:col-span-7 space-y-6">
          <div className="bg-white rounded-[24px] shadow-xl border border-slate-200 p-8">
            <h2 className="text-[18px] font-bold mb-6 flex items-center gap-2 text-indigo-600">
              <Zap size={18} /> Configuration
            </h2>

            {customError && (
              <div className="mb-6 bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg flex items-center gap-2">
                <AlertTriangle size={16} />
                <span className="text-sm font-medium">{customError}</span>
              </div>
            )}

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
              <div className="group relative border-2 border-dashed border-slate-200 rounded-2xl p-8 text-center hover:border-indigo-500 hover:bg-indigo-50/30 transition-all cursor-pointer">
                <Upload
                  size={32}
                  className="text-slate-400 group-hover:text-indigo-600 mx-auto mb-2"
                />
                <p className="text-[14px] font-semibold text-slate-700">
                  Select Carrier
                </p>
                <input
                  type="file"
                  className="absolute inset-0 opacity-0 cursor-pointer"
                  accept={
                    selectedAlgo === "EchoHiding"
                      ? "audio/wav"
                      : selectedAlgo === "DWT"
                        ? "video/*"
                        : "image/*"
                  }
                  onChange={(e) => {
                    const file = e.target.files?.[0]
                    if (!file) return
                    setSelectedFile(file)
                    setPreview({
                      url: URL.createObjectURL(file),
                      type: file.type,
                    })
                    setShowResult(false)
                  }}
                />
              </div>

              <div className="bg-slate-50 rounded-2xl flex items-center justify-center overflow-hidden border border-slate-100 p-4">
                {preview ? (
                  preview.type.includes("image") ? (
                    <img
                      src={preview.url}
                      alt="Preview"
                      className="h-32 object-contain"
                    />
                  ) : preview.type.includes("video") ? (
                    <div className="flex flex-col items-center gap-2">
                      <Video size={40} className="text-indigo-500" />
                      <span className="text-[10px] font-mono text-slate-500 text-center px-2 truncate w-full">
                        {selectedFile?.name}
                      </span>
                    </div>
                  ) : (
                    <div className="flex flex-col items-center gap-2">
                      <Waves size={40} className="text-pink-500" />
                      <span className="text-[10px] font-mono text-slate-500 text-center px-2 truncate w-full">
                        {selectedFile?.name}
                      </span>
                    </div>
                  )
                ) : (
                  <p className="text-slate-400 text-[13px]">
                    No preview available
                  </p>
                )}
              </div>
            </div>

            <div className="space-y-3 mb-6">
              <label className="text-[13px] font-bold text-slate-500 uppercase tracking-widest ml-1">
                Secret Message
              </label>
              <textarea
                rows={3}
                value={message}
                onChange={(e) => setMessage(e.target.value)}
                placeholder="Enter sensitive data..."
                className="w-full bg-slate-50 border border-slate-200 rounded-xl px-4 py-3 text-[15px] outline-none focus:border-indigo-500 transition-all"
              />
            </div>

            <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-8">
              {ALGORITHMS.map((algo) => (
                <button
                  key={algo.id}
                  onClick={() => setSelectedAlgo(algo.id)}
                  className={`p-4 rounded-xl border-2 text-left transition-all ${
                    selectedAlgo === algo.id
                      ? "border-indigo-600 bg-indigo-50"
                      : "border-slate-100 bg-white"
                  }`}
                >
                  <span
                    className={`text-[14px] font-bold block ${selectedAlgo === algo.id ? "text-indigo-700" : "text-slate-700"}`}
                  >
                    {algo.label}
                  </span>
                  <span className="text-[10px] text-slate-400 whitespace-nowrap">
                    {algo.tag}
                  </span>
                </button>
              ))}
            </div>

            <button
              onClick={handleEmbed}
              disabled={isPending}
              className="w-full py-4 rounded-xl bg-indigo-600 text-white font-bold hover:bg-indigo-700 transition-all disabled:opacity-50"
            >
              {isPending
                ? "Processing Transformation..."
                : "Generate Stego-Object"}
            </button>
          </div>
        </div>

        {/* Right Column: Results */}
        <div className="lg:col-span-5">
          <div className="bg-slate-900 rounded-[24px] p-8 min-h-[500px] flex flex-col shadow-2xl relative overflow-hidden">
            <h3 className="text-white/40 text-[11px] font-bold uppercase tracking-[0.2em] mb-8 flex items-center gap-2">
              <div
                className={`w-2 h-2 rounded-full ${showResult ? "bg-emerald-500 animate-pulse" : "bg-white/20"}`}
              />
              Forensic Analysis
            </h3>

            {showResult && activeResult ? (
              <div className="space-y-6 animate-in fade-in slide-in-from-right-4 duration-500">
                <div className="bg-white/5 border border-white/10 p-4 rounded-xl flex items-center gap-4">
                  <div
                    className={`p-2 rounded-lg ${
                      resultType === "video"
                        ? "bg-indigo-500/20"
                        : resultType === "audio"
                          ? "bg-pink-500/20"
                          : "bg-emerald-500/20"
                    }`}
                  >
                    {resultType === "video" ? (
                      <Video size={20} className="text-indigo-400" />
                    ) : resultType === "audio" ? (
                      <Waves size={20} className="text-pink-400" />
                    ) : (
                      <Database size={20} className="text-emerald-400" />
                    )}
                  </div>
                  <div className="flex-1 overflow-hidden">
                    <p className="text-white text-[14px] font-bold truncate">
                      {activeResult.output_file}
                    </p>
                    <p className="text-white/40 text-[11px] uppercase">
                      {activeResult.algorithm} • {resultType}
                    </p>
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-3">
                  {/* Dynamic Metrics based on resultType */}
                  {resultType === "video" ? (
                    <>
                      <MetricBox
                        label="Resolution"
                        value={activeResult.details?.resolution || "N/A"}
                        color="text-indigo-400"
                        icon={<Video size={12} />}
                      />
                      <MetricBox
                        label="FPS"
                        value={activeResult.details?.fps?.toFixed(2) || 0}
                        color="text-emerald-400"
                        icon={<Activity size={12} />}
                      />
                      <MetricBox
                        label="Frames Used"
                        value={`${activeResult.details?.frames_used} / ${activeResult.details?.total_frames}`}
                        color="text-blue-400"
                        icon={<Layers size={12} />}
                      />
                      <MetricBox
                        label="Quantization"
                        value={activeResult.details?.quantisation_step || 0}
                        color="text-amber-400"
                        icon={<BarChart3 size={12} />}
                      />
                      <MetricBox
                        label="Capacity"
                        value={`${activeResult.details?.utilization_percent}%`}
                        color="text-purple-400"
                        icon={<Database size={12} />}
                      />
                      <MetricBox
                        label="Time"
                        value={`${(activeResult.details?.embedding_time_ms / 1000).toFixed(2)}s`}
                        color="text-slate-400"
                        icon={<Clock size={12} />}
                      />
                    </>
                  ) : resultType === "audio" ? (
                    <>
                      <MetricBox
                        label="SNR"
                        value={
                          activeResult.metrics?.snr
                            ? `${activeResult.metrics.snr.toFixed(2)} dB`
                            : "Inaudible"
                        }
                        color="text-yellow-400"
                        icon={<BarChart3 size={12} />}
                      />
                      <MetricBox
                        label="Sample Rate"
                        value={`${activeResult.details?.sample_rate || 0} Hz`}
                        color="text-emerald-400"
                        icon={<Activity size={12} />}
                      />
                      <MetricBox
                        label="Duration"
                        value={`${activeResult.details?.duration_s?.toFixed(2) || 0}s`}
                        color="text-blue-400"
                        icon={<Clock size={12} />}
                      />
                      <MetricBox
                        label="Bits Hidden"
                        value={activeResult.details?.bits_used || 0}
                        color="text-indigo-400"
                        icon={<Zap size={12} />}
                      />
                      <MetricBox
                        label="Capacity"
                        value={
                          activeResult.details?.capacity_used
                            ?.split("(")[1]
                            ?.replace(")", "") || "N/A"
                        }
                        color="text-purple-400"
                        icon={<Database size={12} />}
                      />
                      <MetricBox
                        label="Execution"
                        value={`${activeResult.embedding_time?.toFixed(3)}s`}
                        color="text-slate-400"
                        icon={<Clock size={12} />}
                      />
                    </>
                  ) : (
                    <>
                      <MetricBox
                        label="PSNR"
                        value={`${activeResult.metrics?.psnr?.toFixed(2) || "0"} dB`}
                        color="text-emerald-400"
                      />
                      <MetricBox
                        label="SSIM"
                        value={activeResult.metrics?.ssim?.toFixed(4) || "0"}
                        color="text-blue-400"
                      />
                      <MetricBox
                        label="Capacity"
                        value={
                          activeResult.details?.capacity_used?.split(" ")[1] ||
                          "N/A"
                        }
                        color="text-amber-400"
                      />
                      <MetricBox
                        label="Time"
                        value={`${activeResult.embedding_time?.toFixed(3)}s`}
                        color="text-slate-400"
                      />
                    </>
                  )}
                </div>

                <div className="pt-4 border-t border-white/10">
                  <p className="text-white/30 text-[11px] font-bold mb-3 uppercase tracking-widest">
                    Integrity Notes
                  </p>
                  <div className="p-3 bg-amber-500/10 border border-amber-500/20 rounded-lg flex gap-3">
                    <Info
                      size={14}
                      className="text-amber-500 shrink-0 mt-0.5"
                    />
                    <p className="text-[11px] text-amber-200/80 leading-relaxed">
                      {activeResult.note ||
                        "Process complete. Secure your stego-object locally."}
                    </p>
                  </div>
                </div>

                <button
                  onClick={() => downloadFile(activeResult?.output_file)}
                  disabled={downloadLoading}
                  className="w-full py-4 rounded-xl bg-white text-slate-900 font-bold hover:bg-indigo-50 flex items-center justify-center gap-2 transition-all shadow-lg shadow-white/5"
                >
                  <Download size={18} />
                  {downloadLoading ? "Downloading..." : "Download Result"}
                </button>
              </div>
            ) : (
              <div className="flex-1 flex flex-col items-center justify-center text-center">
                <div className="w-16 h-16 rounded-full border-2 border-dashed border-white/10 flex items-center justify-center mb-4">
                  <Activity size={32} className="text-white/10" />
                </div>
                <p className="text-white/30 text-[14px] max-w-[240px]">
                  {isPending
                    ? "Analyzing frequencies & carrier integrity..."
                    : "Awaiting transmission to generate stego-object"}
                </p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}

function MetricBox({
  label,
  value,
  color,
  icon,
}: {
  label: string
  value: string | number
  color: string
  icon?: React.ReactNode
}) {
  return (
    <div className="bg-white/5 border border-white/10 rounded-xl p-4">
      <div className="flex items-center justify-between mb-1">
        <p className="text-white/30 text-[10px] font-bold uppercase">{label}</p>
        {icon && <div className="text-white/20">{icon}</div>}
      </div>
      <p className={`${color} text-[18px] font-black tracking-tight`}>
        {value}
      </p>
    </div>
  )
}

export default Embedding
