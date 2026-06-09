const BASE = '/api'

export async function queryAssistant(payload) {
  const res = await fetch(`${BASE}/query`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  })
  if (!res.ok) {
    const err = await res.json()
    throw new Error(err.detail || 'Query failed')
  }
  return res.json()
}

export async function searchIncidents(payload) {
  const res = await fetch(`${BASE}/search`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  })
  if (!res.ok) throw new Error('Search failed')
  return res.json()
}

export async function submitReview(payload) {
  const res = await fetch(`${BASE}/review`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  })
  if (!res.ok) throw new Error('Review submission failed')
  return res.json()
}

export async function fetchDeviceStats() {
  const res = await fetch(`${BASE}/device-stats`)
  if (!res.ok) throw new Error('Stats fetch failed')
  return res.json()
}

export async function fetchHealth() {
  const res = await fetch(`${BASE}/health`)
  if (!res.ok) throw new Error('Health check failed')
  return res.json()
}
