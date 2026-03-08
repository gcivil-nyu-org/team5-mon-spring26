<script>
    import { apiVerifyResetToken, apiResetPassword } from "../lib/api.js";
    import { onMount } from "svelte";

    export let navigate;
    export let uid = "";
    export let token = "";

    let password = "";
    let confirmPassword = "";
    let loading = false;
    let error = "";
    let showPassword = false;
    let showConfirm = false;
    let success = false;
    let validLink = null; // null = checking, true = valid, false = invalid

    // Password rules (same as Signup)
    $: pwLong = password.length >= 8;
    $: pwUpper = /[A-Z]/.test(password);
    $: pwLower = /[a-z]/.test(password);
    $: pwDigit = /[0-9]/.test(password);

    onMount(async () => {
        try {
            const data = await apiVerifyResetToken(uid, token);
            validLink = data.valid === true;
        } catch {
            validLink = false;
        }
    });

    async function handleSubmit() {
        if (!password || password.length < 8) {
            error = "Password must be at least 8 characters.";
            return;
        }
        if (!pwUpper || !pwLower || !pwDigit) {
            error = "Password must contain uppercase, lowercase and a number.";
            return;
        }
        if (password !== confirmPassword) {
            error = "Passwords do not match.";
            return;
        }

        loading = true;
        error = "";
        try {
            const data = await apiResetPassword(uid, token, password);
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
    <div class="reset-left">
        <div class="reset-left-content">
            <div
                class="reset-brand"
                on:click={() => navigate("/")}
                on:keydown={(e) => e.key === "Enter" && navigate("/")}
                role="button"
                tabindex="0"
            >
                Tree<span>stagram</span>
            </div>
            <p class="reset-tagline">
                New York City's community for urban tree stewardship. Follow
                trees. Share observations. Protect the canopy.
            </p>
            <span class="tree-illustration">🌳</span>
            <div class="reset-feature">
                <span class="icon">🔐</span>
                <span>Set a strong, secure password</span>
            </div>
            <div class="reset-feature">
                <span class="icon">✅</span>
                <span>Then sign in with your new credentials</span>
            </div>
            <div class="reset-feature">
                <span class="icon">🛡️</span>
                <span>Your account stays safe with us</span>
            </div>
        </div>
    </div>

    <div class="reset-right">
        <div class="reset-form">
            {#if validLink === null}
                <!-- Verifying token -->
                <div class="checking-card">
                    <span class="checking-icon">⏳</span>
                    <h2>Verifying your link…</h2>
                    <p>Please wait while we validate your reset link.</p>
                </div>
            {:else if validLink === false}
                <!-- Invalid / expired token -->
                <div class="expired-card">
                    <span class="expired-icon">⛔</span>
                    <h2>Link expired</h2>
                    <p>
                        This password reset link is invalid or has expired.
                        Please request a new one.
                    </p>
                    <button
                        class="btn-form-submit"
                        on:click={() => navigate("/forgot-password")}
                    >
                        Request New Link
                    </button>
                    <div class="reset-footer">
                        <button
                            class="link-btn"
                            on:click={() => navigate("/login")}
                            >Back to Sign In</button
                        >
                    </div>
                </div>
            {:else if success}
                <!-- Password changed -->
                <div class="success-card">
                    <span class="success-icon">✅</span>
                    <h2>Password reset complete!</h2>
                    <p>
                        Your password has been set. You can now sign in with
                        your new password.
                    </p>
                    <button
                        class="btn-form-submit"
                        on:click={() => navigate("/login")}
                    >
                        Sign In
                    </button>
                </div>
            {:else}
                <!-- Set new password form -->
                <h2>Set a new password</h2>
                <p>Choose a strong password for your account.</p>

                <div class="form-group">
                    <label for="reset-password">New Password</label>
                    <div class="input-wrapper">
                        {#if showPassword}
                            <input
                                id="reset-password"
                                type="text"
                                placeholder="min 8 characters"
                                bind:value={password}
                                on:keydown={handleKeydown}
                            />
                        {:else}
                            <input
                                id="reset-password"
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
                            aria-label={showPassword
                                ? "Hide password"
                                : "Show password"}
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
                    <label for="reset-confirm">Confirm Password</label>
                    <div class="input-wrapper">
                        {#if showConfirm}
                            <input
                                id="reset-confirm"
                                type="text"
                                placeholder="••••••••"
                                bind:value={confirmPassword}
                                on:keydown={handleKeydown}
                            />
                        {:else}
                            <input
                                id="reset-confirm"
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
                            aria-label={showConfirm
                                ? "Hide password"
                                : "Show password"}
                        >
                            {showConfirm ? "🙈" : "👁️"}
                        </button>
                    </div>
                    {#if confirmPassword && password !== confirmPassword}
                        <small class="match-hint no-match"
                            >✗ Passwords don't match</small
                        >
                    {:else if confirmPassword && password === confirmPassword}
                        <small class="match-hint match">✓ Passwords match</small
                        >
                    {/if}
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
                        Resetting…
                    {:else}
                        Reset Password
                    {/if}
                </button>

                <div class="reset-footer">
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
    .reset-left {
        background: var(--bark);
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        padding: 3rem;
        position: relative;
        overflow: hidden;
    }
    .reset-left::before {
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
    .reset-left-content {
        position: relative;
        z-index: 1;
        text-align: center;
        max-width: 400px;
    }
    .reset-brand {
        font-family: "Playfair Display", serif;
        font-size: 2.8rem;
        font-style: italic;
        color: var(--leaf);
        margin-bottom: 1rem;
        cursor: pointer;
        transition: opacity 0.2s;
    }
    .reset-brand:hover {
        opacity: 0.8;
    }
    .reset-brand span {
        color: var(--sun);
        font-style: normal;
    }
    .reset-tagline {
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
    .reset-feature {
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
    .reset-feature .icon {
        font-size: 1.2rem;
        flex-shrink: 0;
    }

    /* ── Right panel ────────────────────────────────────────────── */
    .reset-right {
        background: var(--cream);
        display: flex;
        align-items: center;
        justify-content: center;
        padding: 2rem 3rem;
        overflow-y: auto;
    }
    .reset-form {
        width: 100%;
        max-width: 420px;
    }
    .reset-form h2 {
        font-family: "Playfair Display", serif;
        font-size: 2rem;
        color: var(--bark);
        margin-bottom: 0.5rem;
    }
    .reset-form > p {
        color: var(--sage);
        font-size: 0.9rem;
        margin-bottom: 2rem;
        line-height: 1.6;
    }

    /* ── Form ───────────────────────────────────────────────────── */
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

    /* ── Password rules ─────────────────────────────────────────── */
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

    .reset-footer {
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

    /* ── State cards ────────────────────────────────────────────── */
    .checking-card,
    .expired-card,
    .success-card {
        text-align: center;
    }
    .checking-icon,
    .expired-icon,
    .success-icon {
        font-size: 3rem;
        display: block;
        margin-bottom: 1rem;
    }
    .checking-card h2,
    .expired-card h2,
    .success-card h2 {
        font-family: "Playfair Display", serif;
        font-size: 1.8rem;
        color: var(--bark);
        margin-bottom: 0.75rem;
    }
    .checking-card p,
    .expired-card p,
    .success-card p {
        color: var(--sage);
        font-size: 0.9rem;
        line-height: 1.6;
        margin-bottom: 2rem;
    }
</style>
