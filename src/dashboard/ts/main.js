// --- State ---
let map;
let floodLayer = null;
let hazardLayer = null;
let routesLayer = null;
let habitationsLayer = null;
let customRouteLayer = null;
let dynamicRouteLayer = null;
let selectedHabitation = null;

let boundsData = {};
let needsData = {};
let resourcesData = [];
let scenarioData = {};
let graphGeoJSON = {};
let graphData = {}; // Contains nodes and edges for Dijkstra
let bridgesLayer = null;
let bridgesGeoJSON = {};
let habsGeoJSON = {};
let hospitalsLayer = null;
let hospitalsGeoJSON = {};
let policeLayer = null;
let policeGeoJSON = {};
let basesLayer = null;

const state = {
    currentTime: '22jul',
    showHazard: true,
    showRoutes: true,
    showHospitals: true,
    showPolice: true,
    showBases: true,
    currentDate: null,
    blockedEdgeIds: [],
    customRouteTarget: null,
    activeRouteType: null,
    activeRouteArgs: null
};

function isEdgeBlocked(edgeId) {
    return state.blockedEdgeIds.includes(edgeId) || 
           state.blockedEdgeIds.some(bId => edgeId.startsWith(bId + '_'));
}

// --- Initialization ---
async function init() {
    initMap();
    await loadData();
    setupEventListeners();
    updateDashboard();
}

function initMap() {
    // Dhemaji / Jonai general center
    map = L.map('map').setView([27.77, 95.16], 11);
    
    // Dark base map for command center feel
    L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Dark_Gray_Base/MapServer/tile/{z}/{y}/{x}', {
        attribution: 'Tiles &copy; Esri &mdash; Esri, DeLorme, NAVTEQ',
    }).addTo(map);
}

async function loadData() {
    try {
        const [boundsRes, resRes, scenRes, graphGeoRes, graphDataRes, habsRes, bridgesRes, hospRes, policeRes] = await Promise.all([
            fetch('../../public/overlays/bounds.json?v=1790174961'),
            fetch('../../public/data/resources.json?v=1790174961'),
            fetch('../../public/data/optimization_scenario.json?v=1790174961'),
            fetch('../../public/geojson/roads.geojson?v=1790174961'),
            fetch('../../public/data/graph.json?v=1790174961'),
            fetch('../../public/geojson/habitations.geojson?v=1790174961'),
            fetch('../../public/geojson/bridges.geojson?v=1790174961'),
            fetch('../../public/geojson/hospitals.geojson?v=1790174961'),
            fetch('../../public/geojson/police.geojson?v=1790174961')
        ]);
        
        boundsData = await boundsRes.json();
        resourcesData = await resRes.json();
        scenarioData = await scenRes.json();
        graphGeoJSON = await graphGeoRes.json();
        graphData = await graphDataRes.json();
        habsGeoJSON = await habsRes.json();
        bridgesGeoJSON = await bridgesRes.json();
        
        try { hospitalsGeoJSON = await hospRes.json(); } catch(e) {}
        try { policeGeoJSON = await policeRes.json(); } catch(e) {}
        
        // Draw Bridges
        bridgesLayer = L.geoJSON(bridgesGeoJSON, {
            pointToLayer: (feature, latlng) => {
                let nearestEdgeId = null;
                let minDist = Infinity;
                if (graphGeoJSON.features) {
                    graphGeoJSON.features.forEach(edge => {
                        edge.geometry.coordinates.forEach(coord => {
                            const d = Math.pow(coord[0] - latlng.lng, 2) + Math.pow(coord[1] - latlng.lat, 2);
                            if (d < minDist) { minDist = d; nearestEdgeId = edge.properties.id; }
                        });
                    });
                }
                
                const marker = L.circleMarker(latlng, {
                    radius: 6,
                    fillColor: '#d2b48c',
                    color: '#8b5a2b',
                    weight: 1.5,
                    opacity: 1,
                    fillOpacity: 0.9
                }).bindTooltip("Bridge ID: " + feature.properties.id);
                
                // Add popup that passes the nearest road edge ID to the toggle function
                marker.on('click', () => {
                    const isBlocked = isEdgeBlocked(nearestEdgeId);
                    const btnText = isBlocked ? "Unblock Bridge" : "Block Bridge";
                    const btnClass = isBlocked ? "secondary-btn" : "danger-btn";
                    const popupContent = `
                        <div style="min-width: 150px; text-align: center;">
                            <h4 style="margin: 0 0 5px 0;">Bridge ${feature.properties.id}</h4>
                            <div style="font-size: 0.8rem; margin-bottom: 10px;">Road Segment: ${nearestEdgeId}</div>
                            <button onclick="window.toggleRoadBlock('${nearestEdgeId}'); map.closePopup();" class="${btnClass}" style="width: 100%; padding: 5px;">${btnText}</button>
                        </div>
                    `;
                    marker.bindPopup(popupContent).openPopup();
                });
                
                return marker;
            }
        }).addTo(map);
        
        // Load initial needs
        await fetchNeedsForDate(state.currentTime);
        
        // Populate custom routing dropdowns
        populateDropdowns();
        
        // Draw Habitations & Facilities
        drawHabitations();
        drawFacilities();

    } catch (e) {
        console.error("Error loading data", e);
    }
}

async function fetchNeedsForDate(dateKey) {
    try {
        const res = await fetch(`../../public/data/needs_${dateKey}.json`);
        needsData = await res.json();
    } catch (e) {
        console.error(`Error loading needs for ${dateKey}`, e);
    }
}

