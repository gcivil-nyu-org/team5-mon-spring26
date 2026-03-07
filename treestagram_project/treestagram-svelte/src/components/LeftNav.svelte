<script>
    import { theme, cycleTheme } from "../theme.js";
    import { user, apiLogout } from "../lib/api.js";

    export let navigate;
    export let activePage = "home"; // "home", "dashboard", "chat", "profile", "settings"

    async function logout() {
        await apiLogout();
        user.set(null);
        navigate("/login");
    }
</script>

<nav class="left-nav">
    <div class="left-nav-logo">
        <span class="left-nav-icon">🌳</span>
        <span class="logo-text"
            >Tree<span style="color:#d4a853;font-style:normal">stagram</span
            ></span
        >
    </div>
    <div class="left-nav-items">
        <button
            class="left-nav-btn {activePage === 'home' ? 'active' : ''}"
            on:click={() => navigate("/home")}
        >
            <span class="left-nav-icon">🏡</span>
            <span class="left-nav-label">Home</span>
        </button>
        <button
            class="left-nav-btn {activePage === 'dashboard' ? 'active' : ''}"
            on:click={() => navigate("/dashboard")}
        >
            <span class="left-nav-icon">🗺</span>
            <span class="left-nav-label">Explore Map</span>
        </button>
        <button
            class="left-nav-btn {activePage === 'chat' ? 'active' : ''}"
            on:click={() => navigate("/chat")}
        >
            <span class="left-nav-icon">💬</span>
            <span class="left-nav-label">Group Chats</span>
        </button>
        <button class="left-nav-btn">
            <span class="left-nav-icon">🔔</span>
            <span class="left-nav-label">Notifications</span>
        </button>
        <button
            class="left-nav-btn {activePage === 'profile' ? 'active' : ''}"
            on:click={() => navigate("/profile")}
        >
            <span class="left-nav-icon">👤</span>
            <span class="left-nav-label">Profile</span>
        </button>
        <button
            class="left-nav-btn {activePage === 'settings' ? 'active' : ''}"
            on:click={() => navigate("/settings")}
        >
            <span class="left-nav-icon">⚙️</span>
            <span class="left-nav-label">Settings</span>
        </button>
    </div>
    <div class="left-nav-bottom">
        <button class="left-nav-btn" on:click={cycleTheme}>
            <span class="left-nav-icon"
                >{$theme === "dark"
                    ? "☀️"
                    : $theme === "light"
                      ? "👾"
                      : "🌙"}</span
            >
            <span class="left-nav-label">Theme</span>
        </button>
        <button class="left-nav-btn logout-btn" on:click={logout}>
            <span class="left-nav-icon">↩</span>
            <span class="left-nav-label">Log Out</span>
        </button>
    </div>
</nav>

<style>
    /* ─── Left Nav (hover-expand) ────────────────────────────────────── */
    .left-nav {
        position: fixed;
        left: 0;
        top: 0;
        bottom: 0;
        width: 60px;
        background: var(--bark, #2c1810);
        backdrop-filter: blur(16px);
        border-right: 1px solid var(--t-border, rgba(143, 188, 143, 0.15));
        display: flex;
        flex-direction: column;
        padding: 12px 0;
        z-index: 200;
        overflow: hidden;
        transition: width 0.25s cubic-bezier(0.4, 0, 0.2, 1);
    }
    .left-nav::before {
        content: "";
        position: absolute;
        bottom: -150px;
        left: -150px;
        width: 600px;
        height: 600px;
        background: repeating-radial-gradient(
            circle at center,
            transparent,
            transparent 15px,
            rgba(143, 188, 143, 0.2) 16px,
            rgba(143, 188, 143, 0.2) 17px,
            transparent 18px
        );
        pointer-events: none;
        z-index: -1;
        opacity: 0.6;
    }
    .left-nav:hover {
        width: 200px;
    }

    .left-nav-logo {
        display: flex;
        align-items: center;
        gap: 12px;
        padding: 12px 16px 20px;
        white-space: nowrap;
        min-height: 48px;
    }
    .left-nav-logo .left-nav-icon {
        font-size: 1.4rem;
        flex-shrink: 0;
        width: 28px;
        text-align: center;
    }
    .logo-text {
        font-family: "Playfair Display", serif;
        font-size: 1.4rem;
        font-style: italic;
        color: #8fbc8f;
        letter-spacing: 0.02em;
        opacity: 0;
        transition: opacity 0.2s 0.05s;
    }
    .left-nav:hover .logo-text {
        opacity: 1;
    }
    .logo-text :global(.gold),
    .left-nav-logo :global(.gold) {
        color: #d4a853;
        font-style: normal;
    }

    .left-nav-items {
        display: flex;
        flex-direction: column;
        gap: 2px;
        flex: 1;
        padding: 0 8px;
    }

    .left-nav-btn {
        display: flex;
        align-items: center;
        gap: 14px;
        padding: 11px 8px;
        background: none;
        border: none;
        border-radius: 10px;
        cursor: pointer;
        white-space: nowrap;
        transition:
            background 0.15s,
            transform 0.1s;
        width: 100%;
        text-align: left;
    }
    .left-nav-btn:hover {
        background: rgba(143, 188, 143, 0.12);
        transform: scale(1.02);
    }
    .left-nav-btn.active {
        background: rgba(143, 188, 143, 0.18);
    }
    .left-nav-btn.active .left-nav-label {
        font-weight: 700;
    }
    .left-nav-icon {
        font-size: 1.2rem;
        width: 28px;
        text-align: center;
        flex-shrink: 0;
    }
    .left-nav-label {
        font-size: 0.88rem;
        color: var(--t-text-muted, #c5d5c5);
        font-family: "DM Sans", sans-serif;
        opacity: 0;
        transition: opacity 0.2s 0.05s;
    }
    .left-nav:hover .left-nav-label {
        opacity: 1;
    }

    .left-nav-bottom {
        display: flex;
        flex-direction: column;
        gap: 2px;
        padding: 8px 8px 4px;
        border-top: 1px solid rgba(143, 188, 143, 0.12);
        margin-top: auto;
    }
    .logout-btn:hover {
        background: rgba(220, 60, 60, 0.12) !important;
    }
    .logout-btn .left-nav-label {
        color: #e57373;
    }
</style>
