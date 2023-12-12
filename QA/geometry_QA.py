import os
from simpledbf import Dbf5
import geopandas as gpd
import fiona 
from threading import Timer
import shutil 
from pathlib import Path
import gc


def geometry_check(path1, noSHX_path, geometry_path, extensions):
    global geom_bad_count
    geom_bad_count = 0
    global no_shx_count
    no_shx_count = 0
    global geom_count 
    geom_count = 0
    # Walk through the users QA RAW folder and do stuff:
    for root, dirs, file in os.walk(path1):
        for name in file:  
            if name.endswith("shp"):
                            geom_count += 1
                            root_name = Path(f'{root}/{name}').stem
                            try: 
                                gdf = gpd.read_file(f'{root}/{name}')
                                # We only check Topology/Geometry errors for polygons and multilines
                                if 'Point' in gdf.geom_type:
                                    pass
                                else:
                                    geometry_results = gdf.is_valid.values
                                    if False in geometry_results:
                                        geom_bad_count += 1
                                        print(f"There is a geometry error in {root}/{name}")
                                        # Remove broken shapefile (moves all associated sidecar files - if they exist) 
                                        # for ex in extensions:
                                        #     if os.path.isfile(f'{root}/{root_name}{ex}'):
                                        #         shutil.move(f'{root}/{root_name}{ex}', f'{geometry_path}/{root_name}{ex}') 
                                        
                            except fiona.errors.DriverError: 
                                print('{root}/{name} has no shx and wont be able to open') 
                 
                                no_shx_count += 1 
                                for ex in extensions: 
                                    if os.path.isfile(f'{root}/{root_name}{ex}'): 
                                        shutil.copy2(f'{root}/{root_name}{ex}', f'{noSHX_path}/{root_name}{ex}')
    print(f'{geom_count} files were checked for geometry') 
    print(f'{geom_bad_count} files have geometry errors and have been moved to the GEOMETRY sub-folder')
    print(f'{no_shx_count} files are missing shx and have been moved from the INDEX sub-folder')
                               
        