function populateDropdowns() {
    const sourceSelect = document.getElementById('route-source');
    const destSelect = document.getElementById('route-dest');
    const evacSelect = document.getElementById('evac-source');
    
    if (!sourceSelect || !destSelect) return;
    
    sourceSelect.innerHTML = '';
    destSelect.innerHTML = '';
    if (evacSelect) evacSelect.innerHTML = '';
    
    window.evacuateFromPopup = function(sourceName) {
        const evacSelect = document.getElementById('evac-source');
        if (evacSelect) evacSelect.value = sourceName;
        calculateEvacuationRoute(sourceName);
        map.closePopup();
    };
    const baseName = 'Jonai Response Base';
    sourceSelect.appendChild(new Option(baseName, baseName));
    destSelect.appendChild(new Option(baseName, baseName));
    
    // Add all habitations
    const habsList = habsGeoJSON.features || [];
    habsList.forEach(hab => {
        const name = hab.properties.name;
        sourceSelect.appendChild(new Option(name, name));
        destSelect.appendChild(new Option(name, name));
        if (evacSelect) evacSelect.appendChild(new Option(name, name));
    });
    
    // Add Hospitals
    if (hospitalsGeoJSON.features) {
        hospitalsGeoJSON.features.forEach(h => {
            const name = h.properties.name || 'Hospital';
            sourceSelect.appendChild(new Option(name, name));
            destSelect.appendChild(new Option(name, name));
        });
    }
    
    // Add Police Stations
    if (policeGeoJSON.features) {
        policeGeoJSON.features.forEach(p => {
            const name = p.properties.name || p.properties.NAME || 'Police Station';
            sourceSelect.appendChild(new Option(name, name));
            destSelect.appendChild(new Option(name, name));
        });
    }
    
    // Set default selection
    if (sourceSelect.options[1]) sourceSelect.selectedIndex = 1; // Bahir Sille (first hab)
    if (destSelect.options[4]) destSelect.selectedIndex = 4;     // Rayang (another hab)
    if (evacSelect && evacSelect.options[0]) evacSelect.selectedIndex = 0;
}

function drawHabitations() {
    if (habitationsLayer) {
        map.removeLayer(habitationsLayer);
    }
    
    habitationsLayer = L.geoJSON(habsGeoJSON, {
        pointToLayer: (feature, latlng) => {
            const status = feature.properties.status[state.currentTime];
            const hazard = status ? status.hazard_class : 1;
            const pop = status ? status.affected_pop : 0;
            
            const color = hazard === 4 ? '#dc143c' : 
                          hazard === 3 ? '#ff8c00' : 
                          hazard === 2 ? '#ffd700' : '#228b22';
                          
            const marker = L.circleMarker(latlng, {
                radius: 9,
                fillColor: color,
                color: '#fff',
                weight: 2,
                opacity: 1,
                fillOpacity: 0.85
            });
            
            // Generate detailed breakdown popup
            const habNeed = (needsData.habitations || []).find(n => n.habitation === feature.properties.name);
            let popupContent = `<b>${feature.properties.name}</b><br>`;
            
            if (habNeed && status && status.hazard_class >= 2) {
                const q = habNeed.quantitative_needs;
                let floodDepthStr = "~0.5m - 1.0m";
                if (habNeed.hazard_class === 3) floodDepthStr = "~1.0m - 2.0m";
                if (habNeed.hazard_class === 4) floodDepthStr = "> 2.0m (Severe)";
                
                popupContent += `
                    <div style="font-size: 0.85rem; margin-top: 5px; line-height: 1.4;">
                        <strong>Hazard Class:</strong> <span class="hazard-${habNeed.hazard_class}">${habNeed.hazard_class === 4 ? 'Red (Critical)' : habNeed.hazard_class === 3 ? 'Orange (High)' : 'Yellow (Moderate)'}</span><br>
                        <strong>Est. Flood Depth:</strong> ${floodDepthStr}<br>
                        <strong>Affected Population:</strong> ${habNeed.affected_population.toLocaleString()} / ${feature.properties.population.toLocaleString()}<br>
                        <strong>Est. Children:</strong> ${habNeed.children_est.toLocaleString()}<br>
                        <hr style="margin: 5px 0; border: 0; border-top: 1px solid #ddd;">
                        <strong>Estimated Daily Needs:</strong><br>
                        • Rice/Dal: ${q.food_kg.toLocaleString()} kg (0.5 kg/person)<br>
                        • Clean Water: ${q.water_liters.toLocaleString()} L (3 L/person)<br>
                        • Medical Teams: ${q.medical_teams} (1 per 500)<br>
                        • Rescue Boats: ${q.boats} (capacity 20, 5 trips/day)<br>
                        <strong>Accessibility:</strong> ${habNeed.accessibility}
                    </div>
                    <div style="margin-top: 8px;">
                        <button onclick="window.evacuateFromPopup('${feature.properties.name.replace(/'/g, "\\'")}')" class="primary-btn" style="padding: 4px 8px; font-size: 0.8rem; width: 100%;">[Evacuate to Nearest Safe Area]</button>
                        <button onclick="window.allocateDynamicPopup('${feature.properties.name.replace(/'/g, "\\'")}')" class="secondary-btn" style="padding: 4px 8px; font-size: 0.8rem; width: 100%; margin-top: 5px;">[Check Logistics & Accessibility Route]</button>
                    </div>
                `;
            } else {
                popupContent += `Population: ${feature.properties.population.toLocaleString()}<br><br><span style="color:#228b22;">Currently Safe (No Active Flood)</span>`;
            }
            
            marker.on('click', () => {
                if (window.selectHabitation) {
                    window.selectHabitation(feature.properties.name);
                }
            });
            return marker.bindPopup(popupContent);
        }
    }).addTo(map);
}

