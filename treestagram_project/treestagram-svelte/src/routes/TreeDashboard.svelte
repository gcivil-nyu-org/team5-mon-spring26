<script>
    import LeftNav from "../components/LeftNav.svelte";
    import BackgroundRings from "../components/BackgroundRings.svelte";
    export let navigate;
    export let treeId;

    import { onMount } from "svelte";

    let tree = null;

    onMount(async () => {
        try {
        const res = await fetch(`/trees/api/${treeId}/`, { credentials: "include" });
        if (!res.ok) throw new Error("Failed to fetch tree");
        tree = await res.json();
        console.log("Tree loaded:", tree);
        } catch (err) {
        console.error("Error fetching tree:", err);
        }
    });

    $: diameter =
    tree
        ? (tree.tree_dbh > 0
            ? tree.tree_dbh
            : (tree.stump_diam > 0 ? tree.stump_diam : null))
        : null;

    // estimate stormwater savings
    $: stormwaterSavings =
        diameter ? Math.round(0.6 * diameter * diameter) : null;

    $: problemList =
        tree && tree.problems && tree.problems !== "None"
            ? tree.problems.split(",")
            : [];
</script>

{#if tree}
<div class="page">
    <BackgroundRings />
    <LeftNav {navigate} activePage="explore" />

    <div class="dashboard-hero">
        <div class="dash-hero-content">
            <div class="tree-title-block">
                <div class="tree-species">
                    {tree.spc_latin}
                </div>
                <h1>{tree.spc_common} #{tree.tree_id}<br />{tree.zip_city}</h1>
                <div class="tree-meta-chips">
                    <span class="chip chip-health-good">Health: {tree.health}</span>
                    <span class="chip chip-health-good">Status: {tree.status}</span>
                    <span class="chip chip-health-good">Borough: {tree.borough}</span>
                    <span class="chip chip-health-good">ID: {tree.tree_id}</span>
                    <span class="chip chip-health-good">Latitude: {tree.latitude}</span>
                    <span class="chip chip-health-good">Longitude: {tree.longitude}</span>
                </div>
            </div>
            <div class="dash-tree-actions">
                <button class="btn-follow">🌟 Follow Tree</button>
                <button class="btn-apply-ct" on:click={() => navigate("/chat")}
                    >💬 Group Chat (127)</button
                >
            </div>
        </div>
        <div class="dash-tab-bar">
            <button class="dash-tab active">Overview</button>
            <button class="dash-tab">Posts</button>
        </div>
    </div>

    <div class="dashboard-body">
        <div class="dash-main">
            <div class="stat-grid">
                <div class="stat-card">
                    <div class="s-icon">💧</div>
                    <div class="s-label">Stormwater Savings</div>
                    <div class="s-val">
                        {#if stormwaterSavings}
                            ${stormwaterSavings.toLocaleString()}
                        {:else}
                            Unknown
                        {/if}
                    </div>
                    <div class="s-sub">per year</div>
                </div>
                <div class="stat-card">
                    <div class="s-icon">👥</div>
                    <div class="s-label">Fans</div>
                    <div class="s-val">127</div>
                    <div class="s-sub">following this tree</div>
                </div>
                <div class="stat-card">
                    <div class="s-icon">📸</div>
                    <div class="s-label">Total Posts</div>
                    <div class="s-val">342</div>
                    <div class="s-sub">community posts</div>
                </div>
            </div>

            <div class="content-card">
                <h3>Tree Problems</h3>

                {#if problemList.length > 0}
                    <div class="problem-grid">
                        {#each problemList as problem}
                            <div class="problem-item">
                                ⚠️ {problem}
                            </div>
                        {/each}
                    </div>
                {:else}
                    <div class="no-problem">
                        🌿 No reported problems
                    </div>
                {/if}
            </div>

            <div class="content-card">
                <h3>Root Probelms</h3>
                <div class="env-ratings">
                    <div class="env-item">
                        <div class="env-label">Caused by Stones</div>
                        <div class="env-score">{tree.root_stone ? "YES" : "NO"}</div>
                    </div>
                    <div class="env-item">
                        <div class="env-label">Caused by Metal Grates</div>
                        <div class="env-score">{tree.root_grate ? "YES" : "NO"}</div>
                    </div>
                    <div class="env-item">
                        <div class="env-label">Caused by Others</div>
                        <div class="env-score">{tree.root_other ? "YES" : "NO"}</div>
                    </div>      
                </div>
            </div>

            <div class="content-card">
                <h3>Trunk Probelms</h3>
                <div class="env-ratings">
                    <div class="env-item">
                        <div class="env-label">Caused by Wires or Ropes</div>
                        <div class="env-score">{tree.trunk_wire ? "YES" : "NO"}</div>
                    </div>
                    <div class="env-item">
                        <div class="env-label">Caused by Installed Lighting</div>
                        <div class="env-score">{tree.trnk_light ? "YES" : "NO"}</div>
                    </div>
                    <div class="env-item">
                        <div class="env-label">Caused by Others</div>
                        <div class="env-score">{tree.trnk_other ? "YES" : "NO"}</div>
                    </div>      
                </div>
            </div>

            <div class="content-card">
                <h3>Branch Probelms</h3>
                <div class="env-ratings">
                    <div class="env-item">
                        <div class="env-label">Caused by Lights or Wires</div>
                        <div class="env-score">{tree.brch_light ? "YES" : "NO"}</div>
                    </div>
                    <div class="env-item">
                        <div class="env-label">Caused by Sneakers</div>
                        <div class="env-score">{tree.brch_shoe ? "YES" : "NO"}</div>
                    </div>
                    <div class="env-item">
                        <div class="env-label">Caused by Others</div>
                        <div class="env-score">{tree.brch_other ? "YES" : "NO"}</div>
                    </div>      
                </div>
            </div>

            <div class="content-card">
                <h3>Location & Sidewalk Condition</h3>

                <div class="sidecurb-ratings">
                    <div class="env-item">
                        <div class="env-label">Curb Location</div>
                        <div class="env-score">
                            {tree.curb_loc === "OnCurb" ? "Along the curb" : "Offset from curb"}
                        </div>
                    </div>

                    <div class="env-item">
                        <div class="env-label">Sidewalk Damage</div>
                        <div class="env-score">
                            {tree.sidewalk === "Damage" ? "⚠️ Damage detected" : "No damage"}
                        </div>
                    </div>
                </div>
            </div>

            <div class="content-card">
                <h3>Recent Community Posts</h3>
                <div class="posts-mini">
                      <div class="post-mini">
                        <div class="post-mini-thumb">🍂</div>
                        <div class="post-mini-info">
                            <strong>Beautiful fall foliage this season</strong>
                            <small>@central_park_fan · 3 days ago</small>
                        </div>
                        <span class="post-mini-likes">❤️ 187</span>
                    </div>
                    <div class="post-mini">
                        <div class="post-mini-thumb">🌿</div>
                        <div class="post-mini-info">
                            <strong>New growth on lower branches!</strong>
                            <small>@nyc_nature_walks · 1 week ago</small>
                        </div>
                        <span class="post-mini-likes">❤️ 95</span>
                    </div>
                </div>
            </div>
        </div>

        <aside class="dash-right">
            <div class="ct-card">
                <h3>Caretakers (2/2)</h3>
                <div class="ct-profile">
                    <div class="ct-avatar">🧑</div>
                    <div class="ct-info">
                        <strong>@brooklyn_botanist</strong>
                        <small>Caretaker since Jan 2024</small>
                    </div>
                    <span class="ct-badge">Primary</span>
                </div>
                <div class="ct-profile">
                    <div class="ct-avatar alt">👩</div>
                    <div class="ct-info">
                        <strong>@treelover_nyc</strong>
                        <small>Caretaker since Mar 2024</small>
                    </div>
                </div>
                <div class="ct-notice">
                    Slots full. You can join the waiting list.
                </div>
            </div>

            <div class="ct-card">
                <h3>Tree Info</h3>
                <table class="tree-info-table">
                    <tr><td>Species</td><td>{tree.spc_common}</td></tr>
                    <tr><td>Latin Name</td><td>{tree.spc_latin}</td></tr>
                    <tr>
                        <td>Trunk Diameter</td>
                        <td>{tree.tree_dbh === 0 ? "Unknown" : `${tree.tree_dbh} in`}</td>
                    </tr>
                    <tr>
                        <td>Stump Diameter</td>
                        <td>{tree.stump_diam === 0 ? "Unknown" : `${tree.stump_diam} in`}</td>
                    </tr>
                    <tr><td>Zip City</td><td>{tree.zip_city}</td></tr>
                    <tr><td>Borough</td><td>{tree.borough}</td></tr>
                    <tr><td>Address</td><td>{tree.address}</td></tr>
                </table>
            </div>
        </aside>
    </div>
</div>      

            
{:else}
  <p>Loading tree data...</p>
{/if}

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
        background: #faf9f6; /* Warm White background */
        min-height: 100vh;
        padding-left: 60px;
        color: #4a4a4a;
        position: relative;
        z-index: 0;
        overflow: hidden;
    }
    /* Dashboard Top Bar */
    .dash-top-bar {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 1rem 3rem;
        background: #faf9f6;
        border-bottom: 1px solid var(--mist);
        gap: 1.5rem;
    }
    .search-container {
        flex: 1;
        position: relative;
        max-width: 600px;
    }
    .search-icon {
        position: absolute;
        left: 1rem;
        top: 50%;
        transform: translateY(-50%);
        font-size: 0.9rem;
        opacity: 0.5;
    }
    .dash-search-input {
        width: 100%;
        padding: 0.6rem 1rem 0.6rem 2.8rem;
        border-radius: 20px;
        border: 1.5px solid var(--canopy);
        background: white;
        font-family: "DM Sans", sans-serif;
        font-size: 0.9rem;
        transition: all 0.2s;
        color: var(--ink);
    }
    .dash-search-input:focus {
        outline: none;
        border-color: var(--sage);
        box-shadow: 0 0 0 4px rgba(107, 143, 113, 0.1);
    }
    .btn-filter {
        background: white;
        border: 1.5px solid var(--canopy);
        padding: 0.5rem 1.2rem;
        border-radius: 20px;
        display: flex;
        align-items: center;
        gap: 0.5rem;
        font-family: "DM Sans", sans-serif;
        font-size: 0.85rem;
        font-weight: 600;
        color: var(--bark);
        cursor: pointer;
        transition: all 0.2s;
    }
    .btn-filter:hover {
        background: var(--mist);
        border-color: var(--sage);
    }
    .filter-icon {
        font-size: 0.8rem;
    }

    /* Dashboard Hero */
    .dashboard-hero {
        background: #8a9a5b; /* Sage Leaf Green hero */
        position: relative;
        overflow: hidden;
        padding: 1.5rem 3rem 0;
    }
    .dashboard-hero::before {
        content: "";
        position: absolute;
        inset: 0;
        background: radial-gradient(
            ellipse at 70% 50%,
            rgba(61, 90, 62, 0.4) 0%,
            transparent 60%
        );
    }
    .dash-breadcrumb {
        position: relative;
        z-index: 1;
        display: flex;
        align-items: center;
        gap: 0.5rem;
        color: var(--canopy);
        font-size: 0.8rem;
        margin-bottom: 1.5rem;
    }
    .dash-breadcrumb span {
        color: var(--sage);
    }
    .breadcrumb-link {
        background: none;
        border: none;
        color: var(--leaf);
        cursor: pointer;
        font-family: "DM Sans", sans-serif;
        font-size: 0.8rem;
        padding: 0;
        text-decoration: none;
    }
    .breadcrumb-link:hover {
        text-decoration: underline;
    }
    .dash-hero-content {
        position: relative;
        z-index: 1;
        display: grid;
        grid-template-columns: 1fr auto;
        gap: 2rem;
        align-items: end;
        padding-bottom: 2rem;
    }
    .tree-species {
        font-size: 0.75rem;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        color: var(--leaf);
        margin-bottom: 0.5rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    .tree-title-block h1 {
        font-family: "Playfair Display", serif;
        font-size: 2.8rem;
        color: white;
        line-height: 1.1;
        margin-bottom: 0.8rem;
    }
    .tree-meta-chips {
        display: flex;
        gap: 0.6rem;
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
        background: rgba(250, 249, 246, 0.2);
        color: #faf9f6;
        border: 1px solid rgba(250, 249, 246, 0.4);
    }
    .chip-borough {
        background: rgba(255, 255, 255, 0.1);
        color: var(--canopy);
        border: 1px solid rgba(255, 255, 255, 0.2);
    }
    .chip-id {
        background: #a44a3f;
        color: #faf9f6;
        border: 1px solid rgba(164, 74, 63, 0.3);
        font-family: "DM Mono", monospace;
        font-size: 0.72rem;
    }
    .dash-tree-actions {
        display: flex;
        flex-direction: column;
        gap: 0.6rem;
    }
    .btn-follow {
        background: #36454f; /* Charcoal Gray */
        color: #faf9f6; /* Contrasting text */
        border: none;
        padding: 0.7rem 1.5rem;
        border-radius: 25px;
        font-weight: 700;
        font-family: "DM Sans", sans-serif;
        font-size: 0.9rem;
        cursor: pointer;
        transition: all 0.2s;
    }
    .btn-follow:hover {
        background: var(--sun);
        transform: translateY(-1px);
    }
    .btn-apply-ct {
        background: none;
        color: #faf9f6;
        border: 1.5px solid rgba(250, 249, 246, 0.4);
        padding: 0.6rem 1.2rem;
        border-radius: 25px;
        font-family: "DM Sans", sans-serif;
        font-size: 0.85rem;
        cursor: pointer;
        transition: all 0.2s;
    }
    .btn-apply-ct:hover {
        border-color: #36454f;
        color: #36454f;
    }
    .dash-tab-bar {
        position: relative;
        z-index: 1;
        display: flex;
        gap: 0;
    }
    .dash-tab {
        background: none;
        border: none;
        color: var(--canopy);
        padding: 0.8rem 1.4rem;
        font-family: "DM Sans", sans-serif;
        font-size: 0.88rem;
        cursor: pointer;
        transition: color 0.2s;
        border-radius: 10px 10px 0 0;
    }
    .dash-tab:hover {
        color: white;
    }
    .dash-tab.active {
        color: #2b2b2b;
        background: #faf9f6;
        font-weight: 600;
    }

    /* Dashboard Body */
    .dashboard-body {
        max-width: 1100px;
        margin: 0 auto;
        padding: 2rem 1.5rem;
        display: grid;
        grid-template-columns: 1fr 320px;
        gap: 1.5rem;
    }
    .stat-grid {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 1rem;
        margin-bottom: 1.5rem;
    }
    .stat-card {
        background: #cdd9af; /* Sage Mist */
        border-radius: 14px;
        padding: 1.2rem;
        box-shadow: 0 2px 12px rgba(138, 154, 91, 0.08);
    }
    .stat-card .s-label {
        font-size: 0.72rem;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        color: #a44a3f; /* Redwood Rust */
        margin-bottom: 0.5rem;
    }
    .stat-card .s-val {
        font-family: "Playfair Display", serif;
        font-size: 1.8rem;
        color: var(--ink);
        line-height: 1;
    }
    .stat-card .s-val.green {
        color: var(--moss);
    }
    .stat-card .s-sub {
        font-size: 0.75rem;
        color: var(--sage);
        margin-top: 0.2rem;
    }
    .stat-card .s-icon {
        font-size: 1.5rem;
        margin-bottom: 0.4rem;
    }

    .content-card {
        background: #cdd9af; /* Sage Mist */
        border-radius: 16px;
        padding: 1.4rem;
        box-shadow: 0 2px 12px rgba(138, 154, 91, 0.08);
        margin-bottom: 1.5rem;
    }
    .content-card h3 {
        font-size: 0.75rem;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        color: #a44a3f; /* Redwood Rust */
        margin-bottom: 1rem;
    }

    /* Health history bars */
    .health-history-bar {
        display: flex;
        align-items: flex-end;
        gap: 0.4rem;
        height: 80px;
        margin-bottom: 0.5rem;
    }
    .hh-bar {
        flex: 1;
        border-radius: 4px 4px 0 0;
        cursor: pointer;
        transition: opacity 0.2s;
    }
    .hh-bar:hover {
        opacity: 0.8;
    }
    .hh-bar.good {
        background: var(--leaf);
    }
    .hh-bar.fair {
        background: var(--sun);
    }
    .hh-months {
        display: flex;
        gap: 0.4rem;
        font-size: 0.68rem;
        color: var(--canopy);
        text-align: center;
    }
    .hh-months span {
        flex: 1;
    }
    .legend {
        display: flex;
        gap: 1rem;
        margin-top: 0.8rem;
    }
    .legend span {
        font-size: 0.75rem;
        display: flex;
        align-items: center;
        gap: 0.3rem;
    }
    .dot {
        width: 10px;
        height: 10px;
        border-radius: 2px;
        display: inline-block;
    }
    .good-dot {
        background: var(--leaf);
    }
    .fair-dot {
        background: var(--sun);
    }
    .poor-dot {
        background: #e07070;
    }

    /* Environmental ratings */
    .sidecurb-ratings {
        display: grid;
        grid-template-columns: repeat(2, 1fr);
        gap: 0.8rem;
    }

    /* Environmental ratings */
    .env-ratings {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 0.8rem;
    }
    .env-item {
        background: var(--mist);
        border-radius: 10px;
        padding: 0.8rem;
    }
    .env-item .env-label {
        font-size: 0.72rem;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        color: #a44a3f; /* Redwood Rust */
        display: block;
        margin-bottom: 0.4rem;
    }
    .env-bar-track {
        height: 6px;
        background: var(--canopy);
        border-radius: 3px;
        overflow: hidden;
    }
    .env-bar-fill {
        height: 100%;
        border-radius: 3px;
    }
    .green-fill {
        background: var(--sage);
        width: 80%;
    }
    .green-fill.wide {
        width: 90%;
    }
    .yellow-fill {
        background: var(--sun);
        width: 55%;
    }
    .orange-fill {
        background: #d4874f;
        width: 70%;
    }
    .env-score {
        font-weight: 700;
        font-size: 0.88rem;
        color: var(--ink);
        margin-top: 0.3rem;
    }

    /* Compact posts */
    .posts-mini {
        display: flex;
        flex-direction: column;
        gap: 0.8rem;
    }
    .post-mini {
        display: flex;
        align-items: center;
        gap: 0.8rem;
        padding: 0.8rem;
        border-radius: 10px;
        background: var(--mist);
        cursor: pointer;
        transition: background 0.2s;
    }
    .post-mini:hover {
        background: var(--canopy);
    }
    .post-mini-thumb {
        width: 50px;
        height: 50px;
        border-radius: 8px;
        background: linear-gradient(135deg, var(--moss), var(--leaf));
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.5rem;
        flex-shrink: 0;
    }
    .post-mini-info {
        flex: 1;
        min-width: 0;
    }
    .post-mini-info strong {
        display: block;
        font-size: 0.85rem;
        color: var(--ink);
    }
    .post-mini-info small {
        font-size: 0.75rem;
        color: var(--sage);
    }
    .post-mini-likes {
        font-size: 0.78rem;
        color: var(--sage);
    }

    /* Right sidebar */
    .ct-card {
        background: white;
        border-radius: 16px;
        padding: 1.4rem;
        box-shadow: 0 2px 12px var(--shadow);
        margin-bottom: 1rem;
    }
    .ct-card h3 {
        font-size: 0.75rem;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        color: var(--sage);
        margin-bottom: 1rem;
    }
    .ct-profile {
        display: flex;
        align-items: center;
        gap: 0.8rem;
        margin-bottom: 0.8rem;
    }
    .ct-avatar {
        width: 44px;
        height: 44px;
        border-radius: 50%;
        background: linear-gradient(135deg, var(--bark), #8b4513);
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.2rem;
        flex-shrink: 0;
        border: 2px solid var(--leaf);
    }
    .ct-avatar.alt {
        background: linear-gradient(135deg, var(--moss), var(--sage));
    }
    .ct-info {
        flex: 1;
    }
    .ct-info strong {
        display: block;
        font-size: 0.9rem;
        color: var(--ink);
    }
    .ct-info small {
        font-size: 0.75rem;
        color: var(--sage);
    }
    .ct-badge {
        font-size: 0.65rem;
        background: rgba(61, 90, 62, 0.15);
        color: var(--moss);
        padding: 0.2rem 0.5rem;
        border-radius: 4px;
        font-weight: 600;
    }
    .ct-notice {
        font-size: 0.8rem;
        color: var(--sage);
        background: var(--mist);
        border-radius: 8px;
        padding: 0.6rem;
        margin-top: 0.5rem;
    }
    .fans-count {
        text-align: center;
        padding: 1rem;
        background: var(--mist);
        border-radius: 12px;
    }
    .fans-count .num {
        font-family: "Playfair Display", serif;
        font-size: 2.2rem;
        color: var(--moss);
        display: block;
    }
    .fans-count small {
        font-size: 0.8rem;
        color: var(--sage);
    }
    .fans-avatars {
        display: flex;
        margin-top: 0.5rem;
        justify-content: center;
    }
    .fans-avatars .fa {
        width: 28px;
        height: 28px;
        border-radius: 50%;
        background: linear-gradient(135deg, var(--sage), var(--canopy));
        border: 2px solid white;
        margin-left: -6px;
        font-size: 0.8rem;
        display: flex;
        align-items: center;
        justify-content: center;
    }
    .tree-info-table {
        width: 100%;
        font-size: 0.82rem;
        border-collapse: collapse;
    }
    .tree-info-table tr {
        border-bottom: 1px solid var(--mist);
    }
    .tree-info-table tr:last-child {
        border: none;
    }
    .tree-info-table td {
        padding: 0.4rem 0;
    }
    .tree-info-table td:first-child {
        color: var(--sage);
    }
    .tree-info-table td:last-child {
        color: var(--ink);
        font-weight: 500;
        text-align: right;
    }
</style>
