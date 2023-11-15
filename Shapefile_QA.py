import os
from simpledbf import Dbf5
import geopandas as gpd
import fiona 
from threading import Timer
import shutil 
from pathlib import Path
import gc


# These folders will be set up on the users D: drive
path1 = 'D:/QC_Bucket/RAW/'
valid_path = 'D:/QC_Bucket/VALID/QC_SHAPEFILES/'
topology_path = 'D:/QC_Bucket/INVALID/TOPOLOGY/'
reproject_path = 'D:/QC_Bucket/INVALID/REPROJECT/'
corrupt_path = 'D:/QC_Bucket/INVALID/CORRUPT/'
geometry_path = 'D:/QC_Bucket/INVALID/GEOMETRY/'
noSHX_path = 'D:/QC_Bucket/INVALID/INDEX/'

pathlist = [path1, valid_path, topology_path, reproject_path, corrupt_path, geometry_path, noSHX_path]

# This projection string is present in the .prj file if projection is UTM Zone36N (NEOMs projection):
projection_string = 'PROJCS["WGS_1984_UTM_Zone_36N",GEOGCS["GCS_WGS_1984",DATUM["D_WGS_1984",SPHEROID["WGS_1984",6378137.0,298.257223563]],PRIMEM["Greenwich",0.0],UNIT["Degree",0.0174532925199433]],PROJECTION["Transverse_Mercator"],PARAMETER["False_Easting",500000.0],PARAMETER["False_Northing",0.0],PARAMETER["Central_Meridian",33.0],PARAMETER["Scale_Factor",0.9996],PARAMETER["Latitude_Of_Origin",0.0],UNIT["Meter",1.0]]'

# These are the possible file extensions for a shapefile so they get moved together as one
extensions = ['.cpg', '.dbf', '.prj', '.sbn', '.sbx', '.shp', '.shx', '.xml']

# These counters keep track of the amount of files and errors
file_count = 0
prj_count = 0
empty_count = 0
geom_bad_count = 0
topo_bad_count = 0
no_shx_count = 0

# Start of program
print('Workin on it...')
print('Creating folders if they dont already exist...')

for path in pathlist:
    os.makedirs(os.path.dirname(path), exist_ok=True)

print('Folders have been set up')

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
                        for ex in extensions:
                            if os.path.isfile(f'{root}/{root_name}{ex}'):
                                shutil.copy2(f'{root}/{root_name}{ex}', f'{reproject_path}/{root_name}{ex}')
                            else:
                                print('No file of that kind exists') 
# 2. CORRUPTION CHECK

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

# 3. SHAPEFILE GEOMETRY CHECK

            if name.endswith("shp"):
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
                                for ex in extensions:
                                    if os.path.isfile(f'{root}/{root_name}{ex}'):
                                        shutil.copy2(f'{root}/{root_name}{ex}', f'{geometry_path}/{root_name}{ex}')
                                    else:
                                        print('No file of that kind exists')
            
# 4. SHAPEFILE TOPOLOGY/OVERLAP CHECK

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
                                # Some shapefiles are large, this clears memory after each one to keep things speedy
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
if file_count < 1:
    print('QA folders are initialised, load in some raw shapefiles and run the program again')
else:               
    print(f'{empty_count} files are corrupt and have been moved to the CORRUPT sub-folder') 
    print(f'{prj_count} files need reprojecting and have been moved to the REPROJECT sub-folder')
    print(f'{geom_bad_count} files have geometry errors and have been moved to the GEOMETRY sub-folder')
    print(f'{topo_bad_count} files overlap and have been moved to the TOPOLOGY sub-folder')
    print(f'{no_shx_count} files are missing shx and have been moved from the INDEX sub-folder')
             


