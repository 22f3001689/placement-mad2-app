async function request(path, options = {}) {
  const res = await fetch(`/api${path}`, {
    credentials: 'include',
    headers: { 'Content-Type': 'application/json' },
    ...options,
  })
  const body = await res.json().catch(() => ({}))
  if (!res.ok) {
    const error = new Error(body.error || `Request failed with status ${res.status}`)
    error.status = res.status
    throw error
  }
  return body
}

export function get(path) {
  return request(path)
}

export function post(path, data) {
  return request(path, { method: 'POST', body: JSON.stringify(data) })
}
