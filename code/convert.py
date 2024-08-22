import pandas as pd
import geopandas as gpd
import requests
import io

# Load the CSV data from GitHub
csv_url = 'https://raw.githubusercontent.com/XuZiHan-010/dissertation_2024/main/data/merged_data.csv'
response = requests.get(csv_url)
csv_data = response.content
df = pd.read_csv(io.StringIO(csv_data.decode('utf-8')))

# Convert percentage strings to decimals
columns_to_convert = ['White Population', 'Unemployment Rate', 'Labor Force Participation Rate', 'Public Transit',
                      'Works from Home', 'Bikes or Walks', 'Drives Alone', 'Carpools', 'Bachelor\'s Degree or Higher',
                      'Vehicle Ownership', 'Associate\'s Degree', 'Commute Time Above 30 Minutes']

def convert_percentage(percentage_str):
    if isinstance(percentage_str, str):
        return float(percentage_str.strip().strip('%')) / 100
    return percentage_str

for column in columns_to_convert:
    df[column] = df[column].apply(convert_percentage)

# Adjust 'Vehicle Ownership' and 'Commute Time Below 30 Minutes'
df['Vehicle Ownership'] = (1 - df['Vehicle Ownership']).round(2)
df['Commute Time Below 30 Minutes'] = (1 - df['Commute Time Above 30 Minutes']).round(2)

# Load the GeoJSON data from GitHub
geojson_url = 'https://raw.githubusercontent.com/XuZiHan-010/dissertation_2024/main/data/los-angeles-county.geojson'
geo_df = gpd.read_file(geojson_url)

# Step 5: Merge the CSV data with the GeoJSON data based on the common key 'name'
merged_df = geo_df.merge(df, how='left', on='name')

# Calculate the area of each polygon in the GeoJSON data
merged_df = merged_df.to_crs(epsg=3395)  # Set CRS to a projected system for accurate area calculation
merged_df['Area'] = merged_df['geometry'].area  # Area is calculated in square meters

# Compute the population density (Population / Area in square kilometers)
merged_df['Population Density'] = merged_df['total_pop'] / (merged_df['Area'] / 1e6)  # Area converted to square kilometers

# Add the Population Density to the original DataFrame (df)
df = df.merge(merged_df[['name', 'Population Density']], how='left', on='name')

# Save the modified DataFrame to a CSV file
output_file_path = 'data/merged_data_converted.csv'
df.to_csv(output_file_path, index=False)


print(df.head())
