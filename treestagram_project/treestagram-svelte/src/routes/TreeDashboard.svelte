<script>
    import LeftNav from "../components/LeftNav.svelte";
    import BackgroundRings from "../components/BackgroundRings.svelte";
    import { apiToggleTreeFollow } from "../lib/api.js";
    export let navigate;
    export let treeId;

    import { onMount } from "svelte";

    let tree = null;
    let photos = [];
    let photoCount = 0;
    let posts = [];
    let postCount = 0;
    let followingTree = false;
    let followerCount = 0;
    
    let showLockModal = false;

    // Tab State
    let activeTab = 'overview';

    onMount(() => {
        // any one-time setup
    });

    $: if (treeId) {
        loadDashboard();
    }

    async function loadDashboard() {
        try {
            const res = await fetch(`/trees/api/${treeId}/dashboard/`, { credentials: "include" });
            if (!res.ok) throw new Error("Failed to fetch tree");
            const data = await res.json();
            tree = data;
            photos = data.photos || [];
            photoCount = data.photo_count || 0;
            posts = data.posts || [];
            postCount = data.post_count || 0;
            followerCount = data.follower_count || 0;
        } catch (err) {
            console.error("Error fetching tree:", err);
        }

        // Check follow state
        try {
            const fRes = await fetch(`/api/my-followed-trees/`, { credentials: 'include' });
            if (fRes.ok) {
                const fData = await fRes.json();
                if (fData.success) {
                    followingTree = fData.trees.some(t => String(t.tree_id) === String(treeId));
                }
            }
        } catch (e) { /* ignore */ }
    }

    function timeAgo(isoStr) {
        const diff = (Date.now() - new Date(isoStr).getTime()) / 1000;
        if (diff < 60) return "just now";
        if (diff < 3600) return `${Math.floor(diff / 60)}m ago`;
        if (diff < 86400) return `${Math.floor(diff / 3600)}h ago`;
        if (diff < 604800) return `${Math.floor(diff / 86400)}d ago`;
        return new Date(isoStr).toLocaleDateString();
    }

    $: diameter = tree
        ? (tree.tree_dbh > 0
            ? tree.tree_dbh
            : (tree.stump_diam > 0 ? tree.stump_diam : null))
        : null;

    // --- Scientific Data Calibration (ISA / US Forest Service Standards) ---
    const SPECIES_FACTORS = {
        'honeylocust': 3.0, 'black locust': 2.0, 'silver maple': 3.0, 'Norway maple': 4.5,
        'sugar maple': 5.5, 'red maple': 4.5, 'white oak': 5.0, 'northern red oak': 4.0,
        'pin oak': 3.0, 'London planetree': 4.5, 'American elm': 4.0, 'ginkgo': 4.0,
        'green ash': 4.0, 'white ash': 5.0, 'littleleaf linden': 3.0, 'bradford pear': 3.0,
        'callery pear': 3.0, 'dogwood': 7.0, 'flowering dogwood': 7.0, 'cherry': 3.5,
        'black cherry': 3.5, 'white pine': 5.0, 'scots pine': 3.5, 'cottonwood': 2.0,
        'eastern cottonwood': 2.0, 'catalpa': 3.0, 'horse chestnut': 8.0, 'black walnut': 4.5,
        'boxelder': 3.0, 'river birch': 2.0, 'paper birch': 3.5, 'tulip-poplar': 3.0,
        'sweetgum': 4.0, 'sycamore maple': 4.0, 'dawn redwood': 2.5, 'bald cypress': 2.0,
        'willow': 2.0, 'weeping willow': 2.0, 'japanese zelkova': 4.0, 'mulberry': 2.0
    };

    function getGrowthFactor(name) {
        if (!name) return 4.5;
        const lower = name.toLowerCase();
        for (const [key, factor] of Object.entries(SPECIES_FACTORS)) {
            if (lower.includes(key)) return factor;
        }
        return 4.5;
    }

    $: activeFactor = tree ? getGrowthFactor(tree.spc_common) : 4.5;
    $: stormwaterSavings = diameter ? Math.round(0.6 * diameter * diameter) : null;
    $: estimatedAge = diameter ? Math.round(diameter * activeFactor) : null;
    $: sequestrationIntensity = 6 / activeFactor; 
    $: co2Absorbed = diameter ? Math.round(diameter * 2.5 * sequestrationIntensity) : null;
    $: canopyCover = diameter ? Math.round(Math.PI * Math.pow((diameter / 2), 2) * 1.5) : null;

    $: problemList =
        tree && tree.problems && tree.problems !== "None"
            ? tree.problems.split(",")
            : [];

    let hoveredRing = null;
    $: rings = diameter ? generateRings(diameter) : [];

    function generateRings(dbh) {
        const numRings = Math.min(Math.max(Math.floor(dbh), 5), 25);
        const ringData = [];
        const events = [
            "Planted as a sapling",
            "Survived a harsh winter",
            "First major pruning",
            "Canopy reached full spread",
            "Root expansion detected",
            "Last ecological inspection"
        ];
        let currentRadius = 180;
        const step = currentRadius / numRings;
        for (let i = 0; i < numRings; i++) {
            let year = new Date().getFullYear() - i;
            let event = i === numRings - 1 ? events[0] : 
                       i === 0 ? "Current growth year" :
                       (i % 5 === 0 ? events[(i/5) % events.length] : null);
            ringData.push({
                id: i, radius: currentRadius, year: year, event: event,
                color: i % 2 === 0 ? "rgba(139, 69, 19, 0.15)" : "rgba(160, 82, 45, 0.25)",
                strokeWidth: Math.random() * 2 + 1.5
            });
            currentRadius -= step * (Math.random() * 0.4 + 0.8);
        }
        return ringData;
    }

    const TREE_COLORS = {
        'honeylocust': 'hsl(40, 70%, 42%)', 'golden raintree': 'hsl(45, 80%, 45%)',
        'ginkgo': 'hsl(50, 85%, 44%)', 'red maple': 'hsl(355, 58%, 38%)',
        'red pine': 'hsl(0, 45%, 35%)', 'crimson king maple': 'hsl(340, 55%, 30%)',
        'northern red oak': 'hsl(8, 50%, 36%)', 'scarlet oak': 'hsl(5, 60%, 38%)',
        'cherry': 'hsl(340, 55%, 65%)', 'black cherry': 'hsl(345, 40%, 30%)',
        'flowering dogwood': 'hsl(350, 40%, 75%)', 'crab apple': 'hsl(350, 50%, 55%)',
        'purple-leaf plum': 'hsl(290, 40%, 32%)', 'sweetgum': 'hsl(20, 50%, 40%)',
        'tulip-poplar': 'hsl(45, 55%, 42%)', 'English oak': 'hsl(30, 45%, 34%)',
        'black oak': 'hsl(25, 35%, 25%)', 'pin oak': 'hsl(22, 42%, 35%)',
        'white oak': 'hsl(38, 25%, 50%)', 'silver maple': 'hsl(210, 12%, 55%)',
        'paper birch': 'hsl(40, 10%, 75%)', 'Scots pine': 'hsl(145, 50%, 28%)',
        'white pine': 'hsl(135, 35%, 38%)', 'Norway spruce': 'hsl(155, 50%, 25%)',
        'blue spruce': 'hsl(195, 40%, 40%)', 'Douglas-fir': 'hsl(148, 55%, 26%)',
        'bald cypress': 'hsl(100, 30%, 38%)', 'dawn redwood': 'hsl(15, 40%, 35%)',
        'American elm': 'hsl(100, 35%, 40%)', 'London planetree': 'hsl(75, 28%, 38%)',
        'Japanese zelkova': 'hsl(80, 30%, 42%)', 'green ash': 'hsl(105, 40%, 38%)',
        'weeping willow': 'hsl(85, 45%, 42%)', 'horse chestnut': 'hsl(20, 55%, 32%)',
        'black locust': 'hsl(220, 10%, 28%)', 'black walnut': 'hsl(30, 20%, 25%)',
        'Japanese maple': 'hsl(350, 55%, 40%)', 'Norway maple': 'hsl(90, 30%, 38%)',
        'sugar maple': 'hsl(30, 60%, 42%)', 'boxelder': 'hsl(95, 30%, 42%)',
        'American beech': 'hsl(35, 20%, 52%)', 'magnolia': 'hsl(330, 20%, 60%)',
        'Callery pear': 'hsl(0, 0%, 72%)', 'eastern cottonwood': 'hsl(60, 20%, 48%)',
        'river birch': 'hsl(25, 30%, 42%)', 'Unknown': 'hsl(0, 0%, 45%)',
    };

    function getEarthyColor(name) {
        if (!name) return '#8a9a5b';
        if (TREE_COLORS[name]) return TREE_COLORS[name];
        const lowerName = name.toLowerCase();
        for (const [key, color] of Object.entries(TREE_COLORS)) {
            if (key.toLowerCase() === lowerName) return color;
        }
        let hash = 0;
        for (let i = 0; i < lowerName.length; i++) {
            hash = lowerName.charCodeAt(i) + ((hash << 5) - hash);
        }
        const h = Math.abs(hash) % 130 + 30;
        const s = Math.abs(hash * 2) % 20 + 25;
        const l = Math.abs(hash * 3) % 15 + 35;
        return `hsl(${h}, ${s}%, ${l}%)`;
    }
    
    $: heroBackgroundColor = tree ? getEarthyColor(tree.spc_common) : '#8a9a5b';
