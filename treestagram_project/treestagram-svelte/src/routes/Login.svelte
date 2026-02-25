<script>
  import { user, apiLogin } from '../lib/api.js'

  export let navigate

  let username = ''
  let password = ''
  let loading = false
  let error = ''
  let shake = false
  let focused = ''
  let mounted = false

  import { onMount } from 'svelte'
  onMount(() => setTimeout(() => mounted = true, 50))

  async function handleLogin() {
    if (!username || !password) {
      triggerShake('Please fill in all fields.')
      return
    }
    loading = true
    error = ''
    try {
      const data = await apiLogin({ username, password })
      if (data.success) {
        user.set(data.user)
        navigate('/home')
      } else {
        triggerShake(data.error || 'Invalid credentials.')
      }
    } catch {
      triggerShake('Could not connect to server.')
    }
    loading = false
  }

  function triggerShake(msg) {
    error = msg
    shake = true
    setTimeout(() => shake = false, 600)
  }

  function handleKeydown(e) {
    if (e.key === 'Enter') handleLogin()
  }
</script>

<div class="page" class:mounted>
  <!-- Animated forest background -->
  <div class="forest-bg">
    <div class="layer layer-1"></div>
    <div class="layer layer-2"></div>
    <div class="layer layer-3"></div>
    <div class="fireflies">
      {#each Array(12) as _, i}
        <span class="firefly" style="
          --x: {10 + i * 7.5}%;
          --y: {15 + (i % 5) * 15}%;
          --delay: {i * 0.4}s;
          --dur: {2.5 + (i % 3) * 0.8}s;
        "></span>
      {/each}
    </div>
  </div>

  <!-- Card -->
  <div class="card" class:shake>
    <div class="card-inner">

      <!-- Brand -->
      <div class="brand">
        <div class="logo-wrap">
          <span class="logo-tree">🌳</span>
          <div class="logo-rings">
            <div class="ring r1"></div>
            <div class="ring r2"></div>
          </div>
        </div>
        <h1>Treestagram</h1>
        <p class="tagline">NYC's living urban forest</p>
      </div>

      <!-- Form -->
      <div class="form">
        <div class="field" class:focused={focused === 'username'}>
          <label for="username">
            <span class="label-icon">🪵</span> Username
          </label>
          <input
            id="username"
            type="text"
            placeholder="your_username"
            bind:value={username}
            on:focus={() => focused = 'username'}
            on:blur={() => focused = ''}
            on:keydown={handleKeydown}
            autocomplete="username"
          />
          <div class="field-line"></div>
        </div>

        <div class="field" class:focused={focused === 'password'}>
          <label for="password">
            <span class="label-icon">🔑</span> Password
          </label>
          <input
            id="password"
            type="password"
            placeholder="••••••••"
            bind:value={password}
            on:focus={() => focused = 'password'}
            on:blur={() => focused = ''}
            on:keydown={handleKeydown}
            autocomplete="current-password"
          />
          <div class="field-line"></div>
        </div>

        {#if error}
          <div class="error-msg">
            <span>⚠️</span> {error}
          </div>
        {/if}

        <button class="btn-login" on:click={handleLogin} disabled={loading}>
          {#if loading}
            <span class="btn-spinner"></span> Entering the forest…
          {:else}
            Enter the Forest 🌿
          {/if}
        </button>
      </div>

      <!-- Footer -->
      <div class="footer">
        <span>New to Treestagram?</span>
        <button class="link-btn" on:click={() => navigate('/signup')}>
          Plant your roots →
        </button>
      </div>

    </div>
  </div>
</div>

<style>
  /* ── Page & background ───────────────────────────────────────────────────── */
  .page {
    min-height: 100vh;
    display: flex;
    align-items: center;
    justify-content: center;
    position: relative;
    overflow: hidden;
    padding: 2rem 1rem;
    background: linear-gradient(160deg, #071410 0%, #0d2318 40%, #0a1c12 100%);
  }

  .forest-bg { position: absolute; inset: 0; pointer-events: none; }

  .layer {
    position: absolute;
    bottom: 0;
    width: 100%;
    background-repeat: repeat-x;
  }
  .layer-1 {
    height: 220px;
    background: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 1200 220'%3E%3Cpath d='M0,180 Q50,120 100,160 Q150,100 200,140 Q250,80 300,130 Q350,60 400,110 Q450,50 500,100 Q550,70 600,120 Q650,55 700,105 Q750,80 800,130 Q850,60 900,110 Q950,90 1000,140 Q1050,70 1100,120 Q1150,100 1200,150 L1200,220 L0,220Z' fill='%23122d1e' /%3E%3C/svg%3E");
    background-size: 1200px 220px;
    opacity: 0.9;
    animation: sway1 18s ease-in-out infinite alternate;
  }
  .layer-2 {
    height: 160px;
    background: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 1200 160'%3E%3Cpath d='M0,130 Q80,80 160,120 Q240,60 320,100 Q400,50 480,95 Q560,65 640,105 Q720,55 800,100 Q880,75 960,115 Q1040,60 1120,100 L1200,120 L1200,160 L0,160Z' fill='%231a3d27' /%3E%3C/svg%3E");
    background-size: 1200px 160px;
    opacity: 0.8;
    animation: sway2 12s ease-in-out infinite alternate;
  }
  .layer-3 {
    height: 100px;
    background: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 1200 100'%3E%3Cpath d='M0,80 Q100,40 200,70 Q300,30 400,65 Q500,35 600,60 Q700,40 800,70 Q900,35 1000,60 Q1100,45 1200,65 L1200,100 L0,100Z' fill='%23245c37' /%3E%3C/svg%3E");
    background-size: 1200px 100px;
    opacity: 0.7;
    animation: sway1 8s ease-in-out infinite alternate-reverse;
  }

  @keyframes sway1 {
    from { transform: translateX(0); }
    to   { transform: translateX(-30px); }
  }
  @keyframes sway2 {
    from { transform: translateX(-15px); }
    to   { transform: translateX(20px); }
  }

  /* Fireflies */
  .fireflies { position: absolute; inset: 0; }
  .firefly {
    position: absolute;
    left: var(--x);
    top: var(--y);
    width: 4px;
    height: 4px;
    border-radius: 50%;
    background: #a8f5b0;
    box-shadow: 0 0 6px 2px rgba(168, 245, 176, 0.6);
    animation: float var(--dur) var(--delay) ease-in-out infinite alternate;
  }
  @keyframes float {
    0%   { opacity: 0; transform: translate(0, 0); }
    30%  { opacity: 1; }
    70%  { opacity: 0.8; }
    100% { opacity: 0; transform: translate(20px, -30px); }
  }

  /* ── Card ────────────────────────────────────────────────────────────────── */
  .card {
    position: relative;
    z-index: 10;
    width: 100%;
    max-width: 420px;
    background: rgba(10, 28, 18, 0.75);
    backdrop-filter: blur(24px);
    -webkit-backdrop-filter: blur(24px);
    border: 1px solid rgba(82, 183, 136, 0.18);
    border-radius: 24px;
    box-shadow:
      0 0 0 1px rgba(82, 183, 136, 0.06),
      0 32px 64px rgba(0,0,0,0.5),
      inset 0 1px 0 rgba(255,255,255,0.06);
    transition: opacity 0.6s, transform 0.6s;
    opacity: 0;
    transform: translateY(24px);
  }
  .page.mounted .card {
    opacity: 1;
    transform: translateY(0);
  }
  .card.shake {
    animation: shake 0.5s cubic-bezier(.36,.07,.19,.97);
  }
  @keyframes shake {
    0%, 100% { transform: translateX(0); }
    15%  { transform: translateX(-10px); }
    30%  { transform: translateX(9px); }
    45%  { transform: translateX(-7px); }
    60%  { transform: translateX(5px); }
    75%  { transform: translateX(-3px); }
  }

  .card-inner { padding: 2.8rem 2.6rem 2.2rem; }

  /* ── Brand ───────────────────────────────────────────────────────────────── */
  .brand {
    text-align: center;
    margin-bottom: 2.2rem;
  }
  .logo-wrap {
    position: relative;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    margin-bottom: 1rem;
  }
  .logo-tree {
    font-size: 3rem;
    position: relative;
    z-index: 2;
    filter: drop-shadow(0 0 12px rgba(82,183,136,0.5));
    animation: treeBreathe 4s ease-in-out infinite;
  }
  @keyframes treeBreathe {
    0%, 100% { transform: scale(1); filter: drop-shadow(0 0 12px rgba(82,183,136,0.5)); }
    50%       { transform: scale(1.06); filter: drop-shadow(0 0 20px rgba(82,183,136,0.8)); }
  }
  .logo-rings { position: absolute; inset: -8px; }
  .ring {
    position: absolute;
    inset: 0;
    border-radius: 50%;
    border: 1px solid rgba(82,183,136,0.25);
    animation: ringPulse 3s ease-out infinite;
  }
  .r2 { animation-delay: 1.2s; }
  @keyframes ringPulse {
    0%   { transform: scale(0.9); opacity: 0.8; }
    100% { transform: scale(2); opacity: 0; }
  }
  h1 {
    font-family: 'Playfair Display', serif;
    font-size: 2.2rem;
    font-weight: 900;
    color: #d4f5dd;
    letter-spacing: -0.5px;
    line-height: 1;
    margin-bottom: 6px;
  }
  .tagline {
    font-size: 0.82rem;
    color: rgba(168, 220, 180, 0.55);
    letter-spacing: 2px;
    text-transform: uppercase;
    font-weight: 500;
  }

  /* ── Form ────────────────────────────────────────────────────────────────── */
  .form { display: flex; flex-direction: column; gap: 1.2rem; }

  .field { position: relative; }
  label {
    display: flex;
    align-items: center;
    gap: 6px;
    font-size: 0.75rem;
    font-weight: 600;
    color: rgba(168, 220, 180, 0.5);
    letter-spacing: 1.5px;
    text-transform: uppercase;
    margin-bottom: 8px;
    transition: color 0.2s;
  }
  .field.focused label { color: #52b788; }
  .label-icon { font-size: 0.9rem; }

  input {
    width: 100%;
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(82, 183, 136, 0.15);
    border-radius: 10px;
    padding: 13px 16px;
    font-size: 0.95rem;
    font-family: 'DM Sans', sans-serif;
    color: #d4f5dd;
    outline: none;
    transition: border-color 0.25s, background 0.25s, box-shadow 0.25s;
  }
  input::placeholder { color: rgba(255,255,255,0.18); }
  input:focus {
    border-color: rgba(82, 183, 136, 0.5);
    background: rgba(82, 183, 136, 0.06);
    box-shadow: 0 0 0 3px rgba(82, 183, 136, 0.1);
  }

  .field-line {
    position: absolute;
    bottom: 0;
    left: 16px;
    right: 16px;
    height: 1.5px;
    background: #52b788;
    transform: scaleX(0);
    transform-origin: left;
    transition: transform 0.3s cubic-bezier(0.4,0,0.2,1);
    border-radius: 1px;
  }
  .field.focused .field-line { transform: scaleX(1); }

  .error-msg {
    background: rgba(220, 60, 60, 0.12);
    border: 1px solid rgba(220, 60, 60, 0.25);
    border-radius: 8px;
    padding: 10px 14px;
    font-size: 0.85rem;
    color: #ff9999;
    display: flex;
    align-items: center;
    gap: 8px;
  }

  /* ── Button ──────────────────────────────────────────────────────────────── */
  .btn-login {
    width: 100%;
    padding: 15px;
    margin-top: 0.4rem;
    background: linear-gradient(135deg, #2d6a4f 0%, #40916c 50%, #52b788 100%);
    background-size: 200% 200%;
    border: none;
    border-radius: 12px;
    color: #fff;
    font-size: 1rem;
    font-weight: 600;
    font-family: 'DM Sans', sans-serif;
    cursor: pointer;
    transition: transform 0.15s, box-shadow 0.2s, background-position 0.4s;
    position: relative;
    overflow: hidden;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 8px;
    box-shadow: 0 4px 20px rgba(82,183,136,0.25);
  }
  .btn-login:hover:not(:disabled) {
    background-position: right center;
    transform: translateY(-1px);
    box-shadow: 0 8px 28px rgba(82,183,136,0.38);
  }
  .btn-login:active:not(:disabled) { transform: translateY(1px); }
  .btn-login:disabled { opacity: 0.65; cursor: not-allowed; }

  .btn-spinner {
    width: 16px;
    height: 16px;
    border: 2px solid rgba(255,255,255,0.3);
    border-top-color: #fff;
    border-radius: 50%;
    animation: spin 0.7s linear infinite;
    display: inline-block;
  }
  @keyframes spin { to { transform: rotate(360deg); } }

  /* ── Footer ──────────────────────────────────────────────────────────────── */
  .footer {
    text-align: center;
    margin-top: 1.6rem;
    font-size: 0.87rem;
    color: rgba(168, 220, 180, 0.45);
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 6px;
  }
  .link-btn {
    background: none;
    border: none;
    color: #52b788;
    font-size: 0.87rem;
    font-weight: 600;
    font-family: 'DM Sans', sans-serif;
    cursor: pointer;
    padding: 0;
    transition: color 0.2s, letter-spacing 0.2s;
  }
  .link-btn:hover { color: #95d5b2; letter-spacing: 0.3px; }
</style>
