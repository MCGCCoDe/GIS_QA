# ETL component - QA testing (spatial data)

### This program runs four QA checks on shapefile inputs (or a folder of multiple shapefiles)

- Shapefile projection 
- Shapefile corruption (an empty geom or .dbf)
- Geometry errors
- Topology Overlap errors (e.g. slivers)
- Mising index (no .shx) 

Files that pass are deemed eligable to be loaded into a data store (not included in this program). 

Files that fail are moved to relevant local folders to be QC'd by the next component of the ETL pipeline (not included in this program). 

To run the file, a GDAL installation is required. 