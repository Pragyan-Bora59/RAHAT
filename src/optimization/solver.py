import json
import os
import heapq

def dijkstra(graph_nodes, graph_edges, start_id, target_id, blocked_edge_id=None):
    # Build adjacency list
    adj = {n['id']: [] for n in graph_nodes}
    for e in graph_edges:
        if blocked_edge_id and e['id'] == blocked_edge_id:
            continue
        # Assuming undirected for roads
        adj[e['source']].append((e['target'], e['distance_km'], e['id']))
        adj[e['target']].append((e['source'], e['distance_km'], e['id']))
        
    queue = [(0.0, start_id, [])]
    distances = {start_id: 0.0}
    
    while queue:
        dist, current, path_edges = heapq.heappop(queue)
        
        if current == target_id:
            return dist, path_edges
            
        if dist > distances.get(current, float('inf')):
            continue
            
        for neighbor, weight, edge_id in adj[current]:
            new_dist = dist + weight
            if new_dist < distances.get(neighbor, float('inf')):
                distances[neighbor] = new_dist
                heapq.heappush(queue, (new_dist, neighbor, path_edges + [edge_id]))
                
    return None, []

def run_scenario():
    print("Running initial scenario...")
    
    graph_path = r"d:\flood\public\data\graph.json"
    with open(graph_path, 'r', encoding='utf-8') as f:
        graph = json.load(f)
        
    nodes = graph['nodes']
    edges = graph['edges']
    
    # Just picking some nodes to route between
    # Using 'node_police_Police Station_1' to 'node_hab_Rayeng Mising SC' as an example
    start_node = "node_police_Police Station_1"
    target_node = "node_hab_Rayeng Mising SC"
    
    # Baseline
    base_dist, base_path = dijkstra(nodes, edges, start_node, target_node)
    
    # Disrupted
    blocked_edge = base_path[0] if base_path else None
    sim_dist, sim_path = dijkstra(nodes, edges, start_node, target_node, blocked_edge)
    
    out = {
        "mission": {
            "target": "Rayeng Mising SC",
            "assigned_resource": "2 Boats",
            "source": "Police Station 1"
        },
        "baseline": {
            "distance_km": round(base_dist, 2) if base_dist else 0,
            "estimated_time_hrs": round(base_dist / 30, 2) if base_dist else 0,
            "route_edges": base_path
        },
        "disruption": {
            "blocked_edge_id": blocked_edge,
            "event": "Road submerged"
        },
        "re_optimized": {
            "distance_km": round(sim_dist, 2) if sim_dist else 0,
            "estimated_time_hrs": round(sim_dist / 30, 2) if sim_dist else 0,
            "delay_hrs": round((sim_dist - base_dist) / 30, 2) if (sim_dist and base_dist) else 0,
            "route_edges": sim_path
        }
    }
    
    out_path = r"d:\flood\public\data\optimization_scenario.json"
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(out, f, indent=2)
        
    print(f"Generated scenario at {out_path}")

if __name__ == "__main__":
    run_scenario()
