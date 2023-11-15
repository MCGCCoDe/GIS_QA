import os
from simpledbf import Dbf5
import geopandas as gpd
import fiona 
from threading import Timer
import shutil 
from pathlib import Path
import gc


def topology_check(path1, noSHX_path, topology_path, extensions):
    global topo_bad_count
    topo_bad_count = 0
    global topo_count
    topo_count = 0
    # Walk through the users QA RAW folder and do stuff:
    for root, dirs, file in os.walk(path1):
        for name in file:  
            if name.endswith("shp"):
                            topo_count += 1
                            root_name = Path(f'{root}/{name}').stem
                            try: 
                               # Some shapefiles are large, this clears memory after each one to keep things speedy
                                if os.path.getsize(f'{root}/{name}') < 2000000:
                                    print(f'checking {name} for overlaps')
                                    gc.collect() 
                                    gdf = gpd.read_file(f'{root}/{name}')
                                    # We only check Topology/Geometry errors for polygons and multilines
                                    if 'Point' in gdf.geom_type:
                                        pass
                                    else:
                                        sdf = gdf.sindex.query(gdf.geometry, predicate='overlaps')
                                        if sdf.size != 0:
                                            # Move overlapping shapefile (moves all associated sidecar files - if they exist) 
                                            print(f'There is an overlap in {root}/{name}')
                                            topo_bad_count += 1
                                            for ex in extensions:
                                                    if os.path.isfile(f'{root}/{root_name}{ex}'):
                                                        shutil.move(f'{root}/{root_name}{ex}', f'{topology_path}/{root_name}{ex}')
                                # bigger files (2mb) need to be topology checked in software...
                                else: 
                                    for ex in extensions:
                                                    if os.path.isfile(f'{root}/{root_name}{ex}'):
                                                        shutil.move(f'{root}/{root_name}{ex}', f'{topology_path}/{root_name}{ex}')     
                                
                                       
                                    
                            except fiona.errors.DriverError: 
                                print('{root}/{name} has no shx and wont be able to open')
                                for ex in extensions:
                                    if os.path.isfile(f'{root}/{root_name}{ex}'):
                                        shutil.copy2(f'{root}/{root_name}{ex}', f'{noSHX_path}/{root_name}{ex}')

    print(f'{topo_count} files were checked for overlapping polygons')                                    
    print(f'{topo_bad_count} files overlap and have been moved to the TOPOLOGY sub-folder')                                