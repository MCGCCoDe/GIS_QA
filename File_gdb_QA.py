import os

import geopandas as gpd
import fiona 
from threading import Timer
import shutil 
from pathlib import Path




path1 = 'D:/QC_Bucket/RAW'
valid_path = 'D:/QC_Bucket/VALID/QC_SHAPEFILES'
topology_path = 'D:/QC_Bucket/INVALID/TOPOLOGY'
reproject_path = 'D:/QC_Bucket/INVALID/REPROJECT'
geometry_path = 'D:/QC_Bucket/INVALID/GEOMETRY'



for root, dirs, file in os.walk('C:\Users\SeanGyuris\Downloads\Order_1W1KLI\ll_gda2020\filegdb\whole_of_dataset\victoria'):
    for name in dirs:   
        # Get all the layers from the .gdb file 
        try:
            layers = fiona.listlayers(f'{root}/{name}')
        
            # For each feature class, open and do stuff:
            for layer in layers:
                try:
                    gdf = gpd.read_file(f'{root}/{name}', layer=layer)
                    gdf.to_file(f'{path1}/{layer}.shp', driver='ESRI Shapefile')
                except fiona.errors.DriverSupportError as err:
                    print(f'There was a problem converting this feature class: {layer} -- {err}')
        except fiona.errors.DriverError as err:
            print(f'ERROR: Something happened when opening this gdb, is it a valid file geodatabase? {err} {name}')
            pass

