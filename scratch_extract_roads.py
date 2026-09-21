import pandas as pd
import shapely.wkb
import json

def test():
    print("Loading parquet...")
    df = pd.read_parquet(r"d:\flood\datasets\roads and infrastructure\SOI_Roads.parquet", columns=["OBJECTID", "road_type", "surface", "geometry", "bbox"])
    
    # Filter by Jonai cluster bounding box (approx 94.9 to 95.3, 27.6 to 27.9)
    # The bbox is a struct/dict
    
    # Since bbox is a dictionary/struct in parquet, pandas might load it as a dict.
    print("Extracting bounds...")
    try:
        # Some versions of pyarrow load struct as dict, others as tuple.
        first = df['bbox'].iloc[0]
        print(f"Type of bbox element: {type(first)}")
        print(f"Content: {first}")
        
        # Let's write a simple lambda to extract coords
        df['xmin'] = df['bbox'].apply(lambda b: b['xmin'] if isinstance(b, dict) else b[0])
        df['xmax'] = df['bbox'].apply(lambda b: b['xmax'] if isinstance(b, dict) else b[2])
        df['ymin'] = df['bbox'].apply(lambda b: b['ymin'] if isinstance(b, dict) else b[1])
        df['ymax'] = df['bbox'].apply(lambda b: b['ymax'] if isinstance(b, dict) else b[3])
        
        # Filter
        jonai = df[
            (df['xmin'] >= 94.8) & (df['xmax'] <= 95.3) &
            (df['ymin'] >= 27.6) & (df['ymax'] <= 27.9)
        ]
        
        print(f"Found {len(jonai)} roads in Jonai.")
        
        if len(jonai) > 0:
            geom = shapely.wkb.loads(jonai['geometry'].iloc[0])
            print("Successfully parsed a geometry:", type(geom), geom.wkt[:50])
            
    except Exception as e:
        print("Error:", e)

if __name__ == "__main__":
    test()
