import json
import csv
import os
import math
from collections import defaultdict

def calculate_needs():
    exposure_csv = r"d:\flood\outputs\tables\habitation_exposure.csv"
    
    # Store data per date
    needs_by_date = defaultdict(list)
    
    # Constants for Explainable Requirements
    RICE_DAL_KG_PER_PERSON = 0.5   # 500g per person per day
    WATER_LITERS_PER_PERSON = 3.0  # 3 Liters per person per day
    PERSONS_PER_BOAT = 20          # 1 boat can rescue 20 people at a time
    TRIPS_PER_BOAT_DAY = 5         # Assume 5 round trips per boat per day
    PERSONS_PER_MEDICAL_TEAM = 500 # 1 mobile medical team per 500 affected people
    import heapq
    
    # 1. Pre-compute distances from resource bases to habitations
    graph_path = r"d:\flood\public\data\graph.json"
    hab_distances = {}
    if os.path.exists(graph_path):
        with open(graph_path, 'r', encoding='utf-8') as f:
            graph = json.load(f)
            
        adj = {n['id']: [] for n in graph['nodes']}
        for e in graph['edges']:
            adj[e['source']].append((e['target'], e['distance_km']))
            adj[e['target']].append((e['source'], e['distance_km']))
            
        bases = [n['id'] for n in graph['nodes'] if n.get('type') in ['police', 'hospital', 'base']]
        hab_nodes = [n for n in graph['nodes'] if n.get('type') == 'habitation']
        
        # Multi-source Dijkstra from all bases
        queue = []
        distances = {n['id']: float('inf') for n in graph['nodes']}
        
        for b in bases:
            distances[b] = 0
            heapq.heappush(queue, (0, b))
            
        while queue:
            dist, current = heapq.heappop(queue)
            if dist > distances[current]:
                continue
                
            for neighbor, weight in adj[current]:
                new_dist = dist + weight
                if new_dist < distances[neighbor]:
                    distances[neighbor] = new_dist
                    heapq.heappush(queue, (new_dist, neighbor))
                    
        for hn in hab_nodes:
            hab_name = hn.get('name', '')
            if hab_name:
                dist = distances[hn['id']]
                if dist < float('inf'):
                    # If multiple nodes for same habitation, take minimum
                    hab_distances[hab_name] = min(dist, hab_distances.get(hab_name, float('inf')))

    with open(exposure_csv, 'r') as f:
        reader = csv.DictReader(f)
        
        for row in reader:
            date_key = row['Date']
            hab_name = row['Habitation']
            hazard_class = int(row['Hazard_Class'])
            affected_pop = int(row['Affected_Pop'])
            children_est = int(affected_pop * 0.30) # Estimate 30% are children
            accessibility = row['Accessibility']
            
            # Simple logical rules for urgency based on hazard class and affected pop
            rescue_urgency = "Low"
            water_need = "Low"
            medical_urgency = "Low"
            relocation_req = "Not Required"
            
            # Multiplier for isolation / accessibility
            boat_multiplier = 1.5 if accessibility == "Poor" else 1.0
            
            if hazard_class == 4:
                rescue_urgency = "Critical"
                water_need = "High"
                medical_urgency = "High" if affected_pop > 500 else "Medium"
                relocation_req = "Immediate"
            elif hazard_class == 3:
                rescue_urgency = "High"
                water_need = "High"
                medical_urgency = "Medium"
                relocation_req = "Required"
            elif hazard_class == 2:
                rescue_urgency = "Medium"
                water_need = "Medium"
                medical_urgency = "Low"
                relocation_req = "Standby"
                
    # Quantitative Needs Calculation (Explainable)
            food_kg = affected_pop * RICE_DAL_KG_PER_PERSON
            water_l = affected_pop * WATER_LITERS_PER_PERSON
            medical_teams = int(affected_pop / PERSONS_PER_MEDICAL_TEAM) + (1 if affected_pop > 0 else 0)
            boats = int(affected_pop / (PERSONS_PER_BOAT * TRIPS_PER_BOAT_DAY) * boat_multiplier)
                
            # Score for sorting (Advanced Priority System)
            # Hazard severity is paramount (x50).
            # Children factor heavily due to vulnerability (x0.5).
            # General population is standard (x0.1).
            
            # --- carrying capacity assessment & logistics penalty ---
            # We add a penalty based on distance to nearest resource base
            # Farther away = harder to reach = higher priority (needs faster action)
            min_dist = hab_distances.get(hab_name, 10.0) # default to 10km if not found
            
            # Distance adds up to 50 points to the score (e.g. 25km * 2)
            logistics_penalty = min_dist * 2.0
            
            score = (hazard_class * 50) + (children_est * 0.5) + (affected_pop * 0.1) + logistics_penalty
            
            # Only add to list if actually affected (hazard >= 2 or affected pop > 0)
            # Actually, we should list all so we can show green ones at the bottom, but the prompt
            # implies only at-risk should be prioritized. We will list all but sort them.
            needs_by_date[date_key].append({
                "habitation": hab_name,
                "hazard_class": hazard_class,
                "affected_population": affected_pop,
                "children_est": children_est,
                "accessibility": accessibility,
                "needs": {
                    "rescue": rescue_urgency,
                    "water_food": water_need,
                    "medical": medical_urgency,
                    "relocation": relocation_req
                },
                "quantitative_needs": {
                    "food_kg": food_kg,
                    "water_liters": water_l,
                    "medical_teams": medical_teams,
                    "boats": boats
                },
                "priority_score": round(score, 2)
            })
            
    # Output JSON per date
    for date_key, needs_data in needs_by_date.items():
        # Sort by priority score descending
        needs_data.sort(key=lambda x: x['priority_score'], reverse=True)
        
        # Aggregate totals
        total_food = sum(n["quantitative_needs"]["food_kg"] for n in needs_data)
        total_water = sum(n["quantitative_needs"]["water_liters"] for n in needs_data)
        total_medical = sum(n["quantitative_needs"]["medical_teams"] for n in needs_data)
        total_boats = sum(n["quantitative_needs"]["boats"] for n in needs_data)
        
        out_data = {
            "habitations": needs_data,
            "aggregate_needs": {
                "food_kg": total_food,
                "water_liters": total_water,
                "medical_teams": total_medical,
                "boats": total_boats
            }
        }
        
        needs_json = fr"d:\flood\public\data\needs_{date_key}.json"
        os.makedirs(os.path.dirname(needs_json), exist_ok=True)
        with open(needs_json, 'w') as f:
            json.dump(out_data, f, indent=2)
            
        print(f"Needs assessed for {date_key} and saved to {needs_json}")

if __name__ == "__main__":
    calculate_needs()
