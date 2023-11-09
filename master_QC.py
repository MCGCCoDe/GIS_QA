import os
from simpledbf import Dbf5
import geopandas as gpd
import fiona 
from threading import Timer
from distutils.dir_util import copy_tree
import shutil 
from pathlib import Path
import gc


# Change the path below to the target folder:
dropbox_path = 'D:/QC_Warehouse/VALID'
path1 = 'D:\LM_Noman_Shapefiles'
topology_path = 'D:/QC_Warehouse/INVALID/TOPOLOGY'
reproject_path = 'D:/QC_Warehouse/INVALID/REPROJECT'
corrupt_path = 'D:/QC_Warehouse/INVALID/CORRUPT'
geometry_path = 'D:/QC_Warehouse/INVALID/GEOMETRY'
noSHX_path = 'D:/QC_Warehouse/INVALID/INDEX'

# This projection string is present in the .prj file if projection is UTM Zone36N:
projection_string = 'PROJCS["WGS_1984_UTM_Zone_36N",GEOGCS["GCS_WGS_1984",DATUM["D_WGS_1984",SPHEROID["WGS_1984",6378137.0,298.257223563]],PRIMEM["Greenwich",0.0],UNIT["Degree",0.0174532925199433]],PROJECTION["Transverse_Mercator"],PARAMETER["False_Easting",500000.0],PARAMETER["False_Northing",0.0],PARAMETER["Central_Meridian",33.0],PARAMETER["Scale_Factor",0.9996],PARAMETER["Latitude_Of_Origin",0.0],UNIT["Meter",1.0]]'

# These are the possible file extensions for a shapefile
extensions = ['.cpg', '.dbf', '.prj', '.sbn', '.sbx', '.shp', '.shx', '.xml']

# these counters keep track of the amount of files and errors

file_count = 0
prj_count = 0
empty_count = 0
geom_bad_count = 0
topo_bad_count = 0
no_shx_count = 0

print('Workin on it...')

# EXTRACT FROM DROPBOX TO LOCAL MACHINE:
copy_tree(dropbox_path, path1)

# Walk through the temp QA folder and do stuff:
for root, dirs, file in os.walk(path1):
    for name in file:      
                  
            if name.endswith(".prj"):
                root_name = Path(f'{name}').stem
                file_count += 1
                with open(f'{root}/{name}') as f:
                    first_line = f.readline()
                    if first_line == projection_string:                 
                        pass    
                    else:
                        prj_count += 1
                        print(f'Incorrect projection - {root}/{name}')
                        # # move non-projected shapefile (moves all associated sidecar files - if they exist)                        
                        for ex in extensions:
                            if os.path.isfile(f'{root}/{root_name}{ex}'):
                                shutil.copy2(f'{root}/{root_name}{ex}', f'{reproject_path}/{root_name}{ex}')
                            else:
                                print('No file of that kind exists') 

            if name.endswith(".dbf"):
                root_name = Path(f'{root}/{name}').stem
                attr_table = Dbf5(f'{root}/{name}')
                if attr_table.numrec < 1: 
                    empty_count += 1
                    print(f'{root}/{name} is corrupt')
                    # Move corrupt shapefile (moves all associated sidecar files - if they exist) 
                    for ex in extensions:
                            if os.path.isfile(f'{root}/{root_name}{ex}'):
                                shutil.copy2(f'{root}/{root_name}{ex}', f'{corrupt_path}/{root_name}{ex}')
                            else:
                                print('No file of that kind exists') 

            if name.endswith("shp"):
                    root_name = Path(f'{root}/{name}').stem
                    try: 
                        gdf = gpd.read_file(f'{root}/{name}')
                        geometry_results = gdf.is_valid.values
                        if False in geometry_results:
                            geom_bad_count += 1
                            print(f"There is a geometry error in {root}/{name}")
                            # Remove broken shapefile (moves all associated sidecar files - if they exist) 
                            for ex in extensions:
                                if os.path.isfile(f'{root}/{root_name}{ex}'):
                                    shutil.copy2(f'{root}/{root_name}{ex}', f'{geometry_path}/{root_name}{ex}')
                                else:
                                    print('No file of that kind exists')

                        if gdf.shape[0] < 200000:
                            sdf = gdf.sindex.query(gdf.geometry, predicate='overlaps')
                        if sdf.size != 0:
                            # Move overlapping shapefile (moves all associated sidecar files - if they exist) 
                            print(f'{root}/{name} - Shapefile has overlapping features')
                            topo_bad_count += 1
                            for ex in extensions:
                                    if os.path.isfile(f'{root}/{root_name}{ex}'):
                                        shutil.copy2(f'{root}/{root_name}{ex}', f'{topology_path}/{root_name}{ex}')
                                    else:
                                        print('No file of that kind exists')
                        else:
                            # clear memory to keep things speedy
                             gc.collect()
                    except fiona.errors.DriverError: 
                        print('{root}/{name} has no shx and wont be able to open')
                        no_shx_count += 1
                        for ex in extensions:
                            if os.path.isfile(f'{root}/{root_name}{ex}'):
                                shutil.copy2(f'{root}/{root_name}{ex}', f'{topology_path}/{root_name}{ex}')
                            else:
                                print('No file of that kind exists')
                        

print(f'{file_count} shapefiles have been checked')                 
print(f'{empty_count} files are corrupt and have been moved to the CORRUPT sub-folder') 
print(f'{prj_count} files need reprojecting and have been moved to the REPROJECT sub-folder')
print(f'{geom_bad_count} files have geometry errors and have been moved to the GEOMETRY sub-folder')
print(f'{topo_bad_count} files overlap and have been moved to the TOPOLOGY sub-folder')
print(f'{no_shx_count} files are missing shx and have been moved from the INDEX sub-folder')
             


