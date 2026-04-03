<script>
  import { onMount } from "svelte";
  import LeftNav from "../components/LeftNav.svelte";
  import BackgroundRings from "../components/BackgroundRings.svelte";
  import {
    user,
    apiFetchMyPosts,
    apiFetchFollowedTrees,
    apiCreatePost,
    apiValidateTree,
    apiToggleLike,
    apiAddComment,
    apiEditComment,
    apiDeleteComment,
    apiDeletePost,
    apiFetchPendingApplications,
    apiReviewApplication,
  } from "../lib/api.js";

  export let navigate;

  let mounted = false;
  let myPosts = [];
  let followedTrees = [];
  let loading = true;
  let loadingFollowed = false;
  let activeTab = "posts";

  // ── Create-post carousel modal ──
  let newPostBody = "";
  let newTreeId = "";
  let newBorough = "";
  let newHealth = "Good";
  let newImage = null;
  let newImagePreview = null;
  let newTaggedUsers = "";           // comma-separated @usernames
  let showCreateModal = false;
  let carouselStep = 0;            // 0 = tree info, 1 = photo, 2 = observation + submit
  let slideDirection = "next";      // "next" or "prev" for CSS animation direction
  let posting = false;              // spinner state while submitting

  // Tree ID validation state
  let treeValidationStatus = ""; // "", "checking", "valid", "invalid"
  let treeValidationMsg = "";
  let validatedTree = null;         // tree data from API when valid
  let treeValidationTimer = null;

  // Modal state
  let selectedPost = null;
  let commentDraft = "";
  let showPostMenu = false;       // 3-dot menu open
  let showDeleteConfirm = false;  // inline delete confirmation
  let deleting = false;           // delete spinner

  // Edit / delete comment state
  let editingCommentId = null;
  let editingCommentText = "";

  // ── Admin State ──
  let selectedApplication = null;
  let caretakerApplications = [];
  let loadingApplications = false;

  onMount(async () => {
    setTimeout(() => (mounted = true), 50);
    await Promise.all([loadMyPosts(), loadFollowedTrees(), loadApplications()]);
  });

  async function loadApplications() {
    loadingApplications = true;
    const res = await apiFetchPendingApplications();
    if (res.success) {
      caretakerApplications = res.applications;
    }
    loadingApplications = false;
  }

  async function loadMyPosts() {
    loading = true;
    const res = await apiFetchMyPosts();
    if (res.success) {
      myPosts = res.posts;
    }
    loading = false;
  }

  async function loadFollowedTrees() {
    loadingFollowed = true;
    const res = await apiFetchFollowedTrees();
    if (res.success) {
      followedTrees = res.trees;
    }
    loadingFollowed = false;
  }

  async function validateTreeId(value) {
    const id = value.trim();
    if (!id) {
      treeValidationStatus = "";
      treeValidationMsg = "";
      validatedTree = null;
      return;
    }
    treeValidationStatus = "checking";
    treeValidationMsg = "Checking…";
    validatedTree = null;
    const res = await apiValidateTree(id);
    if (res.exists) {
      treeValidationStatus = "valid";
      treeValidationMsg = `✅ ${res.tree.spc_common} — ${res.tree.address}, ${res.tree.borough}`;
      validatedTree = res.tree;
      // Auto-fill borough and health from the tree
      if (res.tree.borough) newBorough = res.tree.borough;
      if (res.tree.health) newHealth = res.tree.health;
    } else {
      treeValidationStatus = "invalid";
      treeValidationMsg = `❌ ${res.error}`;
      validatedTree = null;
    }
  }

  function onTreeIdInput(e) {
    const val = e.target.value;
    newTreeId = val;
    if (treeValidationTimer) clearTimeout(treeValidationTimer);
    treeValidationTimer = setTimeout(() => validateTreeId(val), 400);
  }

  async function createPost() {
    const body = newPostBody.trim();
    if (treeValidationStatus !== "valid" || !validatedTree) return;
    if (!newImage) return;

    posting = true;
    const res = await apiCreatePost({
      tree_id: newTreeId.trim(),
      borough: newBorough,
      health: newHealth,
      body,
      image: newImage,
      tagged_users: newTaggedUsers,
    });
    posting = false;

    if (res.success) {
      myPosts = [res.post, ...myPosts];
      if (res.user) user.set(res.user);
      closeCreateModal();
    }
  }

  function handleImageSelect(event) {
    const file = event.target.files[0];
    if (file) {
      newImage = file;
      newImagePreview = URL.createObjectURL(file);
    }
  }

  function removeImage() {
    newImage = null;
    newImagePreview = null;
  }

  function triggerNewPost() {
    showCreateModal = true;
    carouselStep = 0;
    slideDirection = "next";
  }

  function closeCreateModal() {
    showCreateModal = false;
    carouselStep = 0;
    newPostBody = "";
    newTreeId = "";
    newBorough = "";
    newHealth = "Good";
    newImage = null;
    newImagePreview = null;
    newTaggedUsers = "";
    posting = false;
    treeValidationStatus = "";
    treeValidationMsg = "";
    validatedTree = null;
  }

  function nextStep() {
    slideDirection = "next";
    carouselStep = Math.min(carouselStep + 1, 2);
  }

  function prevStep() {
    slideDirection = "prev";
    carouselStep = Math.max(carouselStep - 1, 0);
  }

  // Can advance from step 0 only if tree ID is valid
  $: canAdvanceStep0 = treeValidationStatus === "valid";
  // Can advance from step 1 only if an image is uploaded
  $: canAdvanceStep1 = newImage !== null;
  // Can submit from step 2 (valid tree_id and image are required)
  $: canSubmit = treeValidationStatus === "valid" && newImage !== null && !posting;

  function openPost(post) {
    selectedPost = post;
    commentDraft = "";
  }

  function closeModal() {
    selectedPost = null;
    commentDraft = "";
    showPostMenu = false;
    showDeleteConfirm = false;
    deleting = false;
  }

  function togglePostMenu() {
    showPostMenu = !showPostMenu;
    showDeleteConfirm = false;
  }

  function closePostMenu() {
    showPostMenu = false;
    showDeleteConfirm = false;
  }

  async function toggleLikeOnSelected() {
    if (!selectedPost) return;
    const res = await apiToggleLike(selectedPost.id);
    if (res.success) {
      selectedPost = {
        ...selectedPost,
        liked: res.liked,
        likes_count: res.likes_count,
      };
      myPosts = myPosts.map((p) =>
        p.id === selectedPost.id
          ? { ...p, liked: res.liked, likes_count: res.likes_count }
          : p,
      );
    }
  }

  async function addCommentOnSelected() {
    if (!selectedPost || !commentDraft.trim()) return;
    const res = await apiAddComment(selectedPost.id, commentDraft.trim());
    if (res.success) {
      selectedPost = {
        ...selectedPost,
        comments: [...selectedPost.comments, res.comment],
      };
      myPosts = myPosts.map((p) =>
        p.id === selectedPost.id
          ? { ...p, comments: [...p.comments, res.comment] }
          : p,
      );
      commentDraft = "";
    }
  }

  function startEditComment(comment) {
    editingCommentId = comment.id;
    editingCommentText = comment.text;
  }

  function cancelEditComment() {
    editingCommentId = null;
    editingCommentText = "";
  }

  async function saveEditComment() {
    if (!selectedPost || !editingCommentText.trim()) return;
    const res = await apiEditComment(
      editingCommentId,
      editingCommentText.trim(),
    );
    if (res.success) {
      const updatedComments = selectedPost.comments.map((c) =>
        c.id === editingCommentId ? { ...c, text: res.comment.text } : c,
      );
      selectedPost = { ...selectedPost, comments: updatedComments };
      myPosts = myPosts.map((p) =>
        p.id === selectedPost.id ? { ...p, comments: updatedComments } : p,
      );
      cancelEditComment();
    }
  }

  async function deleteCommentOnSelected(commentId) {
    if (!selectedPost) return;
    const res = await apiDeleteComment(commentId);
    if (res.success) {
      const updatedComments = selectedPost.comments.filter(
        (c) => c.id !== commentId,
      );
      selectedPost = { ...selectedPost, comments: updatedComments };
      myPosts = myPosts.map((p) =>
        p.id === selectedPost.id ? { ...p, comments: updatedComments } : p,
      );
    }
  }

  async function confirmDelete(postId) {
    deleting = true;
    const res = await apiDeletePost(postId);
    if (res.success) {
      myPosts = myPosts.filter((p) => p.id !== postId);
      closeModal();
    }
    deleting = false;
  }

  function healthIcon(h) {
    if (h === "Good") return "🌳";
    if (h === "Fair") return "🍂";
    return "🥀";
  }

  function timeAgo(dateStr) {
    const diff = Date.now() - new Date(dateStr).getTime();
    const mins = Math.floor(diff / 60000);
    if (mins < 1) return "just now";
    if (mins < 60) return `${mins}m`;
    const hrs = Math.floor(mins / 60);
    if (hrs < 24) return `${hrs}h`;
    const days = Math.floor(hrs / 24);
    if (days < 7) return `${days}d`;
    const weeks = Math.floor(days / 7);
    return `${weeks}w`;
  }

  // ── Admin Functions ──
  function openApplication(app) {
    selectedApplication = app;
  }

  function closeApplicationModal() {
    selectedApplication = null;
  }

  async function handleApprove(appId) {
    const res = await apiReviewApplication(appId, "approved");
    if (res.success) {
      caretakerApplications = caretakerApplications.filter(a => a.id !== appId);
      if (selectedApplication?.id === appId) closeApplicationModal();
    }
  }

  async function handleReject(appId) {
    const res = await apiReviewApplication(appId, "rejected");
    if (res.success) {
      caretakerApplications = caretakerApplications.filter(a => a.id !== appId);
      if (selectedApplication?.id === appId) closeApplicationModal();
    }
  }

  $: totalLikes = myPosts.reduce((sum, p) => sum + (p.likes_count || 0), 0);
</script>

