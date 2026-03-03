<script>
    import TopNav from "../components/TopNav.svelte";
    import { user } from "../lib/api.js";
    export let navigate;
</script>

<div class="page">
    <TopNav {navigate} activePage="profile" />

    <div class="profile-hero">
        <div class="profile-cover">
            <div class="profile-cover-text">Treestagram Treestagram</div>
            🌳🌿🍃🌲🌳🌿🍃
        </div>
        <div class="profile-info-bar">
            <div class="profile-pic">🌿</div>
            <div class="profile-text">
                <h1>
                    {$user?.first_name || "Your"}
                    {$user?.last_name || "Name"}
                </h1>
                <div class="handle">@{$user?.username || "greenleaf_nyc"}</div>
                <div class="profile-chips">
                    <span class="chip chip-health-good">✦ Credible User</span>
                    <span class="chip chip-borough"
                        >📍 {$user?.borough || "Manhattan"}</span
                    >
                </div>
            </div>
            <div class="profile-actions">
                <button class="btn-edit-profile">Edit Profile</button>
                <button class="btn-edit-profile">⚙️</button>
            </div>
        </div>
        <div class="profile-stats-tabs">
            <div class="p-stat">
                <span class="n">47</span><span class="l">Posts</span>
            </div>
            <div class="p-stat">
                <span class="n">4</span><span class="l">Trees Followed</span>
            </div>
            <div class="p-stat">
                <span class="n">1,280</span><span class="l">Likes Received</span
                >
            </div>
            <div class="p-stat">
                <span class="n">🌱</span><span class="l">28 days active</span>
            </div>
            <div class="profile-tab-links">
                <button class="profile-tab active">Posts</button>
                <button class="profile-tab">Activity</button>
                <button class="profile-tab">About</button>
            </div>
        </div>
    </div>

    <div class="profile-body">
        <div>
            <div class="profile-grid">
                {#each [{ emoji: "🌳", likes: 342, comments: 28 }, { emoji: "🌿", likes: 187, comments: 14 }, { emoji: "🍂", likes: 95, comments: 6 }, { emoji: "🌲", likes: 220, comments: 31 }, { emoji: "🌸", likes: 143, comments: 18 }, { emoji: "🍀", likes: 293, comments: 22 }] as post, i}
                    <div class="profile-post n{i}">
                        {post.emoji}
                        <div class="post-hover">
                            ❤️ {post.likes} &nbsp; 💬 {post.comments}
                        </div>
                    </div>
                {/each}
            </div>
            <div class="load-more">
                <button class="btn-load-more">Load More Posts</button>
            </div>
        </div>

        <aside>
            <div class="profile-right-card">
                <h3>About Me</h3>
                <p class="about-text">
                    Nature lover & amateur botanist. Documenting NYC's urban
                    forest one tree at a time 🌿 Working toward Credible User →
                    Caretaker status!
                </p>
                <div class="joined-date">📅 Joined January 2025</div>
            </div>

            <div class="profile-right-card">
                <h3>Trees I Follow</h3>
                {#each [{ emoji: "🌳", name: "Elm #00482", loc: "Central Park · Good", health: "good" }, { emoji: "🌿", name: "Ginkgo #10293", loc: "Brooklyn · Fair", health: "fair" }, { emoji: "🍁", name: "Maple #03312", loc: "Prospect Park · Good", health: "good" }, { emoji: "🌲", name: "Oak #55721", loc: "Queens · Poor", health: "poor" }] as tree}
                    <div
                        class="followed-tree"
                        on:click={() => navigate("/dashboard")}
                        on:keydown={(e) =>
                            e.key === "Enter" && navigate("/dashboard")}
                        role="button"
                        tabindex="0"
                    >
                        <div class="ft-icon">{tree.emoji}</div>
                        <div class="ft-info">
                            <strong>{tree.name}</strong>
                            <small>{tree.loc}</small>
                        </div>
                        <span class="health-badge health-{tree.health}"
                            >{tree.health.charAt(0).toUpperCase() +
                                tree.health.slice(1)}</span
                        >
                    </div>
                {/each}
            </div>

            <div class="profile-right-card">
                <h3>Progress to Credible User</h3>
                <div class="progress-item">
                    <div class="progress-header">
                        <span class="progress-label">Posts (47/30)</span>
                        <span class="progress-met">✓ Met</span>
                    </div>
                    <div class="progress-track">
                        <div class="progress-fill full"></div>
                    </div>
                </div>
                <div class="progress-item">
                    <div class="progress-header">
                        <span class="progress-label">Likes (1280/100)</span>
                        <span class="progress-met">✓ Met</span>
                    </div>
                    <div class="progress-track">
                        <div class="progress-fill full"></div>
                    </div>
                </div>
                <div class="credible-banner">
                    🎉 You're a Credible User! Apply to be a Caretaker now.
                </div>
            </div>
        </aside>
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
        --mist: #e8ede8;
        --sun: #d4a853;
        --ink: #1a1108;
        --shadow: rgba(44, 24, 16, 0.12);
    }

    .page {
        background: var(--mist);
        min-height: 100vh;
    }

    .profile-hero {
        background: var(--bark);
        padding: 0 3rem;
        position: relative;
        overflow: hidden;
    }
    .profile-hero::before {
        content: "";
        position: absolute;
        inset: 0;
        background: radial-gradient(
            ellipse at 30% 60%,
            rgba(61, 90, 62, 0.5) 0%,
            transparent 70%
        );
    }
    .profile-cover {
        height: 180px;
        position: relative;
        background: linear-gradient(
            135deg,
            #1a3d1a 0%,
            #2d6b2d 50%,
            #1a3d1a 100%
        );
        margin: 0 -3rem;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 4rem;
        letter-spacing: 1rem;
        opacity: 0.4;
        overflow: hidden;
    }
    .profile-cover-text {
        font-family: "Playfair Display", serif;
        font-size: 6rem;
        opacity: 0.15;
        color: var(--leaf);
        position: absolute;
        font-style: italic;
        letter-spacing: 0.2em;
        white-space: nowrap;
    }
    .profile-info-bar {
        position: relative;
        z-index: 1;
        display: flex;
        align-items: flex-end;
        gap: 1.5rem;
        padding-bottom: 1.5rem;
        margin-top: -40px;
    }
    .profile-pic {
        width: 90px;
        height: 90px;
        border-radius: 50%;
        background: linear-gradient(135deg, var(--moss), var(--sage));
        border: 4px solid var(--bark);
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 2.5rem;
        flex-shrink: 0;
    }
    .profile-text {
        flex: 1;
    }
    .profile-text h1 {
        font-family: "Playfair Display", serif;
        font-size: 1.8rem;
        color: white;
        line-height: 1.2;
    }
    .handle {
        color: var(--sage);
        font-size: 0.9rem;
    }
    .profile-chips {
        display: flex;
        gap: 0.4rem;
        margin-top: 0.4rem;
        flex-wrap: wrap;
    }
    .chip {
        padding: 0.35rem 0.8rem;
        border-radius: 20px;
        font-size: 0.78rem;
        font-weight: 500;
        display: inline-flex;
        align-items: center;
        gap: 0.3rem;
    }
    .chip-health-good {
        background: rgba(143, 188, 143, 0.25);
        color: var(--leaf);
        border: 1px solid rgba(143, 188, 143, 0.4);
    }
    .chip-borough {
        background: rgba(255, 255, 255, 0.1);
        color: var(--canopy);
        border: 1px solid rgba(255, 255, 255, 0.2);
    }
    .profile-actions {
        display: flex;
        gap: 0.6rem;
        align-items: center;
    }
    .btn-edit-profile {
        background: none;
        border: 1.5px solid rgba(255, 255, 255, 0.3);
        color: var(--canopy);
        padding: 0.5rem 1.2rem;
        border-radius: 20px;
        font-family: "DM Sans", sans-serif;
        font-size: 0.85rem;
        cursor: pointer;
        transition: all 0.2s;
    }
    .btn-edit-profile:hover {
        border-color: var(--canopy);
        color: white;
    }

    .profile-stats-tabs {
        position: relative;
        z-index: 1;
        display: flex;
        align-items: center;
        gap: 3rem;
        border-top: 1px solid rgba(255, 255, 255, 0.08);
        padding-top: 1rem;
    }
    .p-stat {
        text-align: center;
    }
    .p-stat .n {
        font-family: "Playfair Display", serif;
        font-size: 1.6rem;
        color: var(--leaf);
        display: block;
    }
    .p-stat .l {
        font-size: 0.75rem;
        color: var(--canopy);
    }
    .profile-tab-links {
        display: flex;
        gap: 0;
        margin-left: auto;
    }
    .profile-tab {
        background: none;
        border: none;
        color: var(--canopy);
        padding: 0.6rem 1.2rem;
        cursor: pointer;
        font-family: "DM Sans", sans-serif;
        font-size: 0.85rem;
        border-bottom: 2px solid transparent;
        transition: all 0.2s;
    }
    .profile-tab:hover {
        color: var(--canopy);
    }
    .profile-tab.active {
        color: var(--leaf);
        border-bottom-color: var(--leaf);
    }

    .profile-body {
        max-width: 1000px;
        margin: 0 auto;
        padding: 2rem 1.5rem;
        display: grid;
        grid-template-columns: 1fr 260px;
        gap: 1.5rem;
    }
    .profile-grid {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 0.8rem;
    }
    .profile-post {
        aspect-ratio: 1;
        border-radius: 12px;
        background: linear-gradient(135deg, #1a3d1a, #3a7a30);
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 2.5rem;
        cursor: pointer;
        position: relative;
        overflow: hidden;
        transition: transform 0.2s;
    }
    .profile-post:hover {
        transform: scale(0.97);
    }
    .profile-post.n1 {
        background: linear-gradient(135deg, #2d5a1a, #5a8c30);
    }
    .profile-post.n2 {
        background: linear-gradient(135deg, #0d2b0d, #1e5218);
    }
    .profile-post.n3 {
        background: linear-gradient(135deg, #3d5a1a, #6a8c30);
    }
    .profile-post.n4 {
        background: linear-gradient(135deg, #1a4a2d, #3a8c50);
    }
    .profile-post.n5 {
        background: linear-gradient(135deg, #2d1a0d, #5a3a20);
    }
    .post-hover {
        position: absolute;
        inset: 0;
        background: rgba(0, 0, 0, 0.5);
        opacity: 0;
        transition: opacity 0.2s;
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 1rem;
        color: white;
        font-size: 0.85rem;
    }
    .profile-post:hover .post-hover {
        opacity: 1;
    }

    .load-more {
        text-align: center;
        margin-top: 1.5rem;
    }
    .btn-load-more {
        background: none;
        border: 1.5px solid var(--canopy);
        color: var(--sage);
        padding: 0.6rem 1.5rem;
        border-radius: 20px;
        cursor: pointer;
        font-family: "DM Sans", sans-serif;
        font-size: 0.88rem;
    }

    .profile-right-card {
        background: white;
        border-radius: 16px;
        padding: 1.4rem;
        box-shadow: 0 2px 12px var(--shadow);
        margin-bottom: 1rem;
    }
    .profile-right-card h3 {
        font-size: 0.75rem;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        color: var(--sage);
        margin-bottom: 1rem;
    }
    .about-text {
        font-size: 0.85rem;
        color: var(--sage);
        line-height: 1.6;
    }
    .joined-date {
        margin-top: 0.8rem;
        font-size: 0.8rem;
        color: var(--sage);
    }

    .followed-tree {
        display: flex;
        align-items: center;
        gap: 0.7rem;
        padding: 0.5rem 0;
        border-bottom: 1px solid var(--mist);
        cursor: pointer;
    }
    .followed-tree:last-child {
        border: none;
    }
    .ft-icon {
        width: 32px;
        height: 32px;
        border-radius: 8px;
        background: linear-gradient(135deg, var(--moss), var(--sage));
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 0.9rem;
        flex-shrink: 0;
    }
    .ft-info {
        flex: 1;
        min-width: 0;
    }
    .ft-info strong {
        display: block;
        font-size: 0.82rem;
        color: var(--ink);
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }
    .ft-info small {
        font-size: 0.72rem;
        color: var(--sage);
    }
    .health-badge {
        font-size: 0.65rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        padding: 0.15rem 0.4rem;
        border-radius: 4px;
    }
    .health-good {
        background: #d4edda;
        color: #1e7e34;
    }
    .health-fair {
        background: #fff3cd;
        color: #856404;
    }
    .health-poor {
        background: #f8d7da;
        color: #721c24;
    }

    .progress-item {
        margin-bottom: 0.8rem;
    }
    .progress-header {
        display: flex;
        justify-content: space-between;
        font-size: 0.8rem;
        margin-bottom: 0.3rem;
    }
    .progress-label {
        color: var(--sage);
    }
    .progress-met {
        color: var(--moss);
        font-weight: 600;
    }
    .progress-track {
        height: 6px;
        background: var(--canopy);
        border-radius: 3px;
        overflow: hidden;
    }
    .progress-fill {
        height: 100%;
        border-radius: 3px;
        background: var(--sage);
    }
    .progress-fill.full {
        width: 100%;
    }
    .credible-banner {
        margin-top: 0.8rem;
        background: rgba(61, 90, 62, 0.1);
        border: 1px solid rgba(61, 90, 62, 0.2);
        border-radius: 8px;
        padding: 0.6rem;
        font-size: 0.82rem;
        color: var(--moss);
        text-align: center;
    }
</style>
