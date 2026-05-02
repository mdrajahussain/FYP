import { useMutation } from "@tanstack/react-query"
import { echoExtraction, extract, videoExtraction } from "@/lib/api"

export const useExtracting = () => {
  return useMutation({
    mutationFn: extract,
  })
}

export const useEchoExtracting = () => {
  return useMutation({
    mutationFn: echoExtraction,
  })
}

export const useVideoExtraction = () => {
  return useMutation({
    mutationFn: videoExtraction,
  })
}
