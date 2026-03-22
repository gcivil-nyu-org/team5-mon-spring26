/**
 * theme.js — Enterprise Design Token System for Treestagram
 *
 * Three themes: 'dark' | 'light' | 'pixel'
 *
 * Usage:
 *   import { theme, toggleTheme, cycleTheme, setTheme } from './theme.js'
 *
 *   // In a Svelte component:
 *   import { theme, isPixelTheme } from './theme.js'
 *   $: pixelMode = isPixelTheme($theme)
 *
 * CSS variables are injected onto :root automatically when this module is
 * imported. All components reference var(--t-*) tokens.
 *
 * PIXEL THEME NOTES:
 *   - Uses 'Press Start 2P' for display/headings and 'VT323' for body text
 *   - Fonts are lazy-loaded from Google Fonts only when pixel theme is active
 *   - All radius tokens collapse to 0px (square corners)
 *   - Shadows use hard offset pixel-style (no blur) e.g. '4px 4px 0 #color'
 *   - Transitions use steps() easing for frame-by-frame motion feel
 *   - --t-bg-texture provides a scanline CSS pattern for the page background
 *   - --t-border-width is 2px (vs 1px in dark/light) for chunky outlines
 */

import { writable } from 'svelte/store'

// ─── Token Definitions ───────────────────────────────────────────────────────

