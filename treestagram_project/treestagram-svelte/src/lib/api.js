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

// ── Post / Like / Comment endpoints ─────────────────────────────────────────

export async function apiFetchPosts() {
  const res = await apiFetch('/api/posts/')
  return res.json()
}

export async function apiFetchMyPosts() {
  const res = await apiFetch('/api/my-posts/')
  return res.json()
}

export async function apiFetchMyTaggedPosts() {
  const res = await apiFetch('/api/my-tagged-posts/')
  return res.json()
}

export async function apiFetchTreePosts(treeId) {
  const res = await apiFetch(`/api/trees/${treeId}/posts/`)
  return res.json()
}

export async function apiValidateTree(treeId) {
  const res = await apiFetch(`/api/validate-tree/?tree_id=${encodeURIComponent(treeId)}`)
  return res.json()
}

export async function apiCreatePost(data) {
  const formData = new FormData()
  formData.append('tree_id', data.tree_id)
  if (data.body) formData.append('body', data.body)
  if (data.borough) formData.append('borough', data.borough)
  if (data.health) formData.append('health', data.health)
  if (data.image) formData.append('image', data.image)
  if (data.tagged_users) formData.append('tagged_users', data.tagged_users)

  const res = await apiFetch('/api/posts/create/', {
    method: 'POST',
    body: formData,
  })
  return res.json()
}

export async function apiDeletePost(postId) {
  const res = await apiFetch(`/api/posts/${postId}/delete/`, { method: 'POST' })
  return res.json()
}

export async function apiToggleLike(postId) {
  const res = await apiFetch(`/api/posts/${postId}/like/`, { method: 'POST' })
  return res.json()
}

export async function apiAddComment(postId, text) {
  const res = await apiFetch(`/api/posts/${postId}/comment/`, {
    method: 'POST',
    body: JSON.stringify({ text }),
  })
  return res.json()
}

export async function apiEditComment(commentId, text) {
  const res = await apiFetch(`/api/comments/${commentId}/edit/`, {
    method: 'POST',
    body: JSON.stringify({ text }),
  })
  return res.json()
}

export async function apiDeleteComment(commentId) {
  const res = await apiFetch(`/api/comments/${commentId}/delete/`, { method: 'POST' })
  return res.json()
}

// ── Notification endpoints ───────────────────────────────────────────────────

export async function apiFetchNotifications() {
  const res = await apiFetch('/api/notifications/')
  return res.json()
}

export async function apiFetchUnreadCount() {
  const res = await apiFetch('/api/notifications/unread-count/')
  return res.json()
}

export async function apiMarkNotificationsRead(ids) {
  const res = await apiFetch('/api/notifications/mark-read/', {
    method: 'POST',
    body: JSON.stringify({ ids }),
  })
  return res.json()
}

export async function apiMarkAllNotificationsRead() {
  const res = await apiFetch('/api/notifications/mark-all-read/', {
    method: 'POST',
  })
  return res.json()
}

// API for Tree search - Ramsey

export async function searchTreesMulti(params = {}, offset = 0, limit = 10) {
  const url = new URL("/trees/api/search/", window.location.origin);
  Object.entries(params).forEach(([k, v]) => {
    if (v) url.searchParams.append(k, v); // only append non-empty
  });
  url.searchParams.append("offset", offset);
  url.searchParams.append("limit", limit);

  try {
    const res = await fetch(url.toString(), { credentials: "include" });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return await res.json();
  } catch (err) {
    console.error("Search failed", err);
    return { results: [], count: 0 };
  }
}

// ── Tree Follow endpoints ────────────────────────────────────────────────────

export async function apiToggleTreeFollow(treeId) {
  const res = await apiFetch(`/api/trees/${treeId}/follow/`, { method: 'POST' })
  return res.json()
}

export async function apiFetchFollowedTrees() {
  const res = await apiFetch('/api/my-followed-trees/')
  return res.json()
}

// ------------------ apply for caretaker api -----------------------
export async function apiApplyForCaretaker(data) {
  const res = await apiFetch('/api/apply-for-caretaker/', {
    method: 'POST',
    body: JSON.stringify(data),
  })
  return res.json()
}

export async function apiMyApplicationStatus() {
  const res = await apiFetch('/api/my-application-status/')
  return res.json()
}

export async function apiFetchPendingApplications() {
  const res = await fetch("/api/pending-applications/", { // <-- Matches the new url path
    headers: { "Content-Type": "application/json" },
  });
  if (!res.ok) return { success: false };
  const data = await res.json();
  return { success: true, applications: data.applications };
}

export async function apiReviewApplication(applicationId, action) {
  const res = await fetch("/api/review-application/", { // <-- Matches the url path
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ application_id: applicationId, action }),
  });
  if (!res.ok) return { success: false };
  return { success: true };
}

