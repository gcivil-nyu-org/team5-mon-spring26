<script>
    import { onMount, onDestroy } from "svelte";
    import { theme, cycleTheme } from "../theme.js";
    import {
        user,
        apiLogout,
        apiFetchNotifications,
        apiFetchUnreadCount,
        apiMarkNotificationsRead,
        apiMarkAllNotificationsRead,
    } from "../lib/api.js";

    export let navigate;
    export let activePage = "home"; // "home", "dashboard", "chat", "profile", "settings"

    // ── Notification state ──
    let showNotifPanel = false;
    let notifications = [];
    let unreadCount = 0;
    let loadingNotifs = false;
    let pollTimer = null;

    async function logout() {
        await apiLogout();
        user.set(null);
        navigate("/login");
    }

    // ── Fetch unread count (lightweight, for polling) ──
    async function fetchUnreadCount() {
        try {
            const res = await apiFetchUnreadCount();
            if (res.success) unreadCount = res.unread_count;
        } catch {}
    }

    // ── Fetch full notification list ──
    async function fetchNotifications() {
        loadingNotifs = true;
        try {
            const res = await apiFetchNotifications();
            if (res.success) {
                notifications = res.notifications;
                unreadCount = res.unread_count;
            }
        } catch {}
        loadingNotifs = false;
    }

    // ── Smart poll: fetch full list if panel is open, otherwise just count ──
    async function poll() {
        if (showNotifPanel) {
            await fetchNotifications();
        } else {
            await fetchUnreadCount();
        }
    }

    // ── Toggle the panel ──
    function toggleNotifPanel() {
        showNotifPanel = !showNotifPanel;
        if (showNotifPanel) {
            fetchNotifications();
        }
    }

    // ── Close panel when clicking outside ──
    function handleClickOutside(e) {
        if (showNotifPanel) {
            const panel = document.querySelector(".notif-panel-wrap");
            if (panel && !panel.contains(e.target)) {
                showNotifPanel = false;
            }
        }
    }

    // ── Mark a single notification as read ──
    async function markRead(notif) {
        if (notif.is_read) return;
        notif.is_read = true;
        notifications = notifications; // trigger reactivity
        unreadCount = Math.max(0, unreadCount - 1);
        await apiMarkNotificationsRead([notif.id]);
    }

    // ── Mark all as read ──
    async function markAllRead() {
        notifications = notifications.map((n) => ({ ...n, is_read: true }));
        unreadCount = 0;
        await apiMarkAllNotificationsRead();
    }

    // ── Human-readable relative time ──
    function timeAgo(isoStr) {
        const diff = (Date.now() - new Date(isoStr).getTime()) / 1000;
        if (diff < 60) return "just now";
        if (diff < 3600) return `${Math.floor(diff / 60)}m ago`;
        if (diff < 86400) return `${Math.floor(diff / 3600)}h ago`;
        if (diff < 604800) return `${Math.floor(diff / 86400)}d ago`;
        return new Date(isoStr).toLocaleDateString();
    }

    // ── Notification type → emoji ──
    function typeIcon(type) {
        const icons = {
            like: "❤️",
            comment: "💬",
            tag: "🏷️",
            promotion: "⭐",
        };
        return icons[type] || "🔔";
    }

    onMount(() => {
        // Fetch immediately on mount
        fetchUnreadCount();
        // Poll every 10 seconds — if panel is open, refreshes full list;
        // otherwise just the lightweight unread count
        pollTimer = setInterval(poll, 10000);
        document.addEventListener("click", handleClickOutside, true);
    });

    onDestroy(() => {
        if (pollTimer) clearInterval(pollTimer);
        document.removeEventListener("click", handleClickOutside, true);
    });
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
            class="left-nav-btn {activePage === 'search' ? 'active' : ''}"
            on:click={() => navigate("/search")}
        >
            <span class="left-nav-icon">🔎</span>
            <span class="left-nav-label">Search</span>
        </button>

        <button
            class="left-nav-btn {activePage === 'map' ? 'active' : ''}"
            on:click={() => navigate("/map")}
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
        <button class="left-nav-btn logout-btn" on:click={logout}>
            <span class="left-nav-icon">↩</span>
            <span class="left-nav-label">Log Out</span>
        </button>
    </div>