<div class="page" class:mounted>
  <BackgroundRings />
  <LeftNav {navigate} activePage="profile" />

  <!-- ─── Hero Section ─── -->
  <div class="profile-hero">
    <div class="profile-cover">
      <div class="profile-cover-text">Treestagram Treestagram</div>
      🌳🌿🍃🌲🌳🌿🍃
    </div>
    <div class="profile-info-bar">
      <div class="profile-pic">
        {#if $user?.profile_picture}
          <img
            src={$user.profile_picture}
            alt="Profile"
            class="profile-img-fluid"
          />
        {:else}
          🌿
        {/if}
      </div>
      <div class="profile-text">
        <h1>
          {$user?.first_name || "Your"}
          {$user?.last_name || "Name"}
        </h1>
        <div class="handle">@{$user?.username || "greenleaf_nyc"}</div>
        <div class="profile-chips">
          {#if $user?.role === "credible"}
            <span class="chip chip-health-good">✦ Credible User</span>
          {:else if $user?.role === "caretaker"}
            <span class="chip chip-health-good">🌳 Caretaker</span>
          {:else if $user?.role === "admin"}
            <span class="chip chip-health-good">👑 Admin</span>
          {:else}
            <span class="chip chip-health-good">🌱 Standard User</span>
          {/if}
          <span class="chip chip-borough"
            >📍 {$user?.borough || "NYC"}</span
          >
        </div>
      </div>
      <button class="new-post-hero-btn" on:click={triggerNewPost}>
        <span class="btn-sprout">🌱</span>
        <span class="btn-label">Plant a Post</span>
        <span class="btn-glow"></span>
      </button>
    </div>
    <div class="profile-stats-tabs">
      <div class="profile-tab-links">
        <button
          class="profile-tab"
          class:active={activeTab === "posts"}
          on:click={() => (activeTab = "posts")}
        >Posts</button>
        <button
          class="profile-tab"
          class:active={activeTab === "followed"}
          on:click={() => (activeTab = "followed")}
        >🌿 Followed Trees</button>

        {#if $user?.role === "admin"}
          <button
            class="profile-tab"
            class:active={activeTab === "admin"}
            on:click={() => (activeTab = "admin")}
          >CT Apps</button>
          <button
            class="profile-tab"
            class:active={activeTab === "admin1"}
            on:click={() => (activeTab = "admin1")}
          >Admin1</button>
          <button
            class="profile-tab"
            class:active={activeTab === "admin2"}
            on:click={() => (activeTab = "admin2")}
          >Admin2</button>
        {/if}

      </div>
    </div>
  </div>

  <!-- ─── Body: Grid + Sidebar ─── -->
  <div class="profile-body">
    <div>
      {#if activeTab === "posts"}
        {#if loading}
          <div class="loading-area">
            <div class="loading-spinner"></div>
            <p>Loading your posts…</p>
          </div>
        {:else if myPosts.length === 0}
          <div class="empty-state">
            <span class="empty-icon">📷</span>
            <h3>No Posts Yet</h3>
            <p>Share your first tree observation!</p>
          </div>
        {:else}
          <div class="profile-grid">
            {#each myPosts as post, i}
              <div
                class="profile-post n{i % 6}"
                on:click={() => openPost(post)}
                on:keydown={(e) => e.key === "Enter" && openPost(post)}
                role="button"
                tabindex="0"
              >
                {#if post.image}
                  <img src={post.image} alt={post.tree_name} class="post-img" />
                {:else}
                  <span class="post-emoji">{healthIcon(post.health)}</span>
                {/if}
                <div class="post-hover">
                  ❤️ {post.likes_count} &nbsp; 💬 {post.comments?.length || 0}
                </div>
              </div>
            {/each}
          </div>
        {/if}

      {:else if activeTab === "followed"}
        {#if loadingFollowed}
          <div class="loading-area">
            <div class="loading-spinner"></div>
            <p>Loading followed trees…</p>
          </div>
        {:else if followedTrees.length === 0}
          <div class="empty-state">
            <span class="empty-icon">🌳</span>
            <h3>No Followed Trees Yet</h3>
            <p>When you follow a tree, it will show up here.</p>
          </div>
        {:else}
          <div class="followed-trees-grid">
            {#each followedTrees as tree, i}
              <div
                class="followed-tree-card"
                style="animation-delay: {i * 0.05}s;"
                on:click={() => navigate('/treedashboard/' + tree.tree_id)}
                on:keydown={(e) => e.key === "Enter" && navigate('/treedashboard/' + tree.tree_id)}
                role="button"
                tabindex="0"
              >
                <div class="ft-header">
                  <div class="ft-icon">🌿</div>
                  <div class="ft-info">
                    <h4 class="ft-name">{tree.tree_name}</h4>
                    <span class="ft-id">#{tree.tree_id}</span>
                  </div>
                </div>
                <div class="ft-body">
                  <p class="ft-date">Followed {timeAgo(tree.followed_at)} ago</p>
                  {#if tree.has_messages}
                    <p class="ft-chat">💬 Active Community Chat</p>
                  {/if}
                </div>
                <div class="ft-action">
                  <button class="ft-btn">View Dashboard →</button>
                </div>
                <div class="ft-glow"></div>
              </div>
            {/each}
          </div>
        {/if}

      {:else if activeTab === "admin"}
        <div class="admin-panel">
          <h2 class="admin-panel-title">Pending Caretaker Applications</h2>

          {#if caretakerApplications.length === 0}
            <div class="empty-state">
              <span class="empty-icon">✨</span>
              <h3>All Caught Up!</h3>
              <p>There are no pending applications to review.</p>
            </div>
          {:else}
            <div class="app-list">
              {#each caretakerApplications as app}
                <div 
                  class="app-card" 
                  on:click={() => openApplication(app)} 
                  on:keydown={(e) => e.key === 'Enter' && openApplication(app)}
                  role="button" 
                  tabindex="0"
                >
                  <div class="app-avatar">
                    {app.username.charAt(0).toUpperCase()}
                  </div>
                  <div class="app-info">
                    <strong class="app-user">@{app.username}</strong>
                    <span class="app-tree">Target Tree: <strong>{app.treeId}</strong></span>
                  </div>
                  <div class="app-actions">
                    <button class="btn-reject" on:click|stopPropagation={() => handleReject(app.id)}>
                      Reject
                    </button>
                    <button class="btn-approve" on:click|stopPropagation={() => handleApprove(app.id)}>
                      Approve
                    </button>
                  </div>
                </div>
              {/each}
            </div>
          {/if}
        </div>
      {:else if activeTab === "admin1"}
        <div class="admin-panel">
          <h2 class="admin-panel-title">Admin1</h2>
          <p style="color: var(--t-text-muted); font-size: 0.9rem;">Admin1 content coming soon.</p>
        </div>

      {:else if activeTab === "admin2"}
        <div class="admin-panel">
          <h2 class="admin-panel-title">Admin2</h2>
          <p style="color: var(--t-text-muted); font-size: 0.9rem;">Admin2 content coming soon.</p>
        </div>

      {/if}
    </div>

    <aside>
      <div class="profile-right-card">
        <h3>About Me</h3>
        <p class="about-text">
          {$user?.bio || "Nature lover exploring NYC's urban forest 🌿"}
        </p>
      </div>

      <div class="profile-right-card">
        <h3>My Recent Posts</h3>
        {#if myPosts.length === 0}
          <p class="about-text">No posts yet.</p>
        {:else}
          {#each myPosts.slice(0, 4) as post}
            <div
              class="recent-post-item"
              on:click={() => openPost(post)}
              on:keydown={(e) => e.key === "Enter" && openPost(post)}
              role="button"
              tabindex="0"
            >
              <div class="rp-icon">{healthIcon(post.health)}</div>
              <div class="rp-info">
                <strong>{post.tree_name}</strong>
                <small>{post.borough || "NYC"} · {post.health}</small>
              </div>
              <span class="health-badge health-{post.health.toLowerCase()}"
                >{post.health}</span
              >
            </div>
          {/each}
        {/if}
      </div>

      <div class="profile-right-card">
        <h3>Progress to Credible User</h3>
        <div class="progress-item">
          <div class="progress-header">
            <span class="progress-label"
              >Posts ({$user?.post_count ?? 0}/{$user?.credible_post_threshold ?? 2})</span
            >
            {#if ($user?.post_count ?? 0) >= ($user?.credible_post_threshold ?? 2)}
              <span class="progress-met">✓ Met</span>
            {/if}
          </div>
          <div class="progress-track">
            <div
              class="progress-fill"
              style="width:{Math.min(
                100,
                (($user?.post_count ?? 0) / ($user?.credible_post_threshold ?? 2)) * 100,
              )}%"
            ></div>
          </div>
        </div>
        <div class="progress-item">
          <div class="progress-header">
            <span class="progress-label"
              >Likes ({$user?.total_likes_received ?? 0}/{$user?.credible_like_threshold ?? 2})</span
            >
            {#if ($user?.total_likes_received ?? 0) >= ($user?.credible_like_threshold ?? 2)}
              <span class="progress-met">✓ Met</span>
            {/if}
          </div>
          <div class="progress-track">
            <div
              class="progress-fill"
              style="width:{Math.min(
                100,
                (($user?.total_likes_received ?? 0) / ($user?.credible_like_threshold ?? 2)) * 100,
              )}%"
            ></div>
          </div>
        </div>
        {#if ($user?.post_count ?? 0) >= ($user?.credible_post_threshold ?? 2) && ($user?.total_likes_received ?? 0) >= ($user?.credible_like_threshold ?? 2)}
          <div class="credible-banner">
            🎉 You're a Credible User! Apply to be a Caretaker now.
          </div>
        {/if}
      </div>

      <div class="profile-right-card">
        <h3>Apply to be a Caretaker</h3>
        {#if $user?.role === 'standard'}
          <button class="caretaker-apply-btn disabled" disabled>
            🔒 Requirements Not Met
          </button>
          <p class="caretaker-hint">You need 30+ posts and 100+ likes to apply.</p>
        {:else}
          <button class="caretaker-apply-btn" on:click={() => navigate('/applyforcaretaker')}>
            🌿 Apply Now
          </button>
        {/if}
      </div>
    </aside>
  </div>

  <!-- ─── Application Detail Modal ─── -->
  {#if selectedApplication}
    <div
      class="modal-backdrop"
      on:click={closeApplicationModal}
      on:keydown={(e) => e.key === "Escape" && closeApplicationModal()}
      role="button"
      tabindex="0"
    >
      <div
        class="modal app-modal"
        on:click|stopPropagation
        on:keydown|stopPropagation
        role="button"
        tabindex="0"
      >
        <button class="modal-close-btn" on:click={closeApplicationModal} title="Close">✕</button>

        <div class="app-modal-header">
          <div class="app-modal-avatar">
            {selectedApplication.username.charAt(0).toUpperCase()}
          </div>
          <div class="app-modal-title">
            <h2>Caretaker Application</h2>
            <span>Submitted by <strong>@{selectedApplication.username}</strong></span>
          </div>
        </div>

        <div class="app-modal-body">
          <section class="form-section">
            <h3 class="section-title"><span class="section-dot"></span> Target Tree</h3>
            <div class="app-detail-card">
              <span class="detail-icon">🌳</span>
              <span class="detail-text">Tree ID: <strong>{selectedApplication.treeId}</strong></span>
            </div>
          </section>

          <section class="form-section">
            <h3 class="section-title"><span class="section-dot"></span> Motivation</h3>
            <p class="app-read-text">{selectedApplication.motivation}</p>
          </section>

          <section class="form-section">
            <h3 class="section-title"><span class="section-dot"></span> Experience & Background</h3>
            <p class="app-read-text">{selectedApplication.treeExperience}</p>
          </section>
        </div>

        <div class="app-modal-actions">
          <button class="btn-wizard-reject" on:click={() => handleReject(selectedApplication.id)}>
            ✕ Reject Application
          </button>
          <button class="btn-wizard-approve" on:click={() => handleApprove(selectedApplication.id)}>
            ✓ Approve Caretaker
          </button>
        </div>
      </div>
    </div>
  {/if}

  <!-- ─── Create Post Carousel Modal ─── -->
  {#if showCreateModal}
    <div class="carousel-backdrop" on:click={closeCreateModal} on:keydown={(e) => e.key === "Escape" && closeCreateModal()} role="button" tabindex="0">
      <!-- svelte-ignore a11y-no-noninteractive-element-interactions -->
      <!-- svelte-ignore a11y-click-events-have-key-events -->
      <div class="carousel-modal" on:click|stopPropagation on:keydown|stopPropagation role="dialog">
        <div class="carousel-header">
          <button class="carousel-close" on:click={closeCreateModal}>✕</button>
          <h2>🌱 Plant a Post</h2>
          <div class="step-dots">
            {#each [0, 1, 2] as s}
              <div
                class="dot"
                class:active={carouselStep === s}
                class:done={carouselStep > s}
              ></div>
            {/each}
          </div>
        </div>

        <!-- Carousel body -->
        <div class="carousel-body">
          <div class="carousel-track" class:slide-next={slideDirection === "next"} class:slide-prev={slideDirection === "prev"}>
            {#if carouselStep === 0}
              <!-- Step 1: Tree Info -->
              <div class="carousel-slide" key="step0">
                <div class="slide-icon">🌳</div>
                <h3 class="slide-title">What tree did you see?</h3>
                <p class="slide-subtitle">Enter the Tree ID from the NYC Trees database</p>
                <div class="slide-fields">
                  <label class="field-label">
                    <span class="label-text">Tree ID <span class="required">*</span></span>
                    <input
                      type="text"
                      placeholder="e.g. 180683"
                      value={newTreeId}
                      on:input={onTreeIdInput}
                      class="carousel-input"
                      class:input-valid={treeValidationStatus === "valid"}
                      class:input-invalid={treeValidationStatus === "invalid"}
                    />
                    {#if treeValidationMsg}
                      <span
                        class="tree-validation-msg"
                        class:valid={treeValidationStatus === "valid"}
                        class:invalid={treeValidationStatus === "invalid"}
                        class:checking={treeValidationStatus === "checking"}
                      >
                        {treeValidationMsg}
                      </span>
                    {/if}
                  </label>
                  {#if validatedTree}
                    <div class="tree-info-card">
                      <div class="tree-info-row"><strong>🌳 Species:</strong> {validatedTree.spc_common} <em>({validatedTree.spc_latin})</em></div>
                      <div class="tree-info-row"><strong>📍 Location:</strong> {validatedTree.address}, {validatedTree.borough}</div>
                      <div class="tree-info-row"><strong>💚 Health:</strong> {validatedTree.health}</div>
                    </div>
                  {/if}
                  <label class="field-label">
                    <span class="label-text">Health Status</span>
                    <div class="health-picker">
                      <button
                        class="health-option"
                        class:selected={newHealth === "Good"}
                        on:click={() => (newHealth = "Good")}
                      >🌳 Good</button>
                      <button
                        class="health-option"
                        class:selected={newHealth === "Fair"}
                        on:click={() => (newHealth = "Fair")}
                      >🍂 Fair</button>
                      <button
                        class="health-option"
                        class:selected={newHealth === "Poor"}
                        on:click={() => (newHealth = "Poor")}
                      >🥀 Poor</button>
                    </div>
                  </label>
                </div>
              </div>
            {:else if carouselStep === 1}
              <!-- Step 2: Photo -->
              <div class="carousel-slide" key="step1">
                <div class="slide-icon">📸</div>
                <h3 class="slide-title">Add a photo</h3>
                <p class="slide-subtitle">A picture says a thousand leaves!</p>
                <div class="photo-upload-area">
                  {#if newImagePreview}
                    <div class="photo-preview">
                      <img src={newImagePreview} alt="Preview" />
                      <button class="photo-remove" on:click={removeImage}>✕</button>
                    </div>
                  {:else}
                    <label class="photo-dropzone">
                      <span class="dropzone-icon">📷</span>
                      <span class="dropzone-text">Click to upload a photo</span>
                      <span class="dropzone-hint">JPG, PNG, GIF up to 10MB</span>
                      <input
                        type="file"
                        accept="image/*"
                        on:change={handleImageSelect}
                        style="display:none"
                      />
                    </label>
                  {/if}
                </div>
                <p class="slide-skip" style="color: var(--danger, #ff4444)">A photo is required to submit.</p>
              </div>
            {:else}
              <!-- Step 3: Observation + Tag + Submit -->
              <div class="carousel-slide" key="step2">
                <div class="slide-icon">✍️</div>
                <h3 class="slide-title">Share your observation</h3>
                <p class="slide-subtitle">What did you notice about this tree?</p>
                <div class="slide-fields">
                  <textarea
                    placeholder="The leaves looked vibrant today, and I noticed new growth on the lower branches…"
                    bind:value={newPostBody}
                    class="carousel-textarea"
                    rows="3"
                  ></textarea>
                </div>
                <!-- Preview summary -->
                <div class="post-preview-card">
                  <div class="preview-header">
                    <span class="preview-icon">{healthIcon(newHealth)}</span>
                    <div>
                      <strong>{validatedTree?.spc_common || "Tree"} #{newTreeId || "?"}</strong>
                      <small>{newBorough || "NYC"} · {newHealth}</small>
                    </div>
                  </div>
                  {#if newImagePreview}
                    <img src={newImagePreview} alt="Preview" class="preview-thumb" />
                  {/if}
                  {#if newTaggedUsers.trim()}
                    <div class="preview-tags">
                      🏷️ {newTaggedUsers.split(",").map(u => "@" + u.trim().replace(/^@/, "")).filter(u => u !== "@").join(", ")}
                    </div>
                  {/if}
                </div>
              </div>
            {/if}
          </div>
        </div>

        <!-- Footer navigation -->
        <div class="carousel-footer">
          {#if carouselStep > 0}
            <button class="carousel-nav-btn back" on:click={prevStep}>
              ← Back
            </button>
          {:else}
            <div></div>
          {/if}

          {#if carouselStep < 2}
            <button
              class="carousel-nav-btn next"
              on:click={nextStep}
              disabled={(carouselStep === 0 && !canAdvanceStep0) || (carouselStep === 1 && !canAdvanceStep1)}
            >
              Next →
            </button>
          {:else}
            <button
              class="carousel-nav-btn submit"
              on:click={createPost}
              disabled={!canSubmit}
            >
              {#if posting}
                <span class="btn-spinner"></span> Planting…
              {:else}
                🌱 Plant It!
              {/if}
            </button>
          {/if}
        </div>
      </div>
    </div>
  {/if}

  <!-- THIS PART WAS TOTALLY MISSING AFTER THE REBASE -->
  <!-- ─── Post Detail Modal ─── -->
  {#if selectedPost}
      <!-- svelte-ignore a11y-no-static-element-interactions -->
      <div
        class="modal-backdrop"
        on:click={closeModal}
        on:keydown={(e) => e.key === "Escape" && closeModal()}
      >
        <!-- svelte-ignore a11y-no-noninteractive-element-interactions -->
        <div
          class="modal"
          on:click|stopPropagation
          on:keydown|stopPropagation
          role="dialog"
        >
          <!-- Close button floating on top-right -->
          <button class="modal-close-btn" on:click={closeModal} title="Close">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
          </button>
  
          <!-- Left: Image -->
          <div class="modal-image">
            {#if selectedPost.image}
              <img src={selectedPost.image} alt={selectedPost.tree_name} />
            {:else}
              <div class="modal-placeholder">
                <span class="modal-placeholder-emoji">{healthIcon(selectedPost.health)}</span>
                <span class="modal-placeholder-label">{selectedPost.tree_name}</span>
              </div>
            {/if}
          </div>
  
          <!-- Right: Details -->
          <div class="modal-details">
            <!-- Header -->
            <div class="modal-header">
              <div class="modal-author">
                {#if selectedPost.author?.profile_picture || $user?.profile_picture}
                  <img src={selectedPost.author?.profile_picture || $user?.profile_picture} alt="avatar" class="modal-avatar" />
                {:else}
                  <div class="modal-avatar-placeholder">
                    {(selectedPost.author?.username || $user?.username || "U").charAt(0).toUpperCase()}
                  </div>
                {/if}
                <div class="modal-author-info">
                  <strong>{selectedPost.author?.username || $user?.username}</strong>
                  {#if selectedPost.borough}
                    <span class="modal-loc">📍 {selectedPost.borough}</span>
                  {/if}
                </div>
              </div>
  
              <!-- 3-dot menu -->
              <div class="post-menu-wrapper">
                <button class="post-menu-trigger" on:click={togglePostMenu} title="More options">
                  <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor"><circle cx="12" cy="5" r="2"/><circle cx="12" cy="12" r="2"/><circle cx="12" cy="19" r="2"/></svg>
                </button>
  
                {#if showPostMenu}
                  <!-- svelte-ignore a11y-no-static-element-interactions -->
                  <div class="post-menu-dropdown" on:click|stopPropagation on:keydown|stopPropagation>
                    {#if !showDeleteConfirm}
                      <button class="menu-item menu-item-danger" on:click={() => (showDeleteConfirm = true)}>
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="3 6 5 6 21 6"/><path d="M19 6l-1 14a2 2 0 0 1-2 2H8a2 2 0 0 1-2-2L5 6"/><path d="M10 11v6"/><path d="M14 11v6"/><path d="M9 6V4a1 1 0 0 1 1-1h4a1 1 0 0 1 1 1v2"/></svg>
                        Delete Post
                      </button>
                      <button class="menu-item" on:click={closePostMenu}>
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
                        Cancel
                      </button>
                    {:else}
                      <div class="delete-confirm-panel">
                        <div class="delete-confirm-icon">⚠️</div>
                        <p class="delete-confirm-text">Delete this post permanently?</p>
                        <div class="delete-confirm-actions">
                          <button class="confirm-cancel-btn" on:click={() => (showDeleteConfirm = false)} disabled={deleting}>
                            Keep
                          </button>
                          <button class="confirm-delete-btn" on:click={() => confirmDelete(selectedPost.id)} disabled={deleting}>
                            {#if deleting}
                              <span class="btn-spinner-sm"></span>
                            {:else}
                              Delete
                            {/if}
                          </button>
                        </div>
                      </div>
                    {/if}
                  </div>
                {/if}
              </div>
            </div>
  
            <!-- Body / Content -->
            <div class="modal-body">
              <div class="modal-tree-card">
                <span class="modal-tree-icon">{healthIcon(selectedPost.health)}</span>
                <div class="modal-tree-info">
                  <span class="modal-tree-name">{selectedPost.tree_name}</span>
                  <span class="health-badge health-{selectedPost.health.toLowerCase()}">{selectedPost.health}</span>
                </div>
              </div>
  
              {#if selectedPost.body}
                <p class="modal-text">{selectedPost.body}</p>
              {/if}
  
              {#if selectedPost.tagged_users?.length}
                <div class="modal-tagged">
                  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="flex-shrink:0"><path d="M20.59 13.41l-7.17 7.17a2 2 0 0 1-2.83 0L2 12V2h10l8.59 8.59a2 2 0 0 1 0 2.82z"/><line x1="7" y1="7" x2="7.01" y2="7"/></svg>
                  <span>{selectedPost.tagged_users.map(u => "@" + u.username).join(", ")}</span>
                </div>
              {/if}
  
              <span class="modal-time">{timeAgo(selectedPost.created_at)}</span>
  
              <!-- Comments Section -->
              <div class="modal-comments">
                <div class="comments-header">
                  <span class="comments-label">Comments</span>
                  <span class="comments-count">{selectedPost.comments?.length || 0}</span>
                </div>
                {#if selectedPost.comments?.length}
                  {#each selectedPost.comments as c}
                    <div class="modal-comment">
                      <div class="comment-avatar">
                        {(c.author?.username || "U").charAt(0).toUpperCase()}
                      </div>
                      {#if editingCommentId === c.id}
                        <div class="comment-edit-row">
                          <input
                            type="text"
                            class="comment-edit-input"
                            bind:value={editingCommentText}
                            on:keydown={(e) => e.key === "Enter" && saveEditComment()}
                          />
                          <button class="comment-action-btn save" on:click={saveEditComment}>✓</button>
                          <button class="comment-action-btn" on:click={cancelEditComment}>✕</button>
                        </div>
                      {:else}
                        <div class="comment-content">
                          <strong>{c.author.username}</strong>
                          <span>{c.text}</span>
                        </div>
                        {#if $user && (c.author.id === $user.id || selectedPost.author?.id === $user.id)}
                          <span class="comment-actions">
                            {#if c.author.id === $user.id}
                              <button class="comment-action-btn" on:click={() => startEditComment(c)} title="Edit">✏️</button>
                            {/if}
                            <button class="comment-action-btn delete" on:click={() => deleteCommentOnSelected(c.id)} title="Delete">🗑️</button>
                          </span>
                        {/if}
                      {/if}
                    </div>
                  {/each}
                {:else}
                  <div class="no-comments">
                    <span class="no-comments-icon">💬</span>
                    <span>No comments yet. Be the first!</span>
                  </div>
                {/if}
              </div>
            </div>
  
            <!-- Action Bar -->
            <div class="modal-actions">
              <div class="action-row">
                <button
                  class="like-btn"
                  class:liked={selectedPost.liked}
                  on:click={toggleLikeOnSelected}
                >
                  <svg class="like-icon" width="22" height="22" viewBox="0 0 24 24"
                    fill={selectedPost.liked ? "currentColor" : "none"}
                    stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"/>
                  </svg>
                </button>
                <span class="likes-count">{selectedPost.likes_count} {selectedPost.likes_count === 1 ? "like" : "likes"}</span>
              </div>
              <div class="comment-input-row">
                <input
                  type="text"
                  placeholder="Add a comment…"
                  bind:value={commentDraft}
                  on:keydown={(e) => e.key === "Enter" && addCommentOnSelected()}
                />
                <button
                  class="post-comment-btn"
                  on:click={addCommentOnSelected}
                  disabled={!commentDraft.trim()}
                >
                  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><line x1="22" y1="2" x2="11" y2="13"/><polygon points="22 2 15 22 11 13 2 9 22 2"/></svg>
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    {/if}
  </div>
<style>
  .page {
    background: var(--t-bg-base);
    min-height: 100vh;
    padding-left: 60px;
    color: var(--t-text-body);
    font-family: var(--t-font-body);
    position: relative;
    z-index: 0;
    overflow: hidden;
  }

  /* ─── Hero ──────────────────────────────────────────────────────── */
  .profile-hero {
    background: var(--t-bg-base);
    padding: 0 3rem;
    position: relative;
    overflow: hidden;
  }
  .profile-hero::before {
    content: "";
    position: absolute;
    inset: 0;
    background: linear-gradient(
      135deg,
      color-mix(in srgb, var(--t-brand) 22%, var(--t-bg-base)) 0%,
      color-mix(in srgb, var(--t-brand) 8%, var(--t-bg-base)) 100%
    );
  }
  .profile-cover {
    height: 180px;
    position: relative;
    background: linear-gradient(
      135deg,
      color-mix(in srgb, var(--t-brand) 30%, transparent) 0%,
      color-mix(in srgb, var(--t-brand) 10%, transparent) 60%,
      transparent 100%
    );
    margin: 0 -3rem;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 4rem;
    letter-spacing: 1rem;
    opacity: 0.7;
    overflow: hidden;
  }
  .profile-cover-text {
    font-family: var(--t-font-display);
    font-size: 6rem;
    opacity: 0.15;
    color: var(--t-brand);
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
    background: var(--t-brand-dim);
    border: 4px solid var(--t-bg-base);
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 2.5rem;
    flex-shrink: 0;
    box-shadow: var(--t-shadow-card);
    overflow: hidden;
  }
  .profile-img-fluid {
    width: 100%;
    height: 100%;
    object-fit: cover;
  }
  .profile-text {
    flex: 1;
  }
  .profile-text h1 {
    font-family: var(--t-font-display);
    font-size: 1.8rem;
    color: var(--t-text-heading);
    line-height: 1.2;
    margin: 0;
  }
  .handle {
    color: var(--t-text-muted);
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
    border-radius: var(--t-radius-pill);
    font-size: 0.78rem;
    font-weight: 500;
    display: inline-flex;
    align-items: center;
    gap: 0.3rem;
  }
  .chip-health-good {
    background: var(--t-brand-dim);
    color: var(--t-text-brand);
    border: 1px solid var(--t-brand-muted);
  }
  .chip-borough {
    background: var(--t-bg-hover);
    color: var(--t-text-body);
    border: 1px solid var(--t-border);
  }

  /* ─── Innovative "Plant a Post" Button ─────────────────────────── */

  .new-post-hero-btn {
    margin-left: auto;
    align-self: center;
    position: relative;
    display: inline-flex;
    align-items: center;
    gap: 8px;
    padding: 10px 22px;
    border: none;
    border-radius: var(--t-radius-pill);
    background: linear-gradient(135deg, var(--t-brand), var(--t-brand-glow));
    color: var(--t-bg-base);
    font-size: 0.88rem;
    font-weight: 700;
    font-family: var(--t-font-body);
    cursor: pointer;
    overflow: hidden;
    white-space: nowrap;
    box-shadow:
      0 2px 12px color-mix(in srgb, var(--t-brand) 35%, transparent),
      inset 0 1px 0 rgba(255, 255, 255, 0.2);
    transition:
      transform 0.25s cubic-bezier(0.34, 1.56, 0.64, 1),
      box-shadow 0.3s ease;
    animation: btnBreath 3s ease-in-out infinite;
  }
  @keyframes btnBreath {
    0%, 100% { box-shadow: 0 2px 12px color-mix(in srgb, var(--t-brand) 30%, transparent); }
    50%       { box-shadow: 0 4px 20px color-mix(in srgb, var(--t-brand) 50%, transparent); }
  }
  .new-post-hero-btn:hover {
    transform: scale(1.06);
    box-shadow: 0 6px 24px color-mix(in srgb, var(--t-brand) 50%, transparent);
    animation: none;
  }
  .new-post-hero-btn:active {
    transform: scale(0.97);
  }
  .btn-sprout {
    display: inline-block;
    font-size: 1.1rem;
    transition: transform 0.4s cubic-bezier(0.34, 1.56, 0.64, 1);
  }
  .new-post-hero-btn:hover .btn-sprout {
    transform: scale(1.35) rotate(-8deg);
  }
  .btn-glow {
    position: absolute;
    inset: 0;
    background: linear-gradient(
      105deg,
      transparent 40%,
      rgba(255, 255, 255, 0.25) 50%,
      transparent 60%
    );
    transform: translateX(-100%);
    pointer-events: none;
  }
  .new-post-hero-btn:hover .btn-glow {
    animation: sweep 0.7s ease forwards;
  }
  @keyframes sweep {
    to { transform: translateX(100%); }
  }

  /* ─── Stats & Tabs Row ──────────────────────────────────────────── */
  .profile-stats-tabs {
    position: relative;
    z-index: 1;
    display: flex;
    align-items: center;
    gap: 3rem;
    border-top: 1px solid var(--t-border-soft);
    padding-top: 1rem;
    padding-bottom: 0.5rem;
  }
  .p-stat {
    text-align: center;
  }
  .p-stat .n {
    font-family: var(--t-font-display);
    font-size: 1.6rem;
    color: var(--t-text-heading);
    display: block;
  }
  .p-stat .l {
    font-size: 0.75rem;
    color: var(--t-text-muted);
  }
  .profile-tab-links {
    display: flex;
    gap: 0;
    margin-left: auto;
  }
  .profile-tab {
    background: none;
    border: none;
    color: var(--t-text-muted);
    padding: 0.6rem 1.2rem;
    cursor: pointer;
    font-family: var(--t-font-body);
    font-size: 0.85rem;
    border-bottom: 2px solid transparent;
    transition: all var(--t-transition);
  }
  .profile-tab:hover {
    color: var(--t-text-heading);
  }
  .profile-tab.active {
    color: var(--t-text-heading);
    border-bottom-color: var(--t-brand);
    font-weight: 600;
  }

  /* ─── Body Grid (posts + sidebar) ───────────────────────────────── */
  .profile-body {
    max-width: var(--t-content-max);
    margin: 0 auto;
    padding: 2rem 1.5rem;
    display: grid;
    grid-template-columns: 1fr 260px;
    gap: 1.5rem;
    opacity: 0;
    transform: translateY(16px);
    transition:
      opacity var(--t-transition-slow) 0.15s,
      transform var(--t-transition-slow) 0.15s;
  }
  .page.mounted .profile-body {
    opacity: 1;
    transform: translateY(0);
  }

  /* ─── Posts Grid ────────────────────────────────────────────────── */
  .profile-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 0.8rem;
  }
  .profile-post {
    aspect-ratio: 1;
    border-radius: var(--t-radius-md);
    background: var(--t-bg-surface);
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 2.5rem;
    cursor: pointer;
    position: relative;
    overflow: hidden;
    transition: transform var(--t-transition);
    border: 1px solid var(--t-border-soft);
  }
  .profile-post:hover {
    transform: scale(0.97);
  }
  .profile-post.n0 { background: var(--t-bg-surface); }
  .profile-post.n1 { background: var(--t-bg-elevated); }
  .profile-post.n2 { background: var(--t-bg-surface); }
  .profile-post.n3 { background: var(--t-bg-elevated); }
  .profile-post.n4 { background: var(--t-bg-surface); }
  .profile-post.n5 { background: var(--t-bg-elevated); }
  .post-img {
    width: 100%;
    height: 100%;
    object-fit: cover;
    position: absolute;
    inset: 0;
  }
  .post-emoji {
    font-size: 2.5rem;
    position: relative;
    z-index: 1;
  }
  .post-hover {
    position: absolute;
    inset: 0;
    background: var(--t-bg-overlay);
    opacity: 0;
    transition: opacity var(--t-transition);
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: 0.5rem;
    color: var(--t-text-heading);
    font-size: 0.85rem;
    z-index: 2;
  }
  .profile-post:hover .post-hover {
    opacity: 1;
  }

  /* ─── Loading & Empty ───────────────────────────────────────────── */
  .loading-area {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 1rem;
    padding: 4rem 1rem;
    color: var(--t-text-muted);
    font-size: 0.9rem;
  }
  .loading-spinner {
    width: 30px;
    height: 30px;
    border: 3px solid var(--t-border);
    border-top-color: var(--t-brand);
    border-radius: 50%;
    animation: spin 0.8s linear infinite;
  }
  @keyframes spin {
    to { transform: rotate(360deg); }
  }
  .empty-state {
    text-align: center;
    padding: 4rem 1rem;
  }
  .empty-icon {
    font-size: 4rem;
    display: block;
    margin-bottom: 0.8rem;
  }
  .empty-state h3 {
    font-size: 1.4rem;
    font-weight: 300;
    color: var(--t-text-heading);
    margin: 0 0 0.4rem;
  }
  .empty-state p {
    color: var(--t-text-muted);
    font-size: 0.9rem;
    margin: 0 0 1.2rem;
  }

  /* ─── Followed Trees Grid ───────────────────────────────────────── */
  .followed-trees-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
    gap: 1.2rem;
    padding: 0.5rem 0;
  }
  .followed-tree-card {
    background: linear-gradient(145deg, var(--t-bg-elevated), var(--t-bg-surface));
    border: 1px solid var(--t-border-soft);
    border-radius: 16px;
    padding: 18px;
    position: relative;
    overflow: hidden;
    cursor: pointer;
    box-shadow: 0 4px 15px rgba(0,0,0,0.04);
    transition: all 0.4s cubic-bezier(0.16, 1, 0.3, 1);
    display: flex;
    flex-direction: column;
    gap: 14px;
    animation: fadeUp 0.5s both;
  }
  .followed-tree-card:hover {
    transform: translateY(-4px) scale(1.01);
    box-shadow: 0 12px 30px rgba(45, 122, 58, 0.12), inset 0 1px 2px rgba(255,255,255,0.4);
    border-color: rgba(82, 154, 103, 0.4);
  }
  .ft-header {
    display: flex;
    align-items: center;
    gap: 12px;
  }
  .ft-icon {
    width: 44px;
    height: 44px;
    border-radius: 12px;
    background: linear-gradient(135deg, rgba(82,154,103,0.15), rgba(45,122,58,0.05));
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.5rem;
    box-shadow: inset 0 2px 4px rgba(255,255,255,0.3);
  }
  .ft-info {
    display: flex;
    flex-direction: column;
    gap: 2px;
  }
  .ft-name {
    margin: 0;
    font-size: 1rem;
    font-weight: 700;
    color: var(--t-text-heading);
    text-transform: capitalize;
  }
  .ft-id {
    font-family: 'DM Mono', monospace;
    font-size: 0.75rem;
    color: var(--t-text-brand);
    font-weight: 600;
  }
  .ft-body {
    flex: 1;
    display: flex;
    flex-direction: column;
    gap: 6px;
  }
  .ft-date {
    margin: 0;
    font-size: 0.78rem;
    color: var(--t-text-muted);
  }
  .ft-chat {
    margin: 0;
    font-size: 0.72rem;
    font-weight: 600;
    color: var(--t-status-good);
    background: rgba(45, 122, 58, 0.08);
    display: inline-block;
    padding: 3px 8px;
    border-radius: 8px;
    align-self: flex-start;
  }
  .ft-action {
    display: flex;
    justify-content: flex-end;
  }
  .ft-btn {
    background: transparent;
    border: none;
    color: var(--t-text-brand);
    font-weight: 700;
    font-size: 0.8rem;
    padding: 6px 0;
    cursor: pointer;
    transition: transform 0.2s ease;
  }
  .followed-tree-card:hover .ft-btn {
    transform: translateX(4px);
  }
  .ft-glow {
    position: absolute;
    top: 0;
    left: -100%;
    width: 50%;
    height: 100%;
    background: linear-gradient(to right, transparent, rgba(255,255,255,0.4), transparent);
    transform: skewX(-20deg);
    transition: none;
  }
  .followed-tree-card:hover .ft-glow {
    animation: ftSweep 0.8s ease-in-out;
  }
  @keyframes ftSweep {
    0%   { left: -100%; }
    100% { left: 200%; }
  }

  /* ─── Admin Panel ───────────────────────────────────────────────── */
  .admin-panel-title {
    font-family: var(--t-font-display);
    font-size: 1.4rem;
    color: var(--t-text-heading);
    margin: 0 0 1.2rem;
    padding-bottom: 0.8rem;
    border-bottom: 1px solid var(--t-border-soft);
  }
  .app-list {
    display: flex;
    flex-direction: column;
    gap: 1rem;
  }
  .app-card {
    display: flex;
    align-items: center;
    gap: 1rem;
    background: var(--t-bg-surface);
    border: 1px solid var(--t-border);
    border-radius: var(--t-radius-md);
    padding: 1.2rem;
    cursor: pointer;
    transition: all var(--t-transition);
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
  }
  .app-card:hover {
    transform: translateY(-2px);
    border-color: var(--t-brand-muted);
    box-shadow: 0 6px 16px rgba(0, 0, 0, 0.08);
  }
  .app-avatar {
    width: 44px;
    height: 44px;
    border-radius: 50%;
    background: linear-gradient(135deg, var(--t-brand-dim), var(--t-brand-muted));
    color: var(--t-text-brand);
    font-weight: bold;
    font-size: 1.2rem;
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
  }
  .app-info {
    flex: 1;
    display: flex;
    flex-direction: column;
  }
  .app-user {
    font-size: 1rem;
    color: var(--t-text-heading);
  }
  .app-tree {
    font-size: 0.82rem;
    color: var(--t-text-muted);
    margin-top: 2px;
  }
  .app-tree strong {
    color: var(--t-text-body);
  }
  .app-actions {
    display: flex;
    gap: 0.6rem;
  }
  .btn-approve, .btn-reject {
    padding: 0.5rem 1rem;
    border-radius: var(--t-radius-pill);
    font-size: 0.8rem;
    font-weight: 600;
    cursor: pointer;
    border: none;
    transition: all var(--t-transition);
  }
  .btn-approve {
    background: var(--t-status-good);
    color: white;
  }
  .btn-approve:hover {
    background: #2e8b57;
    transform: scale(1.05);
  }
  .btn-reject {
    background: var(--t-bg-hover);
    color: var(--t-text-body);
    border: 1px solid var(--t-border);
  }
  .btn-reject:hover {
    background: #fee2e2;
    color: var(--t-status-poor);
    border-color: var(--t-status-poor);
  }

  /* ─── Application Detail Modal ──────────────────────────────────── */
  .app-modal {
    flex-direction: column;
    max-width: 600px;
    background: var(--t-bg-surface);
  }
  .app-modal-header {
    display: flex;
    align-items: center;
    gap: 1rem;
    padding: 1.5rem 2rem;
    border-bottom: 1px solid var(--t-border-soft);
    background: linear-gradient(to bottom, var(--t-bg-elevated), var(--t-bg-surface));
  }
  .app-modal-avatar {
    width: 50px;
    height: 50px;
    border-radius: 50%;
    background: var(--t-brand);
    color: white;
    font-size: 1.5rem;
    font-weight: bold;
    display: flex;
    align-items: center;
    justify-content: center;
  }
  .app-modal-title h2 {
    margin: 0;
    font-family: var(--t-font-display);
    font-size: 1.3rem;
    color: var(--t-text-heading);
  }
  .app-modal-title span {
    font-size: 0.85rem;
    color: var(--t-text-muted);
  }
  .app-modal-title strong {
    color: var(--t-text-brand);
  }
  .app-modal-body {
    padding: 1.5rem 2rem;
    overflow-y: auto;
    display: flex;
    flex-direction: column;
    gap: 1.8rem;
  }
  .form-section {
    display: flex;
    flex-direction: column;
    gap: 0.6rem;
  }
  .section-title {
    font-size: 0.95rem;
    font-weight: 700;
    color: var(--t-text-heading);
    margin: 0;
    display: flex;
    align-items: center;
    gap: 8px;
    text-transform: uppercase;
    letter-spacing: 0.04em;
  }
  .section-dot {
    width: 8px;
    height: 8px;
    background: var(--t-brand);
    border-radius: 50%;
    display: inline-block;
  }
  .app-read-text {
    font-size: 0.95rem;
    line-height: 1.6;
    color: var(--t-text-body);
    margin: 0;
    background: var(--t-bg-elevated);
    padding: 1rem;
    border-radius: var(--t-radius-md);
    border: 1px solid var(--t-border-soft);
  }
  .app-detail-card {
    display: inline-flex;
    align-items: center;
    gap: 10px;
    background: var(--t-brand-dim);
    border: 1px solid var(--t-brand-muted);
    padding: 0.8rem 1.2rem;
    border-radius: var(--t-radius-md);
    color: var(--t-text-heading);
  }
  .detail-icon { font-size: 1.4rem; }
  .app-modal-actions {
    display: flex;
    gap: 1rem;
    padding: 1.2rem 2rem;
    border-top: 1px solid var(--t-border-soft);
    background: var(--t-bg-elevated);
    justify-content: flex-end;
  }
  .btn-wizard-reject, .btn-wizard-approve {
    padding: 0.8rem 1.5rem;
    border-radius: var(--t-radius-pill);
    font-size: 0.9rem;
    font-weight: 600;
    cursor: pointer;
    border: none;
    transition: all 0.2s ease;
  }
  .btn-wizard-reject {
    background: var(--t-bg-surface);
    color: var(--t-status-poor);
    border: 1px solid var(--t-border);
  }
  .btn-wizard-reject:hover {
    background: #fee2e2;
    border-color: #fca5a5;
  }
  .btn-wizard-approve {
    background: linear-gradient(135deg, var(--t-status-good), #2e8b57);
    color: white;
    box-shadow: 0 4px 12px rgba(46, 139, 87, 0.3);
  }
  .btn-wizard-approve:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 16px rgba(46, 139, 87, 0.4);
  }

  /* ─── Right Sidebar Cards ───────────────────────────────────────── */
  .profile-right-card {
    background: var(--t-bg-elevated);
    border-radius: var(--t-radius-lg);
    padding: 1.4rem;
    box-shadow: var(--t-shadow-card);
    border: 1px solid var(--t-border);
    margin-bottom: 1rem;
  }
  .profile-right-card h3 {
    font-size: 0.75rem;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: var(--t-text-brand);
    margin-bottom: 1rem;
  }
  .about-text {
    font-size: 0.85rem;
    color: var(--t-text-body);
    line-height: 1.6;
    margin: 0;
  }
  .recent-post-item {
    display: flex;
    align-items: center;
    gap: 0.7rem;
    padding: 0.5rem 0;
    border-bottom: 1px solid var(--t-border-soft);
    cursor: pointer;
    transition: background var(--t-transition);
    border-radius: var(--t-radius-sm);
  }
  .recent-post-item:hover {
    background: var(--t-bg-hover);
  }
  .recent-post-item:last-child {
    border: none;
  }
  .rp-icon {
    width: 32px;
    height: 32px;
    border-radius: var(--t-radius-sm);
    background: var(--t-brand-dim);
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 0.9rem;
    flex-shrink: 0;
  }
  .rp-info {
    flex: 1;
    min-width: 0;
  }
  .rp-info strong {
    display: block;
    font-size: 0.82rem;
    color: var(--t-text-heading);
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }
  .rp-info small {
    font-size: 0.72rem;
    color: var(--t-text-muted);
  }
  .health-badge {
    font-size: 0.65rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    padding: 0.15rem 0.4rem;
    border-radius: var(--t-radius-sm);
  }
  .health-good { background: var(--t-role-standard-bg); color: var(--t-status-good); }
  .health-fair { background: var(--t-role-credible-bg); color: var(--t-status-fair); }
  .health-poor { background: var(--t-role-admin-bg); color: var(--t-status-poor); }

  /* ─── Progress Bars ─────────────────────────────────────────────── */
  .progress-item { margin-bottom: 0.8rem; }
  .progress-header {
    display: flex;
    justify-content: space-between;
    font-size: 0.8rem;
    margin-bottom: 0.3rem;
  }
  .progress-label { color: var(--t-text-muted); }
  .progress-met { color: var(--t-status-good); font-weight: 600; }
  .progress-track {
    height: 6px;
    background: var(--t-border-soft);
    border-radius: var(--t-radius-sm);
    overflow: hidden;
  }
  .progress-fill {
    height: 100%;
    border-radius: var(--t-radius-sm);
    background: var(--t-brand);
    transition: width 0.6s ease;
  }
  .credible-banner {
    margin-top: 0.8rem;
    background: var(--t-brand-dim);
    border: 1px solid var(--t-brand-muted);
    border-radius: var(--t-radius-sm);
    padding: 0.6rem;
    font-size: 0.82rem;
    color: var(--t-text-brand);
    text-align: center;
  }

  /* ─── Caretaker Apply Button ────────────────────────────────────── */
  .caretaker-apply-btn {
    display: inline-flex;
    align-items: center;
    gap: 0.4rem;
    padding: 0.55rem 1.25rem;
    background: #3a6b4a;
    color: #fff;
    font-size: 0.875rem;
    font-weight: 600;
    border: none;
    border-radius: 20px;
    cursor: pointer;
    transition:
      background 0.2s ease,
      transform 0.15s ease,
      box-shadow 0.2s ease;
    box-shadow: 0 2px 8px rgba(58, 107, 74, 0.3);
    letter-spacing: 0.01em;
  }
  .caretaker-apply-btn:hover {
    background: #2f5a3e;
    transform: translateY(-1px);
    box-shadow: 0 4px 12px rgba(58, 107, 74, 0.4);
  }
  .caretaker-apply-btn:active {
    transform: translateY(0);
    box-shadow: 0 2px 6px rgba(58, 107, 74, 0.25);
  }
  .caretaker-apply-btn.disabled,
  .caretaker-apply-btn[disabled] {
    background: #c8d8c8;
    color: #8fa88f;
    cursor: not-allowed;
    box-shadow: none;
    transform: none;
  }
  .caretaker-hint {
    margin-top: 0.5rem;
    font-size: 0.8rem;
    color: #9aad9a;
    font-style: italic;
  }

  /* ─── Modal Base ────────────────────────────────────────────────── */
  .modal-backdrop {
    position: fixed;
    inset: 0;
    background: rgba(0, 0, 0, 0.72);
    backdrop-filter: blur(8px);
    -webkit-backdrop-filter: blur(8px);
    z-index: 1000;
    display: flex;
    align-items: center;
    justify-content: center;
    animation: modalFadeIn 0.3s ease;
  }
  @keyframes modalFadeIn {
    from { opacity: 0; }
    to   { opacity: 1; }
  }
  .modal {
    position: relative;
    background: var(--t-bg-surface);
    border-radius: 16px;
    display: flex;
    max-width: 920px;
    width: 94vw;
    max-height: 88vh;
    overflow: hidden;
    box-shadow:
      0 32px 80px rgba(0, 0, 0, 0.45),
      0 0 0 1px var(--t-border-soft),
      inset 0 1px 0 rgba(255, 255, 255, 0.04);
    animation: modalSlideUp 0.35s cubic-bezier(0.34, 1.56, 0.64, 1);
    border: 1px solid var(--t-border);
  }
  @keyframes modalSlideUp {
    from { opacity: 0; transform: translateY(30px) scale(0.97); }
    to   { opacity: 1; transform: translateY(0) scale(1); }
  }
  .modal-close-btn {
    position: absolute;
    top: 12px;
    right: 12px;
    z-index: 10;
    width: 34px;
    height: 34px;
    border-radius: 50%;
    background: var(--t-bg-overlay);
    backdrop-filter: blur(4px);
    border: 1px solid var(--t-border-soft);
    color: var(--t-text-muted);
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: all 0.2s ease;
  }
  .modal-close-btn:hover {
    background: var(--t-bg-active);
    color: var(--t-text-heading);
    transform: rotate(90deg);
  }

   /* Image panel */
    .modal-image {
      flex: 1;
      background: var(--t-bg-photo);
      display: flex;
      align-items: center;
      justify-content: center;
      min-height: 420px;
      max-width: 55%;
      position: relative;
      overflow: hidden;
    }
    .modal-image img {
      width: 100%;
      height: 100%;
      object-fit: contain;
    }
    .modal-placeholder {
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      gap: 0.8rem;
      width: 100%;
      height: 100%;
      background: linear-gradient(160deg, var(--t-brand-dim), var(--t-bg-surface));
    }
    .modal-placeholder-emoji {
      font-size: 5rem;
      filter: drop-shadow(0 4px 12px rgba(0,0,0,0.15));
      animation: floatEmoji 3s ease-in-out infinite;
    }
    @keyframes floatEmoji {
      0%, 100% { transform: translateY(0); }
      50%      { transform: translateY(-8px); }
    }
    .modal-placeholder-label {
      font-family: var(--t-font-display);
      font-size: 1rem;
      color: var(--t-text-muted);
      letter-spacing: 0.02em;
    }

    .modal-details {
      width: 360px;
      display: flex;
      flex-direction: column;
      background: var(--t-bg-elevated);
      border-left: 1px solid var(--t-border-soft);
    }
  
    /* Header */
    .modal-header {
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 16px 18px;
      border-bottom: 1px solid var(--t-border-soft);
    }
    .modal-author {
      display: flex;
      align-items: center;
      gap: 10px;
    }
    .modal-avatar {
      width: 38px;
      height: 38px;
      border-radius: 50%;
      object-fit: cover;
      border: 2px solid var(--t-brand-muted);
    }
    .modal-avatar-placeholder {
      width: 38px;
      height: 38px;
      border-radius: 50%;
      background: linear-gradient(135deg, var(--t-brand), var(--t-brand-glow));
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 0.85rem;
      font-weight: 700;
      color: var(--t-bg-base);
    }
    .modal-author-info {
      display: flex;
      flex-direction: column;
    }
    .modal-author strong {
      font-size: 0.88rem;
      color: var(--t-text-heading);
      line-height: 1.2;
    }
    .modal-loc {
      font-size: 0.72rem;
      color: var(--t-text-muted);
      margin-top: 1px;
    }
  
    /* ─── 3-Dot Menu & Delete Confirm ─────────────────────────────── */
    .post-menu-wrapper {
      position: relative;
    }
    .post-menu-trigger {
      background: none;
      border: none;
      color: var(--t-text-muted);
      cursor: pointer;
      padding: 4px;
      border-radius: 50%;
      display: flex;
      align-items: center;
      justify-content: center;
      transition: all 0.2s ease;
    }
    .post-menu-trigger:hover {
      background: var(--t-bg-hover);
      color: var(--t-text-heading);
    }
    .post-menu-dropdown {
      position: absolute;
      top: calc(100% + 6px);
      right: 0;
      min-width: 180px;
      background: var(--t-bg-surface);
      border: 1px solid var(--t-border);
      border-radius: 12px;
      box-shadow:
        0 12px 40px rgba(0,0,0,0.3),
        0 0 0 1px var(--t-border-soft);
      z-index: 20;
      overflow: hidden;
      animation: menuDrop 0.2s cubic-bezier(0.16, 1, 0.3, 1);
    }
    @keyframes menuDrop {
      from { opacity: 0; transform: translateY(-6px) scale(0.95); }
      to   { opacity: 1; transform: translateY(0) scale(1); }
    }
    .menu-item {
      display: flex;
      align-items: center;
      gap: 10px;
      width: 100%;
      padding: 11px 16px;
      border: none;
      background: none;
      font-size: 0.84rem;
      font-family: var(--t-font-body);
      color: var(--t-text-body);
      cursor: pointer;
      transition: background 0.15s ease;
      text-align: left;
    }
    .menu-item:hover {
      background: var(--t-bg-hover);
    }
    .menu-item-danger {
      color: var(--t-status-poor);
      font-weight: 600;
    }
    .menu-item-danger:hover {
      background: rgba(248, 113, 113, 0.08);
    }
  
    /* Inline delete confirmation */
    .delete-confirm-panel {
      padding: 16px;
      text-align: center;
      animation: menuDrop 0.2s ease;
    }
    .delete-confirm-icon {
      font-size: 1.6rem;
      margin-bottom: 6px;
    }
    .delete-confirm-text {
      font-size: 0.82rem;
      color: var(--t-text-body);
      margin: 0 0 12px;
      line-height: 1.4;
    }
    .delete-confirm-actions {
      display: flex;
      gap: 8px;
    }
    .confirm-cancel-btn {
      flex: 1;
      padding: 8px 14px;
      border-radius: 8px;
      font-size: 0.8rem;
      font-weight: 600;
      font-family: var(--t-font-body);
      border: 1px solid var(--t-border);
      background: var(--t-bg-hover);
      color: var(--t-text-body);
      cursor: pointer;
      transition: all 0.15s ease;
    }
    .confirm-cancel-btn:hover:not(:disabled) {
      background: var(--t-bg-active);
      color: var(--t-text-heading);
    }
    .confirm-delete-btn {
      flex: 1;
      padding: 8px 14px;
      border-radius: 8px;
      font-size: 0.8rem;
      font-weight: 600;
      font-family: var(--t-font-body);
      border: none;
      background: var(--t-status-poor);
      color: #fff;
      cursor: pointer;
      transition: all 0.15s ease;
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 6px;
    }
    .confirm-delete-btn:hover:not(:disabled) {
      background: #ef4444;
      transform: translateY(-1px);
      box-shadow: 0 4px 12px rgba(248, 113, 113, 0.3);
    }
    .confirm-delete-btn:disabled,
    .confirm-cancel-btn:disabled {
      opacity: 0.5;
      cursor: not-allowed;
    }
    .btn-spinner-sm {
      display: inline-block;
      width: 12px;
      height: 12px;
      border: 2px solid rgba(255,255,255,0.3);
      border-top-color: #fff;
      border-radius: 50%;
      animation: spin 0.6s linear infinite;
    }

    /* ─── Modal Body ─────────────────────────────────────────────── */
    .modal-body {
      flex: 1;
      overflow-y: auto;
      padding: 18px 20px;
    }
    .modal-body::-webkit-scrollbar {
      width: 4px;
    }
    .modal-body::-webkit-scrollbar-thumb {
      background: var(--t-border);
      border-radius: 4px;
    }
  
    /* Tree info card */
    .modal-tree-card {
      display: flex;
      align-items: center;
      gap: 12px;
      padding: 12px 14px;
      background: var(--t-brand-dim);
      border: 1px solid var(--t-brand-muted);
      border-radius: 10px;
      margin-bottom: 14px;
    }
    .modal-tree-icon {
      font-size: 1.8rem;
      flex-shrink: 0;
    }
    .modal-tree-info {
      display: flex;
      align-items: center;
      gap: 8px;
      flex: 1;
      min-width: 0;
    }
    .modal-tree-name {
      font-weight: 700;
      font-size: 0.92rem;
      color: var(--t-text-heading);
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }
    .modal-text {
      font-size: 0.86rem;
      color: var(--t-text-body);
      line-height: 1.6;
      margin: 0 0 10px;
    }
    .modal-tagged {
      display: flex;
      align-items: center;
      gap: 6px;
      font-size: 0.8rem;
      color: var(--t-text-brand);
      margin: 0 0 8px;
      font-weight: 500;
      padding: 6px 10px;
      background: var(--t-brand-dim);
      border-radius: 6px;
      border: 1px solid var(--t-brand-muted);
    }
    .modal-time {
      font-size: 0.7rem;
      color: var(--t-text-faint);
      text-transform: uppercase;
      letter-spacing: 0.04em;
      display: block;
      margin-bottom: 2px;
    }
  
    /* Comments */
    .modal-comments {
      margin-top: 16px;
      border-top: 1px solid var(--t-border-soft);
      padding-top: 12px;
    }
    .comments-header {
      display: flex;
      align-items: center;
      gap: 8px;
      margin-bottom: 12px;
    }
    .comments-label {
      font-size: 0.75rem;
      font-weight: 600;
      text-transform: uppercase;
      letter-spacing: 0.06em;
      color: var(--t-text-muted);
    }
    .comments-count {
      font-size: 0.68rem;
      font-weight: 600;
      background: var(--t-bg-hover);
      color: var(--t-text-muted);
      padding: 2px 7px;
      border-radius: 10px;
    }
    .modal-comment {
      display: flex;
      align-items: flex-start;
      gap: 10px;
      margin-bottom: 12px;
      animation: commentFade 0.25s ease;
    }
    @keyframes commentFade {
      from { opacity: 0; transform: translateY(4px); }
      to   { opacity: 1; transform: translateY(0); }
    }
    .comment-avatar {
      width: 28px;
      height: 28px;
      border-radius: 50%;
      background: var(--t-bg-active);
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 0.68rem;
      font-weight: 700;
      color: var(--t-text-brand);
      flex-shrink: 0;
    }
    .comment-content {
      font-size: 0.84rem;
      line-height: 1.45;
      color: var(--t-text-body);
    }
    .comment-content strong {
      color: var(--t-text-heading);
      margin-right: 5px;
      font-size: 0.82rem;
    }
    .comment-actions {
      display: flex;
      gap: 2px;
      opacity: 0;
      transition: opacity var(--t-transition);
      flex-shrink: 0;
      margin-left: auto;
    }
    .modal-comment:hover .comment-actions {
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
      flex: 1;
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
    .no-comments {
      display: flex;
      flex-direction: column;
      align-items: center;
      gap: 6px;
      padding: 16px 0;
      color: var(--t-text-faint);
      font-size: 0.8rem;
    }
    .no-comments-icon {
      font-size: 1.4rem;
      opacity: 0.4;
    }
  
    /* ─── Action Bar ─────────────────────────────────────────────── */
    .modal-actions {
      border-top: 1px solid var(--t-border-soft);
      padding: 12px 18px 14px;
      background: var(--t-bg-elevated);
    }
    .action-row {
      display: flex;
      align-items: center;
      gap: 10px;
      margin-bottom: 10px;
    }
    .like-btn {
      background: none;
      border: none;
      padding: 4px;
      cursor: pointer;
      color: var(--t-text-muted);
      display: flex;
      align-items: center;
      transition: all 0.2s ease;
    }
    .like-btn:hover {
      transform: scale(1.15);
    }
    .like-btn.liked {
      color: #ef4444;
      animation: heartBounce 0.35s cubic-bezier(0.34, 1.56, 0.64, 1);
    }
    @keyframes heartBounce {
      0%   { transform: scale(1); }
      40%  { transform: scale(1.3); }
      100% { transform: scale(1); }
    }
    .like-icon {
      display: block;
    }
    .likes-count {
      font-size: 0.84rem;
      font-weight: 600;
      color: var(--t-text-heading);
    }
  
    /* Comment input */
    .comment-input-row {
      display: flex;
      gap: 8px;
      align-items: center;
      background: var(--t-bg-input);
      border: 1px solid var(--t-border-input);
      border-radius: 24px;
      padding: 2px 4px 2px 16px;
      transition: border-color var(--t-transition), box-shadow var(--t-transition);
    }
    .comment-input-row:focus-within {
      border-color: var(--t-brand);
      box-shadow: 0 0 0 3px color-mix(in srgb, var(--t-brand) 12%, transparent);
    }
    .comment-input-row input {
      flex: 1;
      border: none;
      outline: none;
      font-size: 0.84rem;
      font-family: var(--t-font-body);
      color: var(--t-text-heading);
      padding: 8px 0;
      background: transparent;
    }
    .comment-input-row input::placeholder {
      color: var(--t-text-muted);
    }
    .post-comment-btn {
      width: 34px;
      height: 34px;
      border-radius: 50%;
      border: none;
      background: linear-gradient(135deg, var(--t-brand), var(--t-brand-glow));
      color: var(--t-bg-base);
      cursor: pointer;
      display: flex;
      align-items: center;
      justify-content: center;
      flex-shrink: 0;
      transition: all 0.2s ease;
    }
    .post-comment-btn:hover:not(:disabled) {
      transform: scale(1.08);
      box-shadow: 0 2px 8px color-mix(in srgb, var(--t-brand) 40%, transparent);
    }
    .post-comment-btn:disabled {
      opacity: 0.3;
      cursor: default;
      transform: none;
    }
  
  /* ─── Followed Trees Grid (Scintillating UI) ────────── */
  .followed-trees-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
    gap: 1.2rem;
    padding: 0.5rem 0;
  }
  .followed-tree-card {
    background: linear-gradient(145deg, var(--t-bg-elevated), var(--t-bg-surface));
    border: 1px solid var(--t-border-soft);
    border-radius: 16px;
    padding: 18px;
    position: relative;
    overflow: hidden;
    cursor: pointer;
    box-shadow: 0 4px 15px rgba(0,0,0,0.04);
    transition: all 0.4s cubic-bezier(0.16, 1, 0.3, 1);
    display: flex;
    flex-direction: column;
    gap: 14px;
    animation: fadeUp 0.5s both;
  }
  .followed-tree-card:hover {
    transform: translateY(-4px) scale(1.01);
    box-shadow: 0 12px 30px rgba(45, 122, 58, 0.12), inset 0 1px 2px rgba(255,255,255,0.4);
    border-color: rgba(82, 154, 103, 0.4);
  }
  .ft-header {
    display: flex;
    align-items: center;
    gap: 12px;
  }
  .ft-icon {
    width: 44px;
    height: 44px;
    border-radius: 12px;
    background: linear-gradient(135deg, rgba(82,154,103,0.15), rgba(45,122,58,0.05));
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.5rem;
    box-shadow: inset 0 2px 4px rgba(255,255,255,0.3);
  }
  .ft-info {
    display: flex;
    flex-direction: column;
    gap: 2px;
  }
  .ft-name {
    margin: 0;
    font-size: 1rem;
    font-weight: 700;
    color: var(--t-text-heading);
    text-transform: capitalize;
  }
  .ft-id {
    font-family: 'DM Mono', monospace;
    font-size: 0.75rem;
    color: var(--t-text-brand);
    font-weight: 600;
  }
  .ft-body {
    flex: 1;
    display: flex;
    flex-direction: column;
    gap: 6px;
  }
  .ft-date {
    margin: 0;
    font-size: 0.78rem;
    color: var(--t-text-muted);
  }
  .ft-chat {
    margin: 0;
    font-size: 0.72rem;
    font-weight: 600;
    color: var(--t-status-good);
    background: rgba(45, 122, 58, 0.08);
    display: inline-block;
    padding: 3px 8px;
    border-radius: 8px;
    align-self: flex-start;
  }
  .ft-action {
    display: flex;
    justify-content: flex-end;
  }
  .ft-btn {
    background: transparent;
    border: none;
    color: var(--t-text-brand);
    font-weight: 700;
    font-size: 0.8rem;
    padding: 6px 0;
    cursor: pointer;
    transition: transform 0.2s ease;
  }
  .followed-tree-card:hover .ft-btn {
    transform: translateX(4px);
  }
  .ft-glow {
    position: absolute;
    top: 0;
    left: -100%;
    width: 50%;
    height: 100%;
    background: linear-gradient(to right, transparent, rgba(255,255,255,0.4), transparent);
    transform: skewX(-20deg);
    transition: none;
  }
  .followed-tree-card:hover .ft-glow {
    animation: ftSweep 0.8s ease-in-out;
  }
  @keyframes ftSweep {
    0% { left: -100%; }
    100% { left: 200%; }
  }


    /* ─── Responsive ────────────────────────────────────────────────── */
    @media (max-width: 768px) {
      .profile-hero {
        padding: 0 1rem;
      }
      .profile-cover {
        margin: 0 -1rem;
        height: 120px;
      }
      .profile-info-bar {
        flex-wrap: wrap;
      }
      .profile-stats-tabs {
        flex-wrap: wrap;
        gap: 1.5rem;
      }
      .profile-body {
        grid-template-columns: 1fr;
        padding: 1rem;
      }
      .profile-grid {
        grid-template-columns: repeat(3, 1fr);
        gap: 0.4rem;
      }
      .modal {
        flex-direction: column;
        max-height: 92vh;
        border-radius: 12px;
        width: 96vw;
      }
      .modal-close-btn {
        top: 8px;
        right: 8px;
        width: 30px;
        height: 30px;
      }
      .modal-image {
        max-width: 100%;
        min-height: 220px;
        max-height: 280px;
      }
      .modal-details {
        width: 100%;
        border-left: none;
        border-top: 1px solid var(--t-border-soft);
      }
      .post-menu-dropdown {
        right: -4px;
      }
    }

  /* ─── Create Post Carousel Modal ─────────────────────────────────── */
  .carousel-backdrop {
    position: fixed;
    inset: 0;
    background: rgba(0, 0, 0, 0.6);
    backdrop-filter: blur(6px);
    z-index: 1100;
    display: flex;
    align-items: center;
    justify-content: center;
    animation: cFadeIn 0.25s ease;
  }
  @keyframes cFadeIn {
    from { opacity: 0; }
    to   { opacity: 1; }
  }
  .carousel-modal {
    background: var(--t-bg-elevated);
    border: 1px solid var(--t-border);
    border-radius: 20px;
    width: 480px;
    max-width: 94vw;
    max-height: 90vh;
    display: flex;
    flex-direction: column;
    overflow: hidden;
    box-shadow:
      0 24px 64px rgba(0, 0, 0, 0.3),
      0 0 0 1px var(--t-border-soft);
    animation: cSlideUp 0.35s cubic-bezier(0.34, 1.56, 0.64, 1);
  }
  @keyframes cSlideUp {
    from { opacity: 0; transform: translateY(40px) scale(0.96); }
    to   { opacity: 1; transform: translateY(0) scale(1); }
  }
  .carousel-header {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 18px 20px 14px;
    border-bottom: 1px solid var(--t-border-soft);
    position: relative;
  }
  .carousel-header h2 {
    font-family: var(--t-font-display);
    font-size: 1.15rem;
    color: var(--t-text-heading);
    margin: 0;
    flex: 1;
  }
  .carousel-close {
    position: absolute;
    right: 16px;
    top: 50%;
    transform: translateY(-50%);
    background: var(--t-bg-hover);
    border: none;
    border-radius: 50%;
    width: 30px;
    height: 30px;
    font-size: 0.85rem;
    color: var(--t-text-muted);
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: background var(--t-transition), color var(--t-transition);
  }
  .carousel-close:hover {
    background: var(--t-bg-active);
    color: var(--t-status-poor);
  }
  .step-dots {
    display: flex;
    gap: 6px;
    margin-right: 42px;
  }
  .dot {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background: var(--t-border);
    transition: all 0.35s ease;
  }
  .dot.active {
    width: 22px;
    border-radius: 4px;
    background: var(--t-brand);
  }
  .dot.done {
    background: var(--t-brand-muted);
  }
  .carousel-body {
    flex: 1;
    overflow: hidden;
    position: relative;
    min-height: 340px;
  }
  .carousel-track {
    width: 100%;
    height: 100%;
  }
  .carousel-slide {
    padding: 28px 28px 16px;
    display: flex;
    flex-direction: column;
    align-items: center;
    text-align: center;
    animation: slideEnter 0.35s cubic-bezier(0.25, 0.46, 0.45, 0.94) both;
  }
  .slide-next .carousel-slide { animation-name: slideFromRight; }
  .slide-prev .carousel-slide { animation-name: slideFromLeft; }
  @keyframes slideFromRight {
    from { opacity: 0; transform: translateX(50px); }
    to   { opacity: 1; transform: translateX(0); }
  }
  @keyframes slideFromLeft {
    from { opacity: 0; transform: translateX(-50px); }
    to   { opacity: 1; transform: translateX(0); }
  }
  @keyframes slideEnter {
    from { opacity: 0; transform: translateY(10px); }
    to   { opacity: 1; transform: translateY(0); }
  }
  .slide-icon {
    font-size: 2.8rem;
    margin-bottom: 8px;
    animation: bounceIcon 0.5s 0.15s cubic-bezier(0.34, 1.56, 0.64, 1) both;
  }
  @keyframes bounceIcon {
    from { transform: scale(0.5); opacity: 0; }
    to   { transform: scale(1); opacity: 1; }
  }
  .slide-title {
    font-family: var(--t-font-display);
    font-size: 1.2rem;
    color: var(--t-text-heading);
    margin: 0 0 4px;
  }
  .slide-subtitle {
    font-size: 0.82rem;
    color: var(--t-text-muted);
    margin: 0 0 20px;
  }
  .slide-skip {
    font-size: 0.75rem;
    color: var(--t-text-faint);
    margin-top: 12px;
  }
  .slide-fields {
    width: 100%;
    display: flex;
    flex-direction: column;
    gap: 14px;
    text-align: left;
  }
  .field-label {
    display: flex;
    flex-direction: column;
    gap: 5px;
  }
  .label-text {
    font-size: 0.78rem;
    font-weight: 600;
    color: var(--t-text-muted);
    text-transform: uppercase;
    letter-spacing: 0.04em;
  }
  .required { color: var(--t-status-poor); }
  .carousel-input {
    width: 100%;
    background: var(--t-bg-input);
    border: 1px solid var(--t-border-input);
    border-radius: var(--t-radius-md);
    padding: 10px 14px;
    color: var(--t-text-heading);
    font-size: 0.88rem;
    font-family: var(--t-font-body);
    outline: none;
    box-sizing: border-box;
    transition: border-color var(--t-transition), box-shadow var(--t-transition);
  }
  .carousel-input:focus {
    border-color: var(--t-brand);
    box-shadow: 0 0 0 3px color-mix(in srgb, var(--t-brand) 15%, transparent);
  }
  .carousel-input.input-valid {
    border-color: #22c55e;
    box-shadow: 0 0 0 3px rgba(34, 197, 94, 0.15);
  }
  .carousel-input.input-invalid {
    border-color: #ef4444;
    box-shadow: 0 0 0 3px rgba(239, 68, 68, 0.15);
  }
  .tree-validation-msg {
    display: block;
    font-size: 0.8rem;
    margin-top: 6px;
    color: #888;
  }
  .tree-validation-msg.valid   { color: #22c55e; }
  .tree-validation-msg.invalid { color: #ef4444; }
  .tree-validation-msg.checking { color: #f59e0b; }
  .tree-info-card {
    background: color-mix(in srgb, var(--t-brand) 8%, var(--t-bg-card));
    border: 1px solid color-mix(in srgb, var(--t-brand) 25%, transparent);
    border-radius: var(--t-radius-md);
    padding: 12px 16px;
    margin-top: 8px;
    font-size: 0.85rem;
  }
  .tree-info-row {
    padding: 3px 0;
    color: var(--t-text-body);
  }
  .tree-info-row strong { color: var(--t-text-heading); }
  .tree-info-row em { color: var(--t-text-muted); font-style: italic; }
  .health-picker {
    display: flex;
    gap: 8px;
  }
  .health-option {
    flex: 1;
    padding: 10px 8px;
    border: 2px solid var(--t-border-input);
    border-radius: var(--t-radius-md);
    background: var(--t-bg-input);
    font-size: 0.84rem;
    font-family: var(--t-font-body);
    color: var(--t-text-body);
    cursor: pointer;
    transition: all 0.2s ease;
    text-align: center;
  }
  .health-option:hover {
    background: var(--t-bg-hover);
    border-color: var(--t-brand-muted);
  }
  .health-option.selected {
    background: var(--t-brand-dim);
    border-color: var(--t-brand);
    color: var(--t-text-brand);
    font-weight: 600;
    transform: scale(1.02);
    box-shadow: 0 0 0 3px color-mix(in srgb, var(--t-brand) 12%, transparent);
  }
  .carousel-textarea {
    width: 100%;
    background: var(--t-bg-input);
    border: 1px solid var(--t-border-input);
    border-radius: var(--t-radius-md);
    padding: 10px 14px;
    color: var(--t-text-heading);
    font-size: 0.88rem;
    font-family: var(--t-font-body);
    outline: none;
    box-sizing: border-box;
    resize: vertical;
    min-height: 80px;
    transition: border-color var(--t-transition), box-shadow var(--t-transition);
  }
  .carousel-textarea:focus {
    border-color: var(--t-brand);
    box-shadow: 0 0 0 3px color-mix(in srgb, var(--t-brand) 15%, transparent);
  }
  .photo-upload-area {
    width: 100%;
    max-width: 320px;
  }
  .photo-dropzone {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 8px;
    padding: 32px 20px;
    border: 2px dashed var(--t-border);
    border-radius: var(--t-radius-lg);
    background: var(--t-bg-input);
    cursor: pointer;
    transition: all 0.25s ease;
  }
  .photo-dropzone:hover {
    border-color: var(--t-brand);
    background: var(--t-brand-dim);
  }
  .dropzone-icon {
    font-size: 2.2rem;
    transition: transform 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
  }
  .photo-dropzone:hover .dropzone-icon {
    transform: scale(1.2);
  }
  .dropzone-text {
    font-size: 0.88rem;
    font-weight: 600;
    color: var(--t-text-heading);
  }
  .dropzone-hint {
    font-size: 0.72rem;
    color: var(--t-text-faint);
  }
  .photo-preview {
    position: relative;
    border-radius: var(--t-radius-lg);
    overflow: hidden;
    border: 1px solid var(--t-border);
    max-height: 220px;
  }
  .photo-preview img {
    width: 100%;
    max-height: 220px;
    object-fit: cover;
    display: block;
  }
  .photo-remove {
    position: absolute;
    top: 8px;
    right: 8px;
    width: 28px;
    height: 28px;
    border-radius: 50%;
    background: rgba(0, 0, 0, 0.6);
    color: #fff;
    border: none;
    font-size: 0.75rem;
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: background 0.2s;
  }
  .photo-remove:hover {
    background: rgba(200, 50, 50, 0.85);
  }
  .post-preview-card {
    margin-top: 16px;
    background: var(--t-bg-surface);
    border: 1px solid var(--t-border-soft);
    border-radius: var(--t-radius-md);
    padding: 12px 14px;
    width: 100%;
    text-align: left;
  }
  .preview-header {
    display: flex;
    align-items: center;
    gap: 10px;
  }
  .preview-icon { font-size: 1.6rem; }
  .preview-header strong {
    display: block;
    font-size: 0.85rem;
    color: var(--t-text-heading);
  }
  .preview-header small {
    font-size: 0.72rem;
    color: var(--t-text-muted);
  }
  .preview-thumb {
    width: 100%;
    max-height: 100px;
    object-fit: cover;
    border-radius: var(--t-radius-sm);
    margin-top: 10px;
  }
  .preview-tags {
    margin-top: 8px;
    font-size: 0.78rem;
    color: var(--t-text-brand);
    font-weight: 500;
  }
  .carousel-footer {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 14px 20px 18px;
    border-top: 1px solid var(--t-border-soft);
  }
  .carousel-nav-btn {
    padding: 10px 22px;
    border-radius: var(--t-radius-pill);
    font-size: 0.86rem;
    font-weight: 600;
    font-family: var(--t-font-body);
    cursor: pointer;
    transition: all 0.2s ease;
    border: none;
  }
  .carousel-nav-btn.back {
    background: var(--t-bg-hover);
    color: var(--t-text-muted);
    border: 1px solid var(--t-border);
  }
  .carousel-nav-btn.back:hover {
    background: var(--t-bg-active);
    color: var(--t-text-heading);
  }
  .carousel-nav-btn.next {
    background: linear-gradient(135deg, var(--t-brand), var(--t-brand-glow));
    color: var(--t-bg-base);
    box-shadow: 0 2px 10px color-mix(in srgb, var(--t-brand) 30%, transparent);
  }
  .carousel-nav-btn.next:hover:not(:disabled) {
    transform: translateY(-1px);
    box-shadow: 0 4px 16px color-mix(in srgb, var(--t-brand) 45%, transparent);
  }
  .carousel-nav-btn.next:disabled,
  .carousel-nav-btn.submit:disabled {
    opacity: 0.4;
    cursor: not-allowed;
    transform: none;
    box-shadow: none;
  }
  .carousel-nav-btn.submit {
    background: linear-gradient(135deg, var(--t-brand), var(--t-brand-glow));
    color: var(--t-bg-base);
    box-shadow: 0 2px 10px color-mix(in srgb, var(--t-brand) 30%, transparent);
    display: flex;
    align-items: center;
    gap: 6px;
  }
  .carousel-nav-btn.submit:hover:not(:disabled) {
    transform: translateY(-1px);
    box-shadow: 0 4px 16px color-mix(in srgb, var(--t-brand) 45%, transparent);
  }
  .btn-spinner {
    display: inline-block;
    width: 14px;
    height: 14px;
    border: 2px solid rgba(255, 255, 255, 0.3);
    border-top-color: #fff;
    border-radius: 50%;
    animation: spin 0.7s linear infinite;
  }

  /* ─── Responsive ────────────────────────────────────────────────── */
  @media (max-width: 768px) {
    .profile-hero { padding: 0 1rem; }
    .profile-cover { margin: 0 -1rem; height: 120px; }
    .profile-info-bar { flex-wrap: wrap; }
    .profile-stats-tabs { flex-wrap: wrap; gap: 1.5rem; }
    .profile-body {
      grid-template-columns: 1fr;
      padding: 1rem;
    }
    .profile-grid {
      grid-template-columns: repeat(3, 1fr);
      gap: 0.4rem;
    }
    .modal {
      flex-direction: column;
      max-height: 92vh;
      border-radius: 12px;
      width: 96vw;
    }
    .modal-close-btn { top: 8px; right: 8px; width: 30px; height: 30px; }
  }
</style>