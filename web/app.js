const map = L.map("map", { preferCanvas: true, zoomControl: false }).setView([31.7, -102.2], 7);
L.control.zoom({ position: "topright" }).addTo(map);
L.tileLayer("https://tile.openstreetmap.org/{z}/{x}/{y}.png", {
  attribution: "&copy; OpenStreetMap",
  maxZoom: 16,
}).addTo(map);

const layers = {};
let leaseIndex = [];
let hubCatalog = { hubs: [], operators: {}, prices: {}, regions: {} };
let hubById = {};
let currentPipes = [];
let showHubs = false;

function flareColor(value) {
  if (value >= 20) return "#6e1220";
  if (value >= 5) return "#c2311f";
  if (value >= 1) return "#e36a2c";
  if (value >= 0.25) return "#f0a04a";
  if (value >= 0.05) return "#f3c888";
  return "#f6e0b8";
}

function pipeColor(pipeType) {
  const kind = (pipeType || "").toLowerCase();
  if (kind.includes("gather")) return "#9a6b2f";
  if (kind.includes("intra")) return "#3d6b4f";
  return "#1f4e79";
}

function hubLink(operator) {
  return (hubCatalog.operators || {})[operator || ""] || null;
}

function pipeStyle(feature) {
  if (showHubs) {
    const link = hubLink(feature.properties.operator);
    const hub = link && hubById[link.hub];
    if (hub) return { color: hub.color, weight: 2.6, opacity: 0.95 };
    return { color: "#c4bdb2", weight: 1.1, opacity: 0.45 };
  }
  return { color: pipeColor(feature.properties.pipe_type), weight: 1.6, opacity: 0.85 };
}

function pipePopup(props) {
  const lines = [`<b>${esc(props.operator || "Operator not named")}</b>`, esc(props.pipe_type || "Pipeline")];
  const link = hubLink(props.operator);
  const hub = link && hubById[link.hub];
  if (hub) {
    lines.push(`<b>Pricing point:</b> ${esc(hub.name)}`);
    if (link.note) lines.push(esc(link.note));
  } else if (showHubs) {
    lines.push("No hub is assigned to this pipeline yet.");
  }
  return lines.join("<br>");
}

function paintHubLegend() {
  const box = document.getElementById("hub-legend");
  box.replaceChildren();
  if (!showHubs) {
    box.hidden = true;
    return;
  }
  const used = new Map();
  currentPipes.forEach((feature) => {
    const link = hubLink(feature.properties.operator);
    const hub = link && hubById[link.hub];
    if (hub) used.set(hub.id, hub);
  });
  if (!used.size) {
    box.hidden = true;
    return;
  }
  const title = document.createElement("p");
  title.className = "legend-title";
  title.textContent = "Pipeline hub";
  box.appendChild(title);
  [...used.values()].sort((a, b) => a.name.localeCompare(b.name)).forEach((hub) => {
    const row = document.createElement("div");
    row.className = "swatch";
    row.innerHTML = `<i class="line" style="background:${hub.color}"></i><span>${esc(hub.name)}</span>`;
    box.appendChild(row);
  });
  const plain = document.createElement("div");
  plain.className = "swatch";
  plain.innerHTML = '<i class="line" style="background:#c4bdb2"></i><span>No hub assigned</span>';
  box.appendChild(plain);
  box.hidden = false;
}

function showHubPrice(base) {
  const el = document.getElementById("hub-price");
  const region = (hubCatalog.regions || {})[base];
  const hub = region && hubById[region.hub];
  const price = hub && (hubCatalog.prices || {})[hub.id];
  if (!hub || !price || price.usd_per_mmbtu == null) {
    el.hidden = true;
    el.textContent = "";
    return;
  }
  el.hidden = false;
  el.textContent = (
    `${hub.name} spot ${Number(price.usd_per_mmbtu).toFixed(2)} $/MMBtu on ${price.period}. ` +
    (region.note || "")
  ).trim();
}

