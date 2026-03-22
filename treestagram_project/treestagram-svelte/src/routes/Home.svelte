<script>
  import { onMount } from "svelte";
  import {
    user,
    apiLogout,
    apiFetchPosts,
    apiToggleLike,
    apiAddComment,
    apiEditComment,
    apiDeleteComment,
  } from "../lib/api.js";
  import { theme, toggleTheme, cycleTheme } from "../theme.js";
  import LeftNav from "../components/LeftNav.svelte";
  import BackgroundRings from "../components/BackgroundRings.svelte";

  export let navigate;

  let mounted = false;
  let loading = true;
  let posts = [];

  // ── Comment drafts (keyed by post id) ──
  let commentDrafts = {};
  let showCommentForm = {};

  // ── Edit / delete comment state ──
  let editingCommentId = null;
  let editingCommentText = "";

  onMount(async () => {
    setTimeout(() => (mounted = true), 50);
    await loadPosts();
  });

  async function loadPosts() {
    loading = true;
    const res = await apiFetchPosts();
    if (res.success) {
      posts = res.posts;
    }
    loading = false;
  }

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

  async function toggleLike(index) {
    const post = posts[index];
    if (!post) return;

    const res = await apiToggleLike(post.id);
    if (res.success) {
      posts[index] = {
        ...post,
        liked: res.liked,
        likes_count: res.likes_count,
      };
      posts = [...posts];
    }
  }

  function toggleCommentFormVisibility(index) {
    const post = posts[index];
    if (!post) return;
    showCommentForm[post.id] = !showCommentForm[post.id];
    showCommentForm = { ...showCommentForm };
  }

  async function addComment(index) {
    const post = posts[index];
    if (!post) return;
    const text = (commentDrafts[post.id] || "").trim();
    if (!text) return;

    const res = await apiAddComment(post.id, text);
    if (res.success) {
      posts[index] = {
        ...post,
        comments: [...post.comments, res.comment],
      };
      posts = [...posts];
      commentDrafts[post.id] = "";
      showCommentForm[post.id] = true;
    }
  }

  // ── Edit comment ──
  function startEditComment(comment) {
    editingCommentId = comment.id;
    editingCommentText = comment.text;
  }

  function cancelEditComment() {
    editingCommentId = null;
    editingCommentText = "";
  }

  async function saveEditComment(postIndex) {
    if (!editingCommentText.trim()) return;
    const res = await apiEditComment(editingCommentId, editingCommentText.trim());
    if (res.success) {
      const post = posts[postIndex];
      posts[postIndex] = {
        ...post,
        comments: post.comments.map((c) =>
          c.id === editingCommentId ? { ...c, text: res.comment.text } : c
        ),
      };
      posts = [...posts];
      cancelEditComment();
    }
  }

  // ── Delete comment ──
  async function deleteComment(postIndex, commentId) {
    const res = await apiDeleteComment(commentId);
    if (res.success) {
      const post = posts[postIndex];
      posts[postIndex] = {
        ...post,
        comments: post.comments.filter((c) => c.id !== commentId),
      };
      posts = [...posts];
    }
  }

  // Health emoji helper
  function healthIcon(h) {
    if (h === "Good") return "🌳";
    if (h === "Fair") return "🍂";
    return "🥀";
  }

  $: isDark = $theme === "dark";
</script>

