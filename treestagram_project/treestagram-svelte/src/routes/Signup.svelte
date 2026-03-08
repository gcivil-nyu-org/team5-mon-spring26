<script>
  import { user, apiSignup, apiCheckUsername } from "../lib/api.js";

  export let navigate;

  let firstName = "";
  let lastName = "";
  let email = "";
  let username = "";
  let borough = "";
  let password = "";
  let confirmPassword = "";
  let loading = false;
  let error = "";
  let showPassword = false;
  let showConfirm = false;
  let signupComplete = false;

  $: pwLong = password.length >= 8;
  $: pwUpper = /[A-Z]/.test(password);
  $: pwLower = /[a-z]/.test(password);
  $: pwDigit = /[0-9]/.test(password);
  let usernameStatus = null; // null | 'checking' | 'available' | 'taken' | 'short'
  let usernameTimer = null;

  function checkUsername() {
    clearTimeout(usernameTimer);
    if (username.length < 3) {
      usernameStatus = username.length > 0 ? "short" : null;
      return;
    }
    usernameStatus = "checking";
    usernameTimer = setTimeout(async () => {
      try {
        const res = await apiCheckUsername(username);
        usernameStatus = res.available ? "available" : "taken";
      } catch {
        usernameStatus = null;
      }
    }, 400);
  }

  const boroughs = [
    "Manhattan",
    "Brooklyn",
    "Queens",
    "The Bronx",
    "Staten Island",
  ];

  async function handleSignup() {
    if (!firstName || !lastName) {
      error = "Please enter your name.";
      return;
    }
    if (!email) {
      error = "Email is required.";
      return;
    }
    if (!username || username.length < 3) {
      error = "Username must be at least 3 characters.";
      return;
    }
    if (!password || password.length < 8) {
      error = "Password must be at least 8 characters.";
      return;
    }
    if (password !== confirmPassword) {
      error = "Passwords do not match.";
      return;
    }

    loading = true;
    error = "";
    try {
      const data = await apiSignup({
        first_name: firstName,
        last_name: lastName,
        email,
        username,
        borough: borough === "The Bronx" ? "Bronx" : borough,
        password1: password,
        password2: confirmPassword,
      });
      if (data.success) {
        signupComplete = true;
      } else if (data.errors) {
        // Django form returns errors as { field: [messages] }
        const firstField = Object.keys(data.errors)[0];
        error = data.errors[firstField][0];
      } else {
        error = data.error || "Signup failed. Please try again.";
      }
    } catch {
      error = "Could not connect to server.";
    }
    loading = false;
  }

  function handleKeydown(e) {
    if (e.key === "Enter") handleSignup();
  }
