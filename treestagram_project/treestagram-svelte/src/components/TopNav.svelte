<script>
    export let navigate;
    export let activePage = "feed";
</script>

<nav class="topnav">
    <div
        class="logo"
        on:click={() => navigate("/")}
        on:keydown={(e) => e.key === "Enter" && navigate("/")}
        role="button"
        tabindex="0"
    >
        Tree<span>stagram</span>
    </div>
    <div class="nav-links">
        <button
            class:active={activePage === "feed"}
            on:click={() => navigate("/home")}
        >
            <svg
                fill="none"
                stroke="currentColor"
                stroke-width="2"
                viewBox="0 0 24 24"
                ><path
                    d="M3 9l9-7 9 7v11a2 2 0 01-2 2H5a2 2 0 01-2-2z"
                /><polyline points="9 22 9 12 15 12 15 22" /></svg
            > Feed
        </button>
        <button
            class:active={activePage === "explore"}
            on:click={() => navigate("/dashboard")}
        >
            <svg
                fill="none"
                stroke="currentColor"
                stroke-width="2"
                viewBox="0 0 24 24"
                ><circle cx="12" cy="12" r="10" /><line
                    x1="12"
                    y1="8"
                    x2="12"
                    y2="12"
                /><line x1="12" y1="16" x2="12.01" y2="16" /></svg
            > Explore
        </button>
        <button
            class:active={activePage === "chat"}
            on:click={() => navigate("/chat")}
        >
            <svg
                fill="none"
                stroke="currentColor"
                stroke-width="2"
                viewBox="0 0 24 24"
                ><path
                    d="M21 15a2 2 0 01-2 2H7l-4 4V5a2 2 0 012-2h14a2 2 0 012 2z"
                /></svg
            > Chat
        </button>
    </div>
    <div class="nav-right">
        <div
            class="nav-avatar"
            on:click={() => navigate("/profile")}
            on:keydown={(e) => e.key === "Enter" && navigate("/profile")}
            role="button"
            tabindex="0"
        >
            🌿
        </div>
    </div>
</nav>

<style>
    .topnav {
        position: sticky;
        top: 0;
        z-index: 100;
        background: #2c1810;
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 0 2rem;
        height: 60px;
        box-shadow: 0 2px 20px rgba(0, 0, 0, 0.3);
    }
    .logo {
        font-family: "Playfair Display", serif;
        font-size: 1.4rem;
        font-style: italic;
        color: #8fbc8f;
        letter-spacing: 0.02em;
        cursor: pointer;
    }
    .logo span {
        color: #d4a853;
        font-style: normal;
    }
    .nav-links {
        display: flex;
        gap: 0.25rem;
    }
    .nav-links button {
        background: none;
        border: none;
        color: #c5d5c5;
        font-family: "DM Sans", sans-serif;
        font-size: 0.85rem;
        padding: 0.5rem 0.9rem;
        border-radius: 20px;
        cursor: pointer;
        transition: all 0.2s;
        display: flex;
        align-items: center;
        gap: 0.4rem;
    }
    .nav-links button:hover,
    .nav-links button.active {
        background: #3d5a3e;
        color: white;
    }
    .nav-links button svg {
        width: 16px;
        height: 16px;
    }
    .nav-right {
        display: flex;
        align-items: center;
        gap: 1rem;
    }
    .nav-avatar {
        width: 34px;
        height: 34px;
        border-radius: 50%;
        background: #6b8f71;
        border: 2px solid #8fbc8f;
        cursor: pointer;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 0.8rem;
        color: white;
        font-weight: 600;
        transition: transform 0.2s;
    }
    .nav-avatar:hover {
        transform: scale(1.1);
    }
</style>