function monthLabel(period) {
  if (!period) return "";
  if (String(period).includes("-")) return period;
  return `${period.slice(0, 4)}-${period.slice(4)}`;
}

function leasePopup(props) {
  if (props.unit === "field") {
    return `
      <strong>${esc(props.lease_name || "Unnamed field")}</strong><br>
      Field ${esc(props.lease_no)}, ${esc(props.district)} District<br>
      <b>${props.flared_mmcfd.toFixed(2)} MMcfd</b> gas blown
      (${Math.round(props.flared_mcf).toLocaleString()} Mcf${monthLabel(props.period) ? ` in ${monthLabel(props.period)}` : ""})<br>
      CalGEM reports this for the whole field. The shape is the field boundary.
    `;
  }
  const share = props.produced_mcf > 0
    ? `${(100 * props.flared_mcf / props.produced_mcf).toFixed(1)}% of reported gas`
    : "Produced volume on this filing is zero";
  const who = props.kind === "oil" ? "Oil lease" : "Gas well";
  return `
    <strong>${props.lease_name || "Unnamed lease"}</strong><br>
    ${props.field_name || ""}<br>
    ${who} ${props.lease_no}, district ${props.district}, ${props.county} County<br>
    ${props.operator_name || "Operator " + props.operator_no}<br>
    <b>${props.flared_mmcfd.toFixed(2)} MMcfd</b> vented or flared
    (${Math.round(props.flared_mcf).toLocaleString()} Mcf${monthLabel(props.period) ? ` in ${monthLabel(props.period)}` : ""})<br>
    ${share}. Placed at the centroid of ${props.wells} surface well${props.wells === 1 ? "" : "s"}.
  `;
}

function esc(value) {
  return String(value ?? "").replace(/[&<>"]/g, (ch) => ({
    "&": "&amp;",
    "<": "&lt;",
    ">": "&gt;",
    "\"": "&quot;",
  }[ch]));
}

function poiColor(kv) {
  if (kv >= 345) return "#5c2d91";
  if (kv >= 230) return "#143d66";
  if (kv >= 138) return "#1d6a8a";
  return "#2f7d4a";
}

