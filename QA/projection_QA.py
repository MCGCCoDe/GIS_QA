import os
from simpledbf import Dbf5
import geopandas as gpd
import fiona 
from threading import Timer
import shutil 
from pathlib import Path
import gc


def projection_check(path1, projection_string, reproject_path, extensions):
    global file_count
    file_count = 0
    global prj_count
    prj_count = 0
    # Walk through the users QA RAW folder and do stuff:
    for root, dirs, file in os.walk(path1):
        for name in file:      
    # 1. PROJECTION CHECK

                if name.endswith(".prj"):
                    root_name = Path(f'{name}').stem
                    file_count += 1
                    with open(f'{root}/{name}') as f:
                        first_line = f.readline()
                        if first_line == projection_string:  
                            # Shapefile is correctly projected, do nothing
                            pass    
                        else:
                            prj_count += 1
                            print(f'Incorrect projection - {root}/{name}')
                            # # move non-projected shapefile (moves all associated sidecar files - if they exist)                        
                            # for ex in extensions:
                            #     if os.path.isfile(f'{root}/{root_name}{ex}'):
                            #         shutil.move(f'{root}/{root_name}{ex}', f'{reproject_path}/{root_name}{ex}')
                         
    print(f'{file_count} shapefiles have been checked')  
    if file_count < 1:
        print('QA folders are initialised and ready to go, load in some raw shapefiles and run the program again')
    print(f'{prj_count} files need reprojecting and have been moved to the REPROJECT sub-folder')