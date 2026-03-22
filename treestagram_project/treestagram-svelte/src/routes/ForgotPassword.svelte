<script>
  import { apiForgotPassword } from "../lib/api.js";

  export let navigate;

  let email = "";
  let loading = false;
  let error = "";
  let success = false;

  async function handleSubmit() {
    if (!email) {
      error = "Please enter your email address.";
      return;
    }
    loading = true;
    error = "";
    try {
      const data = await apiForgotPassword(email);
      if (data.success) {
        success = true;
      } else {
        error = data.error || "Something went wrong. Please try again.";
      }
    } catch {
      error = "Could not connect to server.";
    }
    loading = false;
  }

  function handleKeydown(e) {
    if (e.key === "Enter") handleSubmit();
  }
</script>

<div class="page">
  <div class="forgot-left">
    <div class="forgot-left-content">
      <div
        class="forgot-brand"
        on:click={() => navigate("/")}
        on:keydown={(e) => e.key === "Enter" && navigate("/")}
        role="button"
        tabindex="0"
      >
        Tree<span>stagram</span>
      </div>
      <p class="forgot-tagline">
        New York City's community for urban tree stewardship. Follow trees.
        Share observations. Protect the canopy.
      </p>
      <span class="tree-illustration">🌳</span>
      <div class="forgot-feature">
        <span class="icon">🔐</span>
        <span>Securely reset your password via email</span>
      </div>
      <div class="forgot-feature">
        <span class="icon">📧</span>
        <span>Check your inbox for a reset link</span>
      </div>
      <div class="forgot-feature">
        <span class="icon">🛡️</span>
        <span>Your account stays safe with us</span>
      </div>
    </div>
  </div>

  <div class="forgot-right">
    <div class="forgot-form">
      {#if success}
        <div class="success-card">
          <span class="success-icon">✅</span>
          <h2>Check your inbox</h2>
          <p>
            If an account exists for <strong>{email}</strong>, we've sent a
            password reset link. Check your email and follow the instructions.
          </p>
          <button class="btn-form-submit" on:click={() => navigate("/login")}>
            Back to Sign In
          </button>
        </div>
      {:else}
        <h2>Reset your password</h2>
        <p>
          Enter the email address associated with your account and we'll send
          you a link to reset your password.
        </p>

        <div class="form-group">
          <label for="forgot-email">Email Address</label>
          <input
            id="forgot-email"
            type="email"
            placeholder="you@example.com"
            bind:value={email}
            on:keydown={handleKeydown}
          />
        </div>

        {#if error}
          <div class="error-msg">⚠️ {error}</div>
        {/if}

        <button
          class="btn-form-submit"
          on:click={handleSubmit}
          disabled={loading}
        >
          {#if loading}
            Sending…
          {:else}
            Send Reset Link
          {/if}
        </button>

        <div class="forgot-footer">
          Remember your password?
          <button class="link-btn" on:click={() => navigate("/login")}
            >Sign in</button
          >
        </div>
      {/if}
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

  /* ── Left panel ─────────────────────────────────────────────── */
  .forgot-left {
    background: var(--bark);
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    padding: 3rem;
    position: relative;
    overflow: hidden;
  }
  .forgot-left::before {
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
  .forgot-left-content {
    position: relative;
    z-index: 1;
    text-align: center;
    max-width: 400px;
  }
  .forgot-brand {
    font-family: "Playfair Display", serif;
    font-size: 2.8rem;
    font-style: italic;
    color: var(--leaf);
    margin-bottom: 1rem;
    cursor: pointer;
    transition: opacity 0.2s;
  }
  .forgot-brand:hover {
    opacity: 0.8;
  }
  .forgot-brand span {
    color: var(--sun);
    font-style: normal;
  }
  .forgot-tagline {
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
  .forgot-feature {
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
  .forgot-feature .icon {
    font-size: 1.2rem;
    flex-shrink: 0;
  }

  /* ── Right panel ────────────────────────────────────────────── */
  .forgot-right {
    background: var(--cream);
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 3rem;
  }
  .forgot-form {
    width: 100%;
    max-width: 380px;
  }
  .forgot-form h2 {
    font-family: "Playfair Display", serif;
    font-size: 2rem;
    color: var(--bark);
    margin-bottom: 0.5rem;
  }
  .forgot-form > p {
    color: var(--sage);
    font-size: 0.9rem;
    margin-bottom: 2rem;
    line-height: 1.6;
  }

  /* ── Form ───────────────────────────────────────────────────── */
  .form-group {
    margin-bottom: 1.5rem;
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

  .error-msg {
    background: rgba(220, 60, 60, 0.1);
    border: 1px solid rgba(220, 60, 60, 0.25);
    border-radius: 8px;
    padding: 0.6rem 1rem;
    font-size: 0.85rem;
    color: #b91c1c;
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

  .forgot-footer {
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

  /* ── Success card ───────────────────────────────────────────── */
  .success-card {
    text-align: center;
  }
  .success-card .success-icon {
    font-size: 3rem;
    display: block;
    margin-bottom: 1rem;
  }
  .success-card h2 {
    font-family: "Playfair Display", serif;
    font-size: 1.8rem;
    color: var(--bark);
    margin-bottom: 0.75rem;
  }
  .success-card p {
    color: var(--sage);
    font-size: 0.9rem;
    line-height: 1.6;
    margin-bottom: 2rem;
  }
  .success-card strong {
    color: var(--moss);
  }
</style>
