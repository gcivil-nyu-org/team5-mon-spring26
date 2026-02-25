<script>
  import { onMount } from 'svelte'
  import { user, apiLogout } from '../lib/api.js'

  export let navigate

  let mounted = false
  onMount(() => setTimeout(() => mounted = true, 50))

  async function logout() {
    await apiLogout()
    user.set(null)
    navigate('/login')
  }

  const roleColors = {
    standard: { bg: '#1a3d27', text: '#52b788', label: '🌱 Standard' },
    credible: { bg: '#3d3000', text: '#f4c430', label: '⭐ Credible' },
    caretaker: { bg: '#1a2a3d', text: '#60a5fa', label: '🌳 Caretaker' },
    admin: { bg: '#3d1a1a', text: '#f87171', label: '👑 Admin' },
  }

  $: role = roleColors[$user?.role] || roleColors.standard

  const placeholderPosts = [
    { tree: 'London Planetree #4821', borough: 'Brooklyn', health: 'Good', img: '🌳', likes: 24, comment: 'Looking healthy after the rain!' },
    { tree: 'Ginkgo #2047', borough: 'Manhattan', health: 'Fair', img: '🍂', likes: 11, comment: 'Some leaf discoloration noted.' },
    { tree: 'Red Oak #7732', borough: 'Queens', health: 'Good', img: '🌲', likes: 38, comment: 'Beautiful canopy this season!' },
  ]
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
              <div class="progress-fill posts" style="width:{Math.min(100,(($user?.post_count??0)/30)*100)}%"></div>
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
                <div class="post-meta">📍 {post.borough} · <span class="health health-{post.health.toLowerCase()}">{post.health}</span></div>
              </div>
              <button class="follow-btn">+ Follow</button>
            </div>
            <div class="post-body">
              <p>{post.comment}</p>
            </div>
            <div class="post-photo-placeholder">
              <span style="font-size:3rem">{post.img}</span>
              <span style="font-size:.78rem;color:rgba(168,220,180,.3);margin-top:8px">Photo coming soon</span>
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
  .page {
    min-height: 100vh;
    background: linear-gradient(180deg, #071410 0%, #0a1c12 100%);
  }

  /* Navbar */
  .navbar {
    height: 58px;
    background: rgba(10,28,18,.9);
    backdrop-filter: blur(16px);
    border-bottom: 1px solid rgba(82,183,136,.12);
    display: flex; align-items: center; justify-content: space-between;
    padding: 0 1.5rem; position: sticky; top: 0; z-index: 50;
  }
  .nav-brand { display: flex; align-items: center; gap: 8px; }
  .nav-tree { font-size: 1.5rem; filter: drop-shadow(0 0 8px rgba(82,183,136,.5)); }
  .nav-title {
    font-family: 'Playfair Display', serif; font-size: 1.3rem;
    font-weight: 900; color: #d4f5dd;
  }
  .nav-actions { display: flex; gap: 8px; }
  .nav-btn {
    background: rgba(255,255,255,.05); border: 1px solid rgba(82,183,136,.15);
    border-radius: 8px; width: 36px; height: 36px;
    color: rgba(168,220,180,.7); cursor: pointer; font-size: 1rem;
    transition: background .2s;
  }
  .nav-btn:hover { background: rgba(82,183,136,.12); }
  .nav-btn.logout { color: #f87171; }

  /* Layout */
  .layout {
    max-width: 1000px; margin: 0 auto;
    display: grid; grid-template-columns: 260px 1fr; gap: 1.5rem;
    padding: 1.5rem;
    opacity: 0; transform: translateY(16px);
    transition: opacity .5s .1s, transform .5s .1s;
  }
  .page.mounted .layout { opacity: 1; transform: translateY(0); }

  /* Sidebar */
  .sidebar { display: flex; flex-direction: column; gap: 1rem; }
  .profile-card {
    background: rgba(255,255,255,.04);
    border: 1px solid rgba(82,183,136,.14);
    border-radius: 16px; padding: 1.4rem;
    display: flex; flex-direction: column; align-items: center; gap: .75rem;
  }
  .avatar {
    position: relative; width: 70px; height: 70px;
    display: flex; align-items: center; justify-content: center;
  }
  .avatar-emoji { font-size: 2.6rem; position: relative; z-index: 2; }
  .avatar-ring {
    position: absolute; inset: -4px; border-radius: 50%;
    border: 2px solid rgba(82,183,136,.4);
    animation: ringPulse 3s ease-out infinite;
  }
  @keyframes ringPulse {
    0%   { transform: scale(1); opacity: .8; }
    100% { transform: scale(1.4); opacity: 0; }
  }
  .profile-info { text-align: center; }
  .profile-name { font-size: 1rem; font-weight: 700; color: #d4f5dd; }
  .profile-email { font-size: .75rem; color: rgba(168,220,180,.4); margin: 2px 0 8px; }
  .role-badge {
    display: inline-block; padding: 3px 10px; border-radius: 20px;
    font-size: .72rem; font-weight: 700;
  }
  .stats-grid {
    display: grid; grid-template-columns: repeat(3,1fr); gap: 6px;
    width: 100%; margin-top: 4px;
  }
  .stat {
    background: rgba(255,255,255,.04); border-radius: 9px; padding: 8px 4px;
    text-align: center;
  }
  .stat-val { display: block; font-size: .95rem; font-weight: 700; color: #95d5b2; }
  .stat-lbl { font-size: .65rem; color: rgba(168,220,180,.4); }
  .borough-tag {
    font-size: .78rem; color: rgba(168,220,180,.5); margin-top: 2px;
  }

  .quick-links {
    display: flex; flex-direction: column; gap: 4px;
  }
  .quick-btn {
    background: none; border: none; border-radius: 10px; padding: 10px 14px;
    color: rgba(168,220,180,.55); font-size: .88rem;
    font-family: 'DM Sans', sans-serif; cursor: pointer;
    text-align: left; transition: background .2s, color .2s;
  }
  .quick-btn:hover, .quick-btn.active {
    background: rgba(82,183,136,.1); color: #95d5b2;
  }

  /* Feed */
  .feed { display: flex; flex-direction: column; gap: 1rem; }

  .welcome-banner {
    background: linear-gradient(135deg, rgba(45,106,79,.3) 0%, rgba(82,183,136,.1) 100%);
    border: 1px solid rgba(82,183,136,.2);
    border-radius: 16px; padding: 1.4rem 1.6rem;
    display: flex; flex-direction: column; gap: .8rem;
  }
  .banner-text { display: flex; align-items: center; gap: 12px; }
  .banner-emoji { font-size: 2rem; }
  .banner-text h2 { font-size: 1.1rem; color: #d4f5dd; margin-bottom: 2px; }
  .banner-text p { font-size: .84rem; color: rgba(168,220,180,.6); }
  .banner-text strong { color: #52b788; }
  .progress-label { font-size: .73rem; color: rgba(168,220,180,.4); letter-spacing: 1px; text-transform: uppercase; margin-bottom: 5px; }
  .progress-track {
    height: 5px; background: rgba(255,255,255,.08); border-radius: 3px; overflow: hidden;
  }
  .progress-fill { height: 100%; border-radius: 3px; background: linear-gradient(90deg, #2d6a4f, #52b788); transition: width .6s; }
  .progress-hint { font-size: .72rem; color: rgba(168,220,180,.35); margin-top: 4px; }
  .credible-unlocked { font-size: .84rem; color: #f4c430; font-weight: 600; }

  /* Create post */
  .create-post {
    background: rgba(255,255,255,.04); border: 1px solid rgba(82,183,136,.14);
    border-radius: 14px; padding: 14px 16px;
    display: flex; align-items: center; gap: 10px;
  }
  .create-avatar { font-size: 1.6rem; }
  .create-input { flex: 1; }
  .create-input input {
    width: 100%; background: rgba(255,255,255,.05);
    border: 1px solid rgba(82,183,136,.15); border-radius: 20px;
    padding: 9px 16px; color: rgba(168,220,180,.5); font-size: .88rem;
    font-family: 'DM Sans', sans-serif; cursor: pointer; outline: none;
  }
  .create-btn {
    background: rgba(82,183,136,.15); border: 1px solid rgba(82,183,136,.3);
    border-radius: 20px; padding: 8px 16px; color: #52b788;
    font-size: .84rem; font-weight: 600; font-family: 'DM Sans', sans-serif;
    cursor: pointer; white-space: nowrap; transition: background .2s;
  }
  .create-btn:hover { background: rgba(82,183,136,.25); }

  /* Post cards */
  .posts { display: flex; flex-direction: column; gap: .9rem; }
  .post-card {
    background: rgba(255,255,255,.04); border: 1px solid rgba(82,183,136,.12);
    border-radius: 16px; overflow: hidden;
    animation: fadeUp .4s both; opacity: 1;
  }
  @keyframes fadeUp {
    from { opacity: 0; transform: translateY(12px); }
    to   { opacity: 1; transform: translateY(0); }
  }
  .post-header {
    display: flex; align-items: center; gap: 10px; padding: 14px 16px 10px;
  }
  .post-tree-icon { font-size: 2rem; }
  .post-tree-name { font-size: .92rem; font-weight: 600; color: #d4f5dd; }
  .post-meta { font-size: .76rem; color: rgba(168,220,180,.45); margin-top: 1px; }
  .health { font-weight: 600; }
  .health-good { color: #52b788; }
  .health-fair { color: #f4c430; }
  .health-poor { color: #f87171; }
  .follow-btn {
    margin-left: auto; background: none; border: 1px solid rgba(82,183,136,.3);
    border-radius: 16px; padding: 5px 13px; color: #52b788;
    font-size: .78rem; font-weight: 600; font-family: 'DM Sans', sans-serif;
    cursor: pointer; transition: background .2s;
  }
  .follow-btn:hover { background: rgba(82,183,136,.12); }
  .post-body { padding: 0 16px 10px; font-size: .88rem; color: rgba(168,220,180,.7); }
  .post-photo-placeholder {
    background: rgba(0,0,0,.15); height: 160px; display: flex;
    flex-direction: column; align-items: center; justify-content: center;
    border-top: 1px solid rgba(82,183,136,.08); border-bottom: 1px solid rgba(82,183,136,.08);
  }
  .post-actions {
    display: flex; gap: 4px; padding: 10px 12px;
  }
  .action-btn {
    background: none; border: none; border-radius: 8px; padding: 7px 12px;
    color: rgba(168,220,180,.55); font-size: .8rem;
    font-family: 'DM Sans', sans-serif; cursor: pointer; transition: background .2s, color .2s;
  }
  .action-btn:hover { background: rgba(82,183,136,.1); color: #95d5b2; }

  .feed-hint {
    text-align: center; font-size: .82rem; color: rgba(168,220,180,.28);
    padding: .5rem 0 1rem;
  }
</style>
