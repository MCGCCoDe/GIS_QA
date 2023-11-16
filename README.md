# ETL component 1 - QA testing (spatial data)

### This program runs the following four spatial QA checks on shapefile inputs (or a folder of multiple shapefiles):

- Shapefile projection 
- Shapefile corruption (an empty geometry or .dbf)
- Geometry errors
- Topology Overlap errors (e.g. slivers)
- Mising index (no .shx) 

### How it works

'RAW' shapefiles are to be manually loaded into a local directory by the user ':D\QC_BUCKET\RAW'. This can be set up manually or is automatically built when the program first runs.

The program reads from this RAW folder, checks for the above conditions, then distributes each file into:

- <em>'D:\QC_BUCKET\INVALID\CORRUPT'</em> if the shapefile is empty/corrupt
- <em>'D:\QC_BUCKET\INVALID\GEOMETRY'</em>  if the shapefile has a geometry error
- <em>'D:\QC_BUCKET\INVALID\INDEX'</em>  if the shapefile is missing its .shp sidecar
- <em>'D:\QC_BUCKET\INVALID\REPROJECT'</em>  if the shapefile needs to be re-projected
- <em>'D:\QC_BUCKET\INVALID\TOPOLOGY'</em>  if the shapefile has a topology error

Files that pass are deemed eligable to be loaded into a data store (not included in this program). 

Files that fail are moved to relevant local folders to be QC'd by the next component of the ETL pipeline (not included in this program). 

Shapefile_QA.py is the entry. The program requires some GDAL dependancies that are tricky to install on windows. A packaged .exe is on its way 

## To run (currently for internal use only)

- Click open the .exe 
- If QC_BUCKET folders have not been manually set up, the program will first build these 
- Re-run the program once the RAW folder has been loaded with shapefiles