function drawFacilities() {
    if (hospitalsLayer) map.removeLayer(hospitalsLayer);
    if (policeLayer) map.removeLayer(policeLayer);
    if (basesLayer) map.removeLayer(basesLayer);
    
    if (state.showBases && graphData && graphData.nodes) {
        const baseNodes = graphData.nodes.filter(n => n.type === 'base');
        basesLayer = L.layerGroup();
        baseNodes.forEach(n => {
            const latlng = [n.lat, n.lon];
            const name = n.name || 'Unknown';
            const marker = L.circleMarker(latlng, {
                radius: 10,
                fillColor: '#800080', // Purple
                color: '#ffffff',
                weight: 2,
                opacity: 1,
                fillOpacity: 1
            }).bindTooltip("Emergency Base: " + name)
              .bindPopup(window.buildFacilityPopup(name, 'Emergency Base'));
            basesLayer.addLayer(marker);
        });

        // Also draw shelters so they are visible
        const shelterNodes = graphData.nodes.filter(n => n.type === 'shelter');
        shelterNodes.forEach(n => {
            const latlng = [n.lat, n.lon];
            const name = n.name || 'Unknown';
            const marker = L.circleMarker(latlng, {
                radius: 9,
                fillColor: '#00ced1', // Cyan for shelter
                color: '#ffffff',
                weight: 2,
                opacity: 1,
                fillOpacity: 1
            }).bindTooltip("Relief Camp / Shelter: " + name)
              .bindPopup(window.buildFacilityPopup(name, 'Shelter'));
            basesLayer.addLayer(marker);
        });

        basesLayer.addTo(map);
    }
    
    if (state.showHospitals && hospitalsGeoJSON.features) {
        hospitalsLayer = L.geoJSON(hospitalsGeoJSON, {
            pointToLayer: (feature, latlng) => {
                const name = feature.properties.name || 'Unknown';
                return L.circleMarker(latlng, {
                    radius: 8,
                    fillColor: '#ffffff',
                    color: '#ff0000', // White with red border for hospitals
                    weight: 2,
                    opacity: 1,
                    fillOpacity: 1
                }).bindTooltip("Hospital: " + name)
                  .bindPopup(window.buildFacilityPopup(name, 'Hospital'));
            }
        }).addTo(map);
    }
    
    if (state.showPolice && policeGeoJSON.features) {
        policeLayer = L.geoJSON(policeGeoJSON, {
            pointToLayer: (feature, latlng) => {
                const name = feature.properties.name || feature.properties.NAME || 'Unknown';
                return L.circleMarker(latlng, {
                    radius: 8,
                    fillColor: '#0000ff', // Blue for police
                    color: '#ffffff',
                    weight: 2,
                    opacity: 1,
                    fillOpacity: 1
                }).bindTooltip("Police: " + name)
                  .bindPopup(window.buildFacilityPopup(name, 'Police'));
            }
        }).addTo(map);
    }
}

function setupEventListeners() {
    // Temporal controls
    document.querySelectorAll('.time-btn').forEach(btn => {
        btn.addEventListener('click', async (e) => {
            document.querySelectorAll('.time-btn').forEach(b => b.classList.remove('active'));
            const target = e.target;
            target.classList.add('active');
            state.currentTime = target.dataset.time || '22jul';
            
            await fetchNeedsForDate(state.currentTime);
            
            updateDashboard();
        });
    });
    
    // Checkboxes
    const toggleHazard = document.getElementById('toggle-hazard');
    if (toggleHazard) {
        toggleHazard.addEventListener('change', (e) => {
            state.showHazard = e.target.checked;
            updateHazardLayer();
        });
    }
    
    const toggleRoutes = document.getElementById('toggle-routes');
    if (toggleRoutes) {
        toggleRoutes.addEventListener('change', (e) => {
            state.showRoutes = e.target.checked;
            updateRoutesLayer();
        });
    }
    
    const toggleHosp = document.getElementById('toggle-hospitals');
    if (toggleHosp) {
        toggleHosp.addEventListener('change', (e) => {
            state.showHospitals = e.target.checked;
            drawFacilities();
        });
    }
    
    const togglePol = document.getElementById('toggle-police');
    if (togglePol) {
        togglePol.addEventListener('change', (e) => {
            state.showPolice = e.target.checked;
            drawFacilities();
        });
    }
    
    const toggleBases = document.getElementById('toggle-bases');
    if (toggleBases) {
        toggleBases.addEventListener('change', (e) => {
            state.showBases = e.target.checked;
            drawFacilities();
        });
    }
    
    // Removed manual input button logic, replaced with map click logic in window.toggleRoadBlock
    
    const btnReset = document.getElementById('btn-reset-road');
    if (btnReset) {
        btnReset.addEventListener('click', () => {
            state.blockedEdgeIds = [];
            document.getElementById('btn-reset-road').style.display = 'none';
            document.getElementById('scenario-metrics').style.display = 'none';
            
            const statusEl = document.getElementById('rec-status');
            if (statusEl) {
                statusEl.textContent = 'Optimal';
                statusEl.className = 'rec-row status-optimal';
            }
            
            updateRoutesLayer();
            retriggerActiveRoute();
        });
    }
    
    // Custom routing button
    const btnCustomRoute = document.getElementById('btn-calculate-custom-route');
    if (btnCustomRoute) {
        btnCustomRoute.addEventListener('click', () => {
            const srcVal = document.getElementById('route-source').value;
            const destVal = document.getElementById('route-dest').value;
            calculateCustomRoute(srcVal, destVal);
        });
    }
    
    // Evacuation button
    const btnEvacuate = document.getElementById('btn-evacuate');
    if (btnEvacuate) {
        btnEvacuate.addEventListener('click', () => {
            const srcVal = document.getElementById('evac-source').value;
            calculateEvacuationRoute(srcVal);
        });
    }
    
    // Facility routing buttons
    const btnHospital = document.getElementById('btn-hospital');
    if (btnHospital) {
        btnHospital.addEventListener('click', () => {
            const srcVal = document.getElementById('evac-source').value;
            calculateFacilityRoute(srcVal, 'hospital');
        });
    }
    
    const btnPolice = document.getElementById('btn-police');
    if (btnPolice) {
        btnPolice.addEventListener('click', () => {
            const srcVal = document.getElementById('evac-source').value;
            calculateFacilityRoute(srcVal, 'police');
        });
    }

    const btnAllocHospital = document.getElementById('btn-alloc-hospital');
    if (btnAllocHospital) {
        btnAllocHospital.addEventListener('click', () => {
            const dest = (state.activeRouteArgs && state.activeRouteArgs.dest) ? state.activeRouteArgs.dest : selectedHabitation;
            if (dest) calculateFacilityRoute(dest, 'hospital');
        });
    }

    const btnAllocPolice = document.getElementById('btn-alloc-police');
    if (btnAllocPolice) {
        btnAllocPolice.addEventListener('click', () => {
            const dest = (state.activeRouteArgs && state.activeRouteArgs.dest) ? state.activeRouteArgs.dest : selectedHabitation;
            if (dest) calculateFacilityRoute(dest, 'police');
        });
    }
}

window.selectHabitation = function(name) {
    selectedHabitation = name;
    
    if (dynamicRouteLayer) {
        map.removeLayer(dynamicRouteLayer);
        dynamicRouteLayer = null;
    }
    
    const allocContent = document.getElementById('alloc-content');
    const dynResults = document.getElementById('dynamic-allocation-results');
    
    if (dynResults) dynResults.style.display = 'none';
    if (allocContent) {
        allocContent.style.display = 'block';
        allocContent.innerHTML = `<p style="font-size: 0.9em; color: #00ffff;">Selected: <b>${name}</b></p><p style="font-size: 0.9em; color: #ccc;">Click the <b>[Check Logistics & Accessibility Route]</b> button in the map popup to calculate dynamic supply routes for this habitation.</p>`;
    }
};

