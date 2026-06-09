import { useState, useCallback } from 'react'

export function useQuery(apiFn) {
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  const execute = useCallback(async (payload) => {
    setLoading(true)
    setError(null)
    try {
      const result = await apiFn(payload)
      setData(result)
      return result
    } catch (err) {
      setError(err.message)
      return null
    } finally {
      setLoading(false)
    }
  }, [apiFn])

  const reset = () => { setData(null); setError(null) }

  return { data, loading, error, execute, reset }
}
