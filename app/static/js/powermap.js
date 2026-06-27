const powerMapConfig = window.POWERMAP_CONFIG;

const mapStyle = {
  version: 8,
  name: "gsi-pale",
  sources: {
    "gsi-pale": {
      type: "raster",
      tiles: ["https://cyberjapandata.gsi.go.jp/xyz/pale/{z}/{x}/{y}.png"],
      tileSize: 256,
      attribution: "地理院タイル"
    }
  },
  layers: [
    {
      id: "gsi-pale",
      type: "raster",
      source: "gsi-pale",
      paint: {
        "raster-opacity": 1
      }
    }
  ]
};

const queryParams = new URLSearchParams(window.location.search);
const showPowerLayers = queryParams.get("layers") !== "base";
const fallbackTileSize = 256;
const fallbackTileUrl = "https://cyberjapandata.gsi.go.jp/xyz/pale/{z}/{x}/{y}.png";

const hoverLayerIds = [
  "power-plants-points",
  "power-plants-polygons-fill",
  "power-substations-points",
  "power-substations-polygons-fill"
];

const voltage = ["to-number", ["coalesce", ["get", "voltage"], "0"], 0];
const powerLayerGroups = {
  "high-voltage": ["power-lines-high-casing", "power-lines-high"],
  "mid-voltage": ["power-lines-mid-casing", "power-lines-mid"],
  "other-lines": ["power-lines-other-casing", "power-lines-other"],
  towers: ["power-towers"],
  plants: ["power-plants-polygons-fill", "power-plants-polygons-outline", "power-plants-points"],
  substations: ["power-substations-polygons-fill", "power-substations-polygons-outline", "power-substations-points"]
};

const lineCategoryStyles = [
  {
    id: "high",
    color: "#dc2626",
    filter: [">=", voltage, 154000],
    width: 2.6
  },
  {
    id: "mid",
    color: "#2563eb",
    filter: ["all", [">=", voltage, 66000], ["<", voltage, 154000]],
    width: 1.5
  },
  {
    id: "other",
    color: "#6b7280",
    filter: ["<", voltage, 66000],
    width: 0.85
  }
];

function zoomLineWidth(baseWidth, casing = false) {
  const casingWidth = casing ? 1.6 : 0;
  return [
    "interpolate",
    ["linear"],
    ["zoom"],
    5,
    0.9 * baseWidth + casingWidth,
    10,
    1.8 * baseWidth + casingWidth,
    14,
    3 * baseWidth + casingWidth
  ];
}

function property(feature, key) {
  return feature?.properties?.[key] || "";
}

function escapeHtml(value) {
  return String(value || "")
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}

function featureType(feature) {
  const sourceLayer = feature.sourceLayer || "";
  if (sourceLayer.includes("plants")) {
    return "発電所";
  }
  if (sourceLayer.includes("substations")) {
    return "変電所";
  }
  return "";
}

function popupHtml(feature) {
  const name = property(feature, "name") || "(名称なし)";
  const rows = [
    ["種別", featureType(feature)],
    ["名称", name],
    ["ref", property(feature, "ref")],
    ["osm_id", property(feature, "osm_id") || property(feature, "osm_way_id")]
  ].filter((row) => row[1]);
  return rows.map(([label, value]) => `<b>${escapeHtml(label)}</b>: ${escapeHtml(value)}`).join("<br>");
}

function addPowerLineLayers(map) {
  for (const style of lineCategoryStyles) {
    map.addLayer({
      id: `power-lines-${style.id}-casing`,
      type: "line",
      source: "power",
      "source-layer": "power_lines",
      filter: style.filter,
      paint: {
        "line-color": "#ffffff",
        "line-opacity": 0.82,
        "line-width": zoomLineWidth(style.width, true)
      }
    });

    map.addLayer({
      id: `power-lines-${style.id}`,
      type: "line",
      source: "power",
      "source-layer": "power_lines",
      filter: style.filter,
      paint: {
        "line-color": style.color,
        "line-opacity": 0.9,
        "line-width": zoomLineWidth(style.width)
      }
    });
  }
}