const tokens = {

  // ── DARK ────────────────────────────────────────────────────────────────────
  dark: {
    // Canvas / Backgrounds — warm bark-brown palette matching landing page
    '--t-bg-base': '#2C1810',
    '--t-bg-surface': '#332015',
    '--t-bg-elevated': 'rgba(255,255,255,.06)',
    '--t-bg-overlay': 'rgba(44,24,16,.92)',
    '--t-bg-hover': 'rgba(143,188,143,.10)',
    '--t-bg-active': 'rgba(143,188,143,.16)',
    '--t-bg-input': 'rgba(255,255,255,.06)',
    '--t-bg-photo': 'rgba(0,0,0,.20)',
    '--t-bg-texture': 'none',

    // Gradients
    '--t-gradient-page': 'linear-gradient(180deg,#2C1810 0%,#332015 100%)',
    '--t-gradient-banner': 'linear-gradient(135deg,rgba(61,90,62,.35) 0%,rgba(143,188,143,.12) 100%)',
    '--t-gradient-bar': 'linear-gradient(90deg,#3D5A3E,#8FBC8F)',

    // Brand / Accent — sage/leaf greens with gold
    '--t-brand': '#8FBC8F',
    '--t-brand-dim': 'rgba(143,188,143,.15)',
    '--t-brand-muted': 'rgba(143,188,143,.30)',
    '--t-brand-glow': 'rgba(143,188,143,.50)',

    // Borders
    '--t-border': 'rgba(143,188,143,.14)',
    '--t-border-soft': 'rgba(143,188,143,.08)',
    '--t-border-strong': 'rgba(143,188,143,.22)',
    '--t-border-input': 'rgba(143,188,143,.18)',

    // Text — cream/canopy tones
    '--t-text-heading': '#F5F0E8',
    '--t-text-body': 'rgba(197,213,197,.75)',
    '--t-text-muted': 'rgba(197,213,197,.50)',
    '--t-text-faint': 'rgba(197,213,197,.30)',
    '--t-text-brand': '#8FBC8F',
    '--t-text-input': 'rgba(197,213,197,.50)',

    // Status
    '--t-status-good': '#8FBC8F',
    '--t-status-fair': '#D4A853',
    '--t-status-poor': '#f87171',
    '--t-status-info': '#60a5fa',

    // Role badges
    '--t-role-standard-bg': '#2a3d27',
    '--t-role-standard-text': '#8FBC8F',
    '--t-role-credible-bg': '#3d3418',
    '--t-role-credible-text': '#D4A853',
    '--t-role-caretaker-bg': '#1a2a3d',
    '--t-role-caretaker-text': '#60a5fa',
    '--t-role-admin-bg': '#3d1a1a',
    '--t-role-admin-text': '#f87171',

    // Radius
    '--t-radius-sm': '8px',
    '--t-radius-md': '12px',
    '--t-radius-lg': '16px',
    '--t-radius-pill': '9999px',

    // Shadows
    '--t-shadow-card': '0 4px 24px rgba(0,0,0,.40)',
    '--t-shadow-nav': '0 2px 20px rgba(0,0,0,.30)',
    '--t-shadow-pixel': 'none',
    '--t-shadow-pixel-btn': 'none',
    '--t-shadow-pixel-inset': 'none',

    // Motion
    '--t-transition': '0.2s ease',
    '--t-transition-slow': '0.5s ease',
    '--t-transition-pixel': '0.2s ease',

    // Typography
    '--t-font-display': "'Playfair Display', Georgia, serif",
    '--t-font-body': "'DM Sans', system-ui, sans-serif",
    '--t-font-mono': "'JetBrains Mono', monospace",
    '--t-font-pixel': "'DM Sans', system-ui, sans-serif",

    // Sizing
    '--t-nav-height': '58px',
    '--t-sidebar-width': '260px',
    '--t-content-max': '1000px',
    '--t-border-width': '1px',
  },

  // ── LIGHT ───────────────────────────────────────────────────────────────────
  light: {
    // Canvas / Backgrounds
    '--t-bg-base': '#f4faf6',
    '--t-bg-surface': '#edf7f1',
    '--t-bg-elevated': 'rgba(255,255,255,.90)',
    '--t-bg-overlay': 'rgba(244,250,246,.92)',
    '--t-bg-hover': 'rgba(45,106,79,.07)',
    '--t-bg-active': 'rgba(45,106,79,.12)',
    '--t-bg-input': 'rgba(255,255,255,.80)',
    '--t-bg-photo': 'rgba(0,0,0,.05)',
    '--t-bg-texture': 'none',

    // Gradients
    '--t-gradient-page': 'linear-gradient(180deg,#edf7f1 0%,#f4faf6 100%)',
    '--t-gradient-banner': 'linear-gradient(135deg,rgba(45,106,79,.12) 0%,rgba(82,183,136,.06) 100%)',
    '--t-gradient-bar': 'linear-gradient(90deg,#2d6a4f,#52b788)',

    // Brand / Accent
    '--t-brand': '#2d6a4f',
    '--t-brand-dim': 'rgba(45,106,79,.10)',
    '--t-brand-muted': 'rgba(45,106,79,.25)',
    '--t-brand-glow': 'rgba(45,106,79,.30)',

    // Borders
    '--t-border': 'rgba(45,106,79,.14)',
    '--t-border-soft': 'rgba(45,106,79,.08)',
    '--t-border-strong': 'rgba(45,106,79,.22)',
    '--t-border-input': 'rgba(45,106,79,.18)',

    // Text
    '--t-text-heading': '#0f2d1e',
    '--t-text-body': 'rgba(15,45,30,.75)',
    '--t-text-muted': 'rgba(15,45,30,.50)',
    '--t-text-faint': 'rgba(15,45,30,.30)',
    '--t-text-brand': '#2d6a4f',
    '--t-text-input': 'rgba(15,45,30,.45)',

    // Status
    '--t-status-good': '#2d6a4f',
    '--t-status-fair': '#b45309',
    '--t-status-poor': '#b91c1c',
    '--t-status-info': '#1d4ed8',

    // Role badges
    '--t-role-standard-bg': '#d1fae5',
    '--t-role-standard-text': '#065f46',
    '--t-role-credible-bg': '#fef3c7',
    '--t-role-credible-text': '#92400e',
    '--t-role-caretaker-bg': '#dbeafe',
    '--t-role-caretaker-text': '#1e40af',
    '--t-role-admin-bg': '#fee2e2',
    '--t-role-admin-text': '#991b1b',

    // Radius
    '--t-radius-sm': '8px',
    '--t-radius-md': '12px',
    '--t-radius-lg': '16px',
    '--t-radius-pill': '9999px',

    // Shadows
    '--t-shadow-card': '0 2px 16px rgba(0,0,0,.08)',
    '--t-shadow-nav': '0 1px 0 rgba(45,106,79,.10)',
    '--t-shadow-pixel': 'none',
    '--t-shadow-pixel-btn': 'none',
    '--t-shadow-pixel-inset': 'none',

    // Motion
    '--t-transition': '0.2s ease',
    '--t-transition-slow': '0.5s ease',
    '--t-transition-pixel': '0.2s ease',

    // Typography
    '--t-font-display': "'Playfair Display', Georgia, serif",
    '--t-font-body': "'DM Sans', system-ui, sans-serif",
    '--t-font-mono': "'JetBrains Mono', monospace",
    '--t-font-pixel': "'DM Sans', system-ui, sans-serif",

    // Sizing
    '--t-nav-height': '58px',
    '--t-sidebar-width': '260px',
    '--t-content-max': '1000px',
    '--t-border-width': '1px',
  },

  // ── PIXEL ───────────────────────────────────────────────────────────────────
  // Modern dark pixel / retro-RPG aesthetic.
  // Flat + opaque, square-cornered, hard-offset shadows, stepped motion.
  // Palette: deep forest black + neon green + amber — Game Boy meets
  // modern terminal UI.
  pixel: {
    // Canvas / Backgrounds — solid opaques, no glassmorphism
    '--t-bg-base': '#0b1a0f',
    '--t-bg-surface': '#0f2214',
    '--t-bg-elevated': '#162e1c',
    '--t-bg-overlay': '#0b1a0f',
    '--t-bg-hover': '#1e3d26',
    '--t-bg-active': '#254d30',
    '--t-bg-input': '#0f2214',
    '--t-bg-photo': '#0b1a0f',
    // Scanline overlay — apply as background-image on top of bg-base
    '--t-bg-texture':
      'repeating-linear-gradient(0deg,transparent,transparent 2px,rgba(0,0,0,0.18) 2px,rgba(0,0,0,0.18) 4px)',

    // Gradients — flat in pixel mode (just solid colours)
    '--t-gradient-page': '#0b1a0f',
    '--t-gradient-banner': '#162e1c',
    '--t-gradient-bar': '#39d353',  // solid neon green, no gradient

    // Brand / Accent — punchy neon green
    '--t-brand': '#39d353',
    '--t-brand-dim': '#1e3d26',
    '--t-brand-muted': '#2a5c34',
    '--t-brand-glow': '#39d353',

    // Borders — solid, no transparency
    '--t-border': '#2a5c34',
    '--t-border-soft': '#1e3d26',
    '--t-border-strong': '#39d353',
    '--t-border-input': '#2a5c34',

    // Text
    '--t-text-heading': '#b3ffcc',
    '--t-text-body': '#7ecb90',
    '--t-text-muted': '#4a8c5c',
    '--t-text-faint': '#2e5c3a',
    '--t-text-brand': '#39d353',
    '--t-text-input': '#7ecb90',

    // Status — bright, fully saturated
    '--t-status-good': '#39d353',
    '--t-status-fair': '#ffd700',
    '--t-status-poor': '#ff4444',
    '--t-status-info': '#44aaff',

    // Role badges — solid, opaque
    '--t-role-standard-bg': '#1a3d27',
    '--t-role-standard-text': '#39d353',
    '--t-role-credible-bg': '#3d3000',
    '--t-role-credible-text': '#ffd700',
    '--t-role-caretaker-bg': '#0a1f3d',
    '--t-role-caretaker-text': '#44aaff',
    '--t-role-admin-bg': '#3d0a0a',
    '--t-role-admin-text': '#ff4444',

    // Radius — ZERO everywhere. Pixel UIs are square.
    '--t-radius-sm': '0px',
    '--t-radius-md': '0px',
    '--t-radius-lg': '0px',
    '--t-radius-pill': '0px',

    // Shadows — hard pixel offset, zero blur
    // Cards / panels:
    '--t-shadow-card': '4px 4px 0 #39d353',
    // Navbar bottom border replacement:
    '--t-shadow-nav': '0 2px 0 #39d353',
    // Buttons (shifts on :active to simulate press):
    '--t-shadow-pixel-btn': '3px 3px 0 #1e3d26',
    // Pressed / active inset:
    '--t-shadow-pixel-inset': 'inset 2px 2px 0 #0b1a0f',
    // Generic alias:
    '--t-shadow-pixel': '4px 4px 0 #2a5c34',

    // Motion — stepped for frame-by-frame feel
    '--t-transition': '0.15s steps(3)',
    '--t-transition-slow': '0.4s steps(6)',
    '--t-transition-pixel': '0.1s steps(2)',

    // Typography
    // Press Start 2P → headings, labels, badges (dense, use sparingly)
    // VT323 → body text at large sizes (very legible retro feel)
    '--t-font-display': "'Press Start 2P', monospace",
    '--t-font-body': "'VT323', monospace",
    '--t-font-mono': "'Press Start 2P', monospace",
    '--t-font-pixel': "'Press Start 2P', monospace",

    // Sizing — slightly taller nav for pixel font
    '--t-nav-height': '62px',
    '--t-sidebar-width': '260px',
    '--t-content-max': '1000px',
    '--t-border-width': '2px',  // chunky 2px borders throughout
  },
}

