import rasterio
import numpy as np
import os

habitations = [
    {"name": "Jonai Bazar", "lat": 27.766, "lon": 95.166},
    {"name": "Murkongselek Station Area", "lat": 27.781, "lon": 95.172},
    {"name": "Laimekuri", "lat": 27.745, "lon": 95.140},
    {"name": "Rayang", "lat": 27.795, "lon": 95.185},
    {"name": "Dekapam", "lat": 27.750, "lon": 95.190},
    {"name": "Bahir Sille", "lat": 27.810, "lon": 95.150},
    {"name": "Dimow", "lat": 27.730, "lon": 95.120},
    {"name": "Simen Chapori", "lat": 27.680, "lon": 94.980},
    {"name": "Ramdhan", "lat": 27.770, "lon": 95.110},
    {"name": "Oiramghat", "lat": 27.820, "lon": 95.200}
]

dates = ['11jul', '18jul', '22jul', '28jul']
for d in dates:
    p = f"d:/flood/data/flood/hazard_map_{d}.tif"
    if not os.path.exists(p): continue
    src = rasterio.open(p)
    data = src.read(1)
    print(f"=== Date: {d} ===")
    for h in habitations:
        r, c = src.index(h['lon'], h['lat'])
        # Try a few window sizes
        w50 = int(np.max(data[max(0,r-50):min(src.height,r+51), max(0,c-50):min(src.width,c+51)]))
        w70 = int(np.max(data[max(0,r-70):min(src.height,r+71), max(0,c-70):min(src.width,c+71)]))
        w90 = int(np.max(data[max(0,r-90):min(src.height,r+91), max(0,c-90):min(src.width,c+91)]))
        print(f"  {h['name']}: w50={w50}, w70={w70}, w90={w90}")
