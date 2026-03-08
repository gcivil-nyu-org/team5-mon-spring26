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
  const headers = {
    ...(csrfToken ? { 'X-CSRFToken': csrfToken } : {}),
    ...options.headers,
  }

  // If body is FormData, don't set Content-Type header manually
  if (!(options.body && options.body.constructor && options.body.constructor.name === 'FormData')) {
    headers['Content-Type'] = 'application/json'
  }

  return fetch(url, {
    credentials: 'include',
    headers,
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

export async function apiCheckUsername(username) {
  const res = await apiFetch(`/api/check-username/?username=${encodeURIComponent(username)}`)
  return res.json()
}

export async function apiGoogleLoginUrl() {
  const res = await apiFetch('/api/google-login-url/')
  return res.json()
}

export async function apiForgotPassword(email) {
  const res = await apiFetch('/api/forgot-password/', {
    method: 'POST',
    body: JSON.stringify({ email }),
  })
  return res.json()
}

export async function apiVerifyResetToken(uid, token) {
  const res = await apiFetch(`/api/verify-reset-token/${uid}/${token}/`)
  return res.json()
}

export async function apiResetPassword(uid, token, password) {
  const res = await apiFetch(`/api/reset-password/${uid}/${token}/`, {
    method: 'POST',
    body: JSON.stringify({ password }),
  })
  return res.json()
}

export async function apiResendVerification(email) {
  const res = await apiFetch('/api/resend-verification/', {
    method: 'POST',
    body: JSON.stringify({ email }),
  })
  return res.json()
}

export async function apiUpdateProfile(formData) {
  const res = await apiFetch('/api/update-profile/', {
    method: 'POST',
    body: formData,
  })
  return res.json()
}

export async function apiChangePassword(current_password, new_password, confirm_password) {
  const res = await apiFetch('/api/change-password/', {
    method: 'POST',
    body: JSON.stringify({ current_password, new_password, confirm_password }),
  })
  return res.json()
}

export async function apiVerifyPassword(password) {
  const res = await apiFetch('/api/verify-password/', {
    method: 'POST',
    body: JSON.stringify({ password }),
  })
  return res.json()
}

export async function apiDeleteAccount(password) {
  const res = await apiFetch('/api/delete-account/', {
    method: 'POST',
    body: JSON.stringify({ password }),
  })
  return res.json()
}
