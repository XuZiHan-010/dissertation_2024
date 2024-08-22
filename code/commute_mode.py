import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from matplotlib.patches import Patch

# Load the data
geojson_url = 'https://raw.githubusercontent.com/XuZiHan-010/dissertation_2024/main/data/los-angeles-county.geojson'
merged_data_url = 'https://raw.githubusercontent.com/XuZiHan-010/dissertation_2024/main/data/merged_data_converted.csv'

# Load the data
gdf = gpd.read_file(geojson_url)
df = pd.read_csv(merged_data_url)

# Merge the GeoDataFrame with the CSV data on the appropriate key
merged_gdf = gdf.merge(df, left_on='name', right_on='name', how='left')

# Columns to plot
columns_to_plot = ['Public Transit', 'Works from Home', 'Bikes or Walks', 'Drives Alone', 'Carpools']

# Boundary norms for each column
boundary_norms = {
    'Public Transit': [0, 0.03, 0.07, 0.12, 0.21, 0.31],
    'Works from Home': [0.01, 0.05, 0.08, 0.13, 0.20, 0.31],
    'Bikes or Walks': [0, 0.03, 0.07, 0.18, 0.42, 0.44],
    'Drives Alone': [0.19, 0.47, 0.62, 0.71, 0.78, 0.89],
    'Carpools': [0, 0.06, 0.09, 0.12, 0.15, 0.18]
}

# Define the custom color map
colors = ['#ffffb2', '#fecc5c', '#fd8d3c', '#F03B20', '#BD0026']
cmap = mcolors.ListedColormap(colors)

# Create the 3x2 grid of maps
fig, axes = plt.subplots(nrows=3, ncols=2, figsize=(20, 30))
axes = axes.flatten()

# Plot each column
for i, column in enumerate(columns_to_plot):
    ax = axes[i]
    norm = mcolors.BoundaryNorm(boundary_norms[column], cmap.N)

    merged_gdf.plot(column=column, ax=ax, cmap=cmap, norm=norm, linewidth=0.8, edgecolor='0.8', legend=False)

    # Create custom legend
    legend_labels = [f'{boundary_norms[column][j]}-{boundary_norms[column][j+1]}' for j in range(len(boundary_norms[column])-1)] + ['Missing']
    legend_colors = [plt.cm.ScalarMappable(norm=norm, cmap=cmap).to_rgba(boundary_norms[column][j]) for j in range(len(boundary_norms[column])-1)] + ['grey']
    patches = [Patch(color=color, label=label) for color, label in zip(legend_colors, legend_labels)]
    ax.legend(handles=patches, title=f"{column} Percentage", loc='lower left')

    # Set title and remove axis
    ax.set_title(f'{column} Percentage in Los Angeles County', fontsize=20)
    ax.axis('off')

# If the number of plots is odd, remove the last empty subplot
if len(columns_to_plot) % 2 != 0:
    fig.delaxes(axes[-1])

# Adjust layout and save the figure
plt.tight_layout()
plt.savefig('figure/commute_mode_maps_legend.png', dpi=800, bbox_inches='tight')
plt.show()
