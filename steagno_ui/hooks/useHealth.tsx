import { useQuery } from "@tanstack/react-query"
import { systemDetails } from "@/lib/api"

export const useHealth = () => {
  return useQuery({
    queryKey: ["health"],
    queryFn: systemDetails,
    refetchOnWindowFocus: false,
    staleTime: 1000 * 60 * 5, // 5 minutes
  })
}
