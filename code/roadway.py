import geopandas as gpd
import matplotlib.pyplot as plt
import contextily as ctx
from shapely.geometry import box


la_county_geojson = 'data/los-angeles-county.geojson'
la_county = gpd.read_file(la_county_geojson)
freeways_shapefile = 'data/roadway/los-angeles-county-freeways.shp'
freeways = gpd.read_file(freeways_shapefile)


freeways = freeways.to_crs(la_county.crs)

fig, ax = plt.subplots(figsize=(12, 12))  # Increase figure size

# Plot the Los Angeles County GeoJSON data
la_county.plot(ax=ax, color='none', edgecolor='black', label='LA County Border')

# Plot the major freeways on top of the GeoJSON data
freeways.plot(ax=ax, color='blue', linewidth=1, label='Major Freeways')

# Add basemap from OpenStreetMap
ctx.add_basemap(ax, crs=la_county.crs.to_string(), source=ctx.providers.OpenStreetMap.Mapnik)

# Mask the area outside the Los Angeles County and add grey overlay
outside_county = box(ax.get_xlim()[0], ax.get_ylim()[0], ax.get_xlim()[1], ax.get_ylim()[1])
outside_county = gpd.GeoSeries(outside_county, crs=la_county.crs).difference(la_county.unary_union)
outside_county = gpd.GeoDataFrame(geometry=gpd.GeoSeries(outside_county), crs=la_county.crs)
outside_county.plot(ax=ax, color='grey', alpha=0.5, zorder=2)  # Semi-transparent grey overlay




blue_line = plt.Line2D([0], [0], color='blue', linewidth=1, label='Major Freeways')
black_line = plt.Line2D([0], [0], color='black', linewidth=1, label='LA County Border')
ax.legend(handles=[blue_line, black_line], loc='upper right')
ax.set_axis_off()


plt.savefig('figure/roadway.png', dpi=600, bbox_inches='tight', pad_inches=0.1)
plt.show()