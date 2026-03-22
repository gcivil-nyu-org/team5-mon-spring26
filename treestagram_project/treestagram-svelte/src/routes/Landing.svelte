<script>
    export let navigate;
</script>

<div class="page">
    <div class="tree-rings"></div>
    <div class="tree-rings-2"></div>

    <nav class="home-nav">
        <div class="logo">Tree<span>stagram</span></div>
        <div class="home-nav-links">
            <a href="#who">Who Are We</a>
            <a href="#what">What We Do</a>
            <a href="#trees">The Trees</a>
            <button class="btn-login" on:click={() => navigate("/login")}
                >Log In</button
            >
            <button class="btn-signup-nav" on:click={() => navigate("/signup")}
                >Sign Up Free</button
            >
        </div>
    </nav>

    <div class="hero">
        <div class="hero-text">
            <div class="hero-eyebrow">NYC Urban Forest Community</div>
            <h1>Social media,<em>but for trees.</em></h1>
            <p>
                Track, photograph, and protect New York City's 700,000 street
                trees. Join a community that cares about every leaf, every
                trunk, every root.
            </p>
            <div class="hero-ctas">
                <button class="btn-primary" on:click={() => navigate("/signup")}
                    >Explore the Forest →</button
                >
            </div>
        </div>

        <div class="hero-visual">
            <div class="mock-card">
                <div class="mock-card-header">
                    <div class="mock-avatar">🧑</div>
                    <div>
                        <strong>@treewhisperer_nyc</strong>
                        <small
                            >tagged <strong class="highlight"
                                >Elm #00482 · Central Park</strong
                            ></small
                        >
                    </div>
                </div>
                <div class="mock-img">
                    🌳
                    <div class="img-overlay">
                        <div class="tree-name">
                            American Elm · Central Park W
                        </div>
                        <small>Health: Good · 127 fans</small>
                    </div>
                </div>
                <div class="mock-stats">
                    <span>❤️ <strong>342</strong> likes</span>
                    <span>💬 <strong>28</strong> comments</span>
                    <span>🌧 Saved <strong>$2,140</strong>/yr</span>
                </div>
            </div>
            <div class="mock-card offset">
                <div class="mock-card-header">
                    <div class="mock-avatar">🌿</div>
                    <div>
                        <strong>Ginkgo #10293 · Brooklyn</strong>
                        <small>🔴 Flagged by caretaker</small>
                    </div>
                </div>
                <div class="mock-img mock-img-2">
                    🍂
                    <div class="img-overlay">
                        <div class="tree-name">
                            Ginkgo biloba · Flatbush Ave
                        </div>
                        <small>Health: Fair · Needs attention</small>
                    </div>
                </div>
                <div class="mock-stats">
                    <span>❤️ <strong>89</strong> likes</span>
                    <span>💬 <strong>14</strong> comments</span>
                </div>
            </div>
        </div>
    </div>

    <div class="stats-row">
        <div class="stat">
            <span class="num">700K+</span><span class="label"
                >Trees in NYC Database</span
            >
        </div>
        <div class="stat">
            <span class="num">5</span><span class="label">Boroughs Covered</span
            >
        </div>
        <div class="stat">
            <span class="num">∞</span><span class="label"
                >Caretakers Needed</span
            >
        </div>
        <div class="stat">
            <span class="num">🌱</span><span class="label"
                >Join the Movement</span
            >
        </div>
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
        --sun: #d4a853;
    }

    .page {
        background: var(--bark);
        position: relative;
        overflow: hidden;
        min-height: 100vh;
    }

    /* Decorative rings */
    .tree-rings {
        position: absolute;
        top: -200px;
        right: -200px;
        width: 700px;
        height: 700px;
        border-radius: 50%;
        background: repeating-radial-gradient(
            circle,
            transparent 0px,
            transparent 28px,
            rgba(255, 255, 255, 0.03) 28px,
            rgba(255, 255, 255, 0.03) 30px
        );
        animation: slowRotate 60s linear infinite;
    }
    .tree-rings-2 {
        position: absolute;
        bottom: -300px;
        left: -200px;
        width: 600px;
        height: 600px;
        border-radius: 50%;
        background: repeating-radial-gradient(
            circle,
            transparent 0px,
            transparent 22px,
            rgba(143, 188, 143, 0.06) 22px,
            rgba(143, 188, 143, 0.06) 24px
        );
        animation: slowRotate 80s linear infinite reverse;
    }
    @keyframes slowRotate {
        to {
            transform: rotate(360deg);
        }
    }

    .home-nav {
        position: relative;
        z-index: 10;
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 1.5rem 3rem;
    }
    .logo {
        font-family: "Playfair Display", serif;
        font-size: 1.6rem;
        font-style: italic;
        color: var(--leaf);
    }
    .logo span {
        color: var(--sun);
        font-style: normal;
    }
    .home-nav-links {
        display: flex;
        gap: 0.5rem;
        align-items: center;
    }
    .home-nav-links a {
        color: var(--canopy);
        text-decoration: none;
        font-size: 0.9rem;
        padding: 0.4rem 0.8rem;
        border-radius: 4px;
        transition: color 0.2s;
    }
    .home-nav-links a:hover {
        color: white;
    }
    .btn-login {
        background: none;
        border: 1.5px solid var(--sage);
        color: var(--canopy);
        padding: 0.5rem 1.2rem;
        border-radius: 20px;
        cursor: pointer;
        font-family: "DM Sans", sans-serif;
        font-size: 0.9rem;
        transition: all 0.2s;
        margin-left: 0.5rem;
    }
    .btn-login:hover {
        background: var(--sage);
        color: white;
        border-color: var(--sage);
    }
    .btn-signup-nav {
        background: var(--leaf);
        border: none;
        color: var(--bark);
        padding: 0.5rem 1.2rem;
        border-radius: 20px;
        cursor: pointer;
        font-family: "DM Sans", sans-serif;
        font-size: 0.9rem;
        font-weight: 600;
        transition: all 0.2s;
    }
    .btn-signup-nav:hover {
        background: var(--sun);
    }

    .hero {
        position: relative;
        z-index: 10;
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 4rem;
        padding: 6rem 3rem 4rem;
        max-width: 1200px;
        margin: 0 auto;
        align-items: center;
    }
    .hero-eyebrow {
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
        background: rgba(143, 188, 143, 0.15);
        border: 1px solid rgba(143, 188, 143, 0.3);
        color: var(--leaf);
        padding: 0.3rem 0.8rem;
        border-radius: 20px;
        font-size: 0.8rem;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        margin-bottom: 1.5rem;
    }
    .hero-eyebrow::before {
        content: "🌳";
        font-size: 0.9rem;
    }
    .hero h1 {
        font-family: "Playfair Display", serif;
        font-size: 4.5rem;
        line-height: 1.05;
        color: var(--cream);
        margin-bottom: 1.5rem;
    }
    .hero h1 em {
        font-style: italic;
        color: var(--leaf);
        display: block;
    }
    .hero p {
        color: var(--canopy);
        font-size: 1.05rem;
        line-height: 1.7;
        max-width: 440px;
        margin-bottom: 2.5rem;
    }
    .hero-ctas {
        display: flex;
        gap: 1rem;
        flex-wrap: wrap;
    }
    .btn-primary {
        background: var(--leaf);
        color: var(--bark);
        border: none;
        padding: 0.9rem 2rem;
        border-radius: 30px;
        font-size: 1rem;
        font-weight: 600;
        cursor: pointer;
        font-family: "DM Sans", sans-serif;
        transition: all 0.25s;
        box-shadow: 0 4px 20px rgba(143, 188, 143, 0.3);
    }
    .btn-primary:hover {
        background: var(--sun);
        transform: translateY(-2px);
        box-shadow: 0 8px 30px rgba(212, 168, 83, 0.4);
    }
    /* .btn-ghost {
        background: none;
        color: var(--canopy);
        border: 1.5px solid rgba(255, 255, 255, 0.2);
        padding: 0.9rem 2rem;
        border-radius: 30px;
        font-size: 1rem;
        cursor: pointer;
        font-family: "DM Sans", sans-serif;
        transition: all 0.25s;
    }
    .btn-ghost:hover {
        border-color: var(--canopy);
        color: white;
    } */

    .hero-visual {
        position: relative;
        display: flex;
        flex-direction: column;
        gap: 1rem;
    }
    .mock-card {
        background: rgba(255, 255, 255, 0.06);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 16px;
        padding: 1.2rem;
        backdrop-filter: blur(10px);
        transition: transform 0.3s;
    }
    .mock-card:hover {
        transform: translateY(-3px);
    }
    .mock-card.offset {
        margin-left: 2rem;
    }
    .mock-card-header {
        display: flex;
        align-items: center;
        gap: 0.8rem;
        margin-bottom: 0.8rem;
    }
    .mock-avatar {
        width: 36px;
        height: 36px;
        border-radius: 50%;
        background: linear-gradient(135deg, var(--moss), var(--sage));
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1rem;
        flex-shrink: 0;
    }
    .mock-card-header div small {
        display: block;
        color: var(--canopy);
        font-size: 0.75rem;
    }
    .mock-card-header div strong {
        color: var(--leaf);
        font-size: 0.9rem;
    }
    .highlight {
        color: var(--leaf);
    }
    .mock-img {
        width: 100%;
        height: 140px;
        border-radius: 10px;
        background: linear-gradient(135deg, #2d5a27, #4a7c59, #6ba368);
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 3rem;
        margin-bottom: 0.8rem;
        position: relative;
        overflow: hidden;
    }
    .mock-img::after {
        content: "";
        position: absolute;
        inset: 0;
        background: linear-gradient(
            to top,
            rgba(0, 0, 0, 0.4) 0%,
            transparent 60%
        );
    }
    .mock-img-2 {
        background: linear-gradient(135deg, #1a3a20, #3d6b45, #5a8c60);
        height: 100px;
    }
    .img-overlay {
        position: absolute;
        bottom: 0;
        left: 0;
        right: 0;
        padding: 0.8rem;
        z-index: 1;
        color: white;
    }
    .tree-name {
        font-family: "Playfair Display", serif;
        font-size: 0.9rem;
        font-weight: 700;
    }
    .img-overlay small {
        font-size: 0.72rem;
        opacity: 0.8;
    }
    .mock-stats {
        display: flex;
        gap: 1.2rem;
    }
    .mock-stats span {
        font-size: 0.8rem;
        color: var(--canopy);
    }
    .mock-stats span strong {
        color: var(--leaf);
    }

    .stats-row {
        position: relative;
        z-index: 10;
        display: flex;
        justify-content: center;
        gap: 4rem;
        padding: 3rem;
        border-top: 1px solid rgba(255, 255, 255, 0.08);
        max-width: 1200px;
        margin: 0 auto;
    }
    .stat {
        text-align: center;
    }
    .stat .num {
        font-family: "Playfair Display", serif;
        font-size: 2.5rem;
        color: var(--leaf);
        display: block;
    }
    .stat .label {
        color: var(--canopy);
        font-size: 0.85rem;
    }

    /* Animations */
    .hero-text {
        animation: fadeUp 0.6s ease 0.1s both;
    }
    .hero-visual {
        animation: fadeUp 0.6s ease 0.3s both;
    }
    @keyframes fadeUp {
        from {
            opacity: 0;
            transform: translateY(20px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
</style>
