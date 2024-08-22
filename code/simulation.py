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
        else :
            data['simulated_pm25_color'] = '#ffffbf'

    return G, effect_summary

def visualize_effects(effect_summary):
    # Create a DataFrame from the effect summary
    effect_df = pd.DataFrame(effect_summary)
    avg_effects = effect_df.mean().sort_values()

    # Plot
    fig, ax = plt.subplots(figsize=(10, 5))
    avg_effects.plot(kind='bar', ax=ax, color='skyblue')
    ax.set_title('Average Impact of Different Measures on PM2.5 Reduction')
    ax.set_ylabel('Effect on PM2.5')
    ax.grid(True)
    plt.savefig('figure/visualize_fact.png', dpi=800, bbox_inches='tight')
    plt.show()

# Run the simulation and visualize effects
G_simulated, effect_summary = simulate_changes(G, gdf)
visualize_effects(effect_summary)

## Visualization
fig, axes = plt.subplots(1, 2, figsize=(20, 10))

# Define high and low exposure areas
high_exposure_mask = gdf['name'].isin(['Del Aire', 'Harbor Gateway', 'Hawthorne', 'Lawndale', 'West Carson'])
low_exposure_mask = gdf['name'].isin(['Commerce', 'Diamond Bar', 'Elysian Park', 'Hollywood Hills', 'Industry', 'Irwindale', 'Ladera Heights', 'Rancho Dominguez', 'Santa Fe Springs', 'Vernon', 'Veterans Administration', 'Whittier Narrows'])



# Original PM2.5 levels
ax = axes[0]
colors = {'Below 12': 'green', 'Above 12': 'red'}
gdf['pm25_category'] = np.where(gdf['PM2.5 Concentration'] >= 12, 'Above 12', 'Below 12')
gdf.plot(ax=ax, column='pm25_category', cmap=mcolors.ListedColormap([colors['Below 12'], colors['Above 12']]), legend=True)
roadways.plot(ax=ax, color='blue', linewidth=1, label='Major Roadways')  # Plotting roadways in blue
ax.set_title('Original PM2.5 Concentrations',fontsize=20)
ax.axis('off')

# Simulated PM2.5 levels
ax = axes[1]
gdf.plot(ax=ax, color='lightgray')  # Basemap of LA County
gdf[high_exposure_mask].plot(ax=ax, color='blue', alpha=0.5,edgecolor='black', label='High Exposure Areas')
gdf[low_exposure_mask].plot(ax=ax, color='purple', alpha=0.5, edgecolor='black', label='Low Exposure Areas')
for (u, v, data) in G_simulated.edges(data=True):
    if 'simulated_pm25_color' in data:
        color = data['simulated_pm25_color']
        line = LineString([u, v])
        xs, ys = line.xy
        ax.plot(xs, ys, color=color, linewidth=2)
ax.set_title('Simulated PM2.5 Concentrations',fontsize=20)
ax.axis('off')

# Define legends for both plots
legend_elements_original = [
    plt.Line2D([0], [0], color='green', lw=4, label='PM2.5 < 12 µg/m³'),
    plt.Line2D([0], [0], color='red', lw=4, label='PM2.5 ≥ 12 µg/m³'),
    plt.Line2D([0], [0], color='blue', lw=2, label='Major Roadways')
]
legend_elements_simulated = [
    plt.Line2D([0], [0], color='#1a9641', lw=2, label='PM2.5 Remain Below 12'),
    plt.Line2D([0], [0], color='#d7191c', lw=2, label='PM2.5 Improved'),
    plt.Line2D([0], [0], color='#fdae61', lw=2, label='PM2.5 Remain Above 12'),
    plt.Line2D([0], [0], color='#ffffbf', lw=2, label='Missing Data'),
    plt.Line2D([0], [0], color='blue', lw=4, label='self-polluted area'),
    plt.Line2D([0], [0], color='purple', lw=4, label='affected by others'),
]
axes[0].legend(handles=legend_elements_original, loc='upper right')
axes[1].legend(handles=legend_elements_simulated, loc='upper right')

plt.tight_layout()
plt.savefig('figure/simulation_area.png', dpi=800, bbox_inches='tight')
plt.show()
