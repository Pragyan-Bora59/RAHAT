import json
import os
import math
import pandas as pd
import shapely.wkb
import shapely.geometry
import networkx as nx

# Safe Shelters (established in low-risk elevated locations)
shelters = [
    {"name": "Jonai College Relief Camp", "lat": 27.768, "lon": 95.163}
]

def calculate_distance(lat1, lon1, lat2, lon2):
    """Haversine distance in km"""
    R = 6371
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat/2) * math.sin(dlat/2) + \
        math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * \
        math.sin(dlon/2) * math.sin(dlon/2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    return R * c

def extract_bounds(df):
    df['xmin'] = df['bbox'].apply(lambda b: b['xmin'] if isinstance(b, dict) else b[0])
    df['xmax'] = df['bbox'].apply(lambda b: b['xmax'] if isinstance(b, dict) else b[2])
    df['ymin'] = df['bbox'].apply(lambda b: b['ymin'] if isinstance(b, dict) else b[1])
    df['ymax'] = df['bbox'].apply(lambda b: b['ymax'] if isinstance(b, dict) else b[3])
    return df

def build_graph():
    print("Loading datasets...")
    
    # Bbox for Jonai cluster (approx)
    min_lon, max_lon = 94.8, 95.3
    min_lat, max_lat = 27.6, 27.9
    
    roads_df = pd.read_parquet(r"d:\RAHAT\datasets\roads and infrastructure\SOI_Roads.parquet", columns=["OBJECTID", "road_type", "surface", "geometry", "bbox"])
    roads_df = extract_bounds(roads_df)
    roads_jonai = roads_df[
        (roads_df['xmin'] <= max_lon) & (roads_df['xmax'] >= min_lon) &
        (roads_df['ymin'] <= max_lat) & (roads_df['ymax'] >= min_lat)
    ]
    
    bridges_df = pd.read_parquet(r"d:\RAHAT\datasets\roads and infrastructure\SOI_Bridges.parquet", columns=["objectid", "geometry", "bbox"])
    bridges_df = extract_bounds(bridges_df)
    bridges_jonai = bridges_df[
        (bridges_df['xmin'] <= max_lon) & (bridges_df['xmax'] >= min_lon) &
        (bridges_df['ymin'] <= max_lat) & (bridges_df['ymax'] >= min_lat)
    ]
    
    print(f"Extracted {len(roads_jonai)} roads and {len(bridges_jonai)} bridges.")
    
    G = nx.Graph()
    geojson_features = []
    
    # Add road edges
    for idx, row in roads_jonai.iterrows():
        geom = shapely.wkb.loads(row['geometry'])
        if geom.geom_type == 'LineString':
            coords = list(geom.coords)
            
            # Export the full feature for roads.geojson
            edge_id = str(row['OBJECTID'])
            geojson_features.append({
                "type": "Feature",
                "geometry": shapely.geometry.mapping(geom),
                "properties": {
                    "id": edge_id,
                    "risk": "Low",
                    "status": "Open",
                    "type": "road"
                }
            })
            
            # Add each segment as an edge in the graph
            for i in range(len(coords) - 1):
                u = (round(coords[i][0], 5), round(coords[i][1], 5))
                v = (round(coords[i+1][0], 5), round(coords[i+1][1], 5))
                
                dist = calculate_distance(u[1], u[0], v[1], v[0])
                if dist == 0: dist = 0.001
                
                seg_id = f"{edge_id}_{i}"
                G.add_edge(u, v, id=seg_id, weight=dist, risk="Low", status="Open")
                
                if u not in G.nodes: G.nodes[u]['type'] = 'intersection'
                if v not in G.nodes: G.nodes[v]['type'] = 'intersection'

    # Add bridges as points for the map
    bridge_features = []
    for idx, row in bridges_jonai.iterrows():
        geom = shapely.wkb.loads(row['geometry'])
        if geom.geom_type == 'Point':
            bridge_features.append({
                "type": "Feature",
                "geometry": shapely.geometry.mapping(geom),
                "properties": {
                    "id": str(row['objectid']),
                    "type": "bridge"
                }
            })
            
    # Snap Habitations to the nearest road node
    with open(r"d:\RAHAT\public\geojson\habitations.geojson", 'r') as f:
        hab_data = json.load(f)
        
    habs = hab_data['features']
    nodes_list = list(G.nodes)
    
    if not nodes_list:
        print("[!] No road nodes found in this bbox. Ensure bbox is correct.")
        return
        
    # Connect base (Jonai Response Base)
    base_lat, base_lon = 27.770, 95.160
    
    for h in habs:
        props = h['properties']
        h_lon, h_lat = h['geometry']['coordinates']
        # Find 2 closest road nodes to ensure alternative routes exist
        nodes_list.sort(key=lambda n: calculate_distance(h_lat, h_lon, n[1], n[0]))
        closest_nodes = nodes_list[:2]
        
        hab_node = (round(h_lon, 4), round(h_lat, 4))
        for i, c_node in enumerate(closest_nodes):
            G.add_edge(hab_node, c_node, id=f"edge_hab_{props['name']}_{i}", weight=calculate_distance(h_lat, h_lon, c_node[1], c_node[0]), risk="Low", status="Open")
        G.nodes[hab_node]['type'] = 'habitation'
        G.nodes[hab_node]['name'] = props['name']
        
    # Connect shelters to closest road nodes
    for s in shelters:
        s_lon, s_lat = s['lon'], s['lat']
        nodes_list.sort(key=lambda n: calculate_distance(s_lat, s_lon, n[1], n[0]))
        closest_nodes = nodes_list[:2]
        s_node = (round(s_lon, 4), round(s_lat, 4))
        for i, c_node in enumerate(closest_nodes):
            G.add_edge(s_node, c_node, id=f"edge_shelter_{s['name']}_{i}", weight=calculate_distance(s_lat, s_lon, c_node[1], c_node[0]), risk="Low", status="Open")
        G.nodes[s_node]['type'] = 'shelter'
        G.nodes[s_node]['name'] = s['name']
        
    # Connect hospitals
    hosp_path = r"d:\RAHAT\public\geojson\hospitals.geojson"
    if os.path.exists(hosp_path):
        with open(hosp_path, 'r', encoding='utf-8') as f:
            hosp_data = json.load(f)
            for h in hosp_data.get('features', []):
                coords = h['geometry']['coordinates']
                h_lon, h_lat = coords[0], coords[1]
                name = h['properties'].get('name', 'Hospital')
                if not name: name = 'Hospital'
                
                nodes_list.sort(key=lambda n: calculate_distance(h_lat, h_lon, n[1], n[0]))
                closest_nodes = nodes_list[:2]
                h_node = (round(h_lon, 4), round(h_lat, 4))
                for i, c_node in enumerate(closest_nodes):
                    G.add_edge(h_node, c_node, id=f"edge_hosp_{name}_{i}", weight=calculate_distance(h_lat, h_lon, c_node[1], c_node[0]), risk="Low", status="Open")
                G.nodes[h_node]['type'] = 'hospital'
                G.nodes[h_node]['name'] = name
                
    # Connect police stations
    police_path = r"d:\RAHAT\public\geojson\police.geojson"
    if os.path.exists(police_path):
        with open(police_path, 'r', encoding='utf-8') as f:
            police_data = json.load(f)
            for p in police_data.get('features', []):
                coords = p['geometry']['coordinates']
                p_lon, p_lat = coords[0], coords[1]
                name = p['properties'].get('name', p['properties'].get('NAME', 'Police Station'))
                if not name: name = 'Police Station'
                
                nodes_list.sort(key=lambda n: calculate_distance(p_lat, p_lon, n[1], n[0]))
                closest_nodes = nodes_list[:2]
                p_node = (round(p_lon, 4), round(p_lat, 4))
                for i, c_node in enumerate(closest_nodes):
                    G.add_edge(p_node, c_node, id=f"edge_police_{name}_{i}", weight=calculate_distance(p_lat, p_lon, c_node[1], c_node[0]), risk="Low", status="Open")
                G.nodes[p_node]['type'] = 'police'
                G.nodes[p_node]['name'] = name
        
    # Connect base to 3 closest nodes for redundancy
    base_node = (base_lon, base_lat)
    nodes_list.sort(key=lambda n: calculate_distance(base_lat, base_lon, n[1], n[0]))
    for i, c_node in enumerate(nodes_list[:3]):
        G.add_edge(base_node, c_node, id=f"edge_base_connect_{i}", weight=calculate_distance(base_lat, base_lon, c_node[1], c_node[0]), risk="Low", status="Open")
    G.nodes[base_node]['type'] = 'base'
    G.nodes[base_node]['name'] = 'Jonai Response Base'
    
    # Export Graph to JSON for Solver / Dashboard
    export_nodes = []
    for n, data in G.nodes(data=True):
        export_nodes.append({
            "id": f"{n[0]}_{n[1]}",
            "lon": n[0],
            "lat": n[1],
            "type": data.get('type', 'intersection'),
            "name": data.get('name', '')
        })
        
    export_edges = []
    for u, v, data in G.edges(data=True):
        export_edges.append({
            "id": data['id'],
            "source": f"{u[0]}_{u[1]}",
            "target": f"{v[0]}_{v[1]}",
            "distance_km": data['weight'],
            "risk": data.get('risk', 'Low'),
            "status": data.get('status', 'Open')
        })
        
    graph_data = {
        "nodes": export_nodes,
        "edges": export_edges
    }
    
    os.makedirs(r"d:\RAHAT\public\data", exist_ok=True)
    with open(r"d:\RAHAT\public\data\graph.json", 'w') as f:
        json.dump(graph_data, f, indent=2)
        
    with open(r"d:\RAHAT\public\geojson\roads.geojson", 'w') as f:
        json.dump({
            "type": "FeatureCollection",
            "features": geojson_features
        }, f, indent=2)
        
    with open(r"d:\RAHAT\public\geojson\bridges.geojson", 'w') as f:
        json.dump({
            "type": "FeatureCollection",
            "features": bridge_features
        }, f, indent=2)
        
    print(f"Graph built with {len(export_nodes)} nodes and {len(export_edges)} edges.")

if __name__ == "__main__":
    build_graph()
