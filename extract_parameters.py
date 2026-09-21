import os
import json
import rasterio
import pandas as pd
import shapefile

def get_geojson_params(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        features = data.get('features', [])
        if features:
            return list(features[0].get('properties', {}).keys())
    except:
        pass
    return []

def get_parquet_params(filepath):
    try:
        df = pd.read_parquet(filepath)
        return list(df.columns)
    except:
        pass
    return []

def get_csv_params(filepath):
    try:
        df = pd.read_csv(filepath)
        return list(df.columns)
    except:
        pass
    return []

def get_xls_params(filepath):
    try:
        df = pd.read_excel(filepath)
        return list(df.columns)
    except:
        pass
    return []

def get_shapefile_params(filepath):
    try:
        sf = shapefile.Reader(filepath)
        fields = [f[0] for f in sf.fields[1:]] # first is DeletionFlag
        return fields
    except:
        pass
    return []

def get_raster_params(filepath):
    try:
        with rasterio.open(filepath) as src:
            return [f"Band_{i}" for i in src.indexes] + list(src.tags().keys())
    except:
        pass
    return []

def extract_all(datasets_dir):
    results = {}
    for root, dirs, files in os.walk(datasets_dir):
        for file in files:
            filepath = os.path.join(root, file)
            ext = os.path.splitext(file)[1].lower()
            params = []
            
            if ext == '.geojson':
                params = get_geojson_params(filepath)
            elif ext == '.parquet':
                params = get_parquet_params(filepath)
            elif ext == '.csv':
                params = get_csv_params(filepath)
            elif ext in ['.xls', '.xlsx']:
                params = get_xls_params(filepath)
            elif ext == '.shp':
                params = get_shapefile_params(filepath)
            elif ext in ['.tif', '.tiff']:
                params = get_raster_params(filepath)
                
            if params:
                rel_path = os.path.relpath(filepath, datasets_dir)
                results[rel_path] = params
                
    return results

if __name__ == '__main__':
    datasets_dir = r'd:\flood\datasets'
    params_dict = extract_all(datasets_dir)
    
    with open('parameters_list.json', 'w', encoding='utf-8') as f:
        json.dump(params_dict, f, indent=4)
