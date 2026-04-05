<script>
  import LeftNav from "../components/LeftNav.svelte";
  import BackgroundRings from "../components/BackgroundRings.svelte";
  export let navigate;

  import { onMount } from "svelte";
  import L from "leaflet";

  import "leaflet/dist/leaflet.css";

  // Marker clustering
  import "leaflet.markercluster/dist/MarkerCluster.css";
  import "leaflet.markercluster/dist/MarkerCluster.Default.css";
  import "leaflet.markercluster";

  // Custom tree icon
  const treeIcon = L.divIcon({
    html: '<span style="font-size:1.2rem;filter:drop-shadow(0 1px 2px rgba(0,0,0,0.3));cursor:pointer;">🌳</span>',
    className: 'tree-div-icon',
    iconSize: [20, 20],
    iconAnchor: [10, 10],
    popupAnchor: [0, -10],
  });

  let map;
  let markers;
  let loadedTreeIds = new Set();
  let showZoomMessage = true;

  function debounce(fn, delay) {
    let timer;
    return (...args) => {
      clearTimeout(timer);
      timer = setTimeout(() => fn(...args), delay);
    };
  }

  async function loadTreesInView() {
    if (!map) return;

    const zoom = map.getZoom();
    if (zoom < 12) {
      markers.clearLayers();
      loadedTreeIds.clear();
      showZoomMessage = true;
      return;
    }
    showZoomMessage = false;

    const bounds = map.getBounds();
    const limit = 750;

    const url = `/trees/api/?min_lat=${bounds.getSouth()}&max_lat=${bounds.getNorth()}&min_lng=${bounds.getWest()}&max_lng=${bounds.getEast()}&limit=${limit}&offset=0`;

    try {
      const res = await fetch(url, { credentials: "include" });
      if (!res.ok) throw new Error("Failed to fetch trees");
      const trees = await res.json();

      markers.clearLayers();
      loadedTreeIds.clear();

      trees.forEach((tree) => {
        const lat = parseFloat(tree.latitude);
        const lng = parseFloat(tree.longitude);
        if (isNaN(lat) || isNaN(lng)) return;

        const name = tree.spc_common || "Unknown";
        const capitalName = name.charAt(0).toUpperCase() + name.slice(1);
        const popupContent = `
          <div class="tree-popup">
            <div class="tree-popup-header">
              <span class="tree-popup-emoji">🌳</span>
              <div class="tree-popup-title">
                <strong>${capitalName}</strong>
                <span class="tree-popup-id">#${tree.tree_id}</span>
              </div>
            </div>
            <button class="popup-dashboard-btn" data-treeid="${tree.tree_id}">
              View Dashboard →
            </button>
          </div>
        `;

        const marker = L.marker([lat, lng], { icon: treeIcon }).bindPopup(popupContent);
        markers.addLayer(marker);
        loadedTreeIds.add(tree.tree_id);
      });
    } catch (err) {
      console.error("Error loading trees:", err);
    }
  }

  onMount(() => {
    map = L.map("map").setView([40.7128, -74.0060], 12);

    L.tileLayer(
      "https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png",
      {
        attribution: "&copy; OpenStreetMap contributors &copy; Carto",
      }
    ).addTo(map);

    markers = L.markerClusterGroup({
      disableClusteringAtZoom: 17,
      maxClusterRadius: 40,
    });
    map.addLayer(markers);

    loadTreesInView();

    map.on("moveend", debounce(() => {
      loadTreesInView();
    }, 300));

    map.on("popupopen", function (e) {
      const popupNode = e.popup.getElement();
      const btn = popupNode.querySelector(".popup-dashboard-btn");

      if (btn) {
        btn.addEventListener("click", () => {
          const treeId = btn.dataset.treeid;
          navigate(`/treedashboard/${treeId}`);
        });
      }
    });
  });
</script>