// ─── Google Fonts lazy loader ─────────────────────────────────────────────────
// Only loads pixel fonts when the pixel theme is actually activated.

let pixelFontsLoaded = false

function loadPixelFonts() {
  if (pixelFontsLoaded || typeof document === 'undefined') return
  if (document.querySelector('[data-treestagram-fonts="pixel"]')) {
    pixelFontsLoaded = true
    return
  }
  const link = document.createElement('link')
  link.rel = 'stylesheet'
  link.href = 'https://fonts.googleapis.com/css2?family=Press+Start+2P&family=VT323:wght@400&display=swap'
  link.setAttribute('data-treestagram-fonts', 'pixel')
  document.head.appendChild(link)
  pixelFontsLoaded = true
}

// ─── Persistence ──────────────────────────────────────────────────────────────

const STORAGE_KEY = 'treestagram-theme'
const VALID_THEMES = ['dark', 'light', 'pixel']

// ─── Detect initial theme ─────────────────────────────────────────────────────

function detectInitialTheme() {
  // Migrate: clear any stale 'dark' preference so the app uses the intended light default
  if (typeof localStorage !== 'undefined') {
    const migrated = localStorage.getItem('treestagram-theme-v2')
    if (!migrated) {
      localStorage.removeItem(STORAGE_KEY)
      localStorage.setItem('treestagram-theme-v2', '1')
    }
  }

  const saved = typeof localStorage !== 'undefined' && localStorage.getItem(STORAGE_KEY)
  if (VALID_THEMES.includes(saved)) return saved

  // Default to light theme for the brown-nav + light-content design
  return 'light'
}

