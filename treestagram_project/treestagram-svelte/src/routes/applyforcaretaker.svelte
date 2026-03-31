<script>
  import { user } from "../lib/api.js";
  import { apiApplyForCaretaker } from "../lib/api.js";
  export let navigate;

  let motivation = "";
  let treeExperience = "";
  let treeId = ""; // <-- NEW: Added variable for Tree ID
  let submitted = false;
  let submitting = false;
  let errorMsg = "";

  $: meetsRequirements =
    ($user?.post_count ?? 0) >= 30 && ($user?.total_likes_received ?? 0) >= 100;

  async function handleSubmit() {
    // <-- NEW: Added treeId to the validation check
    if (!motivation.trim() || !treeExperience.trim() || !treeId.trim()) {
      errorMsg = "Please fill in all required fields.";
      return;
    }

    submitting = true;
    errorMsg = "";

    try {
      const result = await apiApplyForCaretaker({
        motivation,
        tree_experience: treeExperience,
        tree_id: treeId, // <-- NEW: Added tree_id to the API payload
      });

      if (result.error) {
        errorMsg = result.error;
      } else {
        submitted = true;
      }
    } catch (err) {
      errorMsg = "Something went wrong. Please try again.";
    } finally {
      submitting = false;
    }
  }
</script>

<div class="page-wrapper">
  <div class="leaf-bg" aria-hidden="true">
    <span>🌿</span><span>🍃</span><span>🌱</span><span>🍀</span><span>🌾</span>
  </div>

  <div class="form-container">
    <div class="form-header">
      <div class="header-icon">🌳</div>
      <h1>Apply to be a Caretaker</h1>
      <p class="subtitle">
        Caretakers help nurture and protect our community's trees. Tell us why
        you'd be a great fit.
      </p>
    </div>

    {#if false}
      <div class="requirements-warning">
        <span class="warn-icon">🔒</span>
        <div>
          <strong>Requirements not met</strong>
          <p>
            You need at least <strong>30 posts</strong> and
            <strong>100 likes</strong> to apply.
          </p>
          <p class="current-stats">
            Current: {$user?.post_count ?? 0} posts · {$user?.total_likes_received ??
              0} likes
          </p>
        </div>
      </div>
      <button class="btn-back" on:click={() => navigate("/profile")}>
        ← Back to Profile
      </button>
    {:else if submitted}
      <div class="success-state">
        <div class="success-icon">🎉</div>
        <h2>Application Submitted!</h2>
        <p>
          Our moderators will review your application and get back to you. Thank
          you for wanting to give back to the community.
        </p>
        <button class="btn-back" on:click={() => navigate("/profile")}>
          ← Back to Profile
        </button>
      </div>
    {:else}
      <form on:submit|preventDefault={handleSubmit}>
        <section class="form-section">
          <h2 class="section-title">
            <span class="section-dot"></span> Your Profile
          </h2>

          <div class="profile-snapshot">
            {#if $user?.avatar_url}
              <img
                src={$user.avatar_url}
                alt="avatar"
                class="snapshot-avatar"
              />
            {:else}
              <div class="snapshot-avatar placeholder-avatar">
                {($user?.username ?? "?")[0].toUpperCase()}
              </div>
            {/if}

            <div class="snapshot-info">
              {#if $user?.name}
                <div class="snapshot-name">{$user.name}</div>
              {/if}
              
              <div class="snapshot-username">@{$user?.username ?? "—"}</div>
              
              {#if $user?.email}
                <div class="snapshot-email">{$user.email}</div>
              {/if}
            </div>
          </div>

          <div class="stats-row">
            <div class="stat-chip">
              <span class="stat-value">{$user?.post_count ?? 0}</span>
              <span class="stat-label">Posts</span>
              <span class="stat-badge met">✓</span>
            </div>
            <div class="stat-chip">
              <span class="stat-value">{$user?.total_likes_received ?? 0}</span>
              <span class="stat-label">Likes received</span>
              <span class="stat-badge met">✓</span>
            </div>
          </div>
        </section>

        <section class="form-section">
          <h2 class="section-title">
            <span class="section-dot"></span> Your Application
          </h2>

          <div class="field-group">
            <label for="motivation">
              Why do you want to be a Caretaker?
              <span class="required">*</span>
            </label>
            <p class="field-hint">
              Tell the mods what drives your passion for this role and what
              you'd bring to the community.
            </p>
            <textarea
              id="motivation"
              bind:value={motivation}
              rows="5"
              placeholder="I want to be a caretaker because..."
              maxlength="2000"
            ></textarea>
            <div class="char-count">{motivation.length}/2000</div>
          </div>

          <div class="field-group">
            <label for="tree-experience">
              What's your experience with trees or nature? <span
                class="required">*</span
              >
            </label>
            <p class="field-hint">
              Any background in gardening, ecology, forestry, or just a personal
              story — all welcome.
            </p>
            <textarea
              id="tree-experience"
              bind:value={treeExperience}
              rows="4"
              placeholder="I've been growing plants since..."
              maxlength="1500"
            ></textarea>
            <div class="char-count">{treeExperience.length}/1500</div>
          </div>
        </section>

        <section class="form-section">
          <h2 class="section-title">
            <span class="section-dot"></span> Target Tree
          </h2>

          <div class="field-group">
            <label for="tree-id">
              Tree ID
              <span class="required">*</span>
            </label>
            <p class="field-hint">
              Please enter the unique ID of the tree you are applying to care for.
            </p>
            <input
              type="text"
              id="tree-id"
              bind:value={treeId}
              placeholder="e.g., TR-8492"
              maxlength="50"
            />
          </div>
        </section>

        {#if errorMsg}
          <div class="error-msg">⚠️ {errorMsg}</div>
        {/if}

        <div class="form-actions">
          <button
            type="button"
            class="btn-secondary"
            on:click={() => navigate("/profile")}
          >
            Cancel
          </button>
          <button type="submit" class="btn-primary" disabled={submitting}>
            {submitting ? "Submitting…" : "🌿 Submit Application"}
          </button>
        </div>
      </form>
    {/if}
  </div>
</div>

<style>
  /* ── Layout ── */
  .page-wrapper {
    min-height: 100vh;
    background: #f5f7f2;
    display: flex;
    align-items: flex-start;
    justify-content: center;
    padding: 3rem 1.25rem 5rem;
    position: relative;
    overflow: hidden;
    font-family: "Georgia", serif;
  }

  /* Decorative floating leaves */
  .leaf-bg {
    position: fixed;
    inset: 0;
    pointer-events: none;
    z-index: 0;
  }
  .leaf-bg span {
    position: absolute;
    font-size: 2rem;
    opacity: 0.07;
  }
  .leaf-bg span:nth-child(1) {
    top: 8%;
    left: 5%;
    font-size: 3.5rem;
  }
  .leaf-bg span:nth-child(2) {
    top: 20%;
    right: 6%;
    font-size: 2.5rem;
  }
  .leaf-bg span:nth-child(3) {
    bottom: 30%;
    left: 3%;
    font-size: 4rem;
  }
  .leaf-bg span:nth-child(4) {
    bottom: 10%;
    right: 4%;
    font-size: 3rem;
  }
  .leaf-bg span:nth-child(5) {
    top: 55%;
    left: 50%;
    font-size: 5rem;
  }

  /* ── Card ── */
  .form-container {
    position: relative;
    z-index: 1;
    width: 100%;
    max-width: 640px;
    background: #fff;
    border-radius: 18px;
    box-shadow:
      0 4px 24px rgba(60, 90, 60, 0.09),
      0 1px 4px rgba(60, 90, 60, 0.06);
    overflow: hidden;
  }

  /* ── Form header ── */
  .form-header {
    background: linear-gradient(135deg, #2d5a27 0%, #4a8c3f 60%, #6db56a 100%);
    padding: 2.5rem 2rem 2rem;
    text-align: center;
    color: #fff;
  }
  .header-icon {
    font-size: 3rem;
    margin-bottom: 0.5rem;
    filter: drop-shadow(0 2px 6px rgba(0, 0, 0, 0.2));
  }
  .form-header h1 {
    margin: 0 0 0.5rem;
    font-size: 1.75rem;
    font-weight: 700;
    letter-spacing: -0.02em;
  }
  .subtitle {
    margin: 0;
    font-size: 0.95rem;
    opacity: 0.85;
    line-height: 1.5;
    font-family: system-ui, sans-serif;
  }

  /* ── Sections ── */
  form {
    padding: 2rem;
    display: flex;
    flex-direction: column;
    gap: 0;
  }
  .form-section {
    margin-bottom: 2rem;
  }
  .section-title {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    font-size: 1.05rem;
    font-weight: 700;
    color: #2d5a27;
    margin: 0 0 1.25rem;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    font-family: system-ui, sans-serif;
  }
  .section-dot {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background: #4a8c3f;
    flex-shrink: 0;
  }

  /* ── Profile snapshot ── */
  .profile-snapshot {
    display: flex;
    align-items: center;
    gap: 1rem;
    background: #f5f7f2;
    border: 1px solid #dde8d8;
    border-radius: 12px;
    padding: 1rem 1.25rem;
    margin-bottom: 1rem;
  }
  .snapshot-avatar {
    width: 56px;
    height: 56px;
    border-radius: 50%;
    object-fit: cover;
    border: 2px solid #b8d4b0;
    flex-shrink: 0;
  }
  .placeholder-avatar {
    display: flex;
    align-items: center;
    justify-content: center;
    background: #4a8c3f;
    color: #fff;
    font-size: 1.4rem;
    font-weight: 700;
    font-family: system-ui, sans-serif;
  }
  .snapshot-info {
    font-family: system-ui, sans-serif;
  }
  .snapshot-name {
    font-weight: 700;
    font-size: 1rem;
    color: #1a2e18;
  }
  .snapshot-username {
    font-size: 0.875rem;
    color: #4a8c3f;
    margin-top: 2px;
  }
  .snapshot-email {
    font-size: 0.8rem;
    color: #777;
    margin-top: 2px;
  }

  /* ── Stats ── */
  .stats-row {
    display: flex;
    gap: 0.75rem;
  }
  .stat-chip {
    flex: 1;
    background: #f0f5ee;
    border: 1px solid #c8ddc2;
    border-radius: 10px;
    padding: 0.75rem 1rem;
    display: flex;
    align-items: center;
    gap: 0.5rem;
    font-family: system-ui, sans-serif;
  }
  .stat-value {
    font-size: 1.25rem;
    font-weight: 800;
    color: #2d5a27;
  }
  .stat-label {
    font-size: 0.8rem;
    color: #666;
    flex: 1;
  }
  .stat-badge.met {
    background: #d4edda;
    color: #2d5a27;
    border-radius: 50%;
    width: 22px;
    height: 22px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 0.7rem;
    font-weight: 700;
    flex-shrink: 0;
  }

  /* ── Fields ── */
  .field-group {
    margin-bottom: 1.5rem;
  }
  .field-group label {
    display: block;
    font-size: 0.95rem;
    font-weight: 700;
    color: #1a2e18;
    margin-bottom: 0.25rem;
    font-family: system-ui, sans-serif;
  }
  .required {
    color: #c0392b;
    margin-left: 2px;
  }
  .field-hint {
    font-size: 0.82rem;
    color: #777;
    margin: 0 0 0.6rem;
    line-height: 1.5;
    font-family: system-ui, sans-serif;
  }

  /* <-- NEW: Grouped input[type="text"] styling with textarea to keep themes consistent --> */
  textarea,
  input[type="text"] {
    width: 100%;
    box-sizing: border-box;
    border: 1.5px solid #ccdbc7;
    border-radius: 10px;
    padding: 0.75rem 1rem;
    font-size: 0.95rem;
    font-family: "Georgia", serif;
    color: #1a2e18;
    background: #fafcf9;
    transition:
      border-color 0.2s,
      box-shadow 0.2s;
    line-height: 1.6;
  }
  
  textarea {
    resize: vertical;
  }

  /* <-- NEW: Focus state added for input[type="text"] --> */
  textarea:focus,
  input[type="text"]:focus {
    outline: none;
    border-color: #4a8c3f;
    box-shadow: 0 0 0 3px rgba(74, 140, 63, 0.12);
    background: #fff;
  }
  .char-count {
    text-align: right;
    font-size: 0.75rem;
    color: #aaa;
    margin-top: 0.3rem;
    font-family: system-ui, sans-serif;
  }

  /* ── Actions ── */
  .form-actions {
    display: flex;
    gap: 0.75rem;
    justify-content: flex-end;
    padding-top: 0.5rem;
    border-top: 1px solid #e8f0e5;
  }
  .btn-primary {
    background: linear-gradient(135deg, #2d5a27, #4a8c3f);
    color: #fff;
    border: none;
    border-radius: 10px;
    padding: 0.75rem 1.75rem;
    font-size: 0.95rem;
    font-weight: 700;
    cursor: pointer;
    font-family: system-ui, sans-serif;
    transition:
      opacity 0.2s,
      transform 0.15s;
    letter-spacing: 0.01em;
  }
  .btn-primary:hover:not(:disabled) {
    opacity: 0.92;
    transform: translateY(-1px);
  }
  .btn-primary:disabled {
    opacity: 0.6;
    cursor: not-allowed;
  }
  .btn-secondary {
    background: transparent;
    color: #555;
    border: 1.5px solid #ccc;
    border-radius: 10px;
    padding: 0.75rem 1.25rem;
    font-size: 0.9rem;
    cursor: pointer;
    font-family: system-ui, sans-serif;
    transition:
      border-color 0.2s,
      color 0.2s;
  }
  .btn-secondary:hover {
    border-color: #4a8c3f;
    color: #2d5a27;
  }

  /* ── Error ── */
  .error-msg {
    background: #fff0ee;
    border: 1px solid #f5c0b8;
    border-radius: 8px;
    padding: 0.75rem 1rem;
    color: #c0392b;
    font-size: 0.875rem;
    margin-bottom: 1rem;
    font-family: system-ui, sans-serif;
  }

  /* ── Requirements warning ── */
  .requirements-warning {
    margin: 2rem;
    background: #fff8e1;
    border: 1px solid #ffe082;
    border-radius: 12px;
    padding: 1.25rem;
    display: flex;
    gap: 1rem;
    align-items: flex-start;
    font-family: system-ui, sans-serif;
  }
  .warn-icon {
    font-size: 1.5rem;
    flex-shrink: 0;
  }
  .requirements-warning strong {
    color: #5d4037;
    display: block;
    margin-bottom: 0.25rem;
  }
  .requirements-warning p {
    margin: 0 0 0.25rem;
    color: #795548;
    font-size: 0.9rem;
  }
  .current-stats {
    font-size: 0.8rem !important;
    color: #a1887f !important;
  }
  .btn-back {
    display: block;
    margin: 0 2rem 2rem;
    background: transparent;
    border: 1.5px solid #ccc;
    border-radius: 10px;
    padding: 0.65rem 1.25rem;
    font-size: 0.9rem;
    cursor: pointer;
    font-family: system-ui, sans-serif;
    color: #555;
    transition:
      border-color 0.2s,
      color 0.2s;
    width: fit-content;
  }
  .btn-back:hover {
    border-color: #4a8c3f;
    color: #2d5a27;
  }

  /* ── Success state ── */
  .success-state {
    text-align: center;
    padding: 3rem 2rem;
    font-family: system-ui, sans-serif;
  }
  .success-icon {
    font-size: 3.5rem;
    margin-bottom: 1rem;
  }
  .success-state h2 {
    color: #2d5a27;
    margin-bottom: 0.75rem;
  }
  .success-state p {
    color: #555;
    line-height: 1.6;
    margin-bottom: 1.5rem;
    max-width: 400px;
    margin-left: auto;
    margin-right: auto;
  }
</style>