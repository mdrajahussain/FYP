export const systemDetails = async () => {
  try {
    const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/health`)

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }
    const data = await response.json()

    return data
  } catch (error) {
    console.error("Error fetching system details:", error)
    throw error
  }
}

// chat ai
export const chatAI = async ({ query }: { query: string }) => {
  try {
    const formData = new URLSearchParams()
    formData.append("query", query)
    const response = await fetch(
      `${process.env.NEXT_PUBLIC_API_URL}/chatbot/ask`,
      {
        method: "POST",
        headers: {
          "Content-Type": "application/x-www-form-urlencoded",
        },
        body: formData.toString(),
      },
    )

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }
    const data = await response.json()

    return data
  } catch (error) {
    console.error("Error fetching system details:", error)
    throw error
  }
}

// embedding
export const embedding = async ({ formData }: { formData: FormData }) => {
  try {
    const response = await fetch(
      `${process.env.NEXT_PUBLIC_API_URL}/stego/embed`,
      {
        method: "POST",
        body: formData,
      },
    )

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }
    const data = await response.json()

    return data
  } catch (error) {
    console.error("Error fetching system details:", error)
    throw error
  }
}

export const echoEmbedding = async ({ formData }: { formData: FormData }) => {
  try {
    const response = await fetch(
      `${process.env.NEXT_PUBLIC_API_URL}/echo/embed`,
      {
        method: "POST",
        body: formData,
      },
    )

    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.detail || `HTTP error! status: ${response.status}`)
    }

    const data = await response.json()
    return data
  } catch (error) {
    console.error("Error in echo embedding:", error)
    throw error
  }
}

export const videoEmbedding = async ({ formData }: { formData: FormData }) => {
  try {
    const response = await fetch(
      `${process.env.NEXT_PUBLIC_API_URL}/video/embed`,
      {
        method: "POST",
        body: formData,
      },
    )

    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.detail || `HTTP error! status: ${response.status}`)
    }

    const data = await response.json()
    return data
  } catch (error) {
    console.error("Error in video embedding:", error)
    throw error
  }
}

// extract
export const extract = async ({ formData }: { formData: FormData }) => {
  try {
    const response = await fetch(
      `${process.env.NEXT_PUBLIC_API_URL}/stego/extract`,
      {
        method: "POST",
        body: formData,
      },
    )

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }
    const data = await response.json()

    return data
  } catch (error) {
    console.error("Error extracting system details:", error)
    throw error
  }
}

export const echoExtraction = async ({ formData }: { formData: FormData }) => {
  try {
    const response = await fetch(
      `${process.env.NEXT_PUBLIC_API_URL}/echo/extract`,
      {
        method: "POST",
        body: formData,
      },
    )

    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.detail || `HTTP error! status: ${response.status}`)
    }

    const data = await response.json()
    return data
  } catch (error) {
    console.error("Error in echo extraction:", error)
    throw error
  }
}

export const videoExtraction = async ({ formData }: { formData: FormData }) => {
  try {
    const response = await fetch(
      `${process.env.NEXT_PUBLIC_API_URL}/video/extract`,
      {
        method: "POST",
        body: formData,
      },
    )

    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.detail || `HTTP error! status: ${response.status}`)
    }

    const data = await response.json()
    return data
  } catch (error) {
    console.error("Error in video extraction:", error)
    throw error
  }
}

//analyze
export const analyze = async ({ formData }: { formData: FormData }) => {
  try {
    const response = await fetch(
      `${process.env.NEXT_PUBLIC_API_URL}/metrics/analyze`,
      {
        method: "POST",
        body: formData,
      },
    )

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }
    const data = await response.json()

    return data
  } catch (error) {
    console.error("Error analyzing system details:", error)
    throw error
  }
}

// auth
export const login = async ({
  email,
  password,
}: {
  email: string
  password: string
}) => {
  try {
    const response = await fetch(
      `${process.env.NEXT_PUBLIC_API_URL}/auth/login`,
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ email, password }),
      },
    )

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }
    const data = await response.json()
    if (!data.success || !data.access_token) {
      throw new Error(
        data?.message ||
          "Login failed: Please check your credentials and try again.",
      )
    }

    return data
  } catch (error) {
    console.error("Error during login:", error)
    throw error
  }
}

export const register = async ({
  full_name,
  email,
  password,
}: {
  full_name: string
  email: string
  password: string
}) => {
  try {
    const response = await fetch(
      `${process.env.NEXT_PUBLIC_API_URL}/auth/register`,
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ full_name, email, password }),
      },
    )

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }
    const data = await response.json()

    return data
  } catch (error) {
    console.error("Error during registration:", error)
    throw error
  }
}
