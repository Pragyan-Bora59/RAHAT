import * as L from 'leaflet';

// --- State ---
let map: L.Map;
let floodLayer: L.ImageOverlay | null = null;
let hazardLayer: L.ImageOverlay | null = null;
let routesLayer: L.GeoJSON | null = null;
let habitationsLayer: L.GeoJSON | null = null;
let selectedHabitation: string | null = null;

let boundsData: any = {};
let needsData: any = [];
let resourcesData: any = [];
let scenarioData: any = {};
let graphGeoJSON: any = {};

const state = {
    currentTime: '22jul',
    showHazard: true,
    showRoutes: true,
    isRoadBlocked: false
};

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
    L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
        attribution: '&copy; OpenStreetMap contributors &copy; CARTO'
    }).addTo(map);
}

async function loadData() {
    try {
        const [boundsRes, needsRes, resRes, scenRes, graphRes, habsRes] = await Promise.all([
            fetch('./overlays/bounds.json'),
            fetch('./data/needs.json'),
            fetch('./data/resources.json'),
            fetch('./data/optimization_scenario.json'),
            fetch('./geojson/roads.geojson'),
            fetch('./geojson/habitations.geojson')
        ]);
        
        boundsData = await boundsRes.json();
        needsData = await needsRes.json();
        resourcesData = await resRes.json();
        scenarioData = await scenRes.json();
        graphGeoJSON = await graphRes.json();
        const habsGeoJSON = await habsRes.json();
        
        // Draw Habitations
        habitationsLayer = L.geoJSON(habsGeoJSON, {
            pointToLayer: (feature, latlng) => {
                const hazard = feature.properties.hazard_class;
                const color = hazard === 4 ? '#dc143c' : 
                              hazard === 3 ? '#ff8c00' : 
                              hazard === 2 ? '#ffd700' : '#228b22';
                const marker = L.circleMarker(latlng, {
                    radius: 6,
                    fillColor: color,
                    color: '#fff',
                    weight: 1,
                    opacity: 1,
                    fillOpacity: 0.8
                }).bindTooltip(feature.properties.name);
                
                marker.on('click', () => {
                    if ((window as any).selectHabitation) {
                        (window as any).selectHabitation(feature.properties.name);
                    }
                });
                return marker;
            }
        }).addTo(map);

    } catch (e) {
        console.error("Error loading data", e);
    }
}

function setupEventListeners() {
    // Temporal controls
    document.querySelectorAll('.time-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
            document.querySelectorAll('.time-btn').forEach(b => b.classList.remove('active'));
            const target = e.target as HTMLElement;
            target.classList.add('active');
            state.currentTime = target.dataset.time || '22jul';
            updateFloodLayer();
        });
    });
    
    // Checkboxes
    document.getElementById('toggle-hazard')?.addEventListener('change', (e) => {
        state.showHazard = (e.target as HTMLInputElement).checked;
        updateHazardLayer();
    });
    
    document.getElementById('toggle-routes')?.addEventListener('change', (e) => {
        state.showRoutes = (e.target as HTMLInputElement).checked;
        updateRoutesLayer();
    });
    
    // Scenario Controls
    document.getElementById('btn-block-road')?.addEventListener('click', () => {
        state.isRoadBlocked = true;
        document.getElementById('btn-block-road')!.style.display = 'none';
        document.getElementById('btn-reset-road')!.style.display = 'block';
        document.getElementById('scenario-metrics')!.style.display = 'block';
        
        const statusEl = document.getElementById('rec-status');
        if (statusEl) {
            statusEl.textContent = 'Road Blocked - Re-routed';
            statusEl.className = 'rec-row status-rerouted';
        }
        
        updateRoutesLayer();
    });
    
    document.getElementById('btn-reset-road')?.addEventListener('click', () => {
        state.isRoadBlocked = false;
        document.getElementById('btn-reset-road')!.style.display = 'none';
        document.getElementById('btn-block-road')!.style.display = 'block';
        document.getElementById('scenario-metrics')!.style.display = 'none';
        
        const statusEl = document.getElementById('rec-status');
        if (statusEl) {
            statusEl.textContent = 'Optimal';
            statusEl.className = 'rec-row status-optimal';
        }
        
        updateRoutesLayer();
    });
}