const OWNER_NOTES = {
  "ONCOR ELECTRIC DELIVERY CO.": {
    label: "Oncor Electric Delivery",
    note: "ERCOT transmission and distribution utility. Request the interconnection through ERCOT, with Oncor as the transmission provider for the local connection.",
  },
  "ONCOR ELECTRIC DELIVERY COMPANY LLC": {
    label: "Oncor Electric Delivery",
    note: "ERCOT transmission and distribution utility. Request the interconnection through ERCOT, with Oncor as the transmission provider for the local connection.",
  },
  "AEP TEXAS NORTH CO.": {
    label: "AEP Texas North",
    note: "ERCOT transmission and distribution utility in West Texas. Request the interconnection through ERCOT, with AEP Texas as the transmission provider for the local connection.",
  },
  "AEP TEXAS NORTH COMPANY": {
    label: "AEP Texas North",
    note: "ERCOT transmission and distribution utility in West Texas. Request the interconnection through ERCOT, with AEP Texas as the transmission provider for the local connection.",
  },
  "TEXAS-NEW MEXICO POWER CO.": {
    label: "Texas-New Mexico Power",
    note: "ERCOT transmission and distribution utility. Request the interconnection through ERCOT.",
  },
  "TEXAS NEW MEXICO POWER": {
    label: "Texas-New Mexico Power",
    note: "ERCOT transmission and distribution utility. Request the interconnection through ERCOT.",
  },
  "SOUTHWESTERN PUBLIC SERVICE CO.": {
    label: "Southwestern Public Service (Xcel Energy)",
    note: "Southwest Power Pool utility, outside ERCOT. A generator here interconnects through SPP, not the ERCOT queue.",
  },
  "SOUTHWESTERN PUBLIC SERVICE CO": {
    label: "Southwestern Public Service (Xcel Energy)",
    note: "Southwest Power Pool utility, outside ERCOT. A generator here interconnects through SPP, not the ERCOT queue.",
  },
  "XCEL ENERGY": {
    label: "Xcel Energy",
    note: "Parent of Southwestern Public Service, the Southwest Power Pool utility on the northern edge of the basin. Treat the request as an SPP interconnection, not ERCOT, and confirm the operating company.",
  },
  "LOWER COLORADO RIVER AUTHORITY": {
    label: "Lower Colorado River Authority",
    note: "Transmission service is provided by LCRA Transmission Services Corporation, an ERCOT transmission provider. Request the interconnection through ERCOT.",
  },
  "SHARYLAND UTILITIES LP": {
    label: "Sharyland Utilities",
    note: "ERCOT transmission and distribution utility named on the line archive. Confirm the owner is still Sharyland before filing.",
  },
  "TXU POWER OR TXU ELECTRIC DELIVERY": {
    label: "Oncor Electric Delivery (listed as TXU)",
    note: "The line record still says TXU Electric Delivery, the former name of Oncor. File the interconnection with Oncor through ERCOT.",
  },
  "LEA COUNTY ELECTRIC COOP, INC": {
    label: "Lea County Electric Cooperative",
    note: "Electric cooperative based in New Mexico, and it also holds a Texas certificate. Request a tie to this line from the cooperative. Do not assume the bus is in ERCOT.",
  },
  "LEA COUNTY ELECTRIC COOPERATIVE": {
    label: "Lea County Electric Cooperative",
    note: "Electric cooperative based in New Mexico, and it also holds a Texas certificate. Request a tie to this line from the cooperative. Do not assume the bus is in ERCOT.",
  },
};

function ownerLabel(name) {
  if (name !== name.toUpperCase()) return name;
  return name.toLowerCase().replace(/\b([a-z])/g, (letter) => letter.toUpperCase());
}

function ownerProfile(name) {
  const known = OWNER_NOTES[name];
  if (known) return known;
  if (/COOP|COOPERATIVE/i.test(name || "")) {
    return {
      label: ownerLabel(name),
      note: "Electric cooperative. Request a connection to this line from the cooperative. A higher-voltage bus at the same site can belong to a different transmission provider, and that provider's process applies to that bus.",
    };
  }
  return {
    label: ownerLabel(name),
    note: "Named on a transmission line within half a mile. Confirm the current owner before filing an interconnection request.",
  };
}

function namedOwners(props) {
  return (props.owners || []).filter((row) => row.name && row.name !== "NOT AVAILABLE");
}

function mergedOwners(props) {
  const byLabel = new Map();
  namedOwners(props).forEach((row) => {
    const profile = ownerProfile(row.name);
    let entry = byLabel.get(profile.label);
    if (!entry) {
      entry = {
        label: profile.label,
        note: profile.note,
        voltages_kv: [],
        miles: row.miles,
      };
      byLabel.set(profile.label, entry);
    }
    row.voltages_kv.forEach((kv) => {
      if (!entry.voltages_kv.includes(kv)) entry.voltages_kv.push(kv);
    });
    entry.miles = Math.min(entry.miles, row.miles);
  });
  const target = props.max_kv || 0;
  const rows = [...byLabel.values()];
  rows.forEach((row) => row.voltages_kv.sort((a, b) => b - a));
  rows.sort((a, b) => {
    const aMatch = a.voltages_kv.some((kv) => kv >= target) ? 1 : 0;
    const bMatch = b.voltages_kv.some((kv) => kv >= target) ? 1 : 0;
    const aCoop = /coop/i.test(a.label) ? 1 : 0;
    const bCoop = /coop/i.test(b.label) ? 1 : 0;
    return bMatch - aMatch
      || Math.max(...b.voltages_kv) - Math.max(...a.voltages_kv)
      || aCoop - bCoop
      || a.miles - b.miles;
  });
  return rows;
}

