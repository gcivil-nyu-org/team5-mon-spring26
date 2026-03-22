<script>
    import { onMount, onDestroy } from "svelte";

    let rings = [];
    let generatedUpTo = 0;
    const SECTION_HEIGHT = 800;

    function rand(min, max) {
        return Math.random() * (max - min) + min;
    }

    // Track ring geometry to prevent overlaps
    // Note: left is a percentage, top is in pixels
    // We'll estimate the pixel X coordinate assuming a typical screen width of 1440px
    // for collision purposes to ensure they don't overlap.
    const ESTIMATED_SCREEN_WIDTH = 1440;

    function createRing(y, existingRingsForCollision) {
        const MAX_ATTEMPTS = 50;

        for (let attempt = 0; attempt < MAX_ATTEMPTS; attempt++) {
            const size = Math.round(rand(350, 900));
            const radius = size / 2;
            const top = Math.round(y + rand(0, SECTION_HEIGHT));
            const leftPerc = rand(-20, 85);

            // Calculate pixel centers for collision math
            const centerX = (leftPerc / 100) * ESTIMATED_SCREEN_WIDTH + radius;
            const centerY = top + radius;

            // Check collision with ALL existing rings (including newly generated ones)
            let hasCollision = false;
            for (const other of existingRingsForCollision) {
                // Distance between centers must be > sum of radii
                const dx = centerX - other.cx;
                const dy = centerY - other.cy;
                const distance = Math.sqrt(dx * dx + dy * dy);

                // Add a small buffer (e.g. 20px) so they don't touch exactly
                if (distance < radius + other.r + 20) {
                    hasCollision = true;
                    break;
                }
            }

            if (!hasCollision) {
                const spacing = Math.round(rand(13, 28));
                const alpha = rand(0.12, 0.22).toFixed(3);
                const opacity = rand(0.3, 0.7).toFixed(2);

                const ringGeometry = { cx: centerX, cy: centerY, r: radius };

                const ringStyle =
                    `top:${top}px;left:${leftPerc}%;width:${size}px;height:${size}px;opacity:${opacity};` +
                    `background:repeating-radial-gradient(circle at center,` +
                    `transparent,transparent ${spacing}px,` +
                    `rgba(143,188,143,${alpha}) ${spacing + 1}px,` +
                    `rgba(143,188,143,${alpha}) ${spacing + 2}px,` +
                    `transparent ${spacing + 3}px)`;

                return {
                    ringData: {
                        id: Math.random().toString(36).slice(2),
                        style: ringStyle,
                    },
                    geometry: ringGeometry,
                };
            }
        }

        return null; // Could not find a non-overlapping spot after max attempts
    }

    // Array to store collision geometry for all active rings
    let collisionData = [];

    function generateRings(fromY, toY) {
        const newRings = [];
        for (let y = fromY; y < toY; y += SECTION_HEIGHT) {
            const count = 2 + Math.floor(Math.random() * 2); // 2-3 per section
            for (let i = 0; i < count; i++) {
                const result = createRing(y, collisionData);
                if (result) {
                    newRings.push(result.ringData);
                    collisionData.push(result.geometry);
                }
            }
        }
        return newRings;
    }

    function handleScroll() {
        const needed = window.scrollY + window.innerHeight + 600;
        if (needed > generatedUpTo) {
            rings = [...rings, ...generateRings(generatedUpTo, needed)];
            generatedUpTo = needed;
        }
    }

    onMount(() => {
        const initialHeight =
            Math.max(
                document.documentElement.scrollHeight,
                window.innerHeight,
            ) + 600;
        rings = generateRings(0, initialHeight);
        generatedUpTo = initialHeight;

        window.addEventListener("scroll", handleScroll, { passive: true });
        window.addEventListener("resize", handleScroll, { passive: true });
    });

    onDestroy(() => {
        window.removeEventListener("scroll", handleScroll);
        window.removeEventListener("resize", handleScroll);
    });
</script>

{#each rings as ring (ring.id)}
    <div class="bg-ring" style={ring.style} />
{/each}

<style>
    .bg-ring {
        position: absolute;
        pointer-events: none;
        z-index: -1;
    }
</style>
