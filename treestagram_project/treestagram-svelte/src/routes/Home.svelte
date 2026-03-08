<script>
  import { onMount } from "svelte";
  import { user, apiLogout } from "../lib/api.js";
  import { theme, toggleTheme, cycleTheme } from "../theme.js";
  import LeftNav from "../components/LeftNav.svelte";
  import BackgroundRings from "../components/BackgroundRings.svelte";

  export let navigate;

  let mounted = false;
  onMount(() => setTimeout(() => (mounted = true), 50));

  async function logout() {
    await apiLogout();
    user.set(null);
    navigate("/login");
  }

  const roleColors = {
    standard: {
      bg: "var(--t-role-standard-bg)",
      text: "var(--t-role-standard-text)",
      label: "🌱 Standard",
    },
    credible: {
      bg: "var(--t-role-credible-bg)",
      text: "var(--t-role-credible-text)",
      label: "⭐ Credible",
    },
    caretaker: {
      bg: "var(--t-role-caretaker-bg)",
      text: "var(--t-role-caretaker-text)",
      label: "🌳 Caretaker",
    },
    admin: {
      bg: "var(--t-role-admin-bg)",
      text: "var(--t-role-admin-text)",
      label: "👑 Admin",
    },
  };

  $: role = roleColors[$user?.role] || roleColors.standard;

  const placeholderPosts = [
    {
      tree: "London Planetree #4821",
      borough: "Brooklyn",
      health: "Good",
      img: "🌳",
      likes: 24,
      comment: "Looking healthy after the rain!",
    },
    {
      tree: "Ginkgo #2047",
      borough: "Manhattan",
      health: "Fair",
      img: "🍂",
      likes: 11,
      comment: "Some leaf discoloration noted.",
    },
    {
      tree: "Red Oak #7732",
      borough: "Queens",
      health: "Good",
      img: "🌲",
      likes: 38,
      comment: "Beautiful canopy this season!",
    },
  ];

  $: isDark = $theme === "dark";
</script>

