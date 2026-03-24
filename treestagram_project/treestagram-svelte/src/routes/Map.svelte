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

  // Fix default Leaflet icons
  delete L.Icon.Default.prototype._getIconUrl;
  L.Icon.Default.mergeOptions({
    iconRetinaUrl:
      "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png",
    iconUrl:
      "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png",
    shadowUrl:
      "https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png",
  });

  let map;
  let markers;
  let loadedTreeIds = new Set(); // avoid duplicates

  async function loadTreesInView() {
    if (!map) return;

    const bounds = map.getBounds();
    let offset = 0;
    const pageLimit = 500;
    let treesFetched = [];

    while (true) {
      const url = `/trees/api/?min_lat=${bounds.getSouth()}&max_lat=${bounds.getNorth()}&min_lng=${bounds.getWest()}&max_lng=${bounds.getEast()}&limit=${pageLimit}&offset=${offset}`;
      try {
        const res = await fetch(url, { credentials: "include" });
        if (!res.ok) throw new Error("Failed to fetch trees");

        const trees = await res.json();
        if (!trees.length) break;

        treesFetched = treesFetched.concat(trees);
        offset += trees.length;

        if (trees.length < pageLimit) break; // last page
      } catch (err) {
        console.error("Error loading trees:", err);
        break;
      }
    }

    // Clear old markers and cluster
    markers.clearLayers();
    loadedTreeIds.clear();

    treesFetched.forEach((tree) => {
      if (loadedTreeIds.has(tree.tree_id)) return;

      const lat = parseFloat(tree.latitude);
      const lng = parseFloat(tree.longitude);
      if (isNaN(lat) || isNaN(lng)) return;

      const popupContent = `
        <div>
          <b>${tree.spc_common || "Unknown"}</b><br>
          ID: ${tree.tree_id}<br>
          <button class="popup-dashboard-btn" data-treeid="${tree.tree_id}">
            Dashboard
          </button>
        </div>
      `;

      const marker = L.marker([lat, lng]).bindPopup(popupContent);
      markers.addLayer(marker);
      loadedTreeIds.add(tree.tree_id);
    });
  }

  onMount(() => {
    // Initialize map
    map = L.map("map").setView([40.7128, -74.0060], 12);

    L.tileLayer(
      "https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png",
      {
        attribution: "&copy; OpenStreetMap contributors &copy; Carto",
      }
    ).addTo(map);

    // Create cluster group
    markers = L.markerClusterGroup();
    map.addLayer(markers);

    // Initial load
    loadTreesInView();

    // Reload when user moves map or zooms
    map.on("moveend", () => {
      loadTreesInView();
    });

    // Handle popup button clicks
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
  }

  #map {
    width: 100%;
    height: 100%;
    z-index: 1;
  }
</style>