</script>

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
        Join New York City's community for urban tree stewardship. Follow trees.
        Share observations. Protect the canopy.
      </p>
      <span class="tree-illustration">🌱</span>
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
      <h2>Plant your roots</h2>
      <p>Create your Treestagram account</p>

      {#if signupComplete}
        <div class="success-panel">
          <span class="success-icon">🌳</span>
          <h3>Account Created!</h3>
          <p>We've sent a confirmation email to <strong>{email}</strong>.</p>
          <p>
            Click the link in your email to activate your account, then sign in.
          </p>
          <button class="btn-form-submit" on:click={() => navigate("/login")}>
            Go to Sign In
          </button>
        </div>
      {:else}
        <div class="form-row-2">
          <div class="form-group">
            <label for="signup-first">First Name</label>
            <input
              id="signup-first"
              type="text"
              placeholder="Jane"
              bind:value={firstName}
              on:keydown={handleKeydown}
            />
          </div>
          <div class="form-group">
            <label for="signup-last">Last Name</label>
            <input
              id="signup-last"
              type="text"
              placeholder="Doe"
              bind:value={lastName}
              on:keydown={handleKeydown}
            />
          </div>
        </div>

        <div class="form-group">
          <label for="signup-email">Email Address</label>
          <input
            id="signup-email"
            type="email"
            placeholder="you@example.com"
            bind:value={email}
            on:keydown={handleKeydown}
          />
        </div>

        <div class="form-group">
          <label for="signup-username">Username</label>
          <div class="input-wrapper">
            <input
              id="signup-username"
              type="text"
              placeholder="tree_guardian"
              bind:value={username}
              on:input={checkUsername}
              on:keydown={handleKeydown}
            />
            {#if usernameStatus === "checking"}
              <span class="username-indicator checking">⏳</span>
            {:else if usernameStatus === "available"}
              <span class="username-indicator available">✓</span>
            {:else if usernameStatus === "taken"}
              <span class="username-indicator taken">✗</span>
            {/if}
          </div>
          {#if usernameStatus === "available"}
            <small class="match-hint match">Username is available!</small>
          {:else if usernameStatus === "taken"}
            <small class="match-hint no-match">Username is already taken</small>
          {:else if usernameStatus === "short"}
            <small class="match-hint no-match"
              >Must be at least 3 characters</small
            >
          {/if}
        </div>

        <div class="form-group">
          <label for="signup-borough">Borough</label>
          <div class="borough-grid">
            {#each boroughs as b}
              <button
                class="borough-btn"
                class:selected={borough === b}
                on:click={() => (borough = b)}
                type="button"
              >
                {b === "Manhattan"
                  ? "🏙️"
                  : b === "Brooklyn"
                    ? "🌉"
                    : b === "Queens"
                      ? "🌳"
                      : b === "The Bronx"
                        ? "🌿"
                        : "⛴️"}
                {b}
              </button>
            {/each}
          </div>
        </div>

        <div class="form-group">
          <label for="signup-password">Password</label>
          <div class="input-wrapper">
            {#if showPassword}
              <input
                id="signup-password"
                type="text"
                placeholder="min 8 characters"
                bind:value={password}
                on:keydown={handleKeydown}
              />
            {:else}
              <input
                id="signup-password"
                type="password"
                placeholder="min 8 characters"
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
          {#if password.length > 0}
            <div class="pw-rules">
              <div class="pw-rule" class:met={pwLong}>
                {pwLong ? "✓" : "○"} At least 8 characters
              </div>
              <div class="pw-rule" class:met={pwUpper}>
                {pwUpper ? "✓" : "○"} One uppercase letter
              </div>
              <div class="pw-rule" class:met={pwLower}>
                {pwLower ? "✓" : "○"} One lowercase letter
              </div>
              <div class="pw-rule" class:met={pwDigit}>
                {pwDigit ? "✓" : "○"} One number
              </div>
            </div>
          {/if}
        </div>

        <div class="form-group">
          <label for="signup-confirm">Confirm Password</label>
          <div class="input-wrapper">
            {#if showConfirm}
              <input
                id="signup-confirm"
                type="text"
                placeholder="••••••••"
                bind:value={confirmPassword}
                on:keydown={handleKeydown}
              />
            {:else}
              <input
                id="signup-confirm"
                type="password"
                placeholder="••••••••"
                bind:value={confirmPassword}
                on:keydown={handleKeydown}
              />
            {/if}
            <button
              type="button"
              class="toggle-pw"
              on:click={() => (showConfirm = !showConfirm)}
              aria-label={showConfirm ? "Hide password" : "Show password"}
            >
              {showConfirm ? "🙈" : "👁️"}
            </button>
          </div>
          {#if confirmPassword && password !== confirmPassword}
            <small class="match-hint no-match">✗ Passwords don't match</small>
          {:else if confirmPassword && password === confirmPassword}
            <small class="match-hint match">✓ Passwords match</small>
          {/if}
        </div>

        {#if error}
          <div class="error-msg">⚠️ {error}</div>
        {/if}

        <button
          class="btn-form-submit"
          on:click={handleSignup}
          disabled={loading}
        >
          {#if loading}
            Creating account…
          {:else}
            Create Account 🌿
          {/if}
        </button>

        <div class="login-footer">
          Already have an account? <button
            class="link-btn"
            on:click={() => navigate("/login")}>Sign in</button
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
    padding: 2rem 3rem;
    overflow-y: auto;
  }
  .login-form {
    width: 100%;
    max-width: 420px;
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
    margin-bottom: 1.5rem;
  }

  .form-row-2 {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 0.8rem;
  }
  .form-group {
    margin-bottom: 1rem;
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
    padding: 0.7rem 1rem;
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
  .pw-rules {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 0.15rem 0.8rem;
    margin-top: 0.4rem;
  }
  .pw-rule {
    font-size: 0.75rem;
    color: var(--canopy);
    transition: color 0.2s;
  }
  .pw-rule.met {
    color: var(--moss);
    font-weight: 600;
  }
  .username-indicator {
    position: absolute;
    right: 0.8rem;
    font-size: 1rem;
    font-weight: 700;
  }
  .username-indicator.checking {
    opacity: 0.5;
  }
  .username-indicator.available {
    color: var(--moss);
  }
  .username-indicator.taken {
    color: #b91c1c;
  }

  .borough-grid {
    display: flex;
    flex-wrap: wrap;
    gap: 0.4rem;
  }
  .borough-btn {
    padding: 0.4rem 0.8rem;
    border: 1.5px solid var(--canopy);
    border-radius: 20px;
    background: white;
    color: var(--moss);
    font-family: "DM Sans", sans-serif;
    font-size: 0.82rem;
    cursor: pointer;
    transition: all 0.2s;
  }
  .borough-btn:hover {
    border-color: var(--sage);
  }
  .borough-btn.selected {
    background: var(--moss);
    color: white;
    border-color: var(--moss);
  }

  .match-hint {
    display: block;
    font-size: 0.78rem;
    margin-top: 0.3rem;
  }
  .match-hint.no-match {
    color: #b91c1c;
  }
  .match-hint.match {
    color: var(--moss);
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

  .success-panel {
    text-align: center;
    padding: 2rem 1rem;
  }
  .success-panel .success-icon {
    font-size: 3rem;
    display: block;
    margin-bottom: 1rem;
  }
  .success-panel h3 {
    font-family: "Playfair Display", serif;
    font-size: 1.5rem;
    color: var(--moss);
    margin-bottom: 0.5rem;
  }
  .success-panel p {
    color: var(--sage);
    font-size: 0.9rem;
    margin-bottom: 0.5rem;
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
  }
  .link-btn:hover {
    text-decoration: underline;
  }
</style>
