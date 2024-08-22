import numpy as np
import osmnx as ox
import networkx as nx
import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from shapely.geometry import LineString

# Configure osmnx
ox.settings.use_cache = True
ox.settings.log_console = True

# Load data
geojson_url = 'https://raw.githubusercontent.com/XuZiHan-010/dissertation_2024/main/data/los-angeles-county.geojson'
merged_data_url = 'https://raw.githubusercontent.com/XuZiHan-010/dissertation_2024/main/data/merged_data_converted.csv'
roadway_path = 'data/roadway/los-angeles-county-freeways.shp'

gdf = gpd.read_file(geojson_url)
roadways = gpd.read_file(roadway_path).to_crs(gdf.crs)
merged_data = pd.read_csv(merged_data_url)
gdf = gdf.merge(merged_data, on='name', how='left')

# Create a graph from roadway data
G = nx.Graph()
for idx, row in roadways.iterrows():
    if isinstance(row.geometry, LineString):
        coords = list(row.geometry.coords)
        for i in range(len(coords) - 1):
            G.add_edge(coords[i], coords[i + 1], length=LineString([coords[i], coords[i + 1]]).length)

# Assign CRS to the graph
G.graph['crs'] = roadways.crs

def simulate_changes(G, gdf):
    # Adding effect breakdown
    effect_summary = {'income_effect': [], 'density_effect': [], 'ev_effect': [], 'transit_effect': [],
                      'drive_effect': []}

    for (u, v, data) in G.edges(data=True):
        local_data = gdf[gdf['geometry'].intersects(LineString([u, v]))]
        if local_data.empty:
            continue

        initial_pm25 = local_data['PM2.5 Concentration'].mean()
        income_mod = np.log1p(local_data['Median Household Income'].mean() / 100000)
        density_mod = np.log1p(local_data['Population Density'].mean() / 1000)

        # Individual effects
        transit_effect = -0.03 * income_mod
        ev_effect = 0.07 * income_mod
        active_travel_effect = 0.04 * density_mod
        solo_drive_effect = -0.06 * income_mod
        short_commute_effect = 0.05 * (density_mod if local_data['Public Transit'].mean() > 0.1 else 0)

        # Store effects
        effect_summary['income_effect'].append(transit_effect + ev_effect + solo_drive_effect)
        effect_summary['density_effect'].append(active_travel_effect)
        effect_summary['ev_effect'].append(ev_effect)
        effect_summary['transit_effect'].append(transit_effect)
        effect_summary['drive_effect'].append(solo_drive_effect)

        # Apply total effect
        total_effect = sum([transit_effect, ev_effect, active_travel_effect, solo_drive_effect, short_commute_effect])
        simulated_pm25 = max(0, initial_pm25 * (1 + total_effect))
        data['pm25_reduction'] = initial_pm25 - simulated_pm25

        # Assign color based on the simulation result
        if simulated_pm25 < 12 and initial_pm25 < 12:
            data['simulated_pm25_color'] = '#1a9641'
        elif simulated_pm25 < 12 and initial_pm25 >= 12:
            data['simulated_pm25_color'] = '#d7191c'
        elif simulated_pm25 >= 12 and initial_pm25 >= 12:
            data['simulated_pm25_color'] = '#fdae61'
        else:
            data['simulated_pm25_color'] = '#ffffbf'

    return G, effect_summary

# Run the simulation
G_simulated, effect_summary = simulate_changes(G, gdf)

# Visualization for Simulated PM2.5 levels
fig, ax = plt.subplots(figsize=(12, 10))  # Adjust size as necessary

# Plot the general basemap of LA County in light gray
gdf.plot(ax=ax, color='lightgray')  # Basemap of LA County

# Highlight the specific areas with high and low exposure using shading
high_exposure_mask = gdf['name'].isin(['Del Aire', 'Harbor Gateway', 'Hawthorne', 'Lawndale', 'West Carson'])
low_exposure_mask = gdf['name'].isin(['Commerce', 'Diamond Bar', 'Elysian Park', 'Hollywood Hills', 'Industry', 'Irwindale', 'Ladera Heights', 'Rancho Dominguez', 'Santa Fe Springs', 'Vernon', 'Veterans Administration', 'Whittier Narrows'])

