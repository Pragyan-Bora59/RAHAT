import csv
import json
import os
import yaml
import re

def prepare_baseline():
    input_csv = r"d:\flood\datasets\shelters and resources\current_resource_inventory_updated.csv"
    output_csv = r"d:\flood\data\resources\resource_baseline.csv"
    output_json = r"d:\flood\public\data\resources.json"
    config_yaml = r"d:\flood\config\allocation_weights.yaml"
    
    with open(config_yaml, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
        
    location_mapping = config.get('location_mapping', {})
    
    baseline_data = []
    
    with open(input_csv, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            raw_type = row['resource_type'].lower()
            raw_qty = row['quantity']
            
            # Normalize resource type
            resource_type = "other"
            if "boat" in raw_type:
                resource_type = "boat"
            elif "medical" in raw_type:
                resource_type = "medical_team"
            elif "rice" in raw_type or "dal" in raw_type or "food" in raw_type:
                resource_type = "food_kg"
            elif "water purifying" in raw_type:
                resource_type = "water_liters"
                
            if resource_type == "other":
                continue # Skip for optimization mapping prototype
                
            # Normalize quantity
            qty = 0.0
            if "MT" in raw_qty:
                val = float(re.sub(r'[^\d.]', '', raw_qty))
                qty = val * 1000 # MT to kg
            elif "teams" in raw_qty or "team" in raw_qty:
                qty = float(re.sub(r'[^\d.]', '', raw_qty))
            else:
                try:
                    qty = float(re.sub(r'[^\d.]', '', raw_qty))
                except:
                    qty = 0.0
                    
            # For water purifiers, multiply by capacity per day if applicable
            if resource_type == "water_liters" and "5000 L/day" in row.get('capacity', ''):
                qty = qty * 5000
                
            # Map location
            original_loc = row['location']
            mapped_loc = location_mapping.get(original_loc, original_loc)
            
            item = {
                "resource_id": row['resource_id'],
                "resource_type": resource_type,
                "quantity": qty,
                "location": mapped_loc,
                "original_location": original_loc,
                "purpose": row.get('capacity', 'Relief & Rescue'),
                "source": row['source'],
                "source_date": row['last_updated'],
                "status_type": "Official Government Baseline" 
            }
            baseline_data.append(item)
            
    # Write transformed CSV
    os.makedirs(os.path.dirname(output_csv), exist_ok=True)
    with open(output_csv, 'w', encoding='utf-8', newline='') as f:
        if baseline_data:
            writer = csv.DictWriter(f, fieldnames=baseline_data[0].keys())
            writer.writeheader()
            writer.writerows(baseline_data)
            
    # Write JSON for frontend
    os.makedirs(os.path.dirname(output_json), exist_ok=True)
    with open(output_json, 'w', encoding='utf-8') as f:
        json.dump(baseline_data, f, indent=2)
        
    print(f"Processed {len(baseline_data)} resources to {output_json}")

if __name__ == "__main__":
    prepare_baseline()
