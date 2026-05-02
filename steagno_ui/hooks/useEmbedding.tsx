import { useMutation } from "@tanstack/react-query"
import { echoEmbedding, embedding, videoEmbedding } from "@/lib/api"

export const useEmbedding = () => {
  return useMutation({
    mutationFn: embedding,
  })
}

export const useEchoEmbedding = () => {
  return useMutation({
    mutationFn: echoEmbedding,
  })
}

export const useVideoEmbedding = () => {
  return useMutation({
    mutationFn: videoEmbedding,
  })
}
