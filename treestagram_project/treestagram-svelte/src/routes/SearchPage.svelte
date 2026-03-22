<script>
  import { searchTreesMulti } from "../lib/api.js";
  import LeftNav from "../components/LeftNav.svelte";
  import BackgroundRings from "../components/BackgroundRings.svelte";
  export let navigate;

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

  async function doSearch() {
    offset = 0;
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
</script>

<div class="search-page">
  <LeftNav {navigate} activePage="search" />
  <div class="content">
    <h1>Search Trees</h1>
    <div class="search-bar">
        <input type="text" placeholder="Tree ID" bind:value={tree_id} />
        <input type="text" placeholder="Common Name" bind:value={spc_common} />
        <input type="text" placeholder="Latin Name" bind:value={spc_latin} />
        <input type="text" placeholder="Status (Alive, Dead, Stump)" bind:value={status} />
        <input type="text" placeholder="Health (Good, Fair, Poor)" bind:value={health} />
        <input type="text" placeholder="Borough" bind:value={borough} />
        <button on:click={doSearch}>Search</button>
  </div>

    {#if loading}
      <p>Loading...</p>
    {:else if results.length === 0}
      <p>No results found.</p>
    {:else}
      <ul class="tree-list">
        {#each results as tree}
          <li class="tree-item" on:click={() => goToTree(tree.tree_id)}>
            🌳 {tree.tree_id} {tree.spc_common} ({tree.spc_latin}) — {tree.status}, {tree.health} — {tree.borough}
          </li>
        {/each}
      </ul>

      <div class="pagination">
        <button on:click={prevPage} disabled={offset === 0}>Prev</button>
        <span>{offset + 1} – {Math.min(offset + limit, totalCount)} of {totalCount}</span>
        <button on:click={nextPage} disabled={offset + limit >= totalCount}>Next</button>
      </div>
    {/if}
  </div>
</div>

<style>
    .search-page { padding: 1rem 2rem; border-radius: var(--t-radius-pill);}
    .search-bar { display: flex; flex-wrap: wrap; gap: 0.5rem; margin-bottom: 1rem; }
     input { flex: 1 1 150px; padding: 0.5rem; font-size: 0.9rem; }
     button { 
        padding: 0.5rem 1rem; 
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
    .tree-list { list-style: none; padding: 0; }
    .tree-item { padding: 0.5rem; cursor: pointer; border-bottom: 1px solid #ddd; }
    .tree-item:hover { background: #f0f0f0; }
    .pagination { margin-top: 1rem; display: flex; gap: 1rem; align-items: center; }
    .pagination button[disabled] { opacity: 0.5; cursor: not-allowed; }

    /* Add left padding to avoid the sidebar */
    .search-page .content {
    padding-left: 60px; /* matches collapsed sidebar width */
    transition: padding-left 0.25s;
    }

    /* Optional: expand padding when sidebar is hovered (200px) */
    .left-nav:hover ~ .search-page .content {
    padding-left: 200px;
    }

    input, button {
    border-radius: 8px;
    }

    .search-bar input {
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

    .tree-list {
        list-style: none;
        padding: 0;
        margin: 0;
    }

    .tree-item {
        padding: 0.6rem 0.8rem;
        border-bottom: 1px solid rgba(138, 154, 91, 0.2);
        cursor: pointer;
        border-radius: 8px;
        transition: background 0.2s;
    }

    .tree-item:hover {
        background: rgba(138, 154, 91, 0.1);
    }
</style>