function voltageList(values) {
  if (values.length === 1) return `${values[0]} kV`;
  if (values.length === 2) return `${values[0]} and ${values[1]} kV`;
  return `${values.slice(0, -1).join(", ")}, and ${values[values.length - 1]} kV`;
}

function distanceText(miles) {
  if (miles <= 0.05) return "at the site";
  return `${miles.toFixed(2)} miles away`;
}

function voltageSpan(props) {
  if (props.min_kv && props.max_kv && props.min_kv !== props.max_kv) {
    return `${props.min_kv}–${props.max_kv} kV`;
  }
  if (props.max_kv) return `${props.max_kv} kV`;
  return "Voltage not published";
}

function poiTooltip(props) {
  const owners = mergedOwners(props);
  const owner = owners[0] || null;
  const others = owners.slice(1);
  const blank = (props.owners || []).filter((row) => row.name === "NOT AVAILABLE");
  const place = [props.city, `${props.county} County`, props.state].filter(Boolean).join(", ");
  const corroborated = owners.some((row) => row.voltages_kv.some((kv) => kv >= (props.max_kv || 0)));
  const lines = [];
  lines.push(`<strong>${esc(props.name)}</strong>`);
  lines.push(`${esc(props.type)} · ${esc(props.status)}`);
  lines.push(esc(place));
  lines.push(`<b>${esc(voltageSpan(props))}</b>`);
  if (props.line_count > 0) {
    lines.push(`Station record lists ${props.line_count} line${props.line_count === 1 ? "" : "s"}.`);
  }
  if (props.max_inferred && !corroborated) {
    lines.push("Highest voltage was inferred, not taken from a nameplate.");
  }

  lines.push('<span class="label">Owner</span>');
  if (owner) {
    lines.push(`<b>${esc(owner.label)}</b> · ${esc(voltageList(owner.voltages_kv))}, ${distanceText(owner.miles)}`);
    lines.push(`<span class="role">${esc(owner.note)}</span>`);
  } else {
    lines.push("No transmission line within half a mile names an owner.");
  }
  blank.forEach((row) => {
    lines.push(`A ${esc(voltageList(row.voltages_kv))} line is ${distanceText(row.miles)}, and the line record does not name its owner.`);
  });

  if (others.length) {
    lines.push('<span class="label">Other lines within half a mile</span>');
    others.forEach((row) => {
      lines.push(`<b>${esc(row.label)}</b> · ${esc(voltageList(row.voltages_kv))}, ${distanceText(row.miles)}`);
    });
  }

  const circuits = [];
  const seenCircuits = new Set();
  (props.circuits || []).forEach((circuit) => {
    const ends = [circuit.from_name, circuit.to_name].filter(Boolean).join(" to ");
    if (!ends) return;
    const who = circuit.owner && circuit.owner !== "NOT AVAILABLE" ? `${ownerProfile(circuit.owner).label}, ` : "";
    const text = `${who}${ends}, ${circuit.voltage_kv} kV`;
    if (seenCircuits.has(text)) return;
    seenCircuits.add(text);
    circuits.push(text);
  });
  if (circuits.length) {
    lines.push('<span class="label">Named line ends</span>');
    circuits.slice(0, 3).forEach((text) => lines.push(esc(text)));
  }

  const tie = [];
  if (props.type === "Tap") {
    tie.push("This is a tap on a line, not a substation bus. The owner may still require a new switching station before a generator can connect.");
  }
  if (props.status === "Under construction") {
    tie.push("The station record says this site is under construction.");
  }
  if (owner) {
    const ownerMax = Math.max(...owner.voltages_kv);
    if (props.max_kv && ownerMax + 1 < props.max_kv) {
      tie.push(`The station record lists ${props.max_kv} kV, while lines within half a mile top out at ${ownerMax} kV.`);
    }
    tie.push(`A gen-tie lands on a bus here, usually at ${voltageSpan(props)}, unless the interconnection study assigns a different voltage.`);
  } else {
    tie.push(`Published voltage is ${voltageSpan(props)}. The filing counterparty is not identified on this map.`);
  }
  tie.push("The study decides whether the bus can take the injection. This point is not a signed interconnection and it does not show remaining capacity.");
  lines.push('<span class="label">Tying in</span>');
  lines.push(tie.join(" "));
  return lines.join("<br>");
}