<div class="page" class:mounted>
  <BackgroundRings />
  <!-- Left Nav Sidebar -->
  <LeftNav {navigate} activePage="home" />

  <div class="layout">
    <!-- Feed -->
    <main class="feed">
      <!-- Create post -->
      <div class="create-post">
        <div class="create-avatar">
          {#if $user?.profile_picture}
            <img src={$user.profile_picture} alt="Me" class="avatar-img-sm" />
          {:else}
            🧑‍🌾
          {/if}
        </div>
        <div class="create-input">
          <input
            type="text"
            placeholder="Share an observation about a tree…"
            readonly
          />
        </div>
        <button class="create-btn">📸 Post</button>
      </div>

      <!-- Post cards -->
      <div class="posts">
        {#each placeholderPosts as post, i}
          <div class="post-card" style="animation-delay:{i * 0.1}s">
            <div class="post-header">
              <span class="post-tree-icon">{post.img}</span>
              <div>
                <div class="post-tree-name">{post.tree}</div>
                <div class="post-meta">
                  📍 {post.borough} ·
                  <span class="health health-{post.health.toLowerCase()}"
                    >{post.health}</span
                  >
                </div>
              </div>
              <button class="follow-btn">+ Follow</button>
            </div>
            <div class="post-body">
              <p>{post.comment}</p>
            </div>
            <div class="post-photo-placeholder">
              <span style="font-size:3rem">{post.img}</span>
              <span class="photo-hint">Photo coming soon</span>
            </div>
            <div class="post-actions">
              <button class="action-btn">❤️ {post.likes}</button>
              <button class="action-btn">💬 Comment</button>
              <button class="action-btn">🌿 Rate health</button>
            </div>
          </div>
        {/each}
      </div>

      <div class="feed-hint">🌳 Follow trees to personalize your feed</div>
    </main>
  </div>
</div>

<style>
  /* ─── Page Shell ─────────────────────────────────────────────────── */
  .page {
    min-height: 100vh;
    background: #faf9f6;
    font-family: var(--t-font-body);
    color: #4a4a4a;
    position: relative;
    z-index: 0;
    overflow: hidden;
    padding-left: 60px;
  }
  /* ─── Layout Grid ────────────────────────────────────────────────── */
  .layout {
    max-width: none;
    margin: 0 auto;
    display: grid;
    grid-template-columns: 1fr;
    gap: 1.5rem;
    padding: 1.5rem;
    opacity: 0;
    transform: translateY(16px);
    transition:
      opacity var(--t-transition-slow) 0.1s,
      transform var(--t-transition-slow) 0.1s;
  }
  .page.mounted .layout {
    opacity: 1;
    transform: translateY(0);
  }

  /* ─── Sidebar ────────────────────────────────────────────────────── */
  .sidebar {
    display: flex;
    flex-direction: column;
    gap: 1rem;
  }

  .profile-card {
    background: var(--t-bg-elevated);
    border: 1px solid var(--t-border);
    border-radius: var(--t-radius-lg);
    box-shadow: var(--t-shadow-card);
    padding: 1.4rem;
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 0.75rem;
  }
  .avatar {
    position: relative;
    width: 70px;
    height: 70px;
    display: flex;
    align-items: center;
    justify-content: center;
  }
  .avatar-emoji {
    font-size: 2.6rem;
    position: relative;
    z-index: 2;
  }
  .avatar-ring {
    position: absolute;
    inset: -4px;
    border-radius: 50%;
    border: 2px solid var(--t-brand-muted);
    animation: ringPulse 3s ease-out infinite;
  }
  @keyframes ringPulse {
    0% {
      transform: scale(1);
      opacity: 0.8;
    }
    100% {
      transform: scale(1.4);
      opacity: 0;
    }
  }
  .profile-info {
    text-align: center;
  }
  .profile-name {
    font-size: 1rem;
    font-weight: 700;
    color: var(--t-text-heading);
  }
  .profile-email {
    font-size: 0.75rem;
    color: var(--t-text-faint);
    margin: 2px 0 8px;
  }
  .role-badge {
    display: inline-block;
    padding: 3px 10px;
    border-radius: var(--t-radius-pill);
    font-size: 0.72rem;
    font-weight: 700;
  }

  .stats-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 6px;
    width: 100%;
    margin-top: 4px;
  }
  .stat {
    background: var(--t-bg-hover);
    border-radius: var(--t-radius-md);
    padding: 8px 4px;
    text-align: center;
  }
  .stat-val {
    display: block;
    font-size: 0.95rem;
    font-weight: 700;
    color: var(--t-text-brand);
  }
  .stat-lbl {
    font-size: 0.65rem;
    color: var(--t-text-faint);
  }
  .borough-tag {
    font-size: 0.78rem;
    color: var(--t-text-muted);
    margin-top: 2px;
  }

  .quick-links {
    display: flex;
    flex-direction: column;
    gap: 4px;
  }
  .quick-btn {
    background: none;
    border: none;
    border-radius: var(--t-radius-md);
    padding: 10px 14px;
    color: var(--t-text-muted);
    font-size: 0.88rem;
    font-family: var(--t-font-body);
    cursor: pointer;
    text-align: left;
    transition:
      background var(--t-transition),
      color var(--t-transition);
  }
  .quick-btn:hover,
  .quick-btn.active {
    background: var(--t-bg-hover);
    color: var(--t-text-brand);
  }

  /* ─── Feed ───────────────────────────────────────────────────────── */
  .feed {
    display: flex;
    flex-direction: column;
    width: 40%;
    margin: 0 auto;
    gap: 1rem;
  }

  /* ─── Create Post ────────────────────────────────────────────────── */
  .create-post {
    background: #cdd9af; /* Sage Mist */
    border: 1px solid rgba(164, 74, 63, 0.15);
    border-radius: var(--t-radius-lg);
    padding: 14px 16px;
    display: flex;
    align-items: center;
    gap: 10px;
    box-shadow: 0 4px 20px rgba(138, 154, 91, 0.1);
  }
  .create-avatar {
    width: 40px;
    height: 40px;
    border-radius: 50%;
    background: #36454f; /* Charcoal Gray */
    color: #faf9f6; /* Contrasting text */
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.4rem;
    flex-shrink: 0;
    overflow: hidden;
  }
  .avatar-img-sm {
    width: 100%;
    height: 100%;
    object-fit: cover;
  }
  .create-input {
    flex: 1;
  }
  .create-input input {
    width: 100%;
    background: #faf9f6;
    border: 1px solid #36454f;
    border-radius: var(--t-radius-pill);
    padding: 9px 16px;
    color: #2b2b2b;
    font-size: 0.88rem;
    font-family: var(--t-font-body);
    cursor: pointer;
    outline: none;
  }
  .create-btn {
    background: #36454f; /* Charcoal Gray */
    color: #faf9f6; /* Contrasting text */
    border: 1px solid rgba(138, 154, 91, 0.2);
    border-radius: var(--t-radius-pill);
    padding: 8px 16px;
    color: #8a9a5b; /* Sage text */
    font-size: 0.84rem;
    font-weight: 600;
    font-family: var(--t-font-body);
    cursor: pointer;
    white-space: nowrap;
    transition: background var(--t-transition);
  }
  .create-btn:hover {
    background: var(--t-bg-active);
  }

  /* ─── Post Cards ─────────────────────────────────────────────────── */
  .posts {
    display: flex;
    flex-direction: column;
    gap: 0.9rem;
  }

  .post-card {
    background: #cdd9af; /* Sage Mist */
    border: 1px solid rgba(164, 74, 63, 0.15);
    border-radius: var(--t-radius-lg);
    box-shadow: 0 8px 32px rgba(138, 154, 91, 0.08);
    overflow: hidden;
    animation: fadeUp 0.4s both;
  }
  @keyframes fadeUp {
    from {
      opacity: 0;
      transform: translateY(12px);
    }
    to {
      opacity: 1;
      transform: translateY(0);
    }
  }

  .post-header {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 14px 16px 10px;
  }
  .post-tree-icon {
    font-size: 2rem;
  }
  .post-tree-name {
    font-size: 0.92rem;
    font-weight: 600;
    color: #a44a3f; /* Redwood Rust titles */
  }
  .post-meta {
    font-size: 0.76rem;
    color: rgba(43, 43, 43, 0.7); /* Muted dark stone for meta */
    margin-top: 1px;
  }

  .health {
    font-weight: 600;
  }
  .health-good {
    color: var(--t-status-good);
  }
  .health-fair {
    color: var(--t-status-fair);
  }
  .health-poor {
    color: var(--t-status-poor);
  }

  .follow-btn {
    margin-left: auto;
    background: #36454f; /* Charcoal Gray */
    color: #faf9f6; /* Contrasting text */
    border: none;
    border-radius: var(--t-radius-pill);
    padding: 5px 13px;
    color: #8a9a5b;
    font-size: 0.78rem;
    font-weight: 600;
    font-family: var(--t-font-body);
    cursor: pointer;
    transition: background var(--t-transition);
  }
  .follow-btn:hover {
    background: var(--t-brand-dim);
  }

  .post-body {
    padding: 0 16px 10px;
    font-size: 0.88rem;
    color: #2b2b2b; /* Deep charcoal for legibility */
  }

  .post-photo-placeholder {
    background: var(--t-bg-photo);
    height: 160px;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    border-top: 1px solid var(--t-border-soft);
    border-bottom: 1px solid var(--t-border-soft);
    gap: 8px;
  }
  .photo-hint {
    font-size: 0.78rem;
    color: var(--t-text-faint);
  }

  .post-actions {
    display: flex;
    gap: 4px;
    padding: 10px 12px;
  }
  .action-btn {
    background: none;
    border: none;
    border-radius: var(--t-radius-sm);
    padding: 7px 12px;
    color: rgba(43, 43, 43, 0.6);
    font-size: 0.8rem;
    font-family: var(--t-font-body);
    cursor: pointer;
    transition:
      background var(--t-transition),
      color var(--t-transition);
  }
  .action-btn:hover {
    background: var(--t-bg-hover);
    color: var(--t-text-brand);
  }

  .feed-hint {
    text-align: center;
    font-size: 0.82rem;
    color: #a44a3f; /* Redwood Rust hint */
    padding: 0.5rem 0 1rem;
    opacity: 0.8;
  }
</style>
