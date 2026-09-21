import json
import os
import copy
import heapq

def dijkstra(graph_nodes, graph_edges, start_ids, blocked_edge=None):
    adj = {n['id']: [] for n in graph_nodes}
    for e in graph_edges:
        if blocked_edge and e['id'] == blocked_edge:
            continue
        adj[e['source']].append((e['target'], e['distance_km'], e['id']))
        adj[e['target']].append((e['source'], e['distance_km'], e['id']))
        
    queue = []
    distances = {n['id']: float('inf') for n in graph_nodes}
    paths = {n['id']: [] for n in graph_nodes}
    
    for s in start_ids:
        distances[s] = 0
        heapq.heappush(queue, (0, s, []))
        
    while queue:
        dist, current, path_edges = heapq.heappop(queue)
        
        if dist > distances[current]:
            continue
            
        for neighbor, weight, edge_id in adj[current]:
            new_dist = dist + weight
            if new_dist < distances[neighbor]:
                distances[neighbor] = new_dist
                new_path = path_edges + [edge_id]
                paths[neighbor] = new_path
                heapq.heappush(queue, (new_dist, neighbor, new_path))
                
    return distances, paths

def run_allocation():
    # 1. Load Graph
    graph_path = r"d:\flood\public\data\graph.json"
    with open(graph_path, 'r', encoding='utf-8') as f:
        graph = json.load(f)
        
    # 2. Load Resources (Inventory)
    res_path = r"d:\flood\public\data\resources.json"
    with open(res_path, 'r', encoding='utf-8') as f:
        inventory = json.load(f)
        
    # Standardize inventory
    inv_map = {}
    for r in inventory:
        loc = r['location']
        if loc not in inv_map:
            inv_map[loc] = {}
        rt = r['resource_type'].lower()
        if 'food' in rt: rt = 'food_kg'
        elif 'water' in rt: rt = 'water_liters'
        elif 'medical' in rt: rt = 'medical_teams'
        elif 'boat' in rt: rt = 'boats'
        elif 'truck' in rt: rt = 'trucks'
        inv_map[loc][rt] = inv_map[loc].get(rt, 0) + int(r['quantity'])
        
    base_nodes = {}
    for n in graph['nodes']:
        if n.get('type') in ['police', 'hospital', 'base']:
            base_nodes[n['name']] = n['id']
            
    # 3. Load Needs
    needs_path = r"d:\flood\public\data\needs_22jul.json"
    with open(needs_path, 'r', encoding='utf-8') as f:
        needs_data = json.load(f)
        
    habs = needs_data['habitations']
    hab_nodes = {}
    for n in graph['nodes']:
        if n.get('type') == 'habitation':
            if n['name'] not in hab_nodes:
                hab_nodes[n['name']] = []
            hab_nodes[n['name']].append(n['id'])
            
    def allocate_scenario(blocked_edge=None):
        # Reset inventory for scenario
        current_inv = copy.deepcopy(inv_map)
        allocations = []
        dest_summary = []
        
        # Calculate distances from all bases to all habitations
        base_dists = {}
        base_paths = {}
        for b_name, b_id in base_nodes.items():
            dists, paths = dijkstra(graph['nodes'], graph['edges'], [b_id], blocked_edge)
            base_dists[b_name] = dists
            base_paths[b_name] = paths
            
        # Greedy Allocation based on Priority Score
        for hab in habs:
            hab_name = hab['habitation']
            target_ids = hab_nodes.get(hab_name, [])
            if not target_ids:
                continue
                
            req = hab['quantitative_needs']
            allocated_here = {'food_kg': 0, 'water_liters': 0, 'medical_teams': 0, 'boats': 0}
            
            # For each resource type, find the closest base that has it
            for res_type in ['medical_teams', 'boats', 'food_kg', 'water_liters']:
                demand = req.get(res_type, 0)
                if demand <= 0: continue
                
                # Sort bases by distance to this habitation
                closest_bases = []
                for b_name, b_id in base_nodes.items():
                    # Find min distance to any of the habitation's nodes
                    min_dist = float('inf')
                    best_target = None
                    for t_id in target_ids:
                        if base_dists[b_name][t_id] < min_dist:
                            min_dist = base_dists[b_name][t_id]
                            best_target = t_id
                    if min_dist < float('inf'):
                        closest_bases.append((min_dist, b_name, best_target))
                        
                closest_bases.sort(key=lambda x: x[0])
                
                for dist, b_name, t_id in closest_bases:
                    if demand <= 0: break
                    available = current_inv.get(b_name, {}).get(res_type, 0)
                    if available > 0:
                        take = min(demand, available)
                        
                        # Vehicle constraint logic (Carrying Capacity)
                        # Assume 1 truck carries 2000kg food or 5000L water.
                        # For simplicity in this demo, if they need food/water, we deduct trucks.
                        if res_type in ['food_kg', 'water_liters']:
                            trucks_needed = (take / 2000) if res_type == 'food_kg' else (take / 5000)
                            trucks_avail = current_inv.get(b_name, {}).get('trucks', 0)
                            # If no trucks, we can't send. (Just a simple penalty/cap for the demo)
                            if trucks_avail < 1 and trucks_needed > 0:
                                continue # Can't transport from here
                                
                        current_inv[b_name][res_type] -= take
                        allocated_here[res_type] += take
                        demand -= take
                        
                        allocations.append({
                            "source": b_name,
                            "destination": hab_name,
                            "resource_type": res_type,
                            "quantity": take,
                            "distance_km": round(dist, 2),
                            "route_edges": base_paths[b_name][t_id]
                        })
                        
            total_req = sum(req.values())
            total_alloc = sum(allocated_here.values())
            pct = int((total_alloc / total_req) * 100) if total_req > 0 else 100
            
            dest_summary.append({
                "destination": hab_name,
                "priority_score": hab['priority_score'],
                "fulfillment_percent": pct,
                "demand": req,
                "allocated": allocated_here
            })
            
        return {
            "allocations": allocations,
            "destination_summary": dest_summary
        }
        
    baseline = allocate_scenario(blocked_edge=None)
    disrupted = allocate_scenario(blocked_edge="1536575")
    
    out = {
        "baseline": baseline,
        "disrupted": disrupted
    }
    
    out_path = r"d:\flood\public\data\allocation_plan.json"
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(out, f, indent=2)
        
    print(f"Allocation plan generated at {out_path}")

if __name__ == "__main__":
    run_allocation()
