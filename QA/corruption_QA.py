import os
from simpledbf import Dbf5
import geopandas as gpd
import fiona 
from threading import Timer
import shutil 
from pathlib import Path
import gc


def corruption_check(path1, corrupt_path, extensions):
    global empty_count
    empty_count = 0
    # Walk through the users QA RAW folder and do stuff:
    for root, dirs, file in os.walk(path1):
        for name in file: 
            if name.endswith(".dbf"):
                root_name = Path(f'{root}/{name}').stem
                attr_table = Dbf5(f'{root}/{name}')
                if attr_table.numrec < 1: 
                    empty_count += 1
                    print(f'{root}/{name} is corrupt')
                    # Move corrupt shapefile (moves all associated sidecar files - if they exist) 
                    for ex in extensions:
                            if os.path.isfile(f'{root}/{root_name}{ex}'):
                                shutil.move(f'{root}/{root_name}{ex}', f'{corrupt_path}/{root_name}{ex}')
                    
    print(f'{empty_count} files are corrupt and have been moved to the CORRUPT sub-folder')