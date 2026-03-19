<script>
  import LeftNav from "../components/LeftNav.svelte";
  import BackgroundRings from "../components/BackgroundRings.svelte";
  export let navigate;
  
  import { onMount } from "svelte";
  import L from "leaflet";

  import "leaflet/dist/leaflet.css";

  // FIX: Leaflet marker icons (MUST be here)
  delete L.Icon.Default.prototype._getIconUrl;

  L.Icon.Default.mergeOptions({
    iconRetinaUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png",
    iconUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png",
    shadowUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png",
  });
    //  FIX: Leaflet marker icons (MUST be here)

  let map;
  let trees = [];

  async function fetchTrees() {
    try {
      const res = await fetch("/trees/api/?limit=10", { credentials: "include" });
      if (!res.ok) throw new Error("Failed to fetch");
      trees = await res.json();
      console.log("Fetched trees:", trees); // should be only 10
    } catch (err) {
      console.error("Error fetching trees:", err);
    }
  }

  onMount(async () => {
    await fetchTrees();

    if (!trees.length) return;

    map = L.map("map").setView([40.7128, -74.0060], 12);
    
//  FIX: Leaflet marker icons (MUST be here)
    L.tileLayer(
      "https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png",
      {
        attribution: "&copy; OpenStreetMap contributors &copy; Carto",
      }
    ).addTo(map);
//  FIX: Leaflet marker icons (MUST be here)
    const latlngs = [];

    trees.forEach((tree) => {
      const lat = parseFloat(tree.latitude);
      const lng = parseFloat(tree.longitude);

      if (isNaN(lat) || isNaN(lng)) return;

      // Create popup content with "Dashboard" button
      const popupContent = `
        <div>
          <b>${tree.spc_common}</b><br>
          ID: ${tree.tree_id}<br>
          <button class="popup-dashboard-btn" data-treeid="${tree.tree_id}">Dashboard</button>
        </div>
      `;

//  FIX: Leaflet marker icons (MUST be here)
    const customIcon = L.icon({
      iconUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png",
      iconRetinaUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png",
      shadowUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png",
      iconSize: [25, 41],
      iconAnchor: [12, 41],
      popupAnchor: [1, -34],
      shadowSize: [41, 41],
    });

    const marker = L.marker([lat, lng], { icon: customIcon })
      .bindPopup(popupContent)
      .addTo(map);
//  FIX: Leaflet marker icons (MUST be here)

      latlngs.push([lat, lng]);
    });

    if (latlngs.length > 0) {
      map.fitBounds(latlngs, { padding: [50, 50] });
    }

    // Handle click on "Dashboard" buttons inside popups
    map.on("popupopen", function(e) {
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