window.clearAllocationSelection = function() {
    selectedHabitation = null;
    state.activeRouteType = null;
    state.activeRouteArgs = null;
    
    if (customRouteLayer) {
        map.removeLayer(customRouteLayer);
        customRouteLayer = null;
    }
    if (dynamicRouteLayer) {
        map.removeLayer(dynamicRouteLayer);
        dynamicRouteLayer = null;
    }
    
    const cMetrics = document.getElementById('custom-route-metrics');
    if (cMetrics) cMetrics.style.display = 'none';
    const eMetrics = document.getElementById('evac-metrics');
    if (eMetrics) eMetrics.style.display = 'none';
    
    const allocContent = document.getElementById('alloc-content');
    const dynResults = document.getElementById('dynamic-allocation-results');
    if (allocContent) allocContent.style.display = 'block';
    if (dynResults) dynResults.style.display = 'none';
    
    updateRoutesLayer();
};

window.routeFromBasePopup = function(destName) {
    const srcVal = 'Jonai Response Base';
    const sourceSelect = document.getElementById('route-source');
    const destSelect = document.getElementById('route-dest');
    if (sourceSelect) sourceSelect.value = srcVal;
    if (destSelect) destSelect.value = destName;
    
    calculateCustomRoute(srcVal, destName);
    map.closePopup();
};

window.allocateDynamicPopup = function(destName) {
    calculateDynamicAllocation(destName);
    map.closePopup();
};

window.buildFacilityPopup = function(name, type) {
    const resList = resourcesData.filter(r => 
        r.location === name || 
        r.original_location === name ||
        (type === 'Police' && r.location === 'Police Station')
    );
    let resHtml = '';
    if (resList.length > 0) {
        resHtml = '<strong>Available Resources:</strong><ul style="margin: 5px 0; padding-left: 20px;">';
        resList.forEach(r => {
            resHtml += `<li>${r.quantity} ${r.resource_type} (${r.purpose || 'N/A'})</li>`;
        });
        resHtml += '</ul>';
    } else {
        resHtml = '<div style="color: #888; font-size: 0.85em; font-style: italic;">No specific resources registered.</div>';
    }
    
    return `
        <div style="min-width: 180px;">
            <h4 style="margin: 0 0 8px 0; border-bottom: 1px solid #ccc; padding-bottom: 3px;">
                <span style="color: ${type === 'Hospital' ? '#ff0000' : type === 'Police' ? '#0000ff' : '#800080'};">${type}:</span> ${name}
            </h4>
            <div style="font-size: 0.85rem; margin-bottom: 8px;">
                ${resHtml}
            </div>
            <button onclick="window.routeFromFacilityPopup('${name.replace(/'/g, "\\'")}')" class="primary-btn" style="width: 100%; padding: 4px; font-size: 0.8rem;">Route to Selected Habitation</button>
        </div>
    `;
};

window.routeFromFacilityPopup = function(sourceName) {
    if (!selectedHabitation) {
        alert("Please select a target habitation on the map first!");
        return;
    }
    const sourceSelect = document.getElementById('route-source');
    const destSelect = document.getElementById('route-dest');
    
    if (sourceSelect) {
        let exists = Array.from(sourceSelect.options).some(opt => opt.value === sourceName);
        if (!exists) sourceSelect.appendChild(new Option(sourceName, sourceName));
        sourceSelect.value = sourceName;
    }
    if (destSelect) {
        destSelect.value = selectedHabitation;
    }
    
    calculateCustomRoute(sourceName, selectedHabitation);
    map.closePopup();
};

// Global function to allow popups to trigger state changes
window.toggleRoadBlock = function(id) {
    if (isEdgeBlocked(id)) {
        // Unblock
        state.blockedEdgeIds = state.blockedEdgeIds.filter(eId => eId !== id);
        
        if (state.blockedEdgeIds.length === 0) {
            const btnReset = document.getElementById('btn-reset-road');
            if (btnReset) btnReset.style.display = 'none';
            
            const statusEl = document.getElementById('alloc-status');
            if (statusEl) {
                statusEl.textContent = 'Network: Optimal Baseline';
                statusEl.className = 'rec-row status-optimal';
            }
        }
    } else {
        // Block
        state.blockedEdgeIds.push(id);
        
        const btnReset = document.getElementById('btn-reset-road');
        if (btnReset) btnReset.style.display = 'block';
        
        const statusEl = document.getElementById('alloc-status');
        if (statusEl) {
            statusEl.textContent = 'Road Blocked - Re-routed';
            statusEl.className = 'rec-row status-rerouted';
        }
    }
    
    // Refresh visual layers and recalculate active routes to avoid the block
    updateRoutesLayer();
    retriggerActiveRoute();
};

function retriggerActiveRoute() {
    if (state.activeRouteType === 'custom' && state.activeRouteArgs) {
        calculateCustomRoute(state.activeRouteArgs.src, state.activeRouteArgs.dest);
    } else if (state.activeRouteType === 'evacuation' && state.activeRouteArgs) {
        calculateEvacuationRoute(state.activeRouteArgs.src);
    } else if (state.activeRouteType === 'facility' && state.activeRouteArgs) {
        calculateFacilityRoute(state.activeRouteArgs.src, state.activeRouteArgs.type);
    } else if (state.activeRouteType === 'dynamic_allocation' && state.activeRouteArgs) {
        calculateDynamicAllocation(state.activeRouteArgs.dest);
    }
}

