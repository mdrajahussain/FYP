import { useMutation } from "@tanstack/react-query"
import { analyze } from "@/lib/api"

export const useAnalyze = () => {
  return useMutation({
    mutationFn: analyze,
  })
}
