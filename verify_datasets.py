import os
import json
import rasterio
import pandas as pd
import shapefile

def get_geojson_metadata(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        features = data.get('features', [])
        return {
            'format': 'GeoJSON',
            'features': len(features),
            'crs': data.get('crs', 'WGS84 (assumed)'),
            'status': '✅ VERIFIED' if len(features) > 0 else '❌ INVALID / REPLACE'
        }
    except Exception as e:
        return {'status': '❌ INVALID / REPLACE', 'error': str(e)}

def get_raster_metadata(filepath):
    try:
        with rasterio.open(filepath) as src:
            return {
                'format': 'GeoTIFF',
                'crs': str(src.crs),
                'width': src.width,
                'height': src.height,
                'bounds': [src.bounds.left, src.bounds.bottom, src.bounds.right, src.bounds.top],
                'status': '✅ VERIFIED'
            }
    except Exception as e:
        return {'status': '❌ INVALID / REPLACE', 'error': str(e)}

def get_parquet_metadata(filepath):
    try:
        df = pd.read_parquet(filepath)
        return {
            'format': 'Parquet',
            'rows': len(df),
            'columns': list(df.columns),
            'status': '✅ VERIFIED' if len(df) > 0 else '❌ INVALID / REPLACE'
        }
    except Exception as e:
        return {'status': '❌ INVALID / REPLACE', 'error': str(e)}

def get_shapefile_metadata(filepath):
    try:
        sf = shapefile.Reader(filepath)
        return {
            'format': 'Shapefile',
            'features': len(sf),
            'bbox': list(sf.bbox),
            'status': '✅ VERIFIED' if len(sf) > 0 else '❌ INVALID / REPLACE'
        }
    except Exception as e:
        return {'status': '❌ INVALID / REPLACE', 'error': str(e)}

def verify_all(raw_dir):
    report = []
    for root, dirs, files in os.walk(raw_dir):
        for file in files:
            filepath = os.path.join(root, file)
            category = os.path.basename(root)
            ext = os.path.splitext(file)[1].lower()
            meta = {
                'dataset_name': category,
                'file_name': file,
                'filepath': filepath
            }
            
            if ext == '.geojson':
                meta.update(get_geojson_metadata(filepath))
            elif ext in ['.tif', '.tiff']:
                meta.update(get_raster_metadata(filepath))
            elif ext == '.parquet':
                meta.update(get_parquet_metadata(filepath))
            elif ext == '.shp':
                meta.update(get_shapefile_metadata(filepath))
            elif ext in ['.pdf', '.jpg', '.tar.gz', '.zip']:
                meta['status'] = '❌ INVALID / REPLACE'
                meta['warning'] = f'Raw/compressed/document format {ext} not suitable for direct GIS processing.'
            else:
                meta['status'] = '⚠️ VERIFIED WITH LIMITATIONS'
                meta['warning'] = f'Format {ext} not explicitly checked.'

            report.append(meta)
            
    # Check for mandatory missing datasets
    categories_found = set(r['dataset_name'] for r in report)
    for req in ['flood', 'dem', 'boundaries', 'habitations', 'population', 'roads', 'rivers', 'facilities']:
        if req not in categories_found:
            report.append({
                'dataset_name': req,
                'file_name': 'MISSING',
                'status': '❌ INVALID / REPLACE',
                'warning': f'Mandatory category {req} has no files.'
            })
            
    return report

if __name__ == '__main__':
    raw_dir = r'd:\flood\data\raw'
    report = verify_all(raw_dir)
    out_path = r'd:\flood\data\metadata\data_inventory.json'
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=4)
    print(f'Verification report saved to {out_path}')