function updateDashboard() {
    updateFloodLayer();
    updateHazardLayer();
    updateRoutesLayer();
    drawHabitations(); // Re-draw markers based on current date
    
    // Update summary metrics
    const habsList = needsData.habitations || [];
    const agg = needsData.aggregate_needs || {food_kg: 0, water_liters: 0, boats: 0, medical_teams: 0};
    
    const totalHabs = habsList.filter(h => h.hazard_class >= 2).length;
    const totalPop = habsList.reduce((sum, n) => sum + n.affected_population, 0);
    
    document.getElementById('val-habitations').textContent = totalHabs.toString();
    document.getElementById('val-population').textContent = totalPop.toLocaleString();
    document.getElementById('val-food').textContent = agg.food_kg.toLocaleString();
    const waterEl = document.getElementById('val-water');
    if (waterEl) waterEl.textContent = agg.water_liters.toLocaleString();
    document.getElementById('val-boats').textContent = agg.boats.toString();
    
    // Update priority table
    const tbody = document.querySelector('#priority-table tbody');
    if (tbody) {
        tbody.innerHTML = '';
        habsList.slice(0, 5).forEach((n) => {
            const tr = document.createElement('tr');
            
            const hazardLabel = n.hazard_class === 4 ? 'Red' : 
                                n.hazard_class === 3 ? 'Orange' : 
                                n.hazard_class === 2 ? 'Yellow' : 'Green';
                                
            tr.innerHTML = `
                <td>${n.habitation}</td>
                <td class="hazard-${n.hazard_class}">${hazardLabel}</td>
                <td>${n.needs.rescue}</td>
            `;
            tbody.appendChild(tr);
        });
    }
    
    // Update Resource Strip
    const resContainer = document.getElementById('resource-container');
    if (resContainer) {
        resContainer.innerHTML = '';
        resourcesData.forEach((r) => {
            const item = document.createElement('div');
            item.className = 'resource-item';
            item.innerHTML = `
                <div class="res-type">${r.resource_type}</div>
                <div class="res-qty">${r.quantity}</div>
                <div class="res-loc">${r.location}</div>
            `;
            resContainer.appendChild(item);
        });
    }
    
    // Update Recommendation Card
    if (scenarioData && scenarioData.baseline) {
        document.getElementById('rec-target').textContent = scenarioData.mission.target;
        document.getElementById('rec-resource').textContent = scenarioData.mission.assigned_resource;
        document.getElementById('rec-time').textContent = scenarioData.baseline.estimated_time_hrs;
        document.getElementById('rec-dist').textContent = scenarioData.baseline.distance_km;
        
        document.getElementById('sim-dist').textContent = scenarioData.re_optimized.distance_km;
        document.getElementById('sim-time').textContent = scenarioData.re_optimized.estimated_time_hrs;
        document.getElementById('sim-delay').textContent = scenarioData.re_optimized.delay_hrs;
    }
}

function updateFloodLayer() {
    if (floodLayer) map.removeLayer(floodLayer);
    
    const timeMap = {
        '11jul': 'flood_baseline.png',
        '18jul': 'flood_onset.png',
        '22jul': 'flood_active.png',
        '28jul': 'flood_persistence.png'
    };
    
    const imgName = timeMap[state.currentTime];
    const b = boundsData[imgName.replace('.png', '.tif')];
    
    if (b) {
        const bounds = [b.southWest, b.northEast];
        floodLayer = L.imageOverlay(`../../public/overlays/${imgName}`, bounds, { opacity: 0.7 }).addTo(map);
    }
}

function updateHazardLayer() {
    if (hazardLayer) {
        map.removeLayer(hazardLayer);
        hazardLayer = null;
    }
    
    if (state.showHazard) {
        const hazardImg = `hazard_map_${state.currentTime}.png`;
        const b = boundsData[hazardImg.replace('.png', '.tif')];
        if (b) {
            const bounds = [b.southWest, b.northEast];
            hazardLayer = L.imageOverlay(`../../public/overlays/${hazardImg}`, bounds, { opacity: 0.6 }).addTo(map);
        }
    }
}