// ─── Apply tokens to :root ────────────────────────────────────────────────────

function applyTokens(mode) {
  if (typeof document === 'undefined') return
  const root = document.documentElement
  const vars = tokens[mode] || tokens.dark

  root.setAttribute('data-theme', mode)

  for (const [prop, value] of Object.entries(vars)) {
    root.style.setProperty(prop, value)
  }

  if (mode === 'pixel') loadPixelFonts()
}

// ─── Svelte Store ─────────────────────────────────────────────────────────────

const initial = detectInitialTheme()
applyTokens(initial)

export const theme = writable(initial)

theme.subscribe((mode) => {
  applyTokens(mode)
  if (typeof localStorage !== 'undefined') {
    localStorage.setItem(STORAGE_KEY, mode)
  }
})

// ─── Public API ───────────────────────────────────────────────────────────────

/** Toggle dark ↔ light (skips pixel) */
export function toggleTheme() {
  theme.update(c => (c === 'dark' ? 'light' : 'dark'))
}

/** Cycle all three themes: dark → light → pixel → dark */
export function cycleTheme() {
  theme.update(c => {
    const idx = VALID_THEMES.indexOf(c)
    return VALID_THEMES[(idx + 1) % VALID_THEMES.length]
  })
}

/** Set a specific mode: 'dark' | 'light' | 'pixel' */
export function setTheme(mode) {
  if (!VALID_THEMES.includes(mode)) return
  theme.set(mode)
}

/**
 * Watch OS preference changes in real time.
 * Only applies if the user has not made an explicit choice (incl. pixel).
 * Call once in App.svelte onMount; returns cleanup function.
 */
export function watchSystemTheme() {
  if (typeof window === 'undefined' || !window.matchMedia) return
  const mq = window.matchMedia('(prefers-color-scheme: dark)')
  const handler = (e) => {
    const saved = localStorage.getItem(STORAGE_KEY)
    if (!saved) setTheme(e.matches ? 'dark' : 'light')
  }
  mq.addEventListener('change', handler)
  return () => mq.removeEventListener('change', handler)
}

/** Clear saved preference and revert to default (light) theme */
export function resetToSystemTheme() {
  if (typeof localStorage !== 'undefined') localStorage.removeItem(STORAGE_KEY)
  setTheme('light')
}

/**
 * Returns true if the given (or current) theme is pixel mode.
 *
 * Usage in Svelte:
 *   $: pixelMode = isPixelTheme($theme)
 */
export function isPixelTheme(mode) {
  const m = mode ?? (typeof document !== 'undefined'
    ? document.documentElement.getAttribute('data-theme')
    : 'dark')
  return m === 'pixel'
}

/** Get a raw token value for use in JS (e.g. canvas drawing) */
export function getToken(name, mode) {
  const m = mode ?? (typeof document !== 'undefined'
    ? document.documentElement.getAttribute('data-theme') || 'dark'
    : 'dark')
  return tokens[m]?.[name] ?? ''
}

export { tokens, VALID_THEMES }