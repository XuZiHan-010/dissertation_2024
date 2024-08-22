from matplotlib.patches import Patch
import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors

# Define the URLs for the data
geojson_url = 'https://raw.githubusercontent.com/XuZiHan-010/dissertation_2024/main/data/los-angeles-county.geojson'
pm25_data_url = 'https://raw.githubusercontent.com/XuZiHan-010/dissertation_2024/main/data/merged_data.csv'

# Load the GeoJSON data directly from the URL
gdf = gpd.read_file(geojson_url)

# Load the merged data directly from the URL
merged_data = pd.read_csv(pm25_data_url)

# Merge the GeoDataFrame with the merged data on the appropriate key
merged_gdf = gdf.merge(merged_data, left_on='name', right_on='name', how='left')

boundary_norms_household_size = [2, 3, 4, 5, 6]
boundary_norms_white_population = [0, 0.25, 0.5, 0.75, 0.82]

# Define the custom color map
colors = ['#ffffb2', '#fecc5c', '#fd8d3c', '#F03B20', '#BD0026']
cmap = mcolors.ListedColormap(colors)

# Create the 2x2 grid of maps
fig, axes = plt.subplots(2, 2, figsize=(20, 20))

# Average Household Size map
norm_household_size = mcolors.BoundaryNorm(boundary_norms_household_size, cmap.N)
merged_gdf.plot(column='Average Household Size', cmap=cmap, norm=norm_household_size, linewidth=0.8, ax=axes[0, 0], edgecolor='0.8', legend=False, missing_kwds={'color': 'grey'})
axes[0, 0].set_title('Average Household Size in Los Angeles County', fontsize=20)
axes[0, 0].axis('off')
# Add legend for Average Household Size map
legend_labels_household_size = ['2-3', '3-4', '4-5', '5-6', 'Missing']
legend_colors_household_size = [plt.cm.ScalarMappable(norm=norm_household_size, cmap=cmap).to_rgba(i) for i in boundary_norms_household_size[:-1]] + ['grey']
patches = [Patch(color=color, label=label) for color, label in zip(legend_colors_household_size, legend_labels_household_size)]
axes[0, 0].legend(handles=patches, title="Household Size", loc='lower left')

# White Population map
norm_white_population = mcolors.BoundaryNorm(boundary_norms_white_population, cmap.N)
merged_gdf.plot(column='White Population', cmap=cmap, norm=norm_white_population, linewidth=0.8, ax=axes[0, 1], edgecolor='0.8', legend=False, missing_kwds={'color': 'grey'})
axes[0, 1].set_title('White Population Percentage in Los Angeles County', fontsize=20)
axes[0, 1].axis('off')
# Add legend for White Population map
legend_labels_white_population = ['<25%', '25%-50%', '50%-75%', '>75%', 'Missing']
legend_colors_white_population = [plt.cm.ScalarMappable(norm=norm_white_population, cmap=cmap).to_rgba(i) for i in boundary_norms_white_population[:-1]] + ['grey']
patches_white_population = [Patch(color=color, label=label) for color, label in zip(legend_colors_white_population, legend_labels_white_population)]
axes[0, 1].legend(handles=patches_white_population, title="White Population", loc='lower left')

# Median Earnings map
earnings_labels = ['< $31,000', '$31,000-$77,000', '> $77,000', 'Missing']
merged_gdf['Earnings Category'] = pd.cut(merged_gdf['Median Earnings'], bins=[0, 31000, 77000, 115856.71], labels=earnings_labels[:-1])
earnings_colors = ['#ffffb2', '#fd8d3c', '#BD0026', 'grey']
earnings_cmap = mcolors.ListedColormap(earnings_colors[:-1])
merged_gdf.plot(column='Earnings Category', cmap=earnings_cmap, linewidth=0.8, ax=axes[1, 0], edgecolor='0.8', legend=False, missing_kwds={'color': 'grey'})
axes[1, 0].set_title('Median Earnings in Los Angeles County', fontsize=20)
axes[1, 0].axis('off')
# Add legend for Median Earnings map
legend_colors_earnings = [earnings_cmap(i) for i in range(len(earnings_labels[:-1]))] + ['grey']
patches = [Patch(color=color, label=label) for color, label in zip(legend_colors_earnings, earnings_labels)]
axes[1, 0].legend(handles=patches, title="Earnings", loc='lower left')

# Median Household Income map
income_labels = ['< $65,000', '$65,000-$175,000', '> $175,000', 'Missing']
merged_gdf['Income Category'] = pd.cut(merged_gdf['Median Household Income'], bins=[0, 65000, 175000, 270018.47], labels=income_labels[:-1])
income_colors = ['#ffffb2', '#fd8d3c', '#BD0026', 'grey']
income_cmap = mcolors.ListedColormap(income_colors[:-1])
merged_gdf.plot(column='Income Category', cmap=income_cmap, linewidth=0.8, ax=axes[1, 1], edgecolor='0.8', legend=False, missing_kwds={'color': 'grey'})
axes[1, 1].set_title('Median Household Income in Los Angeles County', fontsize=20)
axes[1, 1].axis('off')
# Add legend for Income map
legend_colors_income = [income_cmap(i) for i in range(len(income_labels[:-1]))] + ['grey']
patches = [Patch(color=color, label=label) for color, label in zip(legend_colors_income, income_labels)]
axes[1, 1].legend(handles=patches, title="Household Income", loc='lower left')

# Adjust layout and save the figure
plt.tight_layout()
plt.savefig('figure/socio_ethnic.png', dpi=800, bbox_inches='tight')
plt.show()
