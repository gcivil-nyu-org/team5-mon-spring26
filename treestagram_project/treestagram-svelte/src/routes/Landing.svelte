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
        <div class="stat map-stat">
            <div class="mini-map">
                <svg viewBox="0 0 80 70" class="mini-map-svg">
                    <!-- Simplified borough shapes -->
                    <ellipse cx="32" cy="30" rx="4" ry="18" fill="rgba(143,188,143,0.3)" stroke="rgba(143,188,143,0.6)" stroke-width="0.8" transform="rotate(-5,32,30)"/>
                    <ellipse cx="42" cy="50" rx="12" ry="8" fill="rgba(143,188,143,0.2)" stroke="rgba(143,188,143,0.5)" stroke-width="0.8"/>
                    <ellipse cx="55" cy="38" rx="14" ry="9" fill="rgba(143,188,143,0.15)" stroke="rgba(143,188,143,0.45)" stroke-width="0.8"/>
                    <ellipse cx="40" cy="12" rx="10" ry="7" fill="rgba(143,188,143,0.15)" stroke="rgba(143,188,143,0.45)" stroke-width="0.8"/>
                    <ellipse cx="16" cy="52" rx="6" ry="5" fill="rgba(143,188,143,0.1)" stroke="rgba(143,188,143,0.35)" stroke-width="0.8"/>
                    <!-- Live tree dots -->
                    <circle cx="32" cy="25" r="1.5" fill="var(--leaf)">
                        <animate attributeName="r" values="1;2.5;1" dur="2s" repeatCount="indefinite"/>
                        <animate attributeName="opacity" values="0.5;1;0.5" dur="2s" repeatCount="indefinite"/>
                    </circle>
                    <circle cx="42" cy="48" r="1.2" fill="var(--leaf)">
                        <animate attributeName="r" values="0.8;2;0.8" dur="2.8s" repeatCount="indefinite"/>
                        <animate attributeName="opacity" values="0.4;0.9;0.4" dur="2.8s" repeatCount="indefinite"/>
                    </circle>
                    <circle cx="55" cy="36" r="1" fill="var(--leaf)">
                        <animate attributeName="r" values="0.6;1.8;0.6" dur="3.2s" repeatCount="indefinite"/>
                        <animate attributeName="opacity" values="0.4;0.8;0.4" dur="3.2s" repeatCount="indefinite"/>
                    </circle>
                    <circle cx="38" cy="14" r="0.8" fill="var(--leaf)">
                        <animate attributeName="r" values="0.5;1.5;0.5" dur="3.5s" repeatCount="indefinite"/>
                        <animate attributeName="opacity" values="0.3;0.7;0.3" dur="3.5s" repeatCount="indefinite"/>
                    </circle>
                </svg>
                <span class="map-live-badge">● LIVE</span>
            </div>
            <span class="label">NYC Tree Map</span>
        </div>
    </div>
    <footer class="made-with-love">
        <div class="love-line"></div>
        <div class="love-text">
            Made with <span class="love-word">Love</span> at
            <span class="nyu-word">NYU</span>
        </div>
        <div class="love-leaf">🌿</div>
    </footer>
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
        --glow-green: rgba(143, 188, 143, 0.25);
        --glow-gold: rgba(212, 168, 83, 0.2);
    }

    /* ── Page & Atmosphere ── */
    .page {
        background: var(--bark);
        position: relative;
        overflow: hidden;
        height: 100vh;
        display: flex;
        flex-direction: column;
    }
    /* Radial hero glow for depth */
    .page::before {
        content: "";
        position: absolute;
        top: 5%;
        left: 50%;
        width: 900px;
        height: 900px;
        transform: translateX(-50%);
        border-radius: 50%;
        background: radial-gradient(
            circle,
            rgba(61, 90, 62, 0.22) 0%,
            rgba(143, 188, 143, 0.08) 35%,
            transparent 70%
        );
        pointer-events: none;
        z-index: 1;
    }
    /* Floating leaf particles — left */
    .page::after {
        content: "🍃";
        position: absolute;
        top: 18%;
        left: 6%;
        font-size: 1rem;
        opacity: 0.1;
        animation: floatLeaf1 12s ease-in-out infinite;
        pointer-events: none;
        z-index: 1;
    }

    /* ── Decorative rings (enhanced) ── */
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
            rgba(255, 255, 255, 0.04) 28px,
            rgba(255, 255, 255, 0.04) 30px
        );
        animation: slowRotate 60s linear infinite;
        filter: blur(0.5px);
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
            rgba(143, 188, 143, 0.07) 22px,
            rgba(143, 188, 143, 0.07) 24px
        );
        animation: slowRotate 80s linear infinite reverse;
        filter: blur(0.5px);
    }
    @keyframes slowRotate {
        to {
            transform: rotate(360deg);
        }
    }
    @keyframes floatLeaf1 {
        0%, 100% {
            transform: translateY(0) rotate(0deg);
            opacity: 0.18;
        }
        25% {
            transform: translateY(-30px) rotate(15deg);
            opacity: 0.25;
        }
        50% {
            transform: translateY(-10px) rotate(-10deg);
            opacity: 0.15;
        }
        75% {
            transform: translateY(-40px) rotate(8deg);
            opacity: 0.22;
        }
    }

    /* ── Nav (polished) ── */
    .home-nav {
        position: relative;
        z-index: 10;
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 0.8rem 2rem 0.8rem 3rem;
        flex-shrink: 0;
    }
    .home-nav::after {
        content: "";
        position: absolute;
        bottom: 0;
        left: 3rem;
        right: 3rem;
        height: 1px;
        background: linear-gradient(
            90deg,
            transparent,
            rgba(143, 188, 143, 0.18),
            rgba(212, 168, 83, 0.12),
            transparent
        );
    }
    .logo {
        font-family: "Playfair Display", serif;
        font-size: 1.6rem;
        font-style: italic;
        color: var(--leaf);
        text-shadow: 0 0 20px rgba(143, 188, 143, 0.15);
    }
    .logo span {
        color: var(--sun);
        font-style: normal;
    }
    .home-nav-links {
        display: flex;
        gap: 0.6rem;
        align-items: center;
    }
    .home-nav-links a {
        color: var(--canopy);
        text-decoration: none;
        font-size: 0.9rem;
        padding: 0.4rem 0.9rem;
        border-radius: 6px;
        transition: color 0.25s, background 0.25s;
        position: relative;
    }
    .home-nav-links a:hover {
        color: white;
        background: rgba(255, 255, 255, 0.05);
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
        transition: all 0.3s;
        margin-left: 0.5rem;
    }
    .btn-login:hover {
        background: var(--sage);
        color: white;
        border-color: var(--sage);
        box-shadow: 0 0 16px rgba(107, 143, 113, 0.3);
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
        transition: all 0.3s;
    }
    .btn-signup-nav:hover {
        background: var(--sun);
        box-shadow: 0 0 20px rgba(212, 168, 83, 0.35);
    }

    /* ── Hero ── */
    .hero {
        position: relative;
        z-index: 10;
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 3rem;
        padding: 2rem 3rem 1.5rem;
        max-width: 1200px;
        margin: 0 auto;
        align-items: center;
        flex: 1;
    }
    .hero-eyebrow {
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
        background: rgba(143, 188, 143, 0.12);
        border: 1px solid rgba(143, 188, 143, 0.25);
        color: var(--leaf);
        padding: 0.35rem 1rem;
        border-radius: 20px;
        font-size: 0.78rem;
        letter-spacing: 0.12em;
        text-transform: uppercase;
        margin-bottom: 1rem;
        backdrop-filter: blur(6px);
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
        margin-bottom: 1rem;
        text-shadow: 0 2px 30px rgba(245, 240, 232, 0.06);
    }
    .hero h1 em {
        font-style: italic;
        color: var(--leaf);
        display: block;
        text-shadow: 0 0 40px rgba(143, 188, 143, 0.2);
    }
    .hero p {
        color: var(--canopy);
        font-size: 1.05rem;
        line-height: 1.7;
        max-width: 440px;
        margin-bottom: 1.5rem;
    }
    .hero-ctas {
        display: flex;
        gap: 1rem;
        flex-wrap: wrap;
    }

    /* ── CTA Button (with glow) ── */
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
        transition: all 0.35s cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow:
            0 4px 20px rgba(143, 188, 143, 0.3),
            0 0 0 0 rgba(143, 188, 143, 0);
        position: relative;
    }
    .btn-primary::before {
        content: "";
        position: absolute;
        inset: -4px;
        border-radius: 34px;
        background: linear-gradient(135deg, var(--leaf), var(--sun));
        opacity: 0;
        z-index: -1;
        filter: blur(12px);
        transition: opacity 0.4s;
    }
    .btn-primary:hover {
        background: var(--sun);
        transform: translateY(-3px) scale(1.03);
        box-shadow:
            0 8px 30px rgba(212, 168, 83, 0.45),
            0 0 0 4px rgba(212, 168, 83, 0.12);
    }
    .btn-primary:hover::before {
        opacity: 0.5;
    }

    /* ── Hero Visual (cards) ── */
    .hero-visual {
        position: relative;
        display: flex;
        flex-direction: column;
        gap: 1rem;
    }
    /* Floating leaf on the right side of cards */
    .hero-visual::after {
        content: "🌿";
        position: absolute;
        top: -20px;
        right: -15px;
        font-size: 1.5rem;
        opacity: 0.15;
        animation: floatLeaf2 10s ease-in-out infinite;
        pointer-events: none;
    }

    @keyframes floatLeaf2 {
        0%, 100% {
            transform: translateY(0) rotate(-5deg);
        }
        50% {
            transform: translateY(-20px) rotate(10deg);
        }
    }

    /* ── Glassmorphism Cards ── */
    .mock-card {
        background: rgba(255, 255, 255, 0.07);
        border: 1px solid rgba(255, 255, 255, 0.12);
        border-radius: 16px;
        padding: 1rem;
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        transition: transform 0.4s cubic-bezier(0.4, 0, 0.2, 1),
            box-shadow 0.4s cubic-bezier(0.4, 0, 0.2, 1),
            border-color 0.4s;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.25);
        position: relative;
        overflow: hidden;
    }
    /* Shimmer sweep on hover */
    .mock-card::before {
        content: "";
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(
            105deg,
            transparent 40%,
            rgba(255, 255, 255, 0.06) 45%,
            rgba(255, 255, 255, 0.12) 50%,
            rgba(255, 255, 255, 0.06) 55%,
            transparent 60%
        );
        transition: left 0.8s ease;
        z-index: 2;
        pointer-events: none;
    }
    .mock-card:hover::before {
        left: 100%;
    }
    .mock-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 16px 48px rgba(0, 0, 0, 0.3),
            0 0 0 1px rgba(143, 188, 143, 0.15);
        border-color: rgba(143, 188, 143, 0.2);
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
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
    }
    .mock-card-header div small {
        display: block;
        color: var(--sage);
        font-size: 0.75rem;
    }
    .mock-card-header div strong {
        color: #faf9f6;
        font-size: 0.95rem;
        text-shadow: 0 1px 2px rgba(0,0,0,0.3);
    }
    .highlight {
        color: var(--sage);
    }
    .mock-img {
        width: 100%;
        height: 110px;
        border-radius: 10px;
        background: linear-gradient(135deg, #2d5a27, #4a7c59, #6ba368);
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 3rem;
        margin-bottom: 0.8rem;
        position: relative;
        overflow: hidden;
        box-shadow: inset 0 -40px 40px rgba(0, 0, 0, 0.15);
    }
    .mock-img::after {
        content: "";
        position: absolute;
        inset: 0;
        background: linear-gradient(
            to top,
            rgba(0, 0, 0, 0.45) 0%,
            transparent 60%
        );
    }
    .mock-img-2 {
        background: linear-gradient(135deg, #1a3a20, #3d6b45, #5a8c60);
        height: 75px;
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
        text-shadow: 0 1px 4px rgba(0, 0, 0, 0.5);
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



    /* ── Stats Row (animated) ── */
    .stats-row {
        position: relative;
        z-index: 10;
        display: flex;
        justify-content: center;
        gap: 4rem;
        padding: 1.2rem 3rem;
        max-width: 1200px;
        margin: 0 auto;
        flex-shrink: 0;
    }
    .stats-row::before {
        content: "";
        position: absolute;
        top: 0;
        left: 3rem;
        right: 3rem;
        height: 1px;
        background: linear-gradient(
            90deg,
            transparent,
            rgba(143, 188, 143, 0.2),
            rgba(212, 168, 83, 0.15),
            rgba(143, 188, 143, 0.2),
            transparent
        );
    }
    .stat {
        text-align: center;
        transition: transform 0.3s ease;
    }
    .stat:hover {
        transform: translateY(-4px);
    }
    .stat:nth-child(1) {
        animation: fadeUp 0.6s ease 0.5s both;
    }
    .stat:nth-child(2) {
        animation: fadeUp 0.6s ease 0.65s both;
    }
    .stat:nth-child(3) {
        animation: fadeUp 0.6s ease 0.8s both;
    }
    .stat:nth-child(4) {
        animation: fadeUp 0.6s ease 0.95s both;
    }
    .stat .num {
        font-family: "Playfair Display", serif;
        font-size: 2rem;
        color: var(--leaf);
        display: block;
        text-shadow: 0 0 20px rgba(143, 188, 143, 0.15);
        transition: text-shadow 0.3s;
    }
    .stat:hover .num {
        text-shadow: 0 0 30px rgba(143, 188, 143, 0.35);
    }
    .stat .label {
        color: var(--canopy);
        font-size: 0.85rem;
        margin-top: 0.2rem;
        display: block;
    }

    /* ── Mini Map Widget ── */
    .map-stat {
        position: relative;
    }
    .mini-map {
        width: 90px;
        height: 70px;
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(143, 188, 143, 0.25);
        border-radius: 12px;
        display: flex;
        align-items: center;
        justify-content: center;
        margin: 0 auto 0.15rem;
        position: relative;
        overflow: hidden;
        backdrop-filter: blur(8px);
        transition: border-color 0.3s, box-shadow 0.3s;
    }
    .mini-map:hover {
        border-color: rgba(143, 188, 143, 0.5);
        box-shadow: 0 0 20px rgba(143, 188, 143, 0.15);
    }
    .mini-map-svg {
        width: 75px;
        height: 58px;
    }
    .map-live-badge {
        position: absolute;
        top: 4px;
        right: 5px;
        font-size: 0.45rem;
        color: #4ade80;
        letter-spacing: 0.08em;
        font-weight: 600;
        animation: livePulse 2s ease-in-out infinite;
    }
    @keyframes livePulse {
        0%, 100% { opacity: 0.6; }
        50% { opacity: 1; }
    }

    /* ── Entrance Animations ── */
    .hero-text {
        animation: fadeUp 0.8s cubic-bezier(0.4, 0, 0.2, 1) 0.1s both;
    }
    .hero-visual {
        animation: fadeUp 0.8s cubic-bezier(0.4, 0, 0.2, 1) 0.35s both;
    }
    @keyframes fadeUp {
        from {
            opacity: 0;
            transform: translateY(24px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }

    /* ── Made with love footer (refined) ── */
    .made-with-love {
        background: var(--bark);
        text-align: center;
        padding: 0.6rem 1rem 0.5rem;
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: 0.3rem;
        flex-shrink: 0;
        animation: fadeUp 0.6s ease 1.1s both;
    }
    .love-line {
        width: 80px;
        height: 1px;
        background: linear-gradient(
            90deg,
            transparent,
            var(--sage),
            var(--sun),
            var(--sage),
            transparent
        );
        opacity: 0.35;
        animation: pulseGlow 3s ease-in-out infinite;
    }
    @keyframes pulseGlow {
        0%, 100% {
            opacity: 0.3;
            width: 80px;
        }
        50% {
            opacity: 0.55;
            width: 100px;
        }
    }
    .love-text {
        font-family: "DM Sans", sans-serif;
        font-size: 0.8rem;
        letter-spacing: 0.2em;
        text-transform: uppercase;
        color: var(--canopy);
        opacity: 0.6;
    }
    .love-word {
        font-family: "Playfair Display", serif;
        font-style: italic;
        font-weight: 700;
        color: #ef4444;
        opacity: 1;
    }
    .nyu-word {
        font-weight: 700;
        font-size: 1.15rem;
        letter-spacing: 0.25em;
        opacity: 1;
        background: linear-gradient(
            90deg,
            #9b6fbf,
            #d8b4fe,
            #f0d0ff,
            #d8b4fe,
            #9b6fbf
        );
        background-size: 200% auto;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        animation: nyuShimmer 2.5s linear infinite;
    }
    @keyframes nyuShimmer {
        to {
            background-position: 200% center;
        }
    }
    .love-leaf {
        font-size: 0.7rem;
        opacity: 0.5;
        animation: gentleSway 3s ease-in-out infinite;
    }
    @keyframes gentleSway {
        0%,
        100% {
            transform: rotate(-5deg);
        }
        50% {
            transform: rotate(5deg);
        }
    }
</style>