</script>

{#if tree}
<div class="page">
    <BackgroundRings />
    <LeftNav {navigate} activePage="explore" />

    <div class="dashboard-hero" style="background-color: {heroBackgroundColor};">
        <div class="dash-hero-content">
            <div class="tree-title-block">
                <div class="tree-species">{tree.spc_latin}</div>
                <h1>{tree.spc_common} #{tree.tree_id}<br />{tree.zip_city}</h1>
                <div class="tree-meta-chips">
                    <span class="chip chip-fans">👥 {followerCount} fan{followerCount !== 1 ? 's' : ''}</span>
                    <span class="chip chip-health-good">Health: {tree.health}</span>
                    <span class="chip chip-health-good">Status: {tree.status}</span>
                    <span class="chip chip-health-good">Borough: {tree.borough}</span>
                    <span class="chip chip-health-good">ID: {tree.tree_id}</span>
                    <span class="chip chip-health-good">Latitude: {tree.latitude}</span>
                    <span class="chip chip-health-good">Longitude: {tree.longitude}</span>
                </div>
            </div>
            <div class="dash-tree-actions" class:following-state={followingTree}>
                <button class="btn-follow" on:click={async () => {
                    const res = await apiToggleTreeFollow(treeId);
                    if (res.success) { followingTree = res.following; followerCount = res.follower_count; }
                }}>{followingTree ? '✓ Following' : '🌟 Follow Tree'}</button>
                <button class="btn-apply-ct" class:locked={!followingTree} on:click={() => {
                    if (!followingTree) { showLockModal = true; } else { navigate(`/chat?tree=${treeId}`); }
                }}>{#if !followingTree}🔒 {/if}💬 Group Chat</button>
            </div>
        </div>
        <div class="dash-tab-bar">
            <button class="dash-tab {activeTab === 'overview' ? 'active' : ''}" on:click={() => activeTab = 'overview'}>Overview</button>
            <button class="dash-tab {activeTab === 'posts' ? 'active' : ''}" on:click={() => activeTab = 'posts'}>Posts ({postCount})</button>
        </div>
    </div>

    <div class="dashboard-body">
        {#if activeTab === 'overview'}
        <div class="dash-main">
            <div class="stat-grid">
                <div class="stat-card"><div class="s-icon">💧</div><div class="s-label">Stormwater Savings</div><div class="s-val">{#if stormwaterSavings}${stormwaterSavings.toLocaleString()}{:else}Unknown{/if}</div><div class="s-sub">per year</div></div>
                <div class="stat-card"><div class="s-icon">📸</div><div class="s-label">Photos</div><div class="s-val">{photoCount}</div><div class="s-sub">community photos</div></div>
                <div class="stat-card"><div class="s-icon">📝</div><div class="s-label">Total Posts</div><div class="s-val">{postCount}</div><div class="s-sub">community posts</div></div>
            </div>

            <div class="content-card"><h3>Tree Problems</h3>
                {#if problemList.length > 0}<div class="problem-grid">{#each problemList as problem}<div class="problem-item">⚠️ {problem}</div>{/each}</div>{:else}<div class="no-problem">🌿 No reported problems</div>{/if}
            </div>

            <div class="content-card"><h3>Root Problems</h3><div class="env-ratings">
                <div class="env-item"><div class="env-label">Caused by Stones</div><div class="env-score">{tree.root_stone ? "YES" : "NO"}</div></div>
                <div class="env-item"><div class="env-label">Caused by Metal Grates</div><div class="env-score">{tree.root_grate ? "YES" : "NO"}</div></div>
                <div class="env-item"><div class="env-label">Caused by Others</div><div class="env-score">{tree.root_other ? "YES" : "NO"}</div></div>
            </div></div>

            <div class="content-card"><h3>Trunk Problems</h3><div class="env-ratings">
                <div class="env-item"><div class="env-label">Caused by Wires or Ropes</div><div class="env-score">{tree.trunk_wire ? "YES" : "NO"}</div></div>
                <div class="env-item"><div class="env-label">Caused by Installed Lighting</div><div class="env-score">{tree.trnk_light ? "YES" : "NO"}</div></div>
                <div class="env-item"><div class="env-label">Caused by Others</div><div class="env-score">{tree.trnk_other ? "YES" : "NO"}</div></div>
            </div></div>

            <div class="content-card"><h3>Branch Problems</h3><div class="env-ratings">
                <div class="env-item"><div class="env-label">Caused by Lights or Wires</div><div class="env-score">{tree.brch_light ? "YES" : "NO"}</div></div>
                <div class="env-item"><div class="env-label">Caused by Sneakers</div><div class="env-score">{tree.brch_shoe ? "YES" : "NO"}</div></div>
                <div class="env-item"><div class="env-label">Caused by Others</div><div class="env-score">{tree.brch_other ? "YES" : "NO"}</div></div>
            </div></div>

            <div class="content-card"><h3>Location & Sidewalk Condition</h3><div class="sidecurb-ratings">
                <div class="env-item"><div class="env-label">Curb Location</div><div class="env-score">{tree.curb_loc === "OnCurb" ? "Along the curb" : "Offset from curb"}</div></div>
                <div class="env-item"><div class="env-label">Sidewalk Damage</div><div class="env-score">{tree.sidewalk === "Damage" ? "⚠️ Damage detected" : "No damage"}</div></div>
            </div></div>

            <div class="content-card timeline-card">
                <div class="dendro-header"><h3>Dendrochronology Profile</h3><p class="subtitle">Interactive Life Rings</p></div>
                <div class="dendro-container">
                    {#if diameter}
                        <div class="svg-wrapper">
                            <svg viewBox="0 0 400 400" class="tree-rings-svg">
                                <defs>
                                    <filter id="wood-texture" x="-20%" y="-20%" width="140%" height="140%"><feTurbulence type="fractalNoise" baseFrequency="0.03" numOctaves="3" result="noise" /><feDisplacementMap in="SourceGraphic" in2="noise" scale="8" xChannelSelector="R" yChannelSelector="G" /></filter>
                                    <filter id="glow" x="-20%" y="-20%" width="140%" height="140%"><feGaussianBlur stdDeviation="3" result="coloredBlur"/><feMerge><feMergeNode in="coloredBlur"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
                                </defs>
                                <g filter="url(#wood-texture)">
                                    <circle cx="200" cy="200" r="190" fill="#eaddcf" stroke="#6b4423" stroke-width="6" class="bark-layer"/>
                                    {#each rings as ring}
                                        <!-- svelte-ignore a11y-mouse-events-have-key-events -->
                                        <!-- svelte-ignore a11y-no-static-element-interactions -->
                                        <g on:mouseover={() => hoveredRing = ring.id} on:mouseleave={() => hoveredRing = null} style="cursor: crosshair;">
                                            <circle cx="200" cy="200" r={ring.radius} fill="none" stroke="transparent" stroke-width="16" style="pointer-events: stroke;"/>
                                            <circle cx="200" cy="200" r={ring.radius} fill="none" stroke={hoveredRing === ring.id ? "#2d7a3a" : ring.color} stroke-width={hoveredRing === ring.id ? 5 : ring.strokeWidth} class="tree-ring {ring.event ? 'has-event' : ''} {hoveredRing === ring.id ? 'active-ring' : ''}" style="pointer-events: none;"/>
                                            {#if ring.event && hoveredRing !== ring.id}<circle cx="200" cy={200 - ring.radius} r="5" fill="#a44a3f" class="event-dot" style="pointer-events: none;" />{/if}
                                        </g>
                                    {/each}
                                    <circle cx="200" cy="200" r="6" fill="#3e2723" />
                                </g>
                                {#if hoveredRing !== null}
                                    {@const activeRing = rings.find(r => r.id === hoveredRing)}
                                    {#if activeRing.event}<circle cx="200" cy={200 - activeRing.radius} r="6" fill="#ffefca" stroke="#2d7a3a" stroke-width="3" class="active-event-dot" filter="url(#glow)"/>{/if}
                                {/if}
                            </svg>
                        </div>
                        <div class="ring-info-panel">
                            {#if rings.length > 0}
                                {@const activeRing = hoveredRing !== null ? rings.find(r => r.id === hoveredRing) : rings[0]}
                                {#if activeRing}
                                    <div class="ring-details {hoveredRing !== null ? 'active-glow' : ''}">
                                        <div class="rd-header"><h4>Year {activeRing.year}</h4><div class="ring-metric"><span class="metric-value">{Math.round(activeRing.radius)}<small>mm</small></span></div></div>
                                        {#if activeRing.event}<div class="ring-event highlight-event"><div class="event-icon">🌟</div><p>{activeRing.event}</p></div>{:else}<div class="ring-event standard-growth"><div class="event-icon">🌿</div><p>Standard seasonal growth observed. The tree absorbed healthy sunlight and water.</p></div>{/if}
                                    </div>
                                {/if}
                            {/if}
                        </div>
                    {:else}<div class="empty-state"><p>No diameter data available to generate rings.</p></div>{/if}
                </div>
            </div>
        </div>

        <aside class="dash-right">
            <div class="ct-card"><h3>Caretakers ({tree.caretakers?.length || 0}/2)</h3>
                {#if tree.caretakers && tree.caretakers.length > 0}
                    {#each tree.caretakers as ct, index}
                        <div class="ct-profile">
                            <div class="ct-avatar {index % 2 !== 0 ? 'alt' : ''}">
                                {index % 2 === 0 ? '🧑' : '👩'}
                            </div>
                            <div class="ct-info">
                                <strong>@{ct.username}</strong>
                                <small>Caretaker since {new Date(ct.assigned_at).toLocaleDateString(undefined, { month: 'short', year: 'numeric' })}</small>
                            </div>
                            {#if index === 0}
                                <span class="ct-badge">Primary</span>
                            {/if}
                        </div>
                    {/each}
                    {#if tree.caretakers.length >= 2}
                        <div class="ct-notice">Slots full. You can join the waiting list.</div>
                    {/if}
                {:else}
                    <div class="ct-notice">No caretakers yet.</div>
                {/if}
            </div>
            <div class="ct-card"><h3 style="color: #758f6f; font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 1rem;">Tree Info</h3>
                <table class="tree-info-table"><tr><td>Species</td><td>{tree.spc_common}</td></tr><tr><td>Latin Name</td><td>{tree.spc_latin}</td></tr><tr><td>Trunk Diameter</td><td>{tree.tree_dbh === 0 ? "Unknown" : `${tree.tree_dbh} in`}</td></tr><tr><td>Stump Diameter</td><td>{tree.stump_diam === 0 ? "Unknown" : `${tree.stump_diam} in`}</td></tr><tr><td>Zip City</td><td>{tree.zip_city}</td></tr><tr><td>Borough</td><td>{tree.borough}</td></tr><tr><td>Address</td><td>{tree.address}</td></tr></table>
            </div>
            <div class="ct-card"><h3 style="color: #758f6f; font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 1rem;">Ecological Info</h3>
                <table class="tree-info-table"><tr><td>Est. Age</td><td>{estimatedAge ? `${estimatedAge} years` : "Unknown"}</td></tr><tr><td>CO₂ Absorbed</td><td>{co2Absorbed ? `${co2Absorbed.toLocaleString()} lbs/yr` : "Unknown"}</td></tr><tr><td>Canopy Cover</td><td>{canopyCover ? `${canopyCover.toLocaleString()} sq ft` : "Unknown"}</td></tr><tr><td>Stormwater</td><td>{stormwaterSavings ? `$${stormwaterSavings.toLocaleString()}/yr` : "Unknown"}</td></tr></table>
            </div>
        </aside>
        
        {:else if activeTab === 'posts'}
        <div class="dash-main" style="grid-column: 1 / -1;">
            <div class="content-card">
                <!-- <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 2rem;"><h3>Tree Gallery & Posts</h3><button class="btn-primary" on:click={() => navigate('/home')}>+ Create Post</button></div> -->
                {#if posts.length > 0}
                    <div class="posts-grid" style="display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 1.5rem;">
                        {#each posts as post}
                            <div class="post-card" style="border: 1px solid var(--mist); border-radius: 12px; overflow: hidden; background: white; box-shadow: 0 2px 8px rgba(0,0,0,0.05);">
                                {#if post.image_url}<div class="post-img" style="height: 200px; width: 100%; background: #f0f0f0;"><img src={post.image_url} alt="Tree post" style="width: 100%; height: 100%; object-fit: cover;"/></div>{/if}
                                <div class="post-body" style="padding: 1.2rem;">
                                    <div class="post-header" style="display: flex; justify-content: space-between; margin-bottom: 0.8rem;"><strong style="color: var(--moss);">{post.author_username}</strong><small style="color: var(--sage);">{timeAgo(post.created_at)}</small></div>
                                    <p style="margin: 0 0 1rem 0; color: #4a4a4a; line-height: 1.5;">{post.content}</p>
                                    <div class="post-actions" style="display: flex; gap: 1rem; color: var(--sage); font-size: 0.9rem;"><span>❤️ {post.likes_count}</span><span>💬 {post.comments_count}</span></div>
                                </div>
                            </div>
                        {/each}
                    </div>
                {:else}
                    <div class="empty-state" style="text-align: center; padding: 4rem 2rem; color: var(--sage);"><div style="font-size: 3rem; margin-bottom: 1rem;">📸</div><h3 style="font-family: 'Playfair Display', serif; color: var(--bark); margin-bottom: 0.5rem;">No Posts Yet</h3><p>Be the first to share a photo or update about {tree.spc_common} #{tree.tree_id}!</p></div>
                {/if}
            </div>
        </div>
        {/if}
    </div>
</div>      

{:else}
    <div class="loading">Loading Tree Dashboard...</div>
{/if}

{#if showLockModal}
    <!-- svelte-ignore a11y-click-events-have-key-events -->
    <!-- svelte-ignore a11y-no-static-element-interactions -->
    <div class="lock-modal-overlay" on:click={() => showLockModal = false}>
        <div class="lock-modal-card" on:click|stopPropagation>
            <div class="lock-modal-icon">🔒</div>
            <h2 class="lock-modal-title">Group Chat Locked</h2>
            <p class="lock-modal-desc">You must be a fan of <strong>{tree ? tree.spc_common : 'this tree'}</strong> to join its community group chat. Follow this tree to unlock access! 🌿</p>
            <div class="lock-modal-actions">
                <button class="btn-cancel" on:click={() => showLockModal = false}>Close</button>
                <button class="btn-follow-modal" on:click={async () => {
                    const res = await apiToggleTreeFollow(treeId);
                    if (res.success) { followingTree = res.following; followerCount = res.follower_count; showLockModal = false; }
                }}>🌟 Follow Tree Now</button>
            </div>
        </div>
    </div>
{/if}

<style>
    :root { --bark: #2c1810; --moss: #3d5a3e; --sage: #6b8f71; --leaf: #8fbc8f; --canopy: #c5d5c5; --cream: #f5f0e8; --mist: #e8ede8; --sun: #d4a853; --ink: #1a1108; --shadow: rgba(44, 24, 16, 0.12); }
    .page { background: #faf9f6; min-height: 100vh; padding-left: 60px; color: #4a4a4a; position: relative; z-index: 0; overflow: hidden; }
    .dash-top-bar { display: flex; align-items: center; justify-content: space-between; padding: 1rem 3rem; background: #faf9f6; border-bottom: 1px solid var(--mist); gap: 1.5rem; }
    .search-container { flex: 1; position: relative; max-width: 600px; }
    .search-icon { position: absolute; left: 1rem; top: 50%; transform: translateY(-50%); font-size: 0.9rem; opacity: 0.5; }
    .dash-search-input { width: 100%; padding: 0.6rem 1rem 0.6rem 2.8rem; border-radius: 20px; border: 1.5px solid var(--canopy); background: white; font-family: "DM Sans", sans-serif; font-size: 0.9rem; transition: all 0.2s; color: var(--ink); }
    .dash-search-input:focus { outline: none; border-color: var(--sage); box-shadow: 0 0 0 4px rgba(107, 143, 113, 0.1); }
    .btn-filter { background: white; border: 1.5px solid var(--canopy); padding: 0.5rem 1.2rem; border-radius: 20px; display: flex; align-items: center; gap: 0.5rem; font-family: "DM Sans", sans-serif; font-size: 0.85rem; font-weight: 600; color: var(--bark); cursor: pointer; transition: all 0.2s; }
    .btn-filter:hover { background: var(--mist); border-color: var(--sage); }
    .filter-icon { font-size: 0.8rem; }
    .dashboard-hero { position: relative; overflow: hidden; padding: 1.5rem 3rem 0; }
    .dashboard-hero::before { content: ""; position: absolute; inset: -50%; width: 200%; height: 200%; background: radial-gradient(ellipse at 20% 50%, rgba(255,255,255,0.15) 0%, transparent 50%), radial-gradient(ellipse at 80% 20%, rgba(255,255,255,0.1) 0%, transparent 40%), radial-gradient(ellipse at 60% 80%, rgba(0,0,0,0.08) 0%, transparent 45%); animation: waterFlow 12s ease-in-out infinite; pointer-events: none; }
    .dashboard-hero::after { content: ""; position: absolute; inset: -50%; width: 200%; height: 200%; background: radial-gradient(ellipse at 70% 30%, rgba(255,255,255,0.12) 0%, transparent 50%), radial-gradient(ellipse at 30% 70%, rgba(255,255,255,0.08) 0%, transparent 45%), radial-gradient(ellipse at 50% 50%, rgba(0,0,0,0.05) 0%, transparent 60%); animation: waterFlow2 16s ease-in-out infinite; pointer-events: none; }
    @keyframes waterFlow { 0% { transform: translate(0%, 0%) rotate(0deg); } 33% { transform: translate(5%, -3%) rotate(1deg); } 66% { transform: translate(-3%, 4%) rotate(-1deg); } 100% { transform: translate(0%, 0%) rotate(0deg); } }
    @keyframes waterFlow2 { 0% { transform: translate(0%, 0%) rotate(0deg); } 25% { transform: translate(-4%, 3%) rotate(-0.5deg); } 50% { transform: translate(3%, -2%) rotate(0.5deg); } 75% { transform: translate(-2%, -3%) rotate(-0.5deg); } 100% { transform: translate(0%, 0%) rotate(0deg); } }
    .dash-hero-content { position: relative; z-index: 1; display: grid; grid-template-columns: 1fr auto; gap: 2rem; align-items: end; padding-bottom: 2rem; }
    .tree-species { font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.1em; color: rgba(255, 255, 255, 0.9); margin-bottom: 0.5rem; display: flex; align-items: center; gap: 0.5rem; }
    .tree-title-block h1 { font-family: "Playfair Display", serif; font-size: 2.8rem; color: white; line-height: 1.1; margin-bottom: 0.8rem; }
    .tree-meta-chips { display: flex; gap: 0.6rem; flex-wrap: wrap; }
    .chip { padding: 0.35rem 0.8rem; border-radius: 20px; font-size: 0.78rem; font-weight: 500; display: inline-flex; align-items: center; gap: 0.3rem; }
    .chip-health-good { background: rgba(250, 249, 246, 0.2); color: #faf9f6; border: 1px solid rgba(250, 249, 246, 0.4); }
    .chip.chip-fans { background: rgba(60, 125, 76, 0.15); color: #d1efdb; border: 1px solid rgba(60, 125, 76, 0.3); font-weight: 700; }
    .dash-tree-actions { display: inline-flex; gap: 0.8rem; align-items: center; margin-top: 0.2rem; }
    .dash-tree-actions.following-state { background: #3c7d4c; border-radius: 999px; padding: 0.35rem 0.35rem 0.35rem 1.6rem; gap: 1.2rem; box-shadow: 0 4px 12px rgba(60, 125, 76, 0.2); transition: all 0.3s ease; }
    .btn-follow { background: #36454f; color: #faf9f6; border: none; padding: 0.7rem 1.5rem; border-radius: 999px; font-weight: 700; font-family: "DM Sans", sans-serif; font-size: 0.95rem; cursor: pointer; transition: all 0.2s; }
    .btn-follow:hover { background: var(--sun); transform: translateY(-1px); }
    .dash-tree-actions.following-state .btn-follow { background: transparent !important; box-shadow: none !important; color: #fff; font-family: "Outfit", sans-serif; font-weight: 700; font-size: 1.15rem; padding: 0; margin: 0; }
    .dash-tree-actions.following-state .btn-follow:hover { opacity: 0.85; transform: none; }
    .btn-apply-ct { background: rgba(255,255,255,0.05); color: #fff; border: 1px solid rgba(255, 255, 255, 0.35); padding: 0.55rem 1.2rem; border-radius: 999px; font-family: "DM Sans", sans-serif; font-weight: 500; font-size: 0.95rem; cursor: pointer; transition: all 0.2s ease; display: inline-flex; align-items: center; gap: 0.4rem; }
    .btn-apply-ct:hover:not(.locked) { background: rgba(255, 255, 255, 0.15); border-color: rgba(255, 255, 255, 0.5); }
    .btn-apply-ct.locked { opacity: 0.6; border-style: dashed; cursor: not-allowed; }
    .dash-tab-bar { position: relative; z-index: 1; display: flex; gap: 0; }
    .dash-tab { background: none; border: none; color: var(--canopy); padding: 0.8rem 1.4rem; font-family: "DM Sans", sans-serif; font-size: 0.88rem; cursor: pointer; transition: color 0.2s; border-radius: 10px 10px 0 0; }
    .dash-tab:hover { color: white; }
    .dash-tab.active { color: #2b2b2b; background: #faf9f6; font-weight: 600; }
    .dashboard-body { max-width: 1100px; margin: 0 auto; padding: 2rem 1.5rem; display: grid; grid-template-columns: 1fr 320px; gap: 1.5rem; }
    .stat-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 1rem; margin-bottom: 1.5rem; }
    .stat-card { background: #cdd9af; border-radius: 14px; padding: 1.2rem; box-shadow: 0 2px 12px rgba(138, 154, 91, 0.08); }
    .stat-card .s-label { font-size: 0.72rem; text-transform: uppercase; letter-spacing: 0.08em; color: #a44a3f; margin-bottom: 0.5rem; }
    .stat-card .s-val { font-family: "Playfair Display", serif; font-size: 1.8rem; color: var(--ink); line-height: 1; }
    .stat-card .s-sub { font-size: 0.75rem; color: var(--sage); margin-top: 0.2rem; }
    .stat-card .s-icon { font-size: 1.5rem; margin-bottom: 0.4rem; }
    .content-card { background: #cdd9af; border-radius: 16px; padding: 1.4rem; box-shadow: 0 2px 12px rgba(138, 154, 91, 0.08); margin-bottom: 1.5rem; }
    .content-card h3 { font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.08em; color: #a44a3f; margin-bottom: 1rem; }
    .sidecurb-ratings { display: grid; grid-template-columns: repeat(2, 1fr); gap: 0.8rem; }
    .env-ratings { display: grid; grid-template-columns: repeat(3, 1fr); gap: 0.8rem; }
    .env-item { background: var(--mist); border-radius: 10px; padding: 0.8rem; }
    .env-item .env-label { font-size: 0.72rem; text-transform: uppercase; letter-spacing: 0.06em; color: #a44a3f; display: block; margin-bottom: 0.4rem; }
    .env-score { font-weight: 700; font-size: 0.88rem; color: var(--ink); margin-top: 0.3rem; }
    .ct-card { background: white; border-radius: 16px; padding: 1.4rem; box-shadow: 0 2px 12px var(--shadow); margin-bottom: 1rem; }
    .ct-card h3 { font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.08em; color: var(--sage); margin-bottom: 1rem; }
    .ct-profile { display: flex; align-items: center; gap: 0.8rem; margin-bottom: 0.8rem; }
    .ct-avatar { width: 44px; height: 44px; border-radius: 50%; background: linear-gradient(135deg, var(--bark), #8b4513); display: flex; align-items: center; justify-content: center; font-size: 1.2rem; flex-shrink: 0; border: 2px solid var(--leaf); }
    .ct-avatar.alt { background: linear-gradient(135deg, var(--moss), var(--sage)); }
    .ct-info { flex: 1; }
    .ct-info strong { display: block; font-size: 0.9rem; color: var(--ink); }
    .ct-info small { font-size: 0.75rem; color: var(--sage); }
    .ct-badge { font-size: 0.65rem; background: rgba(61, 90, 62, 0.15); color: var(--moss); padding: 0.2rem 0.5rem; border-radius: 4px; font-weight: 600; }
    .ct-notice { font-size: 0.8rem; color: var(--sage); background: var(--mist); border-radius: 8px; padding: 0.6rem; margin-top: 0.5rem; }
    .tree-info-table { width: 100%; font-size: 0.82rem; border-collapse: collapse; }
    .tree-info-table tr { border-bottom: 1px solid var(--mist); }
    .tree-info-table tr:last-child { border: none; }
    .tree-info-table td { padding: 0.4rem 0; }
    .tree-info-table td:first-child { color: var(--sage); }
    .tree-info-table td:last-child { color: var(--ink); font-weight: 500; text-align: right; }
    .timeline-card { margin-top: 1rem; background: linear-gradient(135deg, #ffffff, #faf9f6); position: relative; overflow: hidden; }
    .dendro-header { margin-bottom: 2rem; border-bottom: 2px solid var(--mist); padding-bottom: 1rem; }
    .dendro-header h3 { margin: 0 0 0.5rem 0; font-size: 1.4rem; color: var(--bark); font-family: 'Playfair Display', serif; }
    .dendro-header .subtitle { margin: 0; color: var(--sage); font-family: 'DM Sans', sans-serif; text-transform: uppercase; letter-spacing: 0.1em; font-size: 0.75rem; font-weight: 700; }
    .dendro-container { display: grid; grid-template-columns: 1fr 1fr; gap: 3rem; align-items: center; position: relative; }
    .svg-wrapper { position: relative; cursor: crosshair; filter: drop-shadow(0 20px 40px rgba(139, 69, 19, 0.15)); transition: transform 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275); }
    .svg-wrapper:hover { transform: scale(1.08); z-index: 20; }
    .tree-rings-svg { width: 100%; height: auto; transform: rotate(-15deg); }
    .bark-layer { filter: drop-shadow(0 4px 8px rgba(0,0,0,0.2)); }
    .tree-ring { transition: stroke 0.3s, stroke-width 0.3s; }
    .tree-ring.has-event { stroke-dasharray: 4 2; }
    .tree-ring.active-ring { filter: drop-shadow(0 0 8px rgba(45,122,58,0.5)); }
    .event-dot { pointer-events: none; animation: pulseHeartbeat 4s infinite ease-in-out; }
    .active-event-dot { pointer-events: none; animation: pulseRapid 1.5s infinite alternate ease-in-out; }
    @keyframes pulseHeartbeat { 0%, 100% { transform: scale(1); opacity: 0.85; } 50% { transform: scale(1.15); opacity: 1; } }
    @keyframes pulseRapid { from { transform: scale(1); } to { transform: scale(1.2); } }
    .ring-info-panel { display: flex; flex-direction: column; justify-content: center; perspective: 1000px; }
    .ring-details { background: rgba(255, 255, 255, 0.8); backdrop-filter: blur(12px); -webkit-backdrop-filter: blur(12px); border: 1px solid rgba(255,255,255,0.4); padding: 2rem; border-radius: 20px; box-shadow: 0 10px 30px rgba(0,0,0,0.05), inset 0 2px 5px rgba(255,255,255,0.8); animation: slideInPanel 0.4s cubic-bezier(0.16, 1, 0.3, 1) forwards; }
    .ring-details.active-glow { border-left: 4px solid var(--moss); }
    @keyframes slideInPanel { from { opacity: 0; transform: translateX(-20px) rotateY(-10deg); } to { opacity: 1; transform: translateX(0) rotateY(0); } }
    .rd-header { display: flex; justify-content: space-between; align-items: baseline; margin-bottom: 1.5rem; padding-bottom: 1rem; border-bottom: 1px dashed rgba(164, 74, 63, 0.2); }
    .ring-details h4 { margin: 0; color: var(--bark); font-family: 'Outfit', sans-serif; font-size: 1.8rem; font-weight: 700; }
    .ring-metric .metric-value { font-size: 1.6rem; font-weight: 700; color: var(--sage); font-family: 'DM Sans', sans-serif; }
    .ring-metric small { font-size: 0.9rem; opacity: 0.7; margin-left: 2px; }
    .problem-grid { display: grid; }
    .ring-event { display: flex; gap: 1rem; align-items: flex-start; padding: 1.2rem; border-radius: 12px; background: rgba(245, 240, 232, 0.5); }
    .highlight-event { background: linear-gradient(135deg, rgba(212, 168, 83, 0.1), rgba(164, 74, 63, 0.05)); border: 1px solid rgba(212, 168, 83, 0.2); }
    .standard-growth { background: linear-gradient(135deg, rgba(143, 188, 143, 0.1), transparent); }
    .event-icon { font-size: 1.8rem; filter: drop-shadow(0 2px 4px rgba(0,0,0,0.1)); }
    .ring-event p { margin: 0; color: var(--ink); line-height: 1.6; font-size: 1.05rem; }
    .loading { display: flex; align-items: center; justify-content: center; min-height: 100vh; font-size: 1.2rem; color: var(--sage); }
    .lock-modal-overlay { position: fixed; inset: 0; background: rgba(0,0,0,0.5); backdrop-filter: blur(4px); display: flex; align-items: center; justify-content: center; z-index: 1000; }
    .lock-modal-card { background: white; border-radius: 20px; padding: 2.5rem; max-width: 420px; width: 90%; text-align: center; box-shadow: 0 20px 60px rgba(0,0,0,0.2); }
    .lock-modal-icon { font-size: 3rem; margin-bottom: 1rem; }
    .lock-modal-title { font-family: 'Playfair Display', serif; color: var(--bark); margin-bottom: 0.8rem; }
    .lock-modal-desc { color: var(--sage); line-height: 1.6; margin-bottom: 1.5rem; }
    .lock-modal-actions { display: flex; gap: 0.8rem; justify-content: center; }
    .btn-cancel { background: var(--mist); border: none; padding: 0.7rem 1.5rem; border-radius: 999px; cursor: pointer; font-family: "DM Sans", sans-serif; font-weight: 600; }
    .btn-follow-modal { background: #3c7d4c; color: white; border: none; padding: 0.7rem 1.5rem; border-radius: 999px; cursor: pointer; font-family: "DM Sans", sans-serif; font-weight: 700; }
    .btn-primary { background: var(--moss); color: white; border: none; padding: 0.6rem 1.2rem; border-radius: 999px; font-family: "DM Sans", sans-serif; font-weight: 600; cursor: pointer; }
    @media (max-width: 900px) { .dendro-container { grid-template-columns: 1fr; gap: 2rem; } .svg-wrapper { max-width: 350px; margin: 0 auto; } }
</style>