</nav>

<!-- Floating Notification Bell + Dropdown Panel -->
<div class="notif-panel-wrap">
    <button class="notif-orb" on:click={toggleNotifPanel}>
        <span class="notif-glow"></span>
        <span class="notif-bell">🔔</span>
        {#if unreadCount > 0}
            <span class="notif-dot">{unreadCount > 9 ? "9+" : unreadCount}</span>
        {/if}
        <span class="notif-tooltip">Notifications</span>
    </button>

    {#if showNotifPanel}
        <!-- svelte-ignore a11y-click-events-have-key-events a11y-no-static-element-interactions -->
        <div class="notif-panel" on:click|stopPropagation>
            <div class="notif-panel-header">
                <h3>Notifications</h3>
                {#if unreadCount > 0}
                    <button class="mark-all-btn" on:click={markAllRead}>
                        Mark all read
                    </button>
                {/if}
            </div>

            <div class="notif-panel-body">
                {#if loadingNotifs}
                    <div class="notif-empty">
                        <span class="notif-loading-spinner"></span>
                        Loading...
                    </div>
                {:else if notifications.length === 0}
                    <div class="notif-empty">
                        <span class="notif-empty-icon">🌿</span>
                        <p>No notifications yet</p>
                        <small>When someone likes, comments on, or tags you in a post, you'll see it here.</small>
                    </div>
                {:else}
                    {#each notifications as notif (notif.id)}
                        <button
                            class="notif-item {notif.is_read ? '' : 'unread'}"
                            on:click={() => markRead(notif)}
                        >
                            <span class="notif-item-icon">{typeIcon(notif.notif_type)}</span>
                            <div class="notif-item-content">
                                <p class="notif-item-msg">{notif.message}</p>
                                <small class="notif-item-time">{timeAgo(notif.created_at)}</small>
                            </div>
                            {#if !notif.is_read}
                                <span class="notif-unread-indicator"></span>
                            {/if}
                        </button>
                    {/each}
                {/if}
            </div>
        </div>
    {/if}
</div>

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
    .left-nav-btn:hover .left-nav-label {
        color: #dce8d4;
    }
    .left-nav-btn.active .left-nav-label {
        font-weight: 700;
        color: #dce8d4;
    }
    .left-nav-icon {
        font-size: 1.2rem;
        width: 28px;
        text-align: center;
        flex-shrink: 0;
    }
    .left-nav-label {
        font-size: 0.9rem;
        color: #b5c9ad;
        font-family: var(--t-font-body, "DM Sans", sans-serif);
        font-weight: 500;
        text-shadow: 0 1px 2px rgba(0, 0, 0, 0.3);
        opacity: 0;
        transition:
            opacity 0.2s 0.05s,
            color 0.15s;
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
    .logout-btn .left-nav-icon {
        color: #cd3b3b;
        text-shadow: 0 1px 2px rgba(0, 0, 0, 0.3);
    }
    .logout-btn .left-nav-label {
        color: #cd3b3b;
        text-shadow: 0 1px 2px rgba(0, 0, 0, 0.3);
    }
    .logout-btn:hover .left-nav-icon {
        color: #e05252;
    }
    .logout-btn:hover .left-nav-label {
        color: #e05252;
    }

    /* ─── Notification Bell + Panel Wrapper ─────────────────────────── */
    .notif-panel-wrap {
        position: fixed;
        top: 18px;
        right: 22px;
        z-index: 300;
    }

    /* ─── Floating Notification Orb ─────────────────────────────────── */
    .notif-orb {
        width: 46px;
        height: 46px;
        border-radius: 50%;
        border: 1px solid rgba(143, 188, 143, 0.18);
        cursor: pointer;
        display: flex;
        align-items: center;
        justify-content: center;
        background: var(--t-bg-surface, #332015);
        backdrop-filter: blur(14px);
        -webkit-backdrop-filter: blur(14px);
        box-shadow:
            0 4px 20px rgba(0, 0, 0, 0.2),
            inset 0 1px 0 rgba(143, 188, 143, 0.06);
        transition:
            transform 0.25s cubic-bezier(0.4, 0, 0.2, 1),
            box-shadow 0.25s ease,
            border-color 0.25s ease;
        position: relative;
    }
    .notif-orb:hover {
        transform: scale(1.1);
        border-color: rgba(143, 188, 143, 0.35);
        box-shadow:
            0 6px 28px rgba(0, 0, 0, 0.22),
            0 0 12px rgba(143, 188, 143, 0.12),
            inset 0 1px 0 rgba(143, 188, 143, 0.1);
    }
    .notif-orb:active {
        transform: scale(0.95);
    }

    /* Ambient glow ring */
    .notif-glow {
        position: absolute;
        inset: -5px;
        border-radius: 50%;
        border: 1.5px solid rgba(143, 188, 143, 0.2);
        animation: orbPulse 3.5s ease-in-out infinite;
        pointer-events: none;
    }
    @keyframes orbPulse {
        0%, 100% {
            transform: scale(1);
            opacity: 0.5;
        }
        50% {
            transform: scale(1.22);
            opacity: 0;
        }
    }

    /* Bell icon */
    .notif-bell {
        font-size: 1.15rem;
        display: inline-block;
        transform-origin: 50% 8%;
        transition: transform 0.3s ease;
        position: relative;
        z-index: 2;
    }
    .notif-orb:hover .notif-bell {
        animation: bellSwing 0.65s ease-in-out;
    }
    @keyframes bellSwing {
        0%   { transform: rotate(0deg); }
        12%  { transform: rotate(14deg); }
        28%  { transform: rotate(-12deg); }
        44%  { transform: rotate(8deg); }
        60%  { transform: rotate(-5deg); }
        76%  { transform: rotate(2deg); }
        100% { transform: rotate(0deg); }
    }

    /* Badge count */
    .notif-dot {
        position: absolute;
        top: 2px;
        right: 0px;
        min-width: 18px;
        height: 18px;
        background: #e05252;
        border-radius: 10px;
        border: 2px solid var(--t-bg-surface, #332015);
        z-index: 3;
        font-size: 0.62rem;
        font-weight: 700;
        color: white;
        display: flex;
        align-items: center;
        justify-content: center;
        padding: 0 4px;
        font-family: "DM Sans", sans-serif;
        line-height: 1;
        box-shadow: 0 0 6px rgba(224, 82, 82, 0.45);
        animation: dotBreath 2.5s ease-in-out infinite;
    }
    @keyframes dotBreath {
        0%, 100% {
            box-shadow: 0 0 5px rgba(224, 82, 82, 0.4);
            transform: scale(1);
        }
        50% {
            box-shadow: 0 0 10px rgba(224, 82, 82, 0.55);
            transform: scale(1.08);
        }
    }

    /* Tooltip on hover */
    .notif-tooltip {
        position: absolute;
        right: calc(100% + 10px);
        top: 50%;
        transform: translateY(-50%) translateX(6px);
        background: var(--t-bg-surface, #332015);
        backdrop-filter: blur(10px);
        color: var(--t-text-body, #c5d5c5);
        font-family: var(--t-font-body, "DM Sans", sans-serif);
        font-size: 0.78rem;
        font-weight: 600;
        letter-spacing: 0.01em;
        padding: 6px 12px;
        border-radius: 8px;
        white-space: nowrap;
        pointer-events: none;
        opacity: 0;
        transition:
            opacity 0.2s 0.08s,
            transform 0.2s 0.08s;
        border: 1px solid rgba(143, 188, 143, 0.12);
        box-shadow: 0 2px 12px rgba(0, 0, 0, 0.18);
    }
    .notif-tooltip::after {
        content: "";
        position: absolute;
        top: 50%;
        right: -4px;
        transform: translateY(-50%) rotate(45deg);
        width: 8px;
        height: 8px;
        background: var(--t-bg-surface, #332015);
        border-right: 1px solid rgba(143, 188, 143, 0.12);
        border-bottom: 1px solid rgba(143, 188, 143, 0.12);
    }
    .notif-orb:hover .notif-tooltip {
        opacity: 1;
        transform: translateY(-50%) translateX(0);
    }

    /* ─── Notification Dropdown Panel ───────────────────────────────── */
    .notif-panel {
        position: absolute;
        top: calc(100% + 12px);
        right: 0;
        width: 380px;
        max-height: 520px;
        background: #faf9f6;
        border: 1px solid rgba(143, 188, 143, 0.2);
        border-radius: 16px;
        box-shadow:
            0 12px 48px rgba(0, 0, 0, 0.18),
            0 0 0 1px rgba(143, 188, 143, 0.06);
        display: flex;
        flex-direction: column;
        overflow: hidden;
        animation: panelSlideIn 0.25s cubic-bezier(0.22, 1, 0.36, 1);
    }
    @keyframes panelSlideIn {
        from {
            opacity: 0;
            transform: translateY(-8px) scale(0.97);
        }
        to {
            opacity: 1;
            transform: translateY(0) scale(1);
        }
    }

    .notif-panel-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 14px 18px 10px;
        border-bottom: 1px solid rgba(143, 188, 143, 0.12);
    }
    .notif-panel-header h3 {
        font-family: "Playfair Display", serif;
        font-size: 1.1rem;
        color: #2c1810;
        margin: 0;
    }
    .mark-all-btn {
        background: none;
        border: none;
        color: #3d5a3e;
        font-size: 0.78rem;
        font-weight: 600;
        cursor: pointer;
        padding: 4px 10px;
        border-radius: 6px;
        transition: background 0.15s;
        font-family: "DM Sans", sans-serif;
    }
    .mark-all-btn:hover {
        background: rgba(143, 188, 143, 0.12);
    }

    .notif-panel-body {
        overflow-y: auto;
        flex: 1;
        padding: 4px 0;
    }

    /* ── Individual notification item ── */
    .notif-item {
        display: flex;
        align-items: flex-start;
        gap: 12px;
        padding: 12px 18px;
        background: transparent;
        border: none;
        border-bottom: 1px solid rgba(143, 188, 143, 0.06);
        cursor: pointer;
        width: 100%;
        text-align: left;
        transition: background 0.15s;
        position: relative;
        font-family: "DM Sans", sans-serif;
    }
    .notif-item:hover {
        background: rgba(143, 188, 143, 0.06);
    }
    .notif-item.unread {
        background: rgba(143, 188, 143, 0.08);
    }
    .notif-item.unread:hover {
        background: rgba(143, 188, 143, 0.14);
    }

    .notif-item-icon {
        font-size: 1.3rem;
        flex-shrink: 0;
        margin-top: 2px;
    }
    .notif-item-content {
        flex: 1;
        min-width: 0;
    }
    .notif-item-msg {
        font-size: 0.85rem;
        color: #2c1810;
        line-height: 1.4;
        margin: 0;
        word-wrap: break-word;
    }
    .notif-item.unread .notif-item-msg {
        font-weight: 600;
    }
    .notif-item-time {
        font-size: 0.72rem;
        color: #6b8f71;
        margin-top: 2px;
        display: block;
    }

    .notif-unread-indicator {
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background: #3d5a3e;
        flex-shrink: 0;
        margin-top: 6px;
        box-shadow: 0 0 4px rgba(61, 90, 62, 0.4);
    }

    /* ── Empty state ── */
    .notif-empty {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        padding: 2.5rem 1.5rem;
        text-align: center;
        color: #6b8f71;
    }
    .notif-empty-icon {
        font-size: 2.5rem;
        margin-bottom: 0.8rem;
        opacity: 0.6;
    }
    .notif-empty p {
        font-size: 0.95rem;
        font-weight: 600;
        color: #2c1810;
        margin: 0 0 0.4rem;
    }
    .notif-empty small {
        font-size: 0.78rem;
        color: #6b8f71;
        line-height: 1.5;
    }
    .notif-loading-spinner {
        display: inline-block;
        width: 18px;
        height: 18px;
        border: 2px solid rgba(143, 188, 143, 0.3);
        border-top-color: #3d5a3e;
        border-radius: 50%;
        animation: spin 0.6s linear infinite;
        margin-right: 8px;
    }
    @keyframes spin {
        to { transform: rotate(360deg); }
    }
</style>