function updateRoutesLayer() {
    if (routesLayer) {
        map.removeLayer(routesLayer);
        routesLayer = null;
    }
    
    if (!state.showRoutes) return;
    
    const activeRouteEdges = state.blockedEdgeIds.length > 0 
        ? scenarioData.re_optimized.route_edges 
        : scenarioData.baseline.route_edges;
        
    const blockedEdge = scenarioData.disruption.blocked_edge_id;
    
    routesLayer = L.geoJSON(graphGeoJSON, {
        style: (feature) => {
            const id = feature?.properties?.id;
            
            if (isEdgeBlocked(id)) {
                return { color: '#000000', weight: 8, dashArray: '2, 8' }; // Blocked (Black dotted)
            }
            
            // Background graph
            return { color: '#555555', weight: 4, opacity: 0.4 }; 
        },
        onEachFeature: (feature, layer) => {
            if (feature.properties) {
                const id = feature.properties.id;
                const dist = parseFloat(feature.properties.distance_km || 0).toFixed(2);
                layer.bindTooltip(`Road ID: ${id}`);
                
                const isBlocked = isEdgeBlocked(id);
                const btnText = isBlocked ? "Unblock Road Segment" : "Block Road Segment";
                const btnClass = isBlocked ? "secondary-btn" : "danger-btn";
                
                const popupContent = `
                    <div style="min-width: 150px; text-align: center;">
                        <h4 style="margin: 0 0 5px 0;">Road Segment ${id}</h4>
                        <div style="font-size: 0.8rem; margin-bottom: 10px;">Distance: ${dist} km</div>
                        <button onclick="window.toggleRoadBlock('${id}')" class="${btnClass}" style="width: 100%; padding: 5px;">${btnText}</button>
                    </div>
                `;
                layer.bindPopup(popupContent);
            }
        }
    }).addTo(map);
}

  // --- Route GeoJSON Helper ---
    function buildRouteGeoJSON(pathEdges) {
      if (!pathEdges || pathEdges.length === 0) return { type: "FeatureCollection", features: [] };
      const coords = [];
      let lastNodeId = null;
      
      const edgesInOrder = [...pathEdges].reverse();

      edgesInOrder.forEach(id => {
          const edge = (graphData.edges || []).find(e => e.id === id);
          if (edge) {
              const srcNode = (graphData.nodes || []).find(n => n.id === edge.source);
              const tgtNode = (graphData.nodes || []).find(n => n.id === edge.target);
              if (srcNode && tgtNode) {
                  if (!lastNodeId || lastNodeId === srcNode.id) {
                      if (coords.length === 0) coords.push([srcNode.lon, srcNode.lat]);
                      coords.push([tgtNode.lon, tgtNode.lat]);
                      lastNodeId = tgtNode.id;
                  } else {
                      if (coords.length === 0) coords.push([tgtNode.lon, tgtNode.lat]);
                      coords.push([srcNode.lon, srcNode.lat]);
                      lastNodeId = srcNode.id;
                  }
              }
          }
      });

      return {
          type: "FeatureCollection",
          features: [{
              type: "Feature",
              properties: { id: "custom_route" },
              geometry: {
                  type: "LineString",
                  coordinates: coords
              }
          }]
      };
  }
  
  // --- JS Dijkstra Solver ---
  function calculateCustomRoute(sourceName, destName) {
    if (customRouteLayer) {
        map.removeLayer(customRouteLayer);
        customRouteLayer = null;
    }
    
    if (sourceName === destName) {
        alert("Source and Destination cannot be the same!");
        return;
    }
    
    state.activeRouteType = 'custom';
    state.activeRouteArgs = { src: sourceName, dest: destName };
    
    // Find nodes corresponding to the source and destination names
    const nodes = graphData.nodes || [];
    const edges = graphData.edges || [];
    
    const startNode = nodes.find(n => n.name === sourceName);
    const endNode = nodes.find(n => n.name === destName);
    
    if (!startNode || !endNode) {
        alert("Could not locate nodes in routing graph.");
        return;
    }
    
    // Dijkstra algorithm
    const dist = {};
    const prev = {};
    const pq = new PriorityQueue();
    
    nodes.forEach(n => {
        dist[n.id] = Infinity;
        prev[n.id] = null;
    });
    
    dist[startNode.id] = 0;
    pq.enqueue(startNode.id, 0);
    
    while (!pq.isEmpty()) {
        const { element: u_id } = pq.dequeue();
        
        if (u_id === endNode.id) break; // Reached target
        
        // Find adjacent edges
        const adj = [];
        edges.forEach(e => {
            if (isEdgeBlocked(e.id)) return; // Skip blocked edge
            
            if (e.source === u_id) adj.push({ target: e.target, weight: e.distance_km, edge_id: e.id });
            if (e.target === u_id) adj.push({ target: e.source, weight: e.distance_km, edge_id: e.id });
        });
        
        adj.forEach(({ target: v_id, weight, edge_id }) => {
            const alt = dist[u_id] + weight;
            if (alt < dist[v_id]) {
                dist[v_id] = alt;
                prev[v_id] = { node: u_id, edge: edge_id };
                pq.enqueue(v_id, alt);
            }
        });
    }
    
    if (dist[endNode.id] === Infinity) {
        alert("No path exists between these two locations!");
        return;
    }
    
    // Reconstruct path
    const pathEdges = [];
    let curr = endNode.id;
    
    while (prev[curr]) {
        const step = prev[curr];
        pathEdges.push(step.edge);
        curr = step.node;
    }
    
    const routeGeoJSON = buildRouteGeoJSON(pathEdges);
    
    updateRoutesLayer();
    
    // Draw Custom Route Polyline on map
    customRouteLayer = L.geoJSON(routeGeoJSON, {
        style: {
            color: '#ff8c00', // Distinct Orange
            weight: 7,
            dashArray: '10, 10',
            opacity: 0.9
        }
    }).addTo(map);
    
    // Fit map bounds to custom route
    if (routeGeoJSON.features.length > 0) {
        map.fitBounds(customRouteLayer.getBounds());
    }
    
    // Calculate custom metrics
    const totalDist = dist[endNode.id];
    
    // Detect transport mode based on hazard levels along the path
    // We check the hazard class of both endpoints for simplicity in the frontend
    const srcNeed = (needsData.habitations || []).find(n => n.habitation === sourceName);
    const destNeed = (needsData.habitations || []).find(n => n.habitation === destName);
    const maxHazard = Math.max(
        srcNeed ? srcNeed.hazard_class : 1,
        destNeed ? destNeed.hazard_class : 1
    );
    
    let speed = 25.0; // Ground transport speed
    let transportMode = "Jeep / Ground Relief Truck";
    
    if (maxHazard === 4) {
        speed = 50.0; // Air speed
        transportMode = "Helicopter Air-drop (Critical Red Zone)";
    } else if (maxHazard === 3) {
        speed = 12.0; // Boat speed
        transportMode = "Motorised Rescue Boat (IRB / Submerged Routes)";
    }
    
    const estTime = totalDist / speed;
    
    // Update custom UI elements
    document.getElementById('custom-route-dist').textContent = totalDist.toFixed(2);
    document.getElementById('custom-route-time').textContent = estTime.toFixed(2);
    document.getElementById('custom-route-mode').textContent = transportMode;
    document.getElementById('custom-route-metrics').style.display = 'block';
}

