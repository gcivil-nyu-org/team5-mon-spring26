<script>
  import { searchTreesMulti } from "../lib/api.js";
  import LeftNav from "../components/LeftNav.svelte";
  import BackgroundRings from "../components/BackgroundRings.svelte";
  import { onMount } from "svelte";
  export let navigate;

  let mounted = false;

  let tree_id = "";
  let spc_common = "";
  let spc_latin = "";
  let status = "";
  let health = "";
  let borough = "";

  let results = [];
  let totalCount = 0;
  let offset = 0;
  const limit = 10;
  let loading = false;
  let hasSearched = false;

  // ── Real-time Tree ID preview ──
  let treePreview = null;       // fetched tree data
  let treePreviewStatus = "";   // "", "checking", "found", "not_found"
  let treePreviewTimer = null;

  function onTreeIdInput(e) {
    const val = e.target.value;
    tree_id = val;
    if (treePreviewTimer) clearTimeout(treePreviewTimer);
    const trimmed = val.trim();
    if (!trimmed) {
      treePreview = null;
      treePreviewStatus = "";
      return;
    }
    treePreviewStatus = "checking";
    treePreviewTimer = setTimeout(() => fetchTreePreview(trimmed), 400);
  }

  async function fetchTreePreview(id) {
    try {
      const res = await fetch(`/trees/api/${id}/`, { credentials: "include" });
      if (res.ok) {
        treePreview = await res.json();
        treePreviewStatus = "found";
      } else {
        treePreview = null;
        treePreviewStatus = "not_found";
      }
    } catch {
      treePreview = null;
      treePreviewStatus = "not_found";
    }
  }

  onMount(() => {
    setTimeout(() => (mounted = true), 50);
  });

  async function doSearch() {
    offset = 0;
    hasSearched = true;
    await fetchResults();
  }

  async function fetchResults() {
    loading = true;
    const params = { tree_id, spc_common, spc_latin, status, health, borough };
    const data = await searchTreesMulti(params, offset, limit);
    results = data.results;
    totalCount = data.count;
    loading = false;
  }

  function nextPage() {
    offset += limit;
    fetchResults();
  }

  function prevPage() {
    offset = Math.max(offset - limit, 0);
    fetchResults();
  }

  function goToTree(treeId) {
    navigate(`/treedashboard/${treeId}`);
  }

  function clearFilters() {
    tree_id = "";
    spc_common = "";
    spc_latin = "";
    status = "";
    health = "";
    borough = "";
    results = [];
    totalCount = 0;
    offset = 0;
    hasSearched = false;
    treePreview = null;
    treePreviewStatus = "";
  }

  function healthIcon(h) {
    if (h === "Good") return "🌳";
    if (h === "Fair") return "🍂";
    if (h === "Poor") return "🥀";
    return "🌿";
  }

  function statusIcon(s) {
    if (s === "Alive") return "💚";
    if (s === "Dead") return "💀";
    if (s === "Stump") return "🪵";
    return "❓";
  }

  $: currentPage = Math.floor(offset / limit) + 1;
  $: totalPages = Math.ceil(totalCount / limit);
  $: hasAnyFilter = tree_id || spc_common || spc_latin || status || health || borough;
</script>