gdf[high_exposure_mask].plot(ax=ax, color='blue', alpha=0.5, edgecolor='black', label='High Exposure Areas')
gdf[low_exposure_mask].plot(ax=ax, color='purple', alpha=0.5, edgecolor='black', label='Low Exposure Areas')

# Overlay the simulated PM2.5 reductions with distinct colors
for (u, v, data) in G_simulated.edges(data=True):
    if 'simulated_pm25_color' in data:
        color = data['simulated_pm25_color']
        line = LineString([u, v])
        xs, ys = line.xy
        ax.plot(xs, ys, color=color, linewidth=2)

# Add neighborhood labels with arrows pointing to their approximate locations
neighborhoods = {
    "Del Aire": (-118.379, 33.916),
    "Harbor Gateway": (-118.298, 33.826),
    "Hawthorne": (-118.348, 33.916),
    "Lawndale": (-118.352, 33.887),
    "West Carson": (-118.297, 33.820),
    "Commerce": (-118.159, 33.997),
    "Diamond Bar": (-117.810, 34.028),
    "Elysian Park": (-118.238, 34.083),
    "Hollywood Hills": (-118.335, 34.117),
    "Industry": (-117.957, 34.019),
    "Irwindale": (-117.935, 34.110),
    "Ladera Heights": (-118.372, 33.988),
    "Rancho Dominguez": (-118.213, 33.867),
    "Santa Fe Springs": (-118.086, 33.947),
    "Vernon": (-118.230, 34.003),
    "Veterans Administration": (-118.448, 34.063),
    "Whittier Narrows": (-118.062, 34.032)
}

# Arrow annotations placed in the map's blank areas
annotation_positions = {
    "Del Aire": (-118.6, 33.75),
    "Harbor Gateway": (-118.5, 33.68),
    "Hawthorne": (-118.55, 33.82),
    "Lawndale": (-118.57, 33.79),
    "West Carson": (-118.5, 33.71),
    "Commerce": (-118.4, 34.1),
    "Diamond Bar": (-117.65, 34.2),
    "Elysian Park": (-118.35, 34.2),
    "Hollywood Hills": (-118.4, 34.3),
    "Industry": (-117.8, 34.1),
    "Irwindale": (-117.75, 34.22),
    "Ladera Heights": (-118.55, 34.05),
    "Rancho Dominguez": (-118.45, 33.9),
    "Santa Fe Springs": (-118.2, 33.85),
    "Vernon": (-118.4, 34.05),
    "Veterans Administration": (-118.65, 34.25),
    "Whittier Narrows": (-118.3, 34.25)
}

# Plot arrows and labels
for name, coords in neighborhoods.items():
    ax.annotate(name, xy=coords, xytext=annotation_positions[name],
                arrowprops=dict(facecolor='black', arrowstyle='->', lw=1.5), fontsize=10, ha='center')

ax.axis('off')

# Define and add the legend
legend_elements_simulated = [
    plt.Line2D([0], [0], color='#1a9641', lw=2, label='PM2.5 Remain Below 12'),
    plt.Line2D([0], [0], color='#d7191c', lw=2, label='PM2.5 Improved'),
    plt.Line2D([0], [0], color='#fdae61', lw=2, label='PM2.5 Remain Above 12'),
    plt.Line2D([0], [0], color='#ffffbf', lw=2, label='Missing Data'),
    plt.Line2D([0], [0], color='blue', lw=4, label='Self-Polluted Area'),
    plt.Line2D([0], [0], color='purple', lw=4, label='Affected by Others')
]
ax.legend(handles=legend_elements_simulated, loc='upper right')

# Save and show the figure
plt.tight_layout()
plt.savefig('figure/simulation_area_singlery.png', dpi=800, bbox_inches='tight')
plt.show()