function updateDashboard() {
    updateFloodLayer();
    updateHazardLayer();
    updateRoutesLayer();
    
    // Update summary metrics
    const totalHabs = needsData.length;
    const totalPop = needsData.reduce((sum: number, n: any) => sum + n.affected_population, 0);
    
    document.getElementById('val-habitations')!.textContent = totalHabs.toString();
    document.getElementById('val-population')!.textContent = totalPop.toLocaleString();
    
    // Update priority table
    const tbody = document.querySelector('#priority-table tbody');
    if (tbody) {
        tbody.innerHTML = '';
        needsData.slice(0, 5).forEach((n: any) => {
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
        resourcesData.forEach((r: any) => {
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
        document.getElementById('rec-target')!.textContent = scenarioData.mission.target;
        document.getElementById('rec-resource')!.textContent = scenarioData.mission.assigned_resource;
        document.getElementById('rec-time')!.textContent = scenarioData.baseline.estimated_time_hrs;
        document.getElementById('rec-dist')!.textContent = scenarioData.baseline.distance_km;
        
        document.getElementById('sim-dist')!.textContent = scenarioData.re_optimized.distance_km;
        document.getElementById('sim-time')!.textContent = scenarioData.re_optimized.estimated_time_hrs;
        document.getElementById('sim-delay')!.textContent = scenarioData.re_optimized.delay_hrs;
    }
}

function updateFloodLayer() {
    if (floodLayer) map.removeLayer(floodLayer);
    
    const timeMap: Record<string, string> = {
        '11jul': 'flood_baseline.png',
        '18jul': 'flood_onset.png',
        '22jul': 'flood_active.png',
        '28jul': 'flood_active.png' // Fallback for prototype missing data
    };
    
    const imgName = timeMap[state.currentTime];
    const b = boundsData[imgName.replace('.png', '.tif')];
    
    if (b) {
        const bounds: L.LatLngBoundsExpression = [b.southWest, b.northEast];
        floodLayer = L.imageOverlay(`./overlays/${imgName}`, bounds, { opacity: 0.7 }).addTo(map);
    }
}

function updateHazardLayer() {
    if (hazardLayer) {
        map.removeLayer(hazardLayer);
        hazardLayer = null;
    }
    
    if (state.showHazard) {
        const b = boundsData['hazard_map.tif'];
        if (b) {
            const bounds: L.LatLngBoundsExpression = [b.southWest, b.northEast];
            hazardLayer = L.imageOverlay(`./overlays/hazard_map.png`, bounds, { opacity: 0.6 }).addTo(map);
        }
    }
}

function updateRoutesLayer() {
    if (routesLayer) {
        map.removeLayer(routesLayer);
        routesLayer = null;
    }
    
    if (!state.showRoutes) return;
    
    const activeRouteEdges = state.isRoadBlocked 
        ? scenarioData.re_optimized.route_edges 
        : scenarioData.baseline.route_edges;
        
    const blockedEdge = scenarioData.disruption.blocked_edge_id;
    
    routesLayer = L.geoJSON(graphGeoJSON, {
        style: (feature) => {
            const id = feature?.properties?.id;
            
            if (state.isRoadBlocked && id === blockedEdge) {
                return { color: '#ff0000', weight: 4, dashArray: '5, 10' }; // Blocked
            }
            
            const isTargetSelected = selectedHabitation === scenarioData?.mission?.target;
            if (isTargetSelected && activeRouteEdges.includes(id)) {
                return { color: '#00ffff', weight: 5 }; // Active Route
            }
            
            return { color: '#555555', weight: 2, opacity: 0.5 }; // Background graph
        }
    }).addTo(map);
}

(window as any).selectHabitation = function(name: string) {
    selectedHabitation = name;
    
    const nodeData = needsData.find((n: any) => n.habitation === name);
    const score = nodeData ? nodeData.priority_score : 'N/A';
    
    const allocContent = document.getElementById('alloc-content');
    const allocDetails = document.getElementById('alloc-details');
    if (allocContent) allocContent.style.display = 'none';
    if (allocDetails) allocDetails.style.display = 'block';
    
    const targetName = document.getElementById('alloc-target-name');
    if (targetName) targetName.textContent = name;
    
    const targetScore = document.getElementById('alloc-target-score');
    if (targetScore) targetScore.textContent = score.toString();
    
    const resList = document.getElementById('alloc-resources-list');
    if (resList) {
        if (name === scenarioData?.mission?.target) {
            resList.innerHTML = `<div style="color: #ccc; font-size: 0.9em; margin-bottom: 5px;">Allocated: ${scenarioData.mission.assigned_resource}</div>`;
        } else {
            resList.innerHTML = `<div style="color: #ccc; font-size: 0.9em; margin-bottom: 5px;">No specific active missions yet.</div>`;
        }
    }
    
    updateRoutesLayer();
};

(window as any).clearAllocationSelection = () => {
    selectedHabitation = null;
    const allocContent = document.getElementById('alloc-content');
    const allocDetails = document.getElementById('alloc-details');
    if (allocContent) allocContent.style.display = 'block';
    if (allocDetails) allocDetails.style.display = 'none';
    updateRoutesLayer();
};

// Boot
window.onload = init;
