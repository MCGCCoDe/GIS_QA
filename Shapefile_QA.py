import os
from simpledbf import Dbf5
import geopandas as gpd
import fiona 
from threading import Timer
import shutil 
from pathlib import Path
import gc

from QA.projection_QA import *
from QA.corruption_QA import * 
from QA.geometry_QA import *
from QA.topology_QA import *
from QA.move_valid import *

# need to implement os path joins to reduce string concat errors...

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
extensions = ['.cpg', '.dbf', '.prj', '.sbn', '.sbx', '.shp', '.shx', '.xml', '.qmd', '.qix']


# Start of program
print('Workin on it...')
print('Creating folders if they dont already exist...')

for path in pathlist:
    os.makedirs(os.path.dirname(path), exist_ok=True)

print('Folders have been set up')

# EACH OF THESE FUNCTIONS = ONE ITERATION OF OF THE RAW FILE FOLDER: File numbers get culled based on whether they pass the previous test
     
# 1. PROJECTION CHECK
projection_check(path1, projection_string, reproject_path, extensions)

# 2. CORRUPTION CHECK
corruption_check(path1, corrupt_path, extensions)

# 3. SHAPEFILE GEOMETRY CHECK
geometry_check(path1, noSHX_path, geometry_path, extensions)
           
# 4. SHAPEFILE TOPOLOGY/OVERLAP CHECK
topology_check(path1, noSHX_path, topology_path, extensions)      
                        
# ONCE EACH TEST IS COMPLETED, THE REMAINDING FILES SHOULD BE 'VALID': So they are moved to the valid folder:
move_valid(path1, valid_path, extensions)


