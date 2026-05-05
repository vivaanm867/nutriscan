import { createContext, useCallback, useContext, useEffect, useMemo, useState } from "react"

const AuthContext = createContext(null)
const TOKEN_KEY = "nutriscan_token"

const apiBaseUrl = import.meta.env.VITE_API_URL || "http://localhost:8000"

async function requestJson(url, options = {}) {
  const response = await fetch(url, {
    headers: {
      "Content-Type": "application/json",
      ...(options.headers || {}),
    },
    ...options,
  })

  if (!response.ok) {
    let message = "Request failed"
    try {
      const payload = await response.json()
      message = payload?.detail || payload?.message || message
    } catch {
      // Keep default message
    }
    throw new Error(message)
  }

  return response.json()
}

export function AuthProvider({ children }) {
  const [token, setToken] = useState(() => localStorage.getItem(TOKEN_KEY))
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const loadUser = async () => {
      if (!token) {
        setLoading(false)
        return
      }

      try {
        const data = await requestJson(`${apiBaseUrl}/api/auth/me`, {
          headers: { Authorization: `Bearer ${token}` },
        })
        setUser(data)
      } catch (error) {
        console.error(error)
        setToken(null)
        localStorage.removeItem(TOKEN_KEY)
      } finally {
        setLoading(false)
      }
    }

    loadUser()
  }, [token])

  const login = async ({ email, password }) => {
    const data = await requestJson(`${apiBaseUrl}/api/auth/login`, {
      method: "POST",
      body: JSON.stringify({ email, password }),
    })

    setToken(data.accessToken)
    localStorage.setItem(TOKEN_KEY, data.accessToken)
    setUser(data.user)
    return data
  }

  const signup = async ({ name, email, password }) => {
    const data = await requestJson(`${apiBaseUrl}/api/auth/signup`, {
      method: "POST",
      body: JSON.stringify({ name, email, password }),
    })

    setToken(data.accessToken)
    localStorage.setItem(TOKEN_KEY, data.accessToken)
    setUser(data.user)
    return data
  }

  const logout = () => {
    setToken(null)
    setUser(null)
    localStorage.removeItem(TOKEN_KEY)
  }

  const value = useMemo(
    () => ({
      token,
      user,
      loading,
      login,
      signup,
      logout,
      apiBaseUrl,
    }),
    [token, user, loading]
  )

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error("useAuth must be used within AuthProvider")
  }
  return context
}

export function useAuthedFetch() {
  const { token, apiBaseUrl } = useAuth()

  return useCallback(async (path, options = {}) => {
    const response = await fetch(`${apiBaseUrl}${path}`, {
      ...options,
      headers: {
        ...(options.headers || {}),
        Authorization: `Bearer ${token}`,
      },
    })

    if (!response.ok) {
      let message = "Request failed"
      try {
        const payload = await response.json()
        message = payload?.detail || payload?.message || message
      } catch {
        // Keep default message
      }
      throw new Error(message)
    }

    return response.json()
  }, [apiBaseUrl, token])
}
