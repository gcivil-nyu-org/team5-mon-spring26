<script>
  import { onMount } from "svelte";
  import { user, apiLogin, apiGoogleLoginUrl } from "../lib/api.js";

  export let navigate;

  let username = "";
  let password = "";
  let loading = false;
  let error = "";
  let showPassword = false;
  let requiresVerification = false;
  let confirmationSuccess = false;

  onMount(() => {
    const params = new URLSearchParams(window.location.search);
    if (params.get("confirmed") === "true") {
      confirmationSuccess = true;
      // Clean the URL
      window.history.replaceState({}, "", "/login");
      // Auto-dismiss after 5 seconds
      setTimeout(() => {
        confirmationSuccess = false;
      }, 5000);
    }
  });

  async function handleLogin() {
    if (!username || !password) {
      error = "Please fill in all fields.";
      return;
    }
    loading = true;
    error = "";
    requiresVerification = false;
    try {
      const data = await apiLogin({ username, password });
      if (data.success) {
        user.set(data.user);
        navigate("/home");
      } else {
        error = data.error || "Invalid credentials.";
        if (data.requires_verification) {
          requiresVerification = true;
        }
      }
    } catch {
      error = "Could not connect to server.";
    }
    loading = false;
  }

  async function handleGoogleLogin() {
    try {
      const data = await apiGoogleLoginUrl();
      if (data.url) {
        window.location.href = data.url;
      }
    } catch {
      error = "Could not connect to Google login.";
    }
  }

  function handleKeydown(e) {
    if (e.key === "Enter") handleLogin();
  }
</script>

