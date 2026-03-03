<script>
    import TopNav from "../components/TopNav.svelte";
    export let navigate;
</script>

<div class="page">
    <TopNav {navigate} activePage="explore" />

    <div class="dashboard-hero">
        <div class="dash-breadcrumb">
            <button class="breadcrumb-link" on:click={() => navigate("/home")}
                >NYC Trees</button
            >
            › <span>Manhattan</span> › <span>Elm #00482</span>
        </div>
        <div class="dash-hero-content">
            <div class="tree-title-block">
                <div class="tree-species">
                    🌳 Ulmus americana · American Elm
                </div>
                <h1>Elm #00482<br />Central Park</h1>
                <div class="tree-meta-chips">
                    <span class="chip chip-health-good">✓ Good Health</span>
                    <span class="chip chip-borough">📍 Manhattan</span>
                    <span class="chip chip-id">ID: 00482</span>
                    <span class="chip chip-borough">10024</span>
                </div>
            </div>
            <div class="dash-tree-actions">
                <button class="btn-follow">🌟 Follow Tree</button>
                <button class="btn-apply-ct">Apply as Caretaker</button>
                <button class="btn-apply-ct" on:click={() => navigate("/chat")}
                    >💬 Group Chat (127)</button
                >
            </div>
        </div>
        <div class="dash-tab-bar">
            <button class="dash-tab active">Overview</button>
            <button class="dash-tab">Posts</button>
            <button class="dash-tab">Health History</button>
            <button class="dash-tab">Community</button>
        </div>
    </div>

    <div class="dashboard-body">
        <div class="dash-main">
            <div class="stat-grid">
                <div class="stat-card">
                    <div class="s-icon">💧</div>
                    <div class="s-label">Stormwater Savings</div>
                    <div class="s-val">$2,140</div>
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
                <div class="stat-card">
                    <div class="s-icon">🌡️</div>
                    <div class="s-label">Health Score</div>
                    <div class="s-val green">92</div>
                    <div class="s-sub">out of 100</div>
                </div>
            </div>

            <div class="content-card">
                <h3>Health History — Last 12 Months</h3>
                <div class="health-history-bar">
                    <div class="hh-bar good" style="height:90%"></div>
                    <div class="hh-bar good" style="height:85%"></div>
                    <div class="hh-bar good" style="height:88%"></div>
                    <div class="hh-bar fair" style="height:60%"></div>
                    <div class="hh-bar fair" style="height:65%"></div>
                    <div class="hh-bar good" style="height:80%"></div>
                    <div class="hh-bar good" style="height:92%"></div>
                    <div class="hh-bar good" style="height:95%"></div>
                    <div class="hh-bar good" style="height:90%"></div>
                    <div class="hh-bar good" style="height:88%"></div>
                    <div class="hh-bar good" style="height:86%"></div>
                    <div class="hh-bar good" style="height:92%"></div>
                </div>
                <div class="hh-months">
                    <span>Mar</span><span>Apr</span><span>May</span><span
                        >Jun</span
                    ><span>Jul</span>
                    <span>Aug</span><span>Sep</span><span>Oct</span><span
                        >Nov</span
                    ><span>Dec</span><span>Jan</span><span>Feb</span>
                </div>
                <div class="legend">
                    <span><span class="dot good-dot"></span>Good</span>
                    <span><span class="dot fair-dot"></span>Fair</span>
                    <span><span class="dot poor-dot"></span>Poor</span>
                </div>
            </div>

            <div class="content-card">
                <h3>Environmental Ratings</h3>
                <div class="env-ratings">
                    <div class="env-item">
                        <label>Soil Condition</label>
                        <div class="env-bar-track">
                            <div class="env-bar-fill green-fill"></div>
                        </div>
                        <div class="env-score">Good · 8/10</div>
                    </div>
                    <div class="env-item">
                        <label>Sidewalk Damage</label>
                        <div class="env-bar-track">
                            <div class="env-bar-fill yellow-fill"></div>
                        </div>
                        <div class="env-score">Moderate · 5/10</div>
                    </div>
                    <div class="env-item">
                        <label>Root Space</label>
                        <div class="env-bar-track">
                            <div class="env-bar-fill orange-fill"></div>
                        </div>
                        <div class="env-score">Limited · 7/10</div>
                    </div>
                    <div class="env-item">
                        <label>Canopy Coverage</label>
                        <div class="env-bar-track">
                            <div class="env-bar-fill green-fill wide"></div>
                        </div>
                        <div class="env-score">Excellent · 9/10</div>
                    </div>
                </div>
            </div>

            <div class="content-card">
                <h3>Recent Community Posts</h3>
                <div class="posts-mini">
                    <div class="post-mini">
                        <div class="post-mini-thumb">🌳</div>
                        <div class="post-mini-info">
                            <strong>Winter check-in — looking healthy!</strong>
                            <small>@treewhisperer_nyc · 2 hours ago</small>
                        </div>
                        <span class="post-mini-likes">❤️ 342</span>
                    </div>
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
                <h3>Community</h3>
                <div class="fans-count">
                    <span class="num">127</span>
                    <small>fans following this tree</small>
                    <div class="fans-avatars">
                        <div class="fa">🌿</div>
                        <div class="fa">🧑</div>
                        <div class="fa">👩</div>
                        <div class="fa">🌱</div>
                        <div class="fa">+123</div>
                    </div>
                </div>
            </div>

            <div class="ct-card">
                <h3>Tree Info</h3>
                <table class="tree-info-table">
                    <tr><td>Species</td><td>American Elm</td></tr>
                    <tr><td>Diameter</td><td>24 in</td></tr>
                    <tr><td>Zipcode</td><td>10024</td></tr>
                    <tr><td>Borough</td><td>Manhattan</td></tr>
                    <tr><td>Census Year</td><td>2015</td></tr>
                </table>
            </div>
        </aside>
    </div>
