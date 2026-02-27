<script>
  import { onMount } from 'svelte'
  import { user, apiLogout } from '../lib/api.js'
  import { theme, toggleTheme, cycleTheme } from '../theme.js'

  export let navigate

  let mounted = false
  onMount(() => setTimeout(() => mounted = true, 50))

  async function logout() {
    await apiLogout()
    user.set(null)
    navigate('/login')
  }

  const roleColors = {
    standard:  { bg: 'var(--t-role-standard-bg)',  text: 'var(--t-role-standard-text)',  label: '🌱 Standard'  },
    credible:  { bg: 'var(--t-role-credible-bg)',  text: 'var(--t-role-credible-text)',  label: '⭐ Credible'  },
    caretaker: { bg: 'var(--t-role-caretaker-bg)', text: 'var(--t-role-caretaker-text)', label: '🌳 Caretaker' },
    admin:     { bg: 'var(--t-role-admin-bg)',      text: 'var(--t-role-admin-text)',      label: '👑 Admin'     },
  }

  $: role = roleColors[$user?.role] || roleColors.standard

  const placeholderPosts = [
    { tree: 'London Planetree #4821', borough: 'Brooklyn', health: 'Good', img: '🌳', likes: 24, comment: 'Looking healthy after the rain!' },
    { tree: 'Ginkgo #2047',           borough: 'Manhattan', health: 'Fair', img: '🍂', likes: 11, comment: 'Some leaf discoloration noted.' },
    { tree: 'Red Oak #7732',          borough: 'Queens',    health: 'Good', img: '🌲', likes: 38, comment: 'Beautiful canopy this season!' },
  ]

  $: isDark = $theme === 'dark'
</script>

