import { writable } from 'svelte/store'

// ── Auth store ──────────────────────────────────────────────────────────────
export const user = writable(null)
export const authLoading = writable(false)

// Get CSRF token from Django cookie
function getCookie(name) {
  const value = `; ${document.cookie}`
  const parts = value.split(`; ${name}=`)
  if (parts.length === 2) return parts.pop().split(';').shift()
  return null
}

// Fetch CSRF token from Django first
export async function initCSRF() {
  await fetch('/api/csrf/', { credentials: 'include' })
}

async function apiFetch(url, options = {}) {
  const csrfToken = getCookie('csrftoken')
  return fetch(url, {
    credentials: 'include',
    headers: {
      'Content-Type': 'application/json',
      ...(csrfToken ? { 'X-CSRFToken': csrfToken } : {}),
      ...options.headers,
    },
    ...options,
  })
}

export async function apiSignup(data) {
  const res = await apiFetch('/api/signup/', {
    method: 'POST',
    body: JSON.stringify(data),
  })
  return res.json()
}

export async function apiLogin(data) {
  const res = await apiFetch('/api/login/', {
    method: 'POST',
    body: JSON.stringify(data),
  })
  return res.json()
}

export async function apiLogout() {
  const res = await apiFetch('/api/logout/', { method: 'POST' })
  return res.json()
}

export async function apiMe() {
  const res = await apiFetch('/api/me/')
  if (res.ok) return res.json()
  return null
}