</div>

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
        background: var(--mist);
        min-height: 100vh;
    }

    /* Dashboard Hero */
    .dashboard-hero {
        background: var(--bark);
        position: relative;
        overflow: hidden;
        padding: 2rem 3rem 0;
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
        background: rgba(143, 188, 143, 0.25);
        color: var(--leaf);
        border: 1px solid rgba(143, 188, 143, 0.4);
    }
    .chip-borough {
        background: rgba(255, 255, 255, 0.1);
        color: var(--canopy);
        border: 1px solid rgba(255, 255, 255, 0.2);
    }
    .chip-id {
        background: rgba(212, 168, 83, 0.2);
        color: var(--sun);
        border: 1px solid rgba(212, 168, 83, 0.3);
        font-family: "DM Mono", monospace;
        font-size: 0.72rem;
    }
    .dash-tree-actions {
        display: flex;
        flex-direction: column;
        gap: 0.6rem;
    }
    .btn-follow {
        background: var(--leaf);
        color: var(--bark);
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
        color: var(--canopy);
        border: 1.5px solid rgba(255, 255, 255, 0.25);
        padding: 0.6rem 1.2rem;
        border-radius: 25px;
        font-family: "DM Sans", sans-serif;
        font-size: 0.85rem;
        cursor: pointer;
        transition: all 0.2s;
    }
    .btn-apply-ct:hover {
        border-color: var(--canopy);
        color: white;
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
        color: var(--ink);
        background: var(--mist);
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
        grid-template-columns: repeat(4, 1fr);
        gap: 1rem;
        margin-bottom: 1.5rem;
    }
    .stat-card {
        background: white;
        border-radius: 14px;
        padding: 1.2rem;
        box-shadow: 0 2px 12px var(--shadow);
    }
    .stat-card .s-label {
        font-size: 0.72rem;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        color: var(--sage);
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
        background: white;
        border-radius: 16px;
        padding: 1.4rem;
        box-shadow: 0 2px 12px var(--shadow);
        margin-bottom: 1.5rem;
    }
    .content-card h3 {
        font-size: 0.75rem;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        color: var(--sage);
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
    .env-ratings {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 0.8rem;
    }
    .env-item {
        background: var(--mist);
        border-radius: 10px;
        padding: 0.8rem;
    }
    .env-item label {
        font-size: 0.72rem;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        color: var(--sage);
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
