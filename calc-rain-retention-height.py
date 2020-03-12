############################################################################################
#
# Determining the amount of stormwater runoff handled in each sewershed area
#
# Input: DEP Green Infrastructure shapefile & Open Sewer Atlas Sewershed shapefile
# Output: A map of sewersheds labeled with the manageable height of water
#
# Process:
#   Read green infrastructure, sewershed and combined sewer area shapefiles as DataFrames
#   Spatially join sewershed DataFrame to GI DataFrame
#   Calculate the total volume of expected rain captured in each sewershed
#   Calculate the combined sewer areas of each sewershed
#   Join the calculated series to the sewershed DataFrame
#   Calculate the height of expected captured rain for 10% of the combined sewer area
#   Display sewersheds labeled with the expected height of captured storm water in inches
#
############################################################################################

# Pandas and GeoPandas allows us to create and manipulate spatial data files
import pandas as pd
import geopandas

# matplotlib let's us create plots
import matplotlib.pyplot as plt
import matplotlib.patheffects as pe
from mpl_toolkits.axes_grid1 import make_axes_locatable

# Read ESRI shapefiles as GeoDataFrames
gi_df = geopandas.read_file("Data/project/green_infrastructure.geojson")
sewershed_df = geopandas.read_file("Data/project/Sewershed.shp")
csda_df = geopandas.read_file("Data/project/combinedsewer_drainage_area.shp")

# Select only the relevant columns
gi_df = gi_df[['asset_id', 'calc_rain', 'status', 'geometry']]

# Select only the constructed green infrastructures
gi_df = gi_df[gi_df.status.str.contains('Constructed')]

# Spatially join the sewershed to the green infrastructure DataFrame
gi_with_sewershed = geopandas.sjoin(gi_df, sewershed_df, how='left', op='within')

# Calculate the total volume of rain each sewershed can hold with green infrastructures
gi_group = gi_with_sewershed.groupby('Sewershed')
tot_calc_rain = gi_group.sum().calc_rain
tot_calc_rain.name = 'total_calc_rain'

# Calculate the combined sewer areas for each sewershed
csda_group = csda_df.groupby('sewershed')
csda_area = csda_group.sum().area
csda_area.name = 'cso_area'

# Join the total rain per sewershed and combined sewer areas to sewershed DataFrame
sewershed_rain = pd.merge(sewershed_df, tot_calc_rain, left_on='Sewershed', right_index=True)
sewershed_cso_rain = pd.merge(sewershed_rain, csda_area, left_on='Sewershed', right_index=True)
sewershed_cso_rain['rain_height'] = (sewershed_cso_rain.total_calc_rain / (sewershed_cso_rain.cso_area*0.10)) * 12

# Plot the combined sewer areas
fig, ax = plt.subplots(figsize=(15, 15))
plt.axis('off')
divider = make_axes_locatable(ax)
cax = divider.append_axes("bottom", size="5%", pad=0.1)
ss_fig = sewershed_df.plot(ax=ax, color='wheat', edgecolor='grey')
cs_fig = sewershed_cso_rain.plot(ax=ax, column='rain_height', edgecolor='black', cmap='Blues',
                                 cax=cax, legend=True, legend_kwds={'label': "Population by Country",
                                                                    'orientation': "horizontal"})

# Label each polygon with the height of rain that can be handled in inches
sewershed_cso_rain.apply(lambda x: cs_fig.annotate(s='{:.4f} in'.format(x['rain_height']),
                                                   xy=x.geometry.centroid.coords[0],
                                                   ha='center',
                                                   color='black',
                                                   path_effects=[pe.withStroke(linewidth=4, foreground="white")]),
                         axis=1)

# Label sewershed with name
# sewershed_cso_rain.apply(lambda x: ss_fig.annotate(s=x['Sewershed'],
#                                                    xy=x.geometry.centroid.coords[0],
#                                                    ha='center',
#                                                    color='black',
#                                                    path_effects=[pe.withStroke(linewidth=4, foreground="white")]),
#                          axis=1)

# Display figure
plt.show()