function addPowerLayers(map) {
  map.addSource("power", {
    type: "vector",
    url: powerMapConfig.tileJsonUrl
  });

  addPowerLineLayers(map);

  map.addLayer({
    id: "power-towers",
    type: "circle",
    source: "power",
    "source-layer": "power_towers",
    minzoom: 12,
    paint: {
      "circle-color": "#111827",
      "circle-opacity": ["interpolate", ["linear"], ["zoom"], 12, 0.2, 14, 0.72],
      "circle-radius": ["interpolate", ["linear"], ["zoom"], 12, 1.1, 14, 2.4],
      "circle-stroke-color": "#ffffff",
      "circle-stroke-width": 0.4
    }
  });

  map.addLayer({
    id: "power-plants-polygons-fill",
    type: "fill",
    source: "power",
    "source-layer": "power_plants_polygons",
    paint: {
      "fill-color": "#facc15",
      "fill-opacity": 0.26
    }
  });
  map.addLayer({
    id: "power-plants-polygons-outline",
    type: "line",
    source: "power",
    "source-layer": "power_plants_polygons",
    paint: {
      "line-color": "#ca8a04",
      "line-width": 1.2
    }
  });
  map.addLayer({
    id: "power-plants-points",
    type: "circle",
    source: "power",
    "source-layer": "power_plants_points",
    paint: {
      "circle-color": "#facc15",
      "circle-radius": ["interpolate", ["linear"], ["zoom"], 5, 3, 14, 7],
      "circle-stroke-color": "#854d0e",
      "circle-stroke-width": 1.2
    }
  });

  map.addLayer({
    id: "power-substations-polygons-fill",
    type: "fill",
    source: "power",
    "source-layer": "power_substations_polygons",
    paint: {
      "fill-color": "#38bdf8",
      "fill-opacity": 0.24
    }
  });
  map.addLayer({
    id: "power-substations-polygons-outline",
    type: "line",
    source: "power",
    "source-layer": "power_substations_polygons",
    paint: {
      "line-color": "#0369a1",
      "line-width": 1.1
    }
  });
  map.addLayer({
    id: "power-substations-points",
    type: "circle",
    source: "power",
    "source-layer": "power_substations_points",
    paint: {
      "circle-color": "#38bdf8",
      "circle-radius": ["interpolate", ["linear"], ["zoom"], 5, 2.5, 14, 6],
      "circle-stroke-color": "#075985",
      "circle-stroke-width": 1.1
    }
  });
}

function setLayerGroupVisibility(map, groupName, visible) {
  for (const layerId of powerLayerGroups[groupName] || []) {
    if (map.getLayer(layerId)) {
      map.setLayoutProperty(layerId, "visibility", visible ? "visible" : "none");
    }
  }
}

function addLegendToggles(map) {
  for (const button of document.querySelectorAll(".legend-toggle[data-layer-group]")) {
    button.addEventListener("click", () => {
      const groupName = button.dataset.layerGroup;
      const nextVisible = button.getAttribute("aria-pressed") !== "true";
      button.setAttribute("aria-pressed", String(nextVisible));
      setLayerGroupVisibility(map, groupName, nextVisible);
    });
  }
}

function addHover(map) {
  const popup = new maplibregl.Popup({
    closeButton: false,
    closeOnClick: false,
    offset: 12
  });

  map.on("mousemove", (event) => {
    const features = map.queryRenderedFeatures(event.point, { layers: hoverLayerIds });
    if (!features.length) {
      map.getCanvas().style.cursor = "";
      popup.remove();
      return;
    }
    map.getCanvas().style.cursor = "pointer";
    popup.setLngLat(event.lngLat).setHTML(popupHtml(features[0])).addTo(map);
  });

  map.on("mouseleave", "power-plants-points", () => popup.remove());
  map.on("mouseleave", "power-substations-points", () => popup.remove());
}