<div class="page">
  <BackgroundRings />
  <LeftNav {navigate} activePage="map" />

  <div class="map-container">
    {#if showZoomMessage}
      <div class="zoom-hint">Zoom in to see individual trees</div>
    {/if}
    <div id="map"></div>
  </div>
</div>

<style>
  .page {
    background: #faf9f6;
    min-height: 100vh;
    padding-left: 60px;
    position: relative;
  }

  .map-container {
    height: 100vh;
    position: relative;
  }

  #map {
    width: 100%;
    height: 100%;
    z-index: 1;
  }


  .zoom-hint {
    position: absolute;
    top: 16px;
    left: 50%;
    transform: translateX(-50%);
    background: rgba(0, 0, 0, 0.65);
    color: white;
    padding: 6px 14px;
    border-radius: 20px;
    font-size: 13px;
    z-index: 999;
    pointer-events: none;
  }

  /* ─── Leaflet Popup Overrides (global because Leaflet injects outside Svelte) ── */
  :global(.leaflet-popup-content-wrapper) {
    background: #faf9f6 !important;
    border-radius: 14px !important;
    box-shadow: 0 6px 24px rgba(0,0,0,0.12), 0 2px 8px rgba(0,0,0,0.06) !important;
    padding: 0 !important;
    border: 1px solid rgba(82,154,103,0.2);
  }
  :global(.leaflet-popup-content) {
    margin: 0 !important;
    min-width: 180px;
  }
  :global(.leaflet-popup-tip) {
    background: #faf9f6 !important;
    border: 1px solid rgba(82,154,103,0.2);
    border-top: none;
    border-left: none;
  }
  :global(.leaflet-popup-close-button) {
    color: #999 !important;
    font-size: 20px !important;
    width: 28px !important;
    height: 28px !important;
    padding: 4px 6px 0 0 !important;
    transition: color 0.15s;
  }
  :global(.leaflet-popup-close-button:hover) {
    color: #333 !important;
  }

  :global(.tree-popup) {
    padding: 14px 16px;
    font-family: 'Inter', 'Segoe UI', system-ui, sans-serif;
  }
  :global(.tree-popup-header) {
    display: flex;
    align-items: center;
    gap: 10px;
    margin-bottom: 10px;
  }
  :global(.tree-popup-emoji) {
    font-size: 1.6rem;
    filter: drop-shadow(0 1px 2px rgba(0,0,0,0.12));
    flex-shrink: 0;
  }
  :global(.tree-popup-title) {
    display: flex;
    flex-direction: column;
  }
  :global(.tree-popup-title strong) {
    font-size: 0.92rem;
    color: #2b2b2b;
    line-height: 1.2;
  }
  :global(.tree-popup-id) {
    display: inline-block;
    margin-top: 2px;
    background: linear-gradient(135deg, rgba(82,154,103,0.1), rgba(45,122,58,0.05));
    border: 1px solid rgba(82,154,103,0.25);
    border-radius: 50px;
    padding: 1px 8px;
    font-size: 0.68rem;
    font-weight: 700;
    color: #529a67;
    font-family: 'DM Mono', 'Courier New', monospace;
    letter-spacing: 0.3px;
    width: fit-content;
  }
  :global(.popup-dashboard-btn) {
    display: block;
    width: 100%;
    background: linear-gradient(135deg, #529a67, #3d7a4e);
    color: #fff;
    border: none;
    border-radius: 8px;
    padding: 8px 12px;
    font-size: 0.82rem;
    font-weight: 600;
    font-family: 'Inter', 'Segoe UI', system-ui, sans-serif;
    cursor: pointer;
    transition: transform 0.15s, box-shadow 0.2s;
    box-shadow: 0 2px 6px rgba(82,154,103,0.25);
  }
  :global(.popup-dashboard-btn:hover) {
    transform: translateY(-1px);
    box-shadow: 0 4px 12px rgba(82,154,103,0.35);
  }
</style>