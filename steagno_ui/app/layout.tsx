import type { Metadata } from "next"
import { Inter, Poppins, Fira_Code } from "next/font/google"
import "./globals.css"
import Sidebar from "@/components/Sidebar"
import Navbar from "@/components/Navbar"
import QueryProvider from "@/provider/query-provider"

import { Toaster } from "sonner"

const inter = Inter({ subsets: ["latin"], variable: "--font-inter" })
const poppins = Poppins({
  weight: "600",
  subsets: ["latin"],
  variable: "--font-poppins",
})
const fira = Fira_Code({ subsets: ["latin"], variable: "--font-fira" })

export const metadata: Metadata = {
  title: "AI-Powered Multi-Media Steganography System",
  description:
    "An advanced forensic suite for hiding sensitive information within standard media using high-frequency domain transformations and AI-driven entropy analysis.",
}

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode
}>) {
  return (
    <html lang="en">
      <body
        className={`${inter.variable} ${poppins.variable} ${fira.variable} antialiased`}
      >
        <QueryProvider>
          <Navbar />
          <Sidebar />
          {children}
          <Toaster position="top-right" richColors />
        </QueryProvider>
      </body>
    </html>
  )
}
