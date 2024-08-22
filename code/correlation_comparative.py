import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import geopandas as gpd
from matplotlib import patheffects

# Load the GeoJSON and CSV data
geojson_url = 'https://raw.githubusercontent.com/XuZiHan-010/dissertation_2024/main/data/los-angeles-county.geojson'
merged_data_url = 'https://raw.githubusercontent.com/XuZiHan-010/dissertation_2024/main/data/merged_data_converted.csv'

# Load the data
gdf = gpd.read_file(geojson_url)
merged_data = pd.read_csv(merged_data_url)
roadway_path = 'data/roadway/los-angeles-county-freeways.shp'

roadways = gpd.read_file(roadway_path)

# Ensure the CRS matches between the GeoDataFrames
roadways = roadways.to_crs(gdf.crs)

# Merge the GeoDataFrame with the CSV data on the appropriate key
merged_gdf = gdf.merge(merged_data, left_on='name', right_on='name', how='left')

# Convert relevant columns to numeric values and handle missing data
columns_to_convert = [
    'Vehicle Ownership', 'Drives Alone', 'Public Transit',
    'Traffic Impacts Percentile', 'PM2.5 Concentration', 'total_ev_count',
    'Bikes or Walks', 'Carpools', 'Works from Home',
    'Median Household Income', 'Unemployment Rate', 'Bachelor\'s Degree or Higher',
    'Commute Time Below 30 Minutes','Population Density'
]
for col in columns_to_convert:
    merged_gdf[col] = pd.to_numeric(merged_gdf[col], errors='coerce')

# Drop rows with missing values in any of the columns of interest
merged_gdf.dropna(subset=columns_to_convert, inplace=True)

# Identify high and low exposure areas
high_exposure_areas = merged_gdf[
    (merged_gdf['PM2.5 Concentration'] >= 12) &
    (merged_gdf['Traffic Impacts Percentile'] >= 66) &
    ((merged_gdf['Vehicle Ownership'] >= 0.9) & (merged_gdf['Drives Alone'] >= 0.7)) &
    (merged_gdf['Commute Time Below 30 Minutes'] >= 0.55) & (merged_gdf['Population Density'] >= 1000)
]

low_exposure_areas_new = merged_gdf[
    (merged_gdf['PM2.5 Concentration'] >= 12) &
    (merged_gdf['Traffic Impacts Percentile'] >= 66) &
   ((((merged_gdf['Drives Alone'] >= 0.7) & (merged_gdf['Population Density'] <= 914)) |
      (merged_gdf['Drives Alone'] <= 0.65)) | (merged_gdf['Vehicle Ownership'] <= 0.9)) &
      (merged_gdf['Population Density'] <= 913)
]

# High Exposure Areas Plot
fig, ax = plt.subplots(figsize=(12, 8))
merged_gdf.plot(ax=ax, color='lightgrey', edgecolor='black')  # Background map
high_exposure_areas.plot(ax=ax, color='red', edgecolor='black', label='High PM2.5 Areas')
low_exposure_areas_new.plot(ax=ax, color='yellow', edgecolor='black', label='Low PM2.5 Areas')
roadways.plot(ax=ax, color='blue', linewidth=0.5)  # Overlay roadways
ax.set_axis_off()

# Label positions - placing in blank areas and using longer arrows
label_positions = {
    "Del Aire": (-119.0, 33.7),
    "Harbor Gateway": (-119.0, 33.8),
    "Hawthorne": (-119.0, 33.9),
    "Lawndale": (-119.0, 33.95),
    "West Carson": (-119.0, 33.9),
    "Commerce": (-118.0, 33.95),
    "Diamond Bar": (-117.5, 34.1),
    "Elysian Park": (-118.0, 34.15),
    "Hollywood Hills": (-118.0, 34.2),
    "Industry": (-117.8, 34.1),
    "Irwindale": (-117.5, 34.1),
    "Ladera Heights": (-119.0, 34.0),
    "Rancho Dominguez": (-119.0, 33.8),
    "Santa Fe Springs": (-117.8, 33.8),
    "Vernon": (-118.0, 33.92),
    "Veterans Administration": (-118.0, 34.3),
    "Whittier Narrows": (-118.0, 34.05)
}

# Manually adjust the positions of the labels to avoid overlapping with features
for idx, row in high_exposure_areas.iterrows():
    label_pos = label_positions.get(row['name'], (row.geometry.centroid.x, row.geometry.centroid.y))
    ax.annotate(row['name'], xy=(row.geometry.centroid.x, row.geometry.centroid.y),
                xytext=label_pos,  # Adjusted to move the label to blank area
                textcoords='data', arrowprops=dict(arrowstyle="->", color='black', lw=1.5),
                fontsize=10, color='black',
                path_effects=[patheffects.withStroke(linewidth=3, foreground="white")])

# Add arrows and text for low exposure areas affected by others
for idx, row in low_exposure_areas_new.iterrows():
    label_pos = label_positions.get(row['name'], (row.geometry.centroid.x, row.geometry.centroid.y))
    ax.annotate(row['name'], xy=(row.geometry.centroid.x, row.geometry.centroid.y),
                xytext=label_pos,  # Adjusted to move the label to blank area
                textcoords='data', arrowprops=dict(arrowstyle="->", color='black', lw=1.5),
                fontsize=10, color='black',
                path_effects=[patheffects.withStroke(linewidth=3, foreground="white")])

# Create and place the legend
handles = [
    plt.Line2D([0], [0], color='red', lw=6, label='Air pollution mostly created by itself'),
    plt.Line2D([0], [0], color='yellow', lw=6, label='Air pollution mostly affected by others'),
    plt.Line2D([0], [0], color='blue', linewidth=1, lw=1, label='Major Roadways in Los Angeles County')
]
legend = ax.legend(handles=handles, loc='upper right', fontsize='medium', title='Legend')

plt.tight_layout()
plt.savefig('figure/comparative_analysis.png', dpi=800, bbox_inches='tight')
plt.show()