function bindToggle(id, key) {
  document.getElementById(id).addEventListener("change", (event) => {
    const layer = layers[key];
    if (!layer) return;
    if (event.target.checked) layer.addTo(map);
    else map.removeLayer(layer);
  });
}

bindToggle("show-leases", "leases");
bindToggle("show-pipes", "pipes");
bindToggle("show-pois", "pois");
bindToggle("show-tieins", "tieins");
bindToggle("show-grid", "grid");

document.getElementById("show-hubs").addEventListener("change", (event) => {
  showHubs = event.target.checked;
  if (layers.pipes) layers.pipes.setStyle(pipeStyle);
  if (layers.pipes) {
    layers.pipes.eachLayer((layer) => {
      if (layer.feature) layer.setPopupContent(pipePopup(layer.feature.properties));
    });
  }
  paintHubLegend();
});

async function loadJson(url) {
  const response = await fetch(url);
  if (!response.ok) throw new Error(url);
  return response.json();
}

function clearMap() {
  Object.values(layers).forEach((layer) => map.removeLayer(layer));
  for (const key of Object.keys(layers)) delete layers[key];
  document.getElementById("ranking").replaceChildren();
}

async function showRegion(base) {
  clearMap();
  const [summary, counties, pipelines, transmission, tieins, leases, pois] = await Promise.all([
    loadJson(`${base}/summary.json`),
    loadJson(`${base}/counties.geojson`),
    loadJson(`${base}/pipelines.geojson`),
    loadJson(`${base}/transmission.geojson`),
    loadJson(`${base}/tieins.geojson`),
    loadJson(`${base}/leases.geojson`),
    loadJson(`${base}/pois.geojson`),
  ]);

  document.getElementById("kicker").textContent = summary.kicker || "Texas Permian";
  document.getElementById("title").textContent = summary.title || "Vented and flared gas by lease";
  showHubPrice(base);
  document.getElementById("headline").textContent = summary.headline || (
    `${summary.flared_mmcfd.toLocaleString()} MMcfd filed on ${summary.leases.toLocaleString()} leases with a surface well ` +
    `(${summary.oil_leases.toLocaleString()} oil leases and ${summary.gas_wells.toLocaleString()} gas wells). ` +
    `Circle size follows that filing. A few leases are far above the rest.`
  );

  document.getElementById("method").textContent = summary.method || (
    "Volumes are the vented-or-flared column on the Railroad Commission Form PR tapes posted September 26, 2026. " +
    "The tape still has one column for that disposition. It does not split flare (code 10) from vent (code 11). " +
    "Each lease is its latest month on the tape, which is July 2026 for most leases. " +
    "MMcfd is that month's Mcf divided by the days in the month, then by 1,000. " +
    "The circle is the centroid of RRC surface wells on that lease, from the well layer posted the same day, joined through the September 23 API extract. " +
    "A well is kept only when the lease name on the API record matches the name on the production filing. " +
    "Pipelines are the EIA centerline compilation from January 2020. " +
    "A tie-in point is the midpoint of a public 230 kV-or-higher line within 3 miles of a gas-pipeline midpoint, thinned to the highest voltage in each roughly 15-mile cell. It is not a signed interconnect. " +
    "This view is the Texas side of the basin. New Mexico is not in these filings. " +
    "Points of interconnection are substations and taps of 69 kV and above inside these counties. " +
    "Locations are a public republish of the former HIFLD Open substation layer, hosted by ccs3543_ut_austin and updated December 1, 2025, not a current DHS map. " +
    "The owner is the utility named on an in-service transmission line of 69 kV or higher within half a mile, from the Esri archive of U.S. Electric Power Transmission Lines, last data update September 30, 2024. " +
    "Where that archive still says TXU Electric Delivery, the utility is now Oncor. " +
    "The hover text is not a hosting-capacity study and not a signed interconnection. " +
    "Counties drawn: " + summary.counties.join(", ") + "."
  );

  const ranking = document.getElementById("ranking");
  (summary.top || []).forEach((row) => {
    const item = document.createElement("li");
    const button = document.createElement("button");
    button.type = "button";
    const place = row.county ? `${row.county} County` : (row.district ? `${row.district} District` : "");
    button.innerHTML = `<b>${row.flared_mmcfd.toFixed(2)} MMcfd</b> ${row.lease_name}<br><span class="meta">${place}${place ? " · " : ""}${row.period}</span>`;
    button.addEventListener("click", () => {
      map.setView([row.lat, row.lon], 11);
      map.panBy([-190, 40], { animate: false });
      const circle = leaseByKey.get(`${row.district}|${row.lease_no}`);
      if (circle) circle.openPopup();
    });
    item.appendChild(button);
    ranking.appendChild(item);
  });

  layers.counties = L.geoJSON(counties, {
    style: { color: "#8d8376", weight: 1, fillColor: "#f7f1e6", fillOpacity: 0.35 },
  }).addTo(map);
  if (counties.features && counties.features.length) {
    map.fitBounds(layers.counties.getBounds(), {
      paddingTopLeft: [410, 24],
      paddingBottomRight: [230, 24],
    });
  }

  layers.grid = L.geoJSON(transmission, {
    style: { color: "#8aa0b8", weight: 1.4, opacity: 0.9 },
    onEachFeature(feature, layer) {
      const props = feature.properties;
      layer.bindPopup(`<b>${props.voltage_kv} kV</b><br>${props.owner || "Owner not named"}`);
    },
  });

  currentPipes = pipelines.features || [];
  layers.pipes = L.geoJSON(pipelines, {
    style: pipeStyle,
    onEachFeature(feature, layer) {
      layer.bindPopup(pipePopup(feature.properties));
    },
  }).addTo(map);
  paintHubLegend();

  layers.pois = L.geoJSON(pois, {
    pointToLayer(feature, latlng) {
      const kv = feature.properties.max_kv || 0;
      const size = kv >= 345 ? 14 : kv >= 230 ? 12 : 10;
      const color = poiColor(kv);
      return L.marker(latlng, {
        icon: L.divIcon({
          className: "poi-marker",
          html: `<div style="width:${size}px;height:${size}px;background:${color};border:2px solid #fff;border-radius:50%;box-shadow:0 0 0 1px ${color}"></div>`,
          iconSize: [size + 2, size + 2],
          iconAnchor: [(size + 2) / 2, (size + 2) / 2],
        }),
        zIndexOffset: kv,
      });
    },
    onEachFeature(feature, layer) {
      const html = poiTooltip(feature.properties);
      layer.bindTooltip(html, {
        className: "poi-tip",
        direction: "auto",
        opacity: 1,
      });
      layer.bindPopup(html, { maxWidth: 320 });
    },
  }).addTo(map);

  layers.tieins = L.geoJSON(tieins, {
    pointToLayer(feature, latlng) {
      return L.marker(latlng, {
        icon: L.divIcon({
          className: "",
          html: '<div style="width:9px;height:9px;background:#143d66;border:2px solid #fff;transform:rotate(45deg);box-shadow:0 0 0 1px #143d66"></div>',
          iconSize: [13, 13],
          iconAnchor: [6, 6],
        }),
      });
    },
    onEachFeature(feature, layer) {
      const props = feature.properties;
      layer.bindPopup(
        `<b>Grid tie-in point</b><br>${props.voltage_kv} kV, ${props.owner || "owner not named"}<br>` +
        `${props.distance_miles} miles from a ${props.pipeline_operator || "gas"} line midpoint`
      );
    },
  }).addTo(map);

  const leaseByKey = new Map();
  const features = leases.features || [];
  const fields = features.filter((feature) => {
    const kind = feature.geometry && feature.geometry.type;
    return kind === "Polygon" || kind === "MultiPolygon";
  });
  const points = features.filter((feature) => feature.geometry && feature.geometry.type === "Point");
  leaseIndex = points.map((feature) => {
    const [lon, lat] = feature.geometry.coordinates;
    const value = feature.properties.flared_mmcfd;
    const circle = L.circle([lat, lon], {
      radius: Math.min(14000, Math.max(350, 700 * Math.sqrt(value))),
      color: "#4a2a22",
      weight: 0.6,
      fillColor: flareColor(value),
      fillOpacity: 0.78,
    });
    circle.bindPopup(leasePopup(feature.properties));
    const props = feature.properties;
    leaseByKey.set(`${props.district}|${props.lease_no}`, circle);
    return circle;
  });
  layers.leases = L.layerGroup(leaseIndex);
  if (fields.length) {
    layers.leases.addLayer(L.geoJSON({ type: "FeatureCollection", features: fields }, {
      style(feature) {
        const value = feature.properties.flared_mmcfd;
        return {
          color: "#4a2a22",
          weight: 1,
          fillColor: flareColor(value),
          fillOpacity: 0.72,
        };
      },
      onEachFeature(feature, layer) {
        layer.bindPopup(leasePopup(feature.properties));
        const props = feature.properties;
        leaseByKey.set(`${props.district}|${props.lease_no}`, layer);
      },
    }));
  }
  layers.leases.addTo(map);
  const leaseLabel = document.getElementById("show-leases").nextSibling;
  if (leaseLabel) leaseLabel.textContent = summary.lease_unit === "field" ? " Fields" : " Leases";
  document.getElementById("ranking-title").textContent = summary.lease_unit === "field"
    ? "Largest fields"
    : "Largest filings";

  ["show-leases", "show-pipes", "show-pois", "show-tieins"].forEach((id) => {
    document.getElementById(id).checked = true;
  });
  document.getElementById("show-grid").checked = false;
}

