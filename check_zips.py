import zipfile
import os

files = [
    r"D:\flood\datasets\flood data\S1A_IW_GRDH_1SDV_20260628T233812_20260628T233841_065176_083757_60CD.zip.crdownload",
    r"D:\flood\datasets\flood data\S1D_IW_GRDH_1SDV_20260703T114808_20260703T114833_003509_00636A_6078.zip.crdownload"
]

for f in files:
    print(f"Checking {f}")
    try:
        with zipfile.ZipFile(f, 'r') as z:
            manifests = [n for n in z.namelist() if 'manifest.safe' in n]
            print(f"Manifests found: {manifests}")
            if manifests:
                content = z.read(manifests[0]).decode('utf-8')
                print(f"Successfully read manifest.safe ({len(content)} bytes)")
    except Exception as e:
        print(f"Error: {e}")