{#if confirmationSuccess}
  <div class="toast-success">
    <span>🌿</span> Email confirmed! Your account is now active. Sign in below.
    <button class="toast-close" on:click={() => (confirmationSuccess = false)}
      >✕</button
    >
  </div>
{/if}

<div class="page">
  <div class="login-left">
    <div class="login-left-content">
      <div
        class="login-brand"
        on:click={() => navigate("/")}
        on:keydown={(e) => e.key === "Enter" && navigate("/")}
        role="button"
        tabindex="0"
      >
        Tree<span>stagram</span>
      </div>
      <p class="login-tagline">
        New York City's community for urban tree stewardship. Follow trees.
        Share observations. Protect the canopy.
      </p>
      <span class="tree-illustration">🌳</span>
      <div class="login-feature">
        <span class="icon">📸</span>
        <span>Post photos and observations of NYC trees</span>
      </div>
      <div class="login-feature">
        <span class="icon">💬</span>
        <span>Join tree-specific group chats with fellow fans</span>
      </div>
      <div class="login-feature">
        <span class="icon">🛡️</span>
        <span>Become a Caretaker and steward your tree</span>
      </div>
    </div>
  </div>

  <div class="login-right">
    <div class="login-form">
      <h2>Welcome back</h2>
      <p>Sign in to your Treestagram account</p>

      <div class="form-group">
        <label for="login-username">Email or Username</label>
        <input
          id="login-username"
          type="text"
          placeholder="you@example.com"
          bind:value={username}
          on:keydown={handleKeydown}
        />
      </div>
      <div class="form-group">
        <label for="login-password">Password</label>
        <div class="input-wrapper">
          {#if showPassword}
            <input
              id="login-password"
              type="text"
              placeholder="••••••••"
              bind:value={password}
              on:keydown={handleKeydown}
            />
          {:else}
            <input
              id="login-password"
              type="password"
              placeholder="••••••••"
              bind:value={password}
              on:keydown={handleKeydown}
            />
          {/if}
          <button
            type="button"
            class="toggle-pw"
            on:click={() => (showPassword = !showPassword)}
            aria-label={showPassword ? "Hide password" : "Show password"}
          >
            {showPassword ? "🙈" : "👁️"}
          </button>
        </div>
      </div>
      <div class="form-row">
        <label><input type="checkbox" /> Remember me</label>
        <button class="link-btn" on:click={() => navigate("/forgot-password")}
          >Forgot password?</button
        >
      </div>

      {#if error}
        <div class="error-msg">⚠️ {error}</div>
      {/if}

      {#if requiresVerification}
        <div class="info-msg">
          📧 Check your inbox for a confirmation link to activate your account.
        </div>
      {/if}

      <button class="btn-form-submit" on:click={handleLogin} disabled={loading}>
        {#if loading}
          Signing in…
        {:else}
          Sign In
        {/if}
      </button>

      <div class="divider">or continue with</div>
      <button class="btn-google" on:click={handleGoogleLogin}>
        <svg width="16" height="16" viewBox="0 0 24 24"
          ><path
            fill="#4285F4"
            d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
          /><path
            fill="#34A853"
            d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
          /><path
            fill="#FBBC05"
            d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"
          /><path
            fill="#EA4335"
            d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"
          /></svg
        >
        Continue with Google
      </button>
      <div class="login-footer">
        Don't have an account? <button
          class="link-btn"
          on:click={() => navigate("/signup")}>Sign up free</button
        >
      </div>
    </div>
  </div>
</div>

<style>
  :root {
    --bark: #2c1810;
    --moss: #3d5a3e;
    --sage: #6b8f71;
    --leaf: #8fbc8f;
    --canopy: #c5d5c5;
    --cream: #f5f0e8;
    --sun: #d4a853;
    --ink: #1a1108;
  }

  .page {
    min-height: 100vh;
    display: grid;
    grid-template-columns: 1fr 1fr;
  }
  .login-left {
    background: var(--bark);
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    padding: 3rem;
    position: relative;
    overflow: hidden;
  }
  .login-left::before {
    content: "";
    position: absolute;
    inset: 0;
    background: repeating-radial-gradient(
      circle at 50% 50%,
      transparent 0,
      transparent 40px,
      rgba(143, 188, 143, 0.04) 40px,
      rgba(143, 188, 143, 0.04) 42px
    );
  }
  .login-left-content {
    position: relative;
    z-index: 1;
    text-align: center;
    max-width: 400px;
  }
  .login-brand {
    font-family: "Playfair Display", serif;
    font-size: 2.8rem;
    font-style: italic;
    color: var(--leaf);
    margin-bottom: 1rem;
    cursor: pointer;
    transition: opacity 0.2s;
  }
  .login-brand:hover {
    opacity: 0.8;
  }
  .login-brand span {
    color: var(--sun);
    font-style: normal;
  }
  .login-tagline {
    color: var(--canopy);
    line-height: 1.6;
    margin-bottom: 2.5rem;
    font-size: 1rem;
  }
  .tree-illustration {
    font-size: 5rem;
    display: block;
    margin-bottom: 1rem;
    animation: sway 4s ease-in-out infinite;
  }
  @keyframes sway {
    0%,
    100% {
      transform: rotate(-2deg);
    }
    50% {
      transform: rotate(2deg);
    }
  }
  .login-feature {
    display: flex;
    align-items: center;
    gap: 0.8rem;
    background: rgba(255, 255, 255, 0.06);
    border: 1px solid rgba(143, 188, 143, 0.2);
    border-radius: 10px;
    padding: 0.8rem 1rem;
    margin-bottom: 0.6rem;
    text-align: left;
    color: var(--canopy);
    font-size: 0.85rem;
  }
  .login-feature .icon {
    font-size: 1.2rem;
    flex-shrink: 0;
  }

  .login-right {
    background: var(--cream);
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 3rem;
  }
  .login-form {
    width: 100%;
    max-width: 380px;
  }
  .login-form h2 {
    font-family: "Playfair Display", serif;
    font-size: 2rem;
    color: var(--bark);
    margin-bottom: 0.5rem;
  }
  .login-form > p {
    color: var(--sage);
    font-size: 0.9rem;
    margin-bottom: 2rem;
  }
  .form-group {
    margin-bottom: 1.2rem;
  }
  .form-group label {
    display: block;
    font-size: 0.8rem;
    font-weight: 500;
    color: var(--moss);
    text-transform: uppercase;
    letter-spacing: 0.06em;
    margin-bottom: 0.4rem;
  }
  .form-group input {
    width: 100%;
    background: white;
    border: 1.5px solid var(--canopy);
    border-radius: 10px;
    padding: 0.75rem 1rem;
    font-family: "DM Sans", sans-serif;
    font-size: 0.95rem;
    color: var(--ink);
    transition:
      border-color 0.2s,
      box-shadow 0.2s;
    outline: none;
  }
  .form-group input:focus {
    border-color: var(--sage);
    box-shadow: 0 0 0 3px rgba(107, 143, 113, 0.15);
  }
  .input-wrapper {
    position: relative;
    display: flex;
    align-items: center;
  }
  .input-wrapper input {
    padding-right: 2.8rem;
  }
  .toggle-pw {
    position: absolute;
    right: 0.6rem;
    background: none;
    border: none;
    cursor: pointer;
    font-size: 1.15rem;
    padding: 0;
    display: flex;
    align-items: center;
    justify-content: center;
    opacity: 0.6;
    transition: opacity 0.2s;
  }
  .toggle-pw:hover {
    opacity: 1;
  }
  .form-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 1.5rem;
  }
  .form-row label {
    display: flex;
    align-items: center;
    gap: 0.4rem;
    font-size: 0.85rem;
    color: var(--moss);
    cursor: pointer;
  }
  .form-row .link-btn {
    font-size: 0.85rem;
    color: var(--sage);
    text-decoration: none;
  }
  .form-row .link-btn:hover {
    color: var(--moss);
    text-decoration: underline;
  }

  .error-msg {
    background: rgba(220, 60, 60, 0.1);
    border: 1px solid rgba(220, 60, 60, 0.25);
    border-radius: 8px;
    padding: 0.6rem 1rem;
    font-size: 0.85rem;
    color: #b91c1c;
    margin-bottom: 1rem;
  }

  .info-msg {
    background: rgba(59, 130, 246, 0.1);
    border: 1px solid rgba(59, 130, 246, 0.25);
    border-radius: 8px;
    padding: 0.6rem 1rem;
    font-size: 0.85rem;
    color: #1d4ed8;
    margin-bottom: 1rem;
  }

  .btn-form-submit {
    width: 100%;
    padding: 0.85rem;
    background: var(--moss);
    color: white;
    border: none;
    border-radius: 10px;
    font-family: "DM Sans", sans-serif;
    font-size: 1rem;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.25s;
    margin-bottom: 1.5rem;
  }
  .btn-form-submit:hover:not(:disabled) {
    background: var(--bark);
    transform: translateY(-1px);
  }
  .btn-form-submit:disabled {
    opacity: 0.65;
    cursor: not-allowed;
  }
  .divider {
    display: flex;
    align-items: center;
    gap: 1rem;
    color: var(--canopy);
    font-size: 0.8rem;
    margin-bottom: 1.5rem;
  }
  .divider::before,
  .divider::after {
    content: "";
    flex: 1;
    height: 1px;
    background: var(--canopy);
  }
  .btn-google {
    width: 100%;
    padding: 0.8rem;
    background: white;
    color: var(--ink);
    border: 1.5px solid var(--canopy);
    border-radius: 10px;
    font-family: "DM Sans", sans-serif;
    font-size: 0.9rem;
    cursor: pointer;
    transition: all 0.2s;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 0.5rem;
    margin-bottom: 1.5rem;
  }
  .btn-google:hover {
    border-color: var(--sage);
    box-shadow: 0 2px 10px rgba(44, 24, 16, 0.12);
  }
  .login-footer {
    text-align: center;
    font-size: 0.85rem;
    color: var(--sage);
  }
  .link-btn {
    background: none;
    border: none;
    color: var(--moss);
    font-weight: 600;
    font-family: "DM Sans", sans-serif;
    font-size: 0.85rem;
    cursor: pointer;
    padding: 0;
    text-decoration: none;
  }
  .link-btn:hover {
    text-decoration: underline;
  }

  .toast-success {
    position: fixed;
    top: 1.5rem;
    left: 50%;
    transform: translateX(-50%);
    background: #3d5a3e;
    color: white;
    padding: 0.85rem 1.5rem;
    border-radius: 12px;
    font-size: 0.92rem;
    font-family: "DM Sans", sans-serif;
    display: flex;
    align-items: center;
    gap: 0.5rem;
    box-shadow: 0 6px 24px rgba(44, 24, 16, 0.2);
    z-index: 1000;
    animation: slideDown 0.4s ease-out;
  }
  @keyframes slideDown {
    from {
      opacity: 0;
      transform: translateX(-50%) translateY(-1rem);
    }
    to {
      opacity: 1;
      transform: translateX(-50%) translateY(0);
    }
  }
  .toast-close {
    background: none;
    border: none;
    color: rgba(255, 255, 255, 0.7);
    font-size: 1rem;
    cursor: pointer;
    padding: 0 0 0 0.5rem;
  }
  .toast-close:hover {
    color: white;
  }
</style>