function calculateEvacuationRoute(sourceName) {
    if (customRouteLayer) {
        map.removeLayer(customRouteLayer);
        customRouteLayer = null;
    }
    
    state.activeRouteType = 'evacuation';
    state.activeRouteArgs = { src: sourceName };
    
    const nodes = graphData.nodes || [];
    const edges = graphData.edges || [];
    const startNode = nodes.find(n => n.name === sourceName);
    
    if (!startNode) {
        alert("Source not found in routing graph.");
        return;
    }
    
    // Find all safe destinations (habitations/shelters/bases with hazard_class == 1)
    const safeDests = [];
    nodes.forEach(n => {
        if (n.type === 'habitation' || n.type === 'shelter' || n.type === 'base') {
            // Check if it's currently safe
            const habStatus = (needsData.habitations || []).find(h => h.habitation === n.name);
            const hazard = habStatus ? habStatus.hazard_class : 1;
            if (hazard === 1 && n.name !== sourceName) {
                safeDests.push(n);
            }
        }
    });
    
    if (safeDests.length === 0) {
        alert("No safe areas found in the region for this date!");
        return;
    }
    
    // Run Dijkstra from startNode to all nodes
    const dist = {};
    const prev = {};
    const pq = new PriorityQueue();
    
    nodes.forEach(n => {
        dist[n.id] = Infinity;
        prev[n.id] = null;
    });
    
    dist[startNode.id] = 0;
    pq.enqueue(startNode.id, 0);
    
    while (!pq.isEmpty()) {
        const { element: u_id } = pq.dequeue();
        
        const adj = [];
        edges.forEach(e => {
            if (isEdgeBlocked(e.id)) return; // Skip blocked
            
            if (e.source === u_id) adj.push({ target: e.target, weight: e.distance_km, edge_id: e.id });
            if (e.target === u_id) adj.push({ target: e.source, weight: e.distance_km, edge_id: e.id });
        });
        
        adj.forEach(({ target: v_id, weight, edge_id }) => {
            const alt = dist[u_id] + weight;
            if (alt < dist[v_id]) {
                dist[v_id] = alt;
                prev[v_id] = { node: u_id, edge: edge_id };
                pq.enqueue(v_id, alt);
            }
        });
    }
    
    // Find the closest safe destination
    let bestDest = null;
    let minDist = Infinity;
    
    safeDests.forEach(d => {
        if (dist[d.id] < minDist) {
            minDist = dist[d.id];
            bestDest = d;
        }
    });
    
    if (!bestDest || minDist === Infinity) {
        alert("No reachable path to a safe area.");
        return;
    }
    
    // Reconstruct path
    const pathEdges = [];
    let curr = bestDest.id;
    
    while (prev[curr]) {
        const step = prev[curr];
        pathEdges.push(step.edge);
        curr = step.node;
    }
    
    const routeGeoJSON = buildRouteGeoJSON(pathEdges);
    
    updateRoutesLayer();
    
    // Draw Evacuation Route
    customRouteLayer = L.geoJSON(routeGeoJSON, {
        style: {
            color: '#32cd32', // Lime green for safe evacuation
            weight: 7,
            dashArray: '10, 10',
            opacity: 0.9
        }
    }).addTo(map);
    if (routeGeoJSON.features.length > 0) {
        map.fitBounds(customRouteLayer.getBounds());
    }
    
    // Transport Mode based on Source Hazard
    const srcNeed = (needsData.habitations || []).find(n => n.habitation === sourceName);
    const maxHazard = srcNeed ? srcNeed.hazard_class : 1;
    let speed = 25.0; 
    let transportMode = "Jeep / Truck";
    
    if (maxHazard === 4) { speed = 50.0; transportMode = "Helicopter Evacuation (Critical)"; }
    else if (maxHazard === 3) { speed = 12.0; transportMode = "Rescue Boat"; }
    
    const estTime = minDist / speed;
    
    // Update Evacuation UI
    document.getElementById('evac-title').textContent = 'Evacuation Plan';
    document.getElementById('evac-target').textContent = bestDest.name;
    document.getElementById('evac-dist').textContent = minDist.toFixed(2);
    document.getElementById('evac-time').textContent = estTime.toFixed(2);
    document.getElementById('evac-mode').textContent = transportMode;
    document.getElementById('evac-metrics').style.display = 'block';
}

function calculateFacilityRoute(sourceName, facilityType) {
    if (customRouteLayer) {
        map.removeLayer(customRouteLayer);
        customRouteLayer = null;
    }
    if (dynamicRouteLayer) {
        map.removeLayer(dynamicRouteLayer);
        dynamicRouteLayer = null;
    }
    
    state.activeRouteType = 'facility';
    state.activeRouteArgs = { src: sourceName, type: facilityType };
    
    const nodes = graphData.nodes || [];
    const edges = graphData.edges || [];
    const startNode = nodes.find(n => n.name === sourceName);
    
    if (!startNode) {
        alert("Source not found in routing graph.");
        return;
    }
    
    // Find targets of specific type
    const targets = nodes.filter(n => n.type === facilityType);
    
    if (targets.length === 0) {
        alert(`No ${facilityType} found in the region!`);
        return;
    }
    
    // Run Dijkstra
    const dist = {};
    const prev = {};
    const pq = new PriorityQueue();
    
    nodes.forEach(n => { dist[n.id] = Infinity; prev[n.id] = null; });
    dist[startNode.id] = 0;
    pq.enqueue(startNode.id, 0);
    
    while (!pq.isEmpty()) {
        const { element: u_id } = pq.dequeue();
        
        const adj = [];
        edges.forEach(e => {
            if (isEdgeBlocked(e.id)) return;
            if (e.source === u_id) adj.push({ target: e.target, weight: e.distance_km, edge_id: e.id });
            if (e.target === u_id) adj.push({ target: e.source, weight: e.distance_km, edge_id: e.id });
        });
        
        adj.forEach(({ target: v_id, weight, edge_id }) => {
            const alt = dist[u_id] + weight;
            if (alt < dist[v_id]) {
                dist[v_id] = alt;
                prev[v_id] = { node: u_id, edge: edge_id };
                pq.enqueue(v_id, alt);
            }
        });
    }
    
    let bestDest = null;
    let minDist = Infinity;
    
    targets.forEach(d => {
        if (dist[d.id] < minDist) {
            minDist = dist[d.id];
            bestDest = d;
        }
    });
    
    if (!bestDest || minDist === Infinity) {
        alert(`No reachable path to a ${facilityType}. Check blockages.`);
        return;
    }
    
    const pathEdges = [];
    let curr = bestDest.id;
    
    while (prev[curr]) {
        const step = prev[curr];
        pathEdges.push(step.edge);
        curr = step.node;
    }
    
    const routeGeoJSON = buildRouteGeoJSON(pathEdges);
    
    updateRoutesLayer(); // Highlight edges
    
    const colors = { hospital: '#ff0000', police: '#0000ff' };
    customRouteLayer = L.geoJSON(routeGeoJSON, {
        style: {
            color: colors[facilityType] || '#ffff00',
            weight: 7,
            dashArray: '10, 10',
            opacity: 0.9
        }
    }).addTo(map);
    if (routeGeoJSON.features.length > 0) {
        map.fitBounds(customRouteLayer.getBounds());
    }
    
    const speed = 25.0; // Assume ground speed for facilities
    const estTime = minDist / speed;
    
    document.getElementById('evac-title').textContent = `Route to ${facilityType.charAt(0).toUpperCase() + facilityType.slice(1)}`;
    document.getElementById('evac-target').textContent = bestDest.name;
    document.getElementById('evac-dist').textContent = minDist.toFixed(2);
    document.getElementById('evac-time').textContent = estTime.toFixed(2);
    document.getElementById('evac-mode').textContent = "Emergency Vehicle";
    document.getElementById('evac-metrics').style.display = 'block';
}