async function main() {
  try {
    hubCatalog = await loadJson("data/hubs.json");
  } catch (error) {
    console.error(error);
  }
  hubById = Object.fromEntries((hubCatalog.hubs || []).map((hub) => [hub.id, hub]));
  let catalog = {
    default: "permian",
    regions: [{ id: "permian", label: "Texas Permian", path: "data" }],
  };
  try {
    catalog = await loadJson("data/regions.json");
  } catch (error) {
    console.error(error);
  }
  const select = document.getElementById("region");
  catalog.regions.forEach((region) => {
    const option = document.createElement("option");
    option.value = region.path;
    option.textContent = region.label;
    if (region.id === catalog.default) option.selected = true;
    select.appendChild(option);
  });
  select.addEventListener("change", () => {
    showRegion(select.value).catch((error) => {
      const chosen = select.selectedOptions[0];
      document.getElementById("kicker").textContent = chosen ? chosen.textContent : "";
      document.getElementById("title").textContent = "Vented and flared gas";
      document.getElementById("headline").textContent = "This region has not been published yet.";
      console.error(error);
    });
  });
  const initial = catalog.regions.find((region) => region.id === catalog.default) || catalog.regions[0];
  await showRegion(initial.path);
}

main().catch((error) => {
  document.getElementById("headline").textContent = "The map data did not load.";
  console.error(error);
});