<div class="page" class:mounted>
  <BackgroundRings />
  <!-- Left Nav Sidebar -->
  <LeftNav {navigate} activePage="home" />

  <div class="layout">
    <!-- Feed -->
    <main class="feed">
      <!-- Post cards -->
      {#if loading}
        <div class="feed-hint">Loading posts…</div>
      {:else if posts.length === 0}
        <div class="feed-hint">
          No posts yet — be the first to share a tree observation! 🌱
        </div>
      {:else}
        <div class="posts">
          {#each posts as post, i}
            <div class="post-card" style="animation-delay:{i * 0.1}s">
              <div class="post-header">
                <span class="post-tree-icon">{healthIcon(post.health)}</span>
                <div>
                  <div class="post-tree-name">{post.tree_name}</div>
                  <div class="post-meta">
                    {#if post.borough}📍 {post.borough} · {/if}
                    <span class="health health-{post.health.toLowerCase()}"
                      >{post.health}</span
                    >
                    · by <strong>{post.author.username}</strong>
                  </div>
                </div>
                <button class="follow-btn">+ Follow</button>
              </div>
              {#if post.body}
                <div class="post-body">
                  <p>{post.body}</p>
                </div>
              {/if}
              {#if post.image}
                <div class="post-photo">
                  <img src={post.image} alt={post.tree_name} />
                </div>
              {:else}
                <div class="post-photo-placeholder">
                  <span style="font-size:3rem"
                    >{healthIcon(post.health)}</span
                  >
                  <span class="photo-hint">No photo yet</span>
                </div>
              {/if}
              <div class="post-actions">
                <button
                  class="action-btn"
                  class:liked={post.liked}
                  on:click={() => toggleLike(i)}
                >
                  ❤️ {post.likes_count}
                </button>
                <button
                  class="action-btn"
                  on:click={() => toggleCommentFormVisibility(i)}
                >
                  💬 {post.comments.length || ""} Comment
                </button>
                <!-- <button class="action-btn">🌿 Rate health</button> -->
              </div>
              {#if showCommentForm[post.id] || (post.comments && post.comments.length)}
                <div class="post-comments">
                  {#if post.comments?.length}
                    <div class="comment-list">
                      {#each post.comments as c}
                        <div class="comment-item">
                          {#if editingCommentId === c.id}
                            <div class="comment-edit-row">
                              <input
                                type="text"
                                class="comment-edit-input"
                                bind:value={editingCommentText}
                                on:keydown={(e) => e.key === "Enter" && saveEditComment(i)}
                              />
                              <button class="comment-action-btn save" on:click={() => saveEditComment(i)}>✓</button>
                              <button class="comment-action-btn" on:click={cancelEditComment}>✕</button>
                            </div>
                          {:else}
                            <span class="comment-text"><strong>{c.author.username}</strong>: {c.text}</span>
                            {#if $user && c.author.id === $user.id}
                              <span class="comment-actions">
                                <button class="comment-action-btn" on:click={() => startEditComment(c)} title="Edit">✏️</button>
                                <button class="comment-action-btn delete" on:click={() => deleteComment(i, c.id)} title="Delete">🗑️</button>
                              </span>
                            {/if}
                          {/if}
                        </div>
                      {/each}
                    </div>
                  {/if}
                  {#if showCommentForm[post.id]}
                    <div class="comment-form">
                      <input
                        type="text"
                        placeholder="Write a comment..."
                        bind:value={commentDrafts[post.id]}
                        on:keydown={(event) =>
                          event.key === "Enter" && addComment(i)}
                      />
                      <button
                        class="comment-submit"
                        on:click={() => addComment(i)}
                      >
                        Post
                      </button>
                    </div>
                  {/if}
                </div>
              {/if}
            </div>
          {/each}
        </div>
      {/if}

      <div class="feed-hint">🌳 Follow trees to personalize your feed</div>
    </main>
  </div>
</div>

<style>
  /* ─── Page Shell ─────────────────────────────────────────────────── */
  .page {
    min-height: 100vh;
    background: var(--t-bg-base);
    font-family: var(--t-font-body);
    color: var(--t-text-body);
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

  /* ─── Post Photo ────────────────────────────────────────────────── */
  .post-photo {
    width: 100%;
    max-height: 400px;
    overflow: hidden;
    border-top: 1px solid var(--t-border-soft);
    border-bottom: 1px solid var(--t-border-soft);
  }
  .post-photo img {
    width: 100%;
    height: auto;
    object-fit: cover;
    display: block;
  }

  /* ─── Post Cards ─────────────────────────────────────────────────── */
  .posts {
    display: flex;
    flex-direction: column;
    gap: 0.9rem;
  }

  .post-card {
    background: var(--t-bg-elevated);
    border: 1px solid var(--t-border);
    border-radius: var(--t-radius-lg);
    box-shadow: var(--t-shadow-card);
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
    color: var(--t-text-brand);
  }
  .post-meta {
    font-size: 0.76rem;
    color: var(--t-text-muted);
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
    background: var(--t-bg-surface);
    border: none;
    border-radius: var(--t-radius-pill);
    padding: 5px 13px;
    color: var(--t-text-brand);
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
    color: var(--t-text-body);
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
    color: var(--t-text-muted);
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
  .action-btn.liked {
    color: var(--t-status-poor);
  }

  .post-comments {
    border-top: 1px solid var(--t-border-soft);
    padding: 10px 12px 12px;
    display: flex;
    flex-direction: column;
    gap: 8px;
  }
  .comment-list {
    display: flex;
    flex-direction: column;
    gap: 6px;
  }
  .comment-item {
    font-size: 0.8rem;
    color: var(--t-text-body);
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 6px;
  }
  .comment-text {
    flex: 1;
    min-width: 0;
  }
  .comment-actions {
    display: flex;
    gap: 2px;
    opacity: 0;
    transition: opacity var(--t-transition);
    flex-shrink: 0;
  }
  .comment-item:hover .comment-actions {
    opacity: 1;
  }
  .comment-action-btn {
    background: none;
    border: none;
    cursor: pointer;
    font-size: 0.72rem;
    padding: 2px 5px;
    border-radius: var(--t-radius-sm);
    color: var(--t-text-muted);
    transition: background var(--t-transition), color var(--t-transition);
  }
  .comment-action-btn:hover {
    background: var(--t-bg-hover);
  }
  .comment-action-btn.save {
    color: var(--t-status-good);
  }
  .comment-action-btn.delete:hover {
    color: var(--t-status-poor);
  }
  .comment-edit-row {
    display: flex;
    align-items: center;
    gap: 4px;
    width: 100%;
  }
  .comment-edit-input {
    flex: 1;
    background: var(--t-bg-input);
    border: 1px solid var(--t-border-input);
    border-radius: var(--t-radius-sm);
    padding: 4px 8px;
    color: var(--t-text-heading);
    font-size: 0.78rem;
    font-family: var(--t-font-body);
    outline: none;
  }
  .comment-edit-input:focus {
    border-color: var(--t-brand);
  }
  .comment-form {
    display: flex;
    gap: 8px;
    align-items: center;
  }
  .comment-form input {
    flex: 1;
    background: var(--t-bg-input);
    border: 1px solid var(--t-border-input);
    border-radius: var(--t-radius-pill);
    padding: 7px 12px;
    color: var(--t-text-heading);
    font-size: 0.78rem;
    font-family: var(--t-font-body);
    outline: none;
  }
  .comment-submit {
    background: var(--t-bg-surface);
    border: none;
    border-radius: var(--t-radius-pill);
    padding: 6px 12px;
    color: var(--t-text-brand);
    font-size: 0.75rem;
    font-weight: 600;
    cursor: pointer;
  }
  .comment-submit:hover {
    background: var(--t-bg-active);
  }

  .feed-hint {
    text-align: center;
    font-size: 0.82rem;
    color: var(--t-text-brand);
    padding: 0.5rem 0 1rem;
    opacity: 0.8;
  }
</style>