function calculateDynamicAllocation(destName) {
    if (customRouteLayer) { map.removeLayer(customRouteLayer); customRouteLayer = null; }
    if (dynamicRouteLayer) { map.removeLayer(dynamicRouteLayer); dynamicRouteLayer = null; }

    state.activeRouteType = 'dynamic_allocation';
    state.activeRouteArgs = { dest: destName };

    const nodes = graphData.nodes || [];
    const edges = graphData.edges || [];
    const destNode = nodes.find(n => n.name === destName);

    if (!destNode) { alert("Destination not found in routing graph."); return; }

    const habNeed = (needsData.habitations || []).find(n => n.habitation === destName);
    if (!habNeed) { alert("No needs data found for " + destName); return; }

    const q = habNeed.quantitative_needs || {};
    let reqWater = q.water_liters || 0;
    let reqFood = q.food_kg || 0;
    let reqMed = q.medical_teams || 0;
    let reqBoats = q.boats || 0;

    // Run Dijkstra from destination to ALL other nodes
    const dist = {};
    const prev = {};
    const pq = new PriorityQueue();
    nodes.forEach(n => { dist[n.id] = Infinity; prev[n.id] = null; });
    
    dist[destNode.id] = 0;
    pq.enqueue(destNode.id, 0);

    while (!pq.isEmpty()) {
        const { element: u_id } = pq.dequeue();
        
        edges.forEach(e => {
            if (state.blockedEdgeIds.includes(e.id)) return;
            let v_id = null;
            if (e.source === u_id) v_id = e.target;
            if (e.target === u_id) v_id = e.source;
            if (v_id) {
                const alt = dist[u_id] + e.distance_km;
                if (alt < dist[v_id]) {
                    dist[v_id] = alt;
                    prev[v_id] = { node: u_id, edge: e.id };
                    pq.enqueue(v_id, alt);
                }
            }
        });
    }

    // Aggregate real capacities from resources.json
    const available = {};
    resourcesData.forEach(r => {
        let loc = r.location;
        if (!available[loc]) available[loc] = { water: 0, food: 0, medical: 0, boats: 0 };
        if (r.resource_type === 'water_liters') available[loc].water += r.quantity;
        if (r.resource_type === 'food_kg') available[loc].food += r.quantity;
        if (r.resource_type === 'medical_team') available[loc].medical += r.quantity;
        if (r.resource_type === 'boat') available[loc].boats += r.quantity;
    });

    // Identify supply nodes that actually have resources
    const supplyNodes = nodes.filter(n => {
        let snName = n.name || 'Unknown';
        if (n.type === 'police') snName = 'Police Station';
        const cap = available[snName];
        if (!cap) return false;
        return dist[n.id] !== Infinity && (cap.water > 0 || cap.food > 0 || cap.medical > 0 || cap.boats > 0);
    });
    
    supplyNodes.sort((a, b) => dist[a.id] - dist[b.id]);

    const allocationRes = { water: [], food: [], med: [], boats: [] };
    const usedEdgesMap = new Map(); // edgeId -> typeKey

    function allocate(req, typeKey, resList) {
        let remaining = req;
        for (const sn of supplyNodes) {
            if (remaining <= 0) break;
            let snName = sn.name || 'Unknown';
            if (sn.type === 'police') snName = 'Police Station';
            
            const capObj = available[snName];
            if (!capObj) continue;
            
            const availAmt = capObj[typeKey] || 0;
            if (availAmt > 0) {
                const taken = Math.min(availAmt, remaining);
                capObj[typeKey] -= taken;
                remaining -= taken;
                resList.push({ source: snName, amount: taken, dist: dist[sn.id] });
                
                // Track path edges back to destination
                let curr = sn.id;
                while (prev[curr]) {
                    const step = prev[curr];
                    const existingType = usedEdgesMap.get(step.edge);
                    if (!existingType) {
                        usedEdgesMap.set(step.edge, typeKey);
                    } else if (existingType !== typeKey && existingType !== 'mixed') {
                        usedEdgesMap.set(step.edge, 'mixed');
                    }
                    curr = step.node;
                }
            }
        }
    }

    allocate(reqWater, 'water', allocationRes.water);
    allocate(reqFood, 'food', allocationRes.food);
    allocate(reqMed, 'medical', allocationRes.med);
    allocate(reqBoats, 'boats', allocationRes.boats);

    // Draw routes
    const pathEdges = Array.from(usedEdgesMap.keys());
    const routeGeoJSON = buildRouteGeoJSON(pathEdges);
    
    dynamicRouteLayer = L.geoJSON(routeGeoJSON, {
        style: (feature) => {
            const type = usedEdgesMap.get(feature.properties.id);
            let edgeColor = '#ff8c00'; // Default Orange (food/water/mixed)
            if (type === 'medical') edgeColor = '#e31a1c'; // Red for medical
            if (type === 'boats') edgeColor = '#1f78b4'; // Blue for boats
            return { color: edgeColor, weight: 6, dashArray: '10, 10', opacity: 0.8 };
        }
    }).addTo(map);

    if (routeGeoJSON.features.length > 0) {
        map.fitBounds(dynamicRouteLayer.getBounds());
    }

    // Update UI
    const titleEl = document.getElementById('dynamic-allocation-title');
    if (titleEl) titleEl.textContent = "Allocation for: " + destName;
    
    const formatList = (arr) => arr.length === 0 ? "<div>No allocation (0 required or no supply)</div>" : arr.map(a => `<div>• ${Math.round(a.amount).toLocaleString()} from ${a.source} (${a.dist.toFixed(1)} km)</div>`).join('');
    
    const wList = document.getElementById('alloc-water-list');
    const fList = document.getElementById('alloc-food-list');
    const mList = document.getElementById('alloc-med-list');
    const bList = document.getElementById('alloc-boats-list');
    
    if (wList) wList.innerHTML = formatList(allocationRes.water);
    if (fList) fList.innerHTML = formatList(allocationRes.food);
    if (mList) mList.innerHTML = formatList(allocationRes.med);
    if (bList) bList.innerHTML = formatList(allocationRes.boats);
    
    const resUI = document.getElementById('dynamic-allocation-results');
    if (resUI) resUI.style.display = 'flex';
    
    const allocContent = document.getElementById('alloc-content');
    if (allocContent) allocContent.style.display = 'none';
    
    // Hide old custom route metrics
    const oldMetrics = document.getElementById('custom-route-metrics');
    if (oldMetrics) oldMetrics.style.display = 'none';
}

// Simple Priority Queue for Dijkstra
class PriorityQueue {
    constructor() {
        this.values = [];
    }
    enqueue(element, priority) {
        this.values.push({ element, priority });
        this.sort();
    }
    dequeue() {
        return this.values.shift();
    }
    isEmpty() {
        return this.values.length === 0;
    }
    sort() {
        this.values.sort((a, b) => a.priority - b.priority);
    }
}

// Boot
window.onload = init;
