import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import geopandas as gpd

# Load the GeoJSON and CSV data
geojson_url = 'https://raw.githubusercontent.com/XuZiHan-010/dissertation_2024/main/data/los-angeles-county.geojson'
merged_data_url = 'https://raw.githubusercontent.com/XuZiHan-010/dissertation_2024/main/data/merged_data_converted.csv'

# Load the data
gdf = gpd.read_file(geojson_url)
merged_data = pd.read_csv(merged_data_url)

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

# Define high and low exposure areas
high_exposure_areas = merged_gdf[
    (merged_gdf['PM2.5 Concentration'] >= 12) &
    (merged_gdf['Traffic Impacts Percentile'] >= 66) &
    ((merged_gdf['Vehicle Ownership'] >= 0.9) & (merged_gdf['Drives Alone'] >= 0.7)) &
    (merged_gdf['Commute Time Below 30 Minutes'] >= 0.55) & (merged_gdf['Population Density'] >=1000)
]

low_exposure_areas = merged_gdf[
    (merged_gdf['PM2.5 Concentration'] >= 12) &
    (merged_gdf['Traffic Impacts Percentile'] >= 66) &
    ((((merged_gdf['Drives Alone'] >= 0.7) & (merged_gdf['Population Density'] <= 914)) | (merged_gdf['Drives Alone'] <= 0.65)) | (merged_gdf['Vehicle Ownership'] <= 0.9)) & (merged_gdf['Population Density'] <= 913)
]

# Descriptive Statistics
high_stats = high_exposure_areas[columns_to_convert].describe()
low_stats = low_exposure_areas[columns_to_convert].describe()

# Save descriptive statistics to CSV
high_stats.to_csv('table/high_exposure_stats.csv')
low_stats.to_csv('table/low_exposure_stats.csv')

# Correlation Matrices
high_corr = high_exposure_areas[columns_to_convert].corr()
low_corr = low_exposure_areas[columns_to_convert].corr()

# Plotting High Exposure Correlation Matrix
plt.figure(figsize=(14, 8))
sns.heatmap(high_corr, annot=True, cmap='coolwarm', vmin=-1, vmax=1)
plt.savefig('figure/high_exposure_correlation.png', dpi=800, bbox_inches='tight')
plt.show()

# Plotting Low Exposure Correlation Matrix
plt.figure(figsize=(14, 8))
sns.heatmap(low_corr, annot=True, cmap='coolwarm', vmin=-1, vmax=1)
plt.savefig('figure/low_exposure_correlation.png', dpi=800, bbox_inches='tight')
plt.show()