function addDeckOverlay(map) {
  if (!showPowerLayers || !window.deck?.MapboxOverlay) {
    return;
  }

  const overlay = new deck.MapboxOverlay({
    interleaved: false,
    layers: []
  });
  map.addControl(overlay);
}

function lonLatToWorldPixel(lng, lat, zoom) {
  const scale = fallbackTileSize * 2 ** zoom;
  const sinLat = Math.sin((Math.max(Math.min(lat, 85.05112878), -85.05112878) * Math.PI) / 180);
  return {
    x: ((lng + 180) / 360) * scale,
    y: (0.5 - Math.log((1 + sinLat) / (1 - sinLat)) / (4 * Math.PI)) * scale
  };
}

function renderFallbackBaseMap(container, center, zoom) {
  if (!container) {
    return;
  }

  const width = container.clientWidth;
  const height = container.clientHeight;
  if (!width || !height) {
    return;
  }

  const tileZoom = Math.max(0, Math.min(18, Math.round(zoom)));
  const tileCount = 2 ** tileZoom;
  const centerPixel = lonLatToWorldPixel(center.lng, center.lat, tileZoom);
  const topLeft = {
    x: centerPixel.x - width / 2,
    y: centerPixel.y - height / 2
  };
  const minTileX = Math.floor(topLeft.x / fallbackTileSize);
  const maxTileX = Math.floor((topLeft.x + width) / fallbackTileSize);
  const minTileY = Math.max(0, Math.floor(topLeft.y / fallbackTileSize));
  const maxTileY = Math.min(tileCount - 1, Math.floor((topLeft.y + height) / fallbackTileSize));
  const fragment = document.createDocumentFragment();

  for (let tileY = minTileY; tileY <= maxTileY; tileY += 1) {
    for (let tileX = minTileX; tileX <= maxTileX; tileX += 1) {
      const wrappedTileX = ((tileX % tileCount) + tileCount) % tileCount;
      const img = document.createElement("img");
      img.alt = "";
      img.decoding = "async";
      img.loading = "eager";
      img.src = fallbackTileUrl
        .replace("{z}", String(tileZoom))
        .replace("{x}", String(wrappedTileX))
        .replace("{y}", String(tileY));
      img.style.left = `${tileX * fallbackTileSize - topLeft.x}px`;
      img.style.top = `${tileY * fallbackTileSize - topLeft.y}px`;
      fragment.appendChild(img);
    }
  }

  container.replaceChildren(fragment);
}

function createFallbackRenderer(map, container) {
  let frameId = 0;
  return () => {
    if (frameId) {
      return;
    }
    frameId = requestAnimationFrame(() => {
      frameId = 0;
      renderFallbackBaseMap(container, map.getCenter(), map.getZoom());
    });
  };
}

document.addEventListener("DOMContentLoaded", () => {
  const mapContainer = document.getElementById("powermap");
  const fallbackContainer = document.getElementById("powermap-fallback");
  if (!powerMapConfig || !mapContainer) {
    return;
  }

  const initial = powerMapConfig.initialViewState;
  renderFallbackBaseMap(fallbackContainer, { lng: initial.longitude, lat: initial.latitude }, initial.zoom);

  const map = new maplibregl.Map({
    container: mapContainer,
    style: mapStyle,
    center: [initial.longitude, initial.latitude],
    zoom: initial.zoom,
    pitch: initial.pitch,
    bearing: initial.bearing
  });

  map.addControl(new maplibregl.NavigationControl({ showCompass: true }), "top-right");
  addDeckOverlay(map);
  const renderFallback = createFallbackRenderer(map, fallbackContainer);

  requestAnimationFrame(() => {
    map.resize();
    renderFallback();
  });

  map.on("load", () => {
    map.resize();
    if (!showPowerLayers) {
      return;
    }
    addPowerLayers(map);
    addLegendToggles(map);
    addHover(map);
  });

  map.on("move", renderFallback);
  map.on("resize", renderFallback);
  window.addEventListener("resize", renderFallback);
});
