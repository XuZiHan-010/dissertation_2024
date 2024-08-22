from matplotlib.patches import Patch
import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors

# Load the data
geojson_url = 'https://raw.githubusercontent.com/XuZiHan-010/dissertation_2024/main/data/los-angeles-county.geojson'
pm25_data_url = 'https://raw.githubusercontent.com/XuZiHan-010/dissertation_2024/main/data/merged_data.csv'
gdf = gpd.read_file(geojson_url)

merged_data = pd.read_csv(pm25_data_url)
merged_gdf = gdf.merge(merged_data, left_on='name', right_on='name', how='left')

# Boundary norms for each column
boundary_norms_pm25 = [0, 12, merged_gdf['PM2.5 Concentration'].max()]
boundary_norms_ev_count = [0, 36, 92, 160, 317, 1525]
boundary_norms_traffic_impacts = [0, 23, 42, 58, 73, 98]
boundary_norms_vehicle_ownership = [0, 6, 11, 19, 29, 35]

# Define the custom color map
colors = ['#ffffb2', '#fecc5c', '#fd8d3c', '#F03B20', '#BD0026']
cmap = mcolors.ListedColormap(colors)

# Create the 2x2 grid of maps
fig, axes = plt.subplots(2, 2, figsize=(20, 20))

# PM2.5 Concentration map
norm_pm25 = mcolors.BoundaryNorm(boundary_norms_pm25, cmap.N)
merged_gdf.plot(column='PM2.5 Concentration', cmap=cmap, norm=norm_pm25, linewidth=0.8, ax=axes[0, 0], edgecolor='0.8', legend=False, missing_kwds={'color': 'grey'})
axes[0, 0].set_title('PM2.5 Concentration in Los Angeles County', fontsize=20)
axes[0, 0].axis('off')
# Add legend for PM2.5 map
legend_labels_pm25 = ['Below 12', 'Above 12', 'Missing']
legend_colors_pm25 = [plt.cm.ScalarMappable(norm=norm_pm25, cmap=cmap).to_rgba(i) for i in boundary_norms_pm25[:-1]] + ['grey']
patches = [Patch(color=color, label=label) for color, label in zip(legend_colors_pm25, legend_labels_pm25)]
axes[0, 0].legend(handles=patches, title="PM2.5 (µg/m³)", loc='lower left')

# Total EV Count map
norm_ev_count = mcolors.BoundaryNorm(boundary_norms_ev_count, cmap.N)
merged_gdf.plot(column='total_ev_count', cmap=cmap, norm=norm_ev_count, linewidth=0.8, ax=axes[0, 1], edgecolor='0.8', legend=False, missing_kwds={'color': 'grey'})
axes[0, 1].set_title('Total EV Count in Los Angeles County', fontsize=20)
axes[0, 1].axis('off')
# Add legend for Total EV Count map
legend_labels_ev_count = ['Below 36', '36-92', '92-160', '160-317', 'Above 317', 'Missing']
legend_colors_ev_count = [plt.cm.ScalarMappable(norm=norm_ev_count, cmap=cmap).to_rgba(i) for i in boundary_norms_ev_count[:-1]] + ['grey']
patches = [Patch(color=color, label=label) for color, label in zip(legend_colors_ev_count, legend_labels_ev_count)]
axes[0, 1].legend(handles=patches, title="EV Count", loc='lower left')

# Traffic Impacts map
norm_traffic_impacts = mcolors.BoundaryNorm(boundary_norms_traffic_impacts, cmap.N)
merged_gdf.plot(column='Traffic Impacts Percentile', cmap=cmap, norm=norm_traffic_impacts, linewidth=0.8, ax=axes[1, 0], edgecolor='0.8', legend=False, missing_kwds={'color': 'grey'})
axes[1, 0].set_title('Traffic Impacts in Los Angeles County', fontsize=20)
axes[1, 0].axis('off')
# Add legend for Traffic Impacts map
legend_labels_traffic_impacts = ['Below 23', '23-42', '42-58', '58-73', 'Above 73', 'Missing']
legend_colors_traffic_impacts = [plt.cm.ScalarMappable(norm=norm_traffic_impacts, cmap=cmap).to_rgba(i) for i in boundary_norms_traffic_impacts[:-1]] + ['grey']
patches = [Patch(color=color, label=label) for color, label in zip(legend_colors_traffic_impacts, legend_labels_traffic_impacts)]
axes[1, 0].legend(handles=patches, title="Traffic Impacts", loc='lower left')

# Vehicle Ownership map
norm_vehicle_ownership = mcolors.BoundaryNorm(boundary_norms_vehicle_ownership, cmap.N)
merged_gdf.plot(column='Vehicle Ownership', cmap=cmap, norm=norm_vehicle_ownership, linewidth=0.8, ax=axes[1, 1], edgecolor='0.8', legend=False, missing_kwds={'color': 'grey'})
axes[1, 1].set_title('Vehicle Ownership in Los Angeles County', fontsize=20)
axes[1, 1].axis('off')
# Add legend for Vehicle Ownership map
legend_labels_vehicle_ownership = ['Below 6%', '6-11%', '11-19%', '19-29%', 'Above 29%', 'Missing']
legend_colors_vehicle_ownership = [plt.cm.ScalarMappable(norm=norm_vehicle_ownership, cmap=cmap).to_rgba(i) for i in boundary_norms_vehicle_ownership[:-1]] + ['grey']
patches = [Patch(color=color, label=label) for color, label in zip(legend_colors_vehicle_ownership, legend_labels_vehicle_ownership)]
axes[1, 1].legend(handles=patches, title="Vehicle Ownership", loc='lower left')

# Adjust layout and save the figure
plt.tight_layout()
plt.savefig('figure/pm2.5_vehicle.png', dpi=800, bbox_inches='tight')
plt.show()