<div class="page" class:mounted>
  <BackgroundRings />
  <LeftNav {navigate} activePage="search" />

  <div class="search-layout">
    <!-- Hero / Header -->
    <div class="search-hero">
      <div class="hero-icon">🔍</div>
      <h1 class="hero-title">Explore NYC Trees</h1>
      <p class="hero-subtitle">Search through 680,000+ trees across all five boroughs</p>
    </div>

    <!-- Search Filters Card -->
    <div class="filters-card">
      <div class="filters-header">
        <h2>🌿 Filter Trees</h2>
        {#if hasAnyFilter}
          <button class="clear-btn" on:click={clearFilters}>✕ Clear All</button>
        {/if}
      </div>

      <!-- Tree ID — full width with live preview -->
      <div class="filter-section-id">
        <label for="tree-id">
          <span class="filter-icon">🆔</span> Tree ID
        </label>
        <input
          id="tree-id"
          type="text"
          placeholder="e.g. 180683"
          value={tree_id}
          on:input={onTreeIdInput}
          on:keydown={(e) => e.key === "Enter" && doSearch()}
          class:input-valid={treePreviewStatus === "found"}
          class:input-invalid={treePreviewStatus === "not_found"}
        />
        {#if treePreviewStatus === "checking"}
          <div class="tree-preview-msg checking">🔄 Looking up tree…</div>
        {:else if treePreviewStatus === "not_found"}
          <div class="tree-preview-msg not-found">❌ No tree found with this ID</div>
        {:else if treePreviewStatus === "found" && treePreview}
          <!-- svelte-ignore a11y-click-events-have-key-events -->
          <!-- svelte-ignore a11y-no-static-element-interactions -->
          <div class="tree-preview-card" on:click={() => goToTree(treePreview.tree_id)}>
            <div class="tp-header">
              <span class="tp-emoji">{healthIcon(treePreview.health)}</span>
              <div class="tp-info">
                <strong>{treePreview.spc_common || "Unknown"}</strong>
                <span class="tp-latin">{treePreview.spc_latin || ""}</span>
              </div>
              <span class="tp-id">#{treePreview.tree_id}</span>
            </div>
            <div class="tp-details">
              <span class="tp-chip">📍 {treePreview.address}, {treePreview.borough}</span>
              <span class="tp-chip health-{(treePreview.health || '').toLowerCase()}">{healthIcon(treePreview.health)} {treePreview.health}</span>
              <span class="tp-chip">{statusIcon(treePreview.status)} {treePreview.status}</span>
            </div>
            <div class="tp-action">View Dashboard →</div>
          </div>
        {/if}
      </div>

      <div class="filter-divider"></div>

      <!-- Text inputs — 2 columns -->
      <div class="filters-row-2">
        <div class="filter-group">
          <label for="common-name">
            <span class="filter-icon">🌳</span> Common Name
          </label>
          <input
            id="common-name"
            type="text"
            placeholder="e.g. Red Maple"
            bind:value={spc_common}
            on:keydown={(e) => e.key === "Enter" && doSearch()}
          />
        </div>

        <div class="filter-group">
          <label for="latin-name">
            <span class="filter-icon">📜</span> Latin Name
          </label>
          <input
            id="latin-name"
            type="text"
            placeholder="e.g. Acer rubrum"
            bind:value={spc_latin}
            on:keydown={(e) => e.key === "Enter" && doSearch()}
          />
        </div>
      </div>

      <!-- Dropdowns — 3 columns -->
      <div class="filters-row-3">
        <div class="filter-group">
          <label for="status-field">
            <span class="filter-icon">📊</span> Status
          </label>
          <select id="status-field" bind:value={status}>
            <option value="">Any Status</option>
            <option value="Alive">💚 Alive</option>
            <option value="Dead">💀 Dead</option>
            <option value="Stump">🪵 Stump</option>
          </select>
        </div>

        <div class="filter-group">
          <label for="health-field">
            <span class="filter-icon">💚</span> Health
          </label>
          <select id="health-field" bind:value={health}>
            <option value="">Any Health</option>
            <option value="Good">🌳 Good</option>
            <option value="Fair">🍂 Fair</option>
            <option value="Poor">🥀 Poor</option>
          </select>
        </div>

        <div class="filter-group">
          <label for="borough-field">
            <span class="filter-icon">📍</span> Borough
          </label>
          <select id="borough-field" bind:value={borough}>
            <option value="">Any Borough</option>
            <option value="Manhattan">Manhattan</option>
            <option value="Brooklyn">Brooklyn</option>
            <option value="Queens">Queens</option>
            <option value="Bronx">Bronx</option>
            <option value="Staten Island">Staten Island</option>
          </select>
        </div>
      </div>

      <button class="search-btn" on:click={doSearch}>
        <span class="search-btn-icon">🔎</span>
        Search Trees
      </button>
    </div>

    <!-- Results Section -->
    <div class="results-section">
      {#if loading}
        <div class="loading-state">
          <div class="loading-spinner"></div>
          <p>Searching the urban forest…</p>
        </div>
      {:else if !hasSearched}
        <div class="empty-state">
          <span class="empty-icon">🌲</span>
          <h3>Ready to Explore?</h3>
          <p>Use the filters above to search for trees across NYC</p>
        </div>
      {:else if results.length === 0}
        <div class="empty-state">
          <span class="empty-icon">🍃</span>
          <h3>No Trees Found</h3>
          <p>Try different search criteria or clear your filters</p>
        </div>
      {:else}
        <!-- Results count -->
        <div class="results-header">
          <span class="results-count">
            🌳 Found <strong>{totalCount.toLocaleString()}</strong> tree{totalCount !== 1 ? 's' : ''}
          </span>
          <span class="results-page">
            Page {currentPage} of {totalPages}
          </span>
        </div>

        <!-- Results grid -->
        <div class="results-grid">
          {#each results as tree, i}
            <!-- svelte-ignore a11y-click-events-have-key-events -->
            <!-- svelte-ignore a11y-no-static-element-interactions -->
            <div
              class="tree-card"
              style="animation-delay: {i * 0.04}s"
              on:click={() => goToTree(tree.tree_id)}
            >
              <div class="tree-card-header">
                <span class="tree-emoji">{healthIcon(tree.health)}</span>
                <div class="tree-card-title">
                  <h4>{tree.spc_common || "Unknown Species"}</h4>
                  <span class="tree-latin">{tree.spc_latin || "—"}</span>
                </div>
                <span class="tree-id-badge">#{tree.tree_id}</span>
              </div>
              <div class="tree-card-body">
                <div class="tree-chip">
                  {statusIcon(tree.status)} {tree.status || "N/A"}
                </div>
                <div class="tree-chip health-chip health-{(tree.health || '').toLowerCase()}">
                  {healthIcon(tree.health)} {tree.health || "N/A"}
                </div>
                <div class="tree-chip borough-chip">
                  📍 {tree.borough || "N/A"}
                </div>
              </div>
              <div class="tree-card-footer">
                <span class="view-link">View Dashboard →</span>
              </div>
              <div class="tree-card-glow"></div>
            </div>
          {/each}
        </div>

        <!-- Pagination -->
        <div class="pagination-bar">
          <button
            class="page-btn"
            on:click={prevPage}
            disabled={offset === 0}
          >
            ← Previous
          </button>
          <span class="page-info">
            {offset + 1}–{Math.min(offset + limit, totalCount)} of {totalCount.toLocaleString()}
          </span>
          <button
            class="page-btn"
            on:click={nextPage}
            disabled={offset + limit >= totalCount}
          >
            Next →
          </button>
        </div>
      {/if}
    </div>
  </div>
</div>

<style>
  /* ─── Page Shell ───────────────────────────────────────────────── */
  .page {
    min-height: 100vh;
    background: var(--t-bg-base);
    font-family: var(--t-font-body);
    color: var(--t-text-body);
    position: relative;
    z-index: 0;
    overflow-x: hidden;
    padding-left: 60px;
  }

  .search-layout {
    max-width: 900px;
    margin: 0 auto;
    padding: 2rem 1.5rem 3rem;
    opacity: 0;
    transform: translateY(16px);
    transition: opacity 0.5s ease 0.1s, transform 0.5s ease 0.1s;
  }
  .page.mounted .search-layout {
    opacity: 1;
    transform: translateY(0);
  }

  /* ─── Hero ───────────────────────────────────────────────────────── */
  .search-hero {
    text-align: center;
    margin-bottom: 2rem;
  }
  .hero-icon {
    font-size: 2.8rem;
    margin-bottom: 0.3rem;
    filter: drop-shadow(0 2px 6px rgba(0,0,0,0.1));
  }
  .hero-title {
    font-family: var(--t-font-heading, var(--t-font-body));
    font-size: 2rem;
    font-weight: 800;
    color: var(--t-text-heading);
    margin: 0 0 0.3rem;
    letter-spacing: -0.02em;
  }
  .hero-subtitle {
    font-size: 0.92rem;
    color: var(--t-text-muted);
    margin: 0;
  }

  /* ─── Filters Card ──────────────────────────────────────────────── */
  .filters-card {
    background: var(--t-bg-elevated);
    border: 1px solid var(--t-border);
    border-radius: var(--t-radius-lg, 16px);
    box-shadow: var(--t-shadow-card);
    padding: 1.5rem;
    margin-bottom: 1.8rem;
  }
  .filters-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 1rem;
  }
  .filters-header h2 {
    font-size: 1.1rem;
    font-weight: 700;
    color: var(--t-text-heading);
    margin: 0;
  }
  .clear-btn {
    background: none;
    border: 1px solid var(--t-border);
    border-radius: var(--t-radius-pill, 50px);
    padding: 4px 12px;
    font-size: 0.75rem;
    color: var(--t-text-muted);
    cursor: pointer;
    transition: all 0.2s;
    font-family: var(--t-font-body);
  }
  .clear-btn:hover {
    color: var(--t-status-poor, #c0392b);
    border-color: var(--t-status-poor, #c0392b);
    background: rgba(192,57,43,0.05);
  }

  /* ─── Filter Sections ─────────────────────────────────────────── */
  .filter-section-id {
    display: flex;
    flex-direction: column;
    gap: 4px;
    margin-bottom: 0;
  }
  .filter-section-id label {
    font-size: 0.75rem;
    font-weight: 600;
    color: var(--t-text-heading);
    display: flex;
    align-items: center;
    gap: 4px;
  }
  .filter-section-id input {
    width: 100%;
    background: var(--t-bg-input, var(--t-bg-base));
    border: 1px solid var(--t-border-input, var(--t-border));
    border-radius: var(--t-radius-md, 10px);
    padding: 9px 12px;
    color: var(--t-text-heading);
    font-size: 0.85rem;
    font-family: var(--t-font-body);
    outline: none;
    transition: border-color 0.2s, box-shadow 0.2s;
    box-sizing: border-box;
  }
  .filter-section-id input:focus {
    border-color: var(--t-brand, #529a67);
    box-shadow: 0 0 0 3px rgba(82,154,103,0.12);
  }
  .filter-section-id input::placeholder {
    color: var(--t-text-faint, #aaa);
  }

  .filter-divider {
    height: 1px;
    background: var(--t-border-soft, rgba(0,0,0,0.06));
    margin: 1rem 0;
  }

  .filters-row-2 {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 1rem;
    margin-bottom: 1rem;
  }

  .filters-row-3 {
    display: grid;
    grid-template-columns: 1fr 1fr 1fr;
    gap: 1rem;
    margin-bottom: 1.2rem;
  }

  .filter-group {
    display: flex;
    flex-direction: column;
    gap: 4px;
  }
  .filter-group label {
    font-size: 0.75rem;
    font-weight: 600;
    color: var(--t-text-heading);
    display: flex;
    align-items: center;
    gap: 4px;
  }
  .filter-icon {
    font-size: 0.82rem;
  }
  .filter-group input,
  .filter-group select {
    width: 100%;
    background: var(--t-bg-input, var(--t-bg-base));
    border: 1px solid var(--t-border-input, var(--t-border));
    border-radius: var(--t-radius-md, 10px);
    padding: 9px 12px;
    color: var(--t-text-heading);
    font-size: 0.85rem;
    font-family: var(--t-font-body);
    outline: none;
    transition: border-color 0.2s, box-shadow 0.2s;
    box-sizing: border-box;
  }
  .filter-group input:focus,
  .filter-group select:focus {
    border-color: var(--t-brand, #529a67);
    box-shadow: 0 0 0 3px rgba(82,154,103,0.12);
  }
  .filter-group input::placeholder {
    color: var(--t-text-faint, #aaa);
  }

  .search-btn {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 8px;
    width: 100%;
    background: linear-gradient(135deg, #529a67, #3d7a4e);
    border: none;
    border-radius: var(--t-radius-md, 10px);
    padding: 12px;
    color: #fff;
    font-size: 0.95rem;
    font-weight: 700;
    font-family: var(--t-font-body);
    cursor: pointer;
    transition: transform 0.15s, box-shadow 0.2s;
    box-shadow: 0 2px 10px rgba(82,154,103,0.25);
  }
  .search-btn:hover {
    transform: translateY(-1px);
    box-shadow: 0 4px 16px rgba(82,154,103,0.35);
  }
  .search-btn:active {
    transform: translateY(0);
  }
  .search-btn-icon {
    font-size: 1.1rem;
  }

  /* ─── Results Section ───────────────────────────────────────────── */
  .results-section {
    min-height: 200px;
  }

  /* Loading */
  .loading-state {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 3rem 1rem;
    gap: 1rem;
    color: var(--t-text-muted);
    font-size: 0.9rem;
  }
  .loading-spinner {
    width: 36px;
    height: 36px;
    border: 3px solid var(--t-border);
    border-top-color: var(--t-brand, #529a67);
    border-radius: 50%;
    animation: spin 0.8s linear infinite;
  }
  @keyframes spin {
    to { transform: rotate(360deg); }
  }

  /* Empty */
  .empty-state {
    text-align: center;
    padding: 3rem 1rem;
  }
  .empty-icon {
    font-size: 3rem;
    display: block;
    margin-bottom: 0.6rem;
    filter: drop-shadow(0 2px 4px rgba(0,0,0,0.1));
  }
  .empty-state h3 {
    font-size: 1.15rem;
    font-weight: 700;
    color: var(--t-text-heading);
    margin: 0 0 0.3rem;
  }
  .empty-state p {
    font-size: 0.85rem;
    color: var(--t-text-muted);
    margin: 0;
  }

  /* Results header */
  .results-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 1rem;
    padding: 0 2px;
  }
  .results-count {
    font-size: 0.88rem;
    color: var(--t-text-muted);
  }
  .results-count strong {
    color: var(--t-text-brand, #529a67);
  }
  .results-page {
    font-size: 0.78rem;
    color: var(--t-text-faint);
  }

  /* ─── Tree Cards ────────────────────────────────────────────────── */
  .results-grid {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 0.9rem;
  }

  .tree-card {
    position: relative;
    background: var(--t-bg-elevated);
    border: 1px solid var(--t-border);
    border-radius: var(--t-radius-lg, 16px);
    box-shadow: var(--t-shadow-card);
    padding: 1rem 1.1rem;
    cursor: pointer;
    overflow: hidden;
    transition: transform 0.2s, box-shadow 0.2s, border-color 0.2s;
    animation: cardFadeUp 0.35s ease both;
  }
  @keyframes cardFadeUp {
    from { opacity: 0; transform: translateY(10px); }
    to   { opacity: 1; transform: translateY(0); }
  }
  .tree-card:hover {
    transform: translateY(-3px);
    box-shadow: 0 8px 24px rgba(82,154,103,0.12);
    border-color: rgba(82,154,103,0.35);
  }
  .tree-card-glow {
    position: absolute;
    top: 0; left: -100%;
    width: 60%; height: 100%;
    background: linear-gradient(to right, transparent, rgba(255,255,255,0.5), transparent);
    transform: skewX(-20deg);
    pointer-events: none;
  }
  .tree-card:hover .tree-card-glow {
    animation: sweepGlow 0.6s ease-in-out;
  }
  @keyframes sweepGlow {
    0%   { left: -100%; }
    100% { left: 200%; }
  }

  .tree-card-header {
    display: flex;
    align-items: center;
    gap: 10px;
    margin-bottom: 8px;
  }
  .tree-emoji {
    font-size: 1.6rem;
    flex-shrink: 0;
    filter: drop-shadow(0 1px 2px rgba(0,0,0,0.12));
  }
  .tree-card-title {
    flex: 1;
    min-width: 0;
  }
  .tree-card-title h4 {
    font-size: 0.92rem;
    font-weight: 700;
    color: var(--t-text-heading);
    margin: 0;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    text-transform: capitalize;
  }
  .tree-latin {
    font-size: 0.72rem;
    color: var(--t-text-faint);
    font-style: italic;
    display: block;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }
  .tree-id-badge {
    background: linear-gradient(135deg, rgba(82,154,103,0.1), rgba(45,122,58,0.05));
    border: 1px solid rgba(82,154,103,0.25);
    border-radius: var(--t-radius-pill, 50px);
    padding: 2px 9px;
    font-size: 0.7rem;
    font-weight: 700;
    color: var(--t-text-brand, #529a67);
    font-family: 'DM Mono', 'Courier New', monospace;
    letter-spacing: 0.3px;
    flex-shrink: 0;
  }

  .tree-card-body {
    display: flex;
    flex-wrap: wrap;
    gap: 6px;
    margin-bottom: 8px;
  }
  .tree-chip {
    background: var(--t-bg-hover, rgba(0,0,0,0.03));
    border-radius: var(--t-radius-pill, 50px);
    padding: 3px 10px;
    font-size: 0.72rem;
    font-weight: 500;
    color: var(--t-text-muted);
  }
  .health-chip.health-good { color: var(--t-status-good, #27ae60); background: rgba(39,174,96,0.08); }
  .health-chip.health-fair { color: var(--t-status-fair, #f39c12); background: rgba(243,156,18,0.08); }
  .health-chip.health-poor { color: var(--t-status-poor, #c0392b); background: rgba(192,57,43,0.08); }

  .tree-card-footer {
    border-top: 1px solid var(--t-border-soft, rgba(0,0,0,0.06));
    padding-top: 8px;
    margin-top: 4px;
  }
  .view-link {
    font-size: 0.78rem;
    font-weight: 600;
    color: var(--t-text-brand, #529a67);
    transition: color 0.2s;
  }
  .tree-card:hover .view-link {
    color: #3d7a4e;
  }

  /* ─── Pagination ────────────────────────────────────────────────── */
  .pagination-bar {
    display: flex;
    justify-content: center;
    align-items: center;
    gap: 1.2rem;
    padding: 1.5rem 0 1rem;
  }
  .page-btn {
    background: var(--t-bg-elevated);
    border: 1px solid var(--t-border);
    border-radius: var(--t-radius-md, 10px);
    padding: 8px 18px;
    font-size: 0.82rem;
    font-weight: 600;
    font-family: var(--t-font-body);
    color: var(--t-text-brand, #529a67);
    cursor: pointer;
    transition: all 0.2s;
  }
  .page-btn:hover:not(:disabled) {
    background: rgba(82,154,103,0.08);
    border-color: rgba(82,154,103,0.3);
    transform: translateY(-1px);
  }
  .page-btn:disabled {
    opacity: 0.4;
    cursor: not-allowed;
  }
  .page-info {
    font-size: 0.8rem;
    color: var(--t-text-muted);
    font-weight: 500;
  }

  /* ─── Responsive ────────────────────────────────────────────────── */
  @media (max-width: 768px) {
    .filters-grid {
      grid-template-columns: 1fr 1fr;
    }
    .results-grid {
      grid-template-columns: 1fr;
    }
    .hero-title {
      font-size: 1.5rem;
    }
    .filters-row-2 {
      grid-template-columns: 1fr;
    }
    .filters-row-3 {
      grid-template-columns: 1fr;
    }
  }
  @media (max-width: 480px) {
    .filters-row-2,
    .filters-row-3 {
      grid-template-columns: 1fr;
    }
  }

  /* ─── Tree ID Preview ───────────────────────────────────────────── */
  .filter-group input.input-valid {
    border-color: var(--t-status-good, #27ae60);
    box-shadow: 0 0 0 3px rgba(39,174,96,0.1);
  }
  .filter-group input.input-invalid {
    border-color: var(--t-status-poor, #c0392b);
    box-shadow: 0 0 0 3px rgba(192,57,43,0.08);
  }
  .tree-preview-msg {
    font-size: 0.78rem;
    margin-top: 6px;
    padding: 4px 0;
  }
  .tree-preview-msg.checking {
    color: var(--t-text-muted);
    animation: pulse-fade 1.2s ease-in-out infinite;
  }
  @keyframes pulse-fade {
    0%, 100% { opacity: 0.5; }
    50% { opacity: 1; }
  }
  .tree-preview-msg.not-found {
    color: var(--t-status-poor, #c0392b);
  }

  .tree-preview-card {
    margin-top: 8px;
    background: linear-gradient(135deg, rgba(82,154,103,0.06), rgba(45,122,58,0.02));
    border: 1px solid rgba(82,154,103,0.25);
    border-radius: var(--t-radius-lg, 14px);
    padding: 12px 14px;
    cursor: pointer;
    transition: all 0.25s;
    animation: cardSlideIn 0.3s ease both;
  }
  @keyframes cardSlideIn {
    from { opacity: 0; transform: translateY(-6px); }
    to   { opacity: 1; transform: translateY(0); }
  }
  .tree-preview-card:hover {
    border-color: rgba(82,154,103,0.5);
    box-shadow: 0 4px 16px rgba(82,154,103,0.1);
    transform: translateY(-1px);
  }

  .tp-header {
    display: flex;
    align-items: center;
    gap: 10px;
    margin-bottom: 8px;
  }
  .tp-emoji {
    font-size: 1.5rem;
    flex-shrink: 0;
    filter: drop-shadow(0 1px 2px rgba(0,0,0,0.1));
  }
  .tp-info {
    flex: 1;
    min-width: 0;
  }
  .tp-info strong {
    display: block;
    font-size: 0.92rem;
    color: var(--t-text-heading);
    text-transform: capitalize;
  }
  .tp-latin {
    font-size: 0.72rem;
    color: var(--t-text-faint);
    font-style: italic;
  }
  .tp-id {
    background: linear-gradient(135deg, rgba(82,154,103,0.12), rgba(45,122,58,0.06));
    border: 1px solid rgba(82,154,103,0.3);
    border-radius: var(--t-radius-pill, 50px);
    padding: 2px 10px;
    font-size: 0.72rem;
    font-weight: 700;
    color: var(--t-text-brand, #529a67);
    font-family: 'DM Mono', 'Courier New', monospace;
    flex-shrink: 0;
  }

  .tp-details {
    display: flex;
    flex-wrap: wrap;
    gap: 6px;
    margin-bottom: 6px;
  }
  .tp-chip {
    background: var(--t-bg-hover, rgba(0,0,0,0.03));
    border-radius: var(--t-radius-pill, 50px);
    padding: 3px 10px;
    font-size: 0.72rem;
    font-weight: 500;
    color: var(--t-text-muted);
  }
  .tp-chip.health-good { color: var(--t-status-good, #27ae60); background: rgba(39,174,96,0.08); }
  .tp-chip.health-fair { color: var(--t-status-fair, #f39c12); background: rgba(243,156,18,0.08); }
  .tp-chip.health-poor { color: var(--t-status-poor, #c0392b); background: rgba(192,57,43,0.08); }

  .tp-action {
    font-size: 0.78rem;
    font-weight: 600;
    color: var(--t-text-brand, #529a67);
    transition: color 0.2s;
  }
  .tree-preview-card:hover .tp-action {
    color: #3d7a4e;
  }
</style>

