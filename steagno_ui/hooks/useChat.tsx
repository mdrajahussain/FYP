import { useMutation } from "@tanstack/react-query"
import { chatAI } from "@/lib/api"

export const useChatAI = () => {
  return useMutation({
    mutationFn: chatAI,
  })
}