<div class="page" class:mounted>
  <!-- Top nav -->
  <nav class="navbar">
    <div class="nav-brand">
      <span class="nav-tree">🌳</span>
      <span class="nav-title">Treestagram</span>
    </div>
    <div class="nav-actions">
      <button class="nav-btn" title="Search trees">🔍</button>
      <button class="nav-btn" title="Notifications">🔔</button>
      <!-- Theme toggle -->
      <!-- <button class="nav-btn theme-toggle" on:click={toggleTheme} title="Toggle theme">
        {isDark ? '☀️' : '🌙'}
      </button> -->
      <button class="nav-btn theme-toggle" on:click={cycleTheme}>
        {$theme === 'dark' ? '☀️' : $theme === 'light' ? '👾' : '🌙'}
      </button>
      <button class="nav-btn logout" on:click={logout} title="Logout">↩</button>
    </div>
  </nav>

  <div class="layout">
    <!-- Sidebar -->
    <aside class="sidebar">
      <div class="profile-card">
        <div class="avatar">
          <span class="avatar-emoji">🧑‍🌾</span>
          <div class="avatar-ring"></div>
        </div>
        <div class="profile-info">
          <div class="profile-name">{$user?.username || 'Treelover'}</div>
          <div class="profile-email">{$user?.email || ''}</div>
          <span class="role-badge" style="background:{role.bg}; color:{role.text}">
            {role.label}
          </span>
        </div>
        <div class="stats-grid">
          <div class="stat">
            <span class="stat-val">{$user?.post_count ?? 0}</span>
            <span class="stat-lbl">Posts</span>
          </div>
          <div class="stat">
            <span class="stat-val">{$user?.total_likes_received ?? 0}</span>
            <span class="stat-lbl">Likes</span>
          </div>
          <div class="stat">
            <span class="stat-val">{$user?.leaves ?? 0}</span>
            <span class="stat-lbl">🍃 Leaves</span>
          </div>
        </div>
        {#if $user?.borough}
          <div class="borough-tag">📍 {$user.borough}</div>
        {/if}
      </div>

      <div class="quick-links">
        <button class="quick-btn active">🏡 Feed</button>
        <button class="quick-btn">🗺 Explore Map</button>
        <button class="quick-btn">🌳 My Trees</button>
        <button class="quick-btn">💬 Group Chats</button>
        <button class="quick-btn">⚙️ Settings</button>
      </div>
    </aside>

    <!-- Feed -->
    <main class="feed">
      <!-- Welcome banner -->
      <div class="welcome-banner">
        <div class="banner-text">
          <span class="banner-emoji">🌿</span>
          <div>
            <h2>Welcome back, {$user?.username}!</h2>
            <p>NYC's urban forest has <strong>683,788 trees</strong> waiting for your care.</p>
          </div>
        </div>
        <div class="banner-cred">
          {#if ($user?.post_count ?? 0) < 30}
            <div class="progress-label">Progress to Credible User</div>
            <div class="progress-track">
              <div class="progress-fill" style="width:{Math.min(100,(($user?.post_count??0)/30)*100)}%"></div>
            </div>
            <div class="progress-hint">{$user?.post_count ?? 0}/30 posts · {$user?.total_likes_received ?? 0}/100 likes</div>
          {:else}
            <div class="credible-unlocked">⭐ Credible status unlocked!</div>
          {/if}
        </div>
      </div>

      <!-- Create post -->
      <div class="create-post">
        <span class="create-avatar">🧑‍🌾</span>
        <div class="create-input">
          <input type="text" placeholder="Share an observation about a tree…" readonly />
        </div>
        <button class="create-btn">📸 Post</button>
      </div>

      <!-- Post cards -->
      <div class="posts">
        {#each placeholderPosts as post, i}
          <div class="post-card" style="animation-delay:{i*0.1}s">
            <div class="post-header">
              <span class="post-tree-icon">{post.img}</span>
              <div>
                <div class="post-tree-name">{post.tree}</div>
                <div class="post-meta">
                  📍 {post.borough} ·
                  <span class="health health-{post.health.toLowerCase()}">{post.health}</span>
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
    background: var(--t-gradient-page);
    font-family: var(--t-font-body);
    color: var(--t-text-body);
  }

  /* ─── Navbar ─────────────────────────────────────────────────────── */
  .navbar {
    height: var(--t-nav-height);
    background: var(--t-bg-overlay);
    backdrop-filter: blur(16px);
    border-bottom: 1px solid var(--t-border);
    box-shadow: var(--t-shadow-nav);
    display: flex; align-items: center; justify-content: space-between;
    padding: 0 1.5rem;
    position: sticky; top: 0; z-index: 50;
  }
  .nav-brand { display: flex; align-items: center; gap: 8px; }
  .nav-tree  { font-size: 1.5rem; filter: drop-shadow(0 0 8px var(--t-brand-glow)); }
  .nav-title {
    font-family: var(--t-font-display);
    font-size: 1.3rem; font-weight: 900;
    color: var(--t-text-heading);
  }
  .nav-actions { display: flex; gap: 8px; }
  .nav-btn {
    background: var(--t-bg-elevated);
    border: 1px solid var(--t-border);
    border-radius: var(--t-radius-sm);
    width: 36px; height: 36px;
    color: var(--t-text-muted);
    cursor: pointer; font-size: 1rem;
    transition: background var(--t-transition);
  }
  .nav-btn:hover  { background: var(--t-bg-hover); }
  .nav-btn.logout { color: var(--t-status-poor); }

  /* ─── Layout Grid ────────────────────────────────────────────────── */
  .layout {
    max-width: var(--t-content-max);
    margin: 0 auto;
    display: grid;
    grid-template-columns: var(--t-sidebar-width) 1fr;
    gap: 1.5rem;
    padding: 1.5rem;
    opacity: 0; transform: translateY(16px);
    transition: opacity var(--t-transition-slow) .1s,
                transform var(--t-transition-slow) .1s;
  }
  .page.mounted .layout { opacity: 1; transform: translateY(0); }

  /* ─── Sidebar ────────────────────────────────────────────────────── */
  .sidebar { display: flex; flex-direction: column; gap: 1rem; }

  .profile-card {
    background: var(--t-bg-elevated);
    border: 1px solid var(--t-border);
    border-radius: var(--t-radius-lg);
    box-shadow: var(--t-shadow-card);
    padding: 1.4rem;
    display: flex; flex-direction: column; align-items: center; gap: .75rem;
  }
  .avatar {
    position: relative; width: 70px; height: 70px;
    display: flex; align-items: center; justify-content: center;
  }
  .avatar-emoji { font-size: 2.6rem; position: relative; z-index: 2; }
  .avatar-ring {
    position: absolute; inset: -4px; border-radius: 50%;
    border: 2px solid var(--t-brand-muted);
    animation: ringPulse 3s ease-out infinite;
  }
  @keyframes ringPulse {
    0%   { transform: scale(1);   opacity: .8; }
    100% { transform: scale(1.4); opacity: 0;  }
  }
  .profile-info  { text-align: center; }
  .profile-name  { font-size: 1rem; font-weight: 700; color: var(--t-text-heading); }
  .profile-email { font-size: .75rem; color: var(--t-text-faint); margin: 2px 0 8px; }
  .role-badge    {
    display: inline-block; padding: 3px 10px;
    border-radius: var(--t-radius-pill);
    font-size: .72rem; font-weight: 700;
  }

  .stats-grid {
    display: grid; grid-template-columns: repeat(3,1fr);
    gap: 6px; width: 100%; margin-top: 4px;
  }
  .stat {
    background: var(--t-bg-hover);
    border-radius: var(--t-radius-md);
    padding: 8px 4px; text-align: center;
  }
  .stat-val { display: block; font-size: .95rem; font-weight: 700; color: var(--t-text-brand); }
  .stat-lbl { font-size: .65rem; color: var(--t-text-faint); }
  .borough-tag { font-size: .78rem; color: var(--t-text-muted); margin-top: 2px; }

  .quick-links { display: flex; flex-direction: column; gap: 4px; }
  .quick-btn {
    background: none; border: none;
    border-radius: var(--t-radius-md);
    padding: 10px 14px;
    color: var(--t-text-muted);
    font-size: .88rem; font-family: var(--t-font-body);
    cursor: pointer; text-align: left;
    transition: background var(--t-transition), color var(--t-transition);
  }
  .quick-btn:hover,
  .quick-btn.active {
    background: var(--t-bg-hover);
    color: var(--t-text-brand);
  }

  /* ─── Feed ───────────────────────────────────────────────────────── */
  .feed { display: flex; flex-direction: column; gap: 1rem; }

  .welcome-banner {
    background: var(--t-gradient-banner);
    border: 1px solid var(--t-border-strong);
    border-radius: var(--t-radius-lg);
    padding: 1.4rem 1.6rem;
    display: flex; flex-direction: column; gap: .8rem;
  }
  .banner-text  { display: flex; align-items: center; gap: 12px; }
  .banner-emoji { font-size: 2rem; }
  .banner-text h2 { font-size: 1.1rem; color: var(--t-text-heading); margin-bottom: 2px; }
  .banner-text p  { font-size: .84rem; color: var(--t-text-muted); }
  .banner-text strong { color: var(--t-brand); }

  .progress-label {
    font-size: .73rem; color: var(--t-text-faint);
    letter-spacing: 1px; text-transform: uppercase; margin-bottom: 5px;
  }
  .progress-track {
    height: 5px; background: var(--t-bg-elevated);
    border-radius: var(--t-radius-pill); overflow: hidden;
  }
  .progress-fill {
    height: 100%; border-radius: var(--t-radius-pill);
    background: var(--t-gradient-bar);
    transition: width .6s;
  }
  .progress-hint { font-size: .72rem; color: var(--t-text-faint); margin-top: 4px; }
  .credible-unlocked { font-size: .84rem; color: var(--t-status-fair); font-weight: 600; }

  /* ─── Create Post ────────────────────────────────────────────────── */
  .create-post {
    background: var(--t-bg-elevated);
    border: 1px solid var(--t-border);
    border-radius: var(--t-radius-lg);
    padding: 14px 16px;
    display: flex; align-items: center; gap: 10px;
  }
  .create-avatar { font-size: 1.6rem; }
  .create-input  { flex: 1; }
  .create-input input {
    width: 100%;
    background: var(--t-bg-input);
    border: 1px solid var(--t-border-input);
    border-radius: var(--t-radius-pill);
    padding: 9px 16px;
    color: var(--t-text-input);
    font-size: .88rem; font-family: var(--t-font-body);
    cursor: pointer; outline: none;
  }
  .create-btn {
    background: var(--t-brand-dim);
    border: 1px solid var(--t-brand-muted);
    border-radius: var(--t-radius-pill);
    padding: 8px 16px;
    color: var(--t-brand);
    font-size: .84rem; font-weight: 600; font-family: var(--t-font-body);
    cursor: pointer; white-space: nowrap;
    transition: background var(--t-transition);
  }
  .create-btn:hover { background: var(--t-bg-active); }

  /* ─── Post Cards ─────────────────────────────────────────────────── */
  .posts { display: flex; flex-direction: column; gap: .9rem; }

  .post-card {
    background: var(--t-bg-elevated);
    border: 1px solid var(--t-border);
    border-radius: var(--t-radius-lg);
    box-shadow: var(--t-shadow-card);
    overflow: hidden;
    animation: fadeUp .4s both;
  }
  @keyframes fadeUp {
    from { opacity: 0; transform: translateY(12px); }
    to   { opacity: 1; transform: translateY(0); }
  }

  .post-header {
    display: flex; align-items: center; gap: 10px;
    padding: 14px 16px 10px;
  }
  .post-tree-icon { font-size: 2rem; }
  .post-tree-name { font-size: .92rem; font-weight: 600; color: var(--t-text-heading); }
  .post-meta      { font-size: .76rem; color: var(--t-text-muted); margin-top: 1px; }

  .health       { font-weight: 600; }
  .health-good  { color: var(--t-status-good); }
  .health-fair  { color: var(--t-status-fair); }
  .health-poor  { color: var(--t-status-poor); }

  .follow-btn {
    margin-left: auto;
    background: none;
    border: 1px solid var(--t-brand-muted);
    border-radius: var(--t-radius-pill);
    padding: 5px 13px;
    color: var(--t-brand);
    font-size: .78rem; font-weight: 600; font-family: var(--t-font-body);
    cursor: pointer; transition: background var(--t-transition);
  }
  .follow-btn:hover { background: var(--t-brand-dim); }

  .post-body { padding: 0 16px 10px; font-size: .88rem; color: var(--t-text-body); }

  .post-photo-placeholder {
    background: var(--t-bg-photo);
    height: 160px;
    display: flex; flex-direction: column; align-items: center; justify-content: center;
    border-top: 1px solid var(--t-border-soft);
    border-bottom: 1px solid var(--t-border-soft);
    gap: 8px;
  }
  .photo-hint { font-size: .78rem; color: var(--t-text-faint); }

  .post-actions {
    display: flex; gap: 4px; padding: 10px 12px;
  }
  .action-btn {
    background: none; border: none;
    border-radius: var(--t-radius-sm);
    padding: 7px 12px;
    color: var(--t-text-muted);
    font-size: .8rem; font-family: var(--t-font-body);
    cursor: pointer;
    transition: background var(--t-transition), color var(--t-transition);
  }
  .action-btn:hover {
    background: var(--t-bg-hover);
    color: var(--t-text-brand);
  }

  .feed-hint {
    text-align: center; font-size: .82rem;
    color: var(--t-text-faint);
    padding: .5rem 0 1rem;
  }
</style>