import geopandas as gpd
import matplotlib.pyplot as plt
import matplotlib

file_names = ['Abbotsford', 'Alphington', 'ChristmasHills', 'Coldstream', 'Heidelberg', 'Templestowe', 'Warrandyte', 'YarraGlen']
numb = 0
f, ax = plt.subplots()

for i in file_names:
    i = gpd.read_file(f'D:/YARRA DATA/SPATIAL/Flow Rates/{i}DailyRiverFlow_XYTableToPoint.shp')
    i.to_crs(i.crs).plot("Max_flow_1", ax=ax)
    
gdf = gpd.read_file(f'D:/YARRA DATA/SPATIAL/Flow Rates/Yarra Catchment Rivers.shp')
gdf.plot(ax=ax)

# gdf2.plot()
plt.savefig('image.jpg')

