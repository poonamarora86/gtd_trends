import geopandas as gpd
import pandas as pd
import numpy as np
import math
import json

from bokeh.io import curdoc, output_notebook, show, output_file
from bokeh.models import Slider, HoverTool
from bokeh.layouts import widgetbox, row, column

from bokeh.layouts import gridplot
from bokeh.plotting import figure, show, output_file
from bokeh.models import ColumnDataSource, HoverTool, BasicTicker, ColorBar, ColumnDataSource, LinearColorMapper, PrintfTickFormatter, GeoJSONDataSource, ColorBar
from bokeh.plotting import figure
from bokeh.transform import dodge, transform
from bokeh.palettes import brewer


#Define function that returns json_data for year selected by user.
    
GTD = pd.read_pickle("/Users/poonamarora/Desktop/Aleph/Datasets/GTD_Dataset.pkl")

shapefile = '/Users/poonamarora/Desktop/Aleph/Datasets/ne_110m_admin_0_countries/ne_110m_admin_0_countries.shp'
#Read shapefile using Geopandas
gdf = gpd.read_file(shapefile)[['ADMIN', 'ADM0_A3', 'geometry']]
#Rename columns.
gdf.columns = ['country', 'country_code', 'geometry']

Map_GTD = GTD.groupby(['iyear', 'country_txt']).agg({'nkill':'sum'})
Map_GTD = Map_GTD.groupby(level=0).apply(lambda x:
                                               100 * x / float(x.sum()))
Map_GTD = Map_GTD.reset_index()
Map_GTD = Map_GTD.rename(columns= {'iyear' :'Year',
                                  'country_txt' :'Country',
                                  'nkill':'Attacks'})

Map_GTD["Country"].replace({"United States": "United States of America"}, inplace=True)


def json_data(selectedYear):
    yr = selectedYear
    df_yr = Map_GTD[Map_GTD['Year'] == yr]
    merged = gdf.merge(df_yr, left_on = 'country', right_on = 'Country', how = 'left')
#     merged.fillna('No data', inplace = True)
    merged_json = json.loads(merged.to_json())
    json_data = json.dumps(merged_json)
    return json_data

#Input GeoJSON source that contains features for plotting.
geosource = GeoJSONDataSource(geojson = json_data(2001))

#Define a sequential multi-hue color palette.
palette = brewer['YlGnBu'][8]

#Reverse color order so that dark blue is highest obesity.
palette = palette[::-1]

#Instantiate LinearColorMapper that linearly maps numbers in a range, into a sequence of colors. Input nan_color.
color_mapper = LinearColorMapper(palette = palette, low = 0, high = 40, nan_color = '#d9d9d9')

#Define custom tick labels for color bar.
tick_labels = {'0': '0%', '5': '5%', '10':'10%', '15':'15%', '20':'20%', '25':'25%', '30':'30%','35':'35%', '40': '>40%'}

#Add hover tool
hover = HoverTool(tooltips = [ ('Country/region','@country'),('Fatalities', '@Attacks')])

#Create color bar. 
color_bar = ColorBar(color_mapper=color_mapper, label_standoff=8,width = 500, height = 20,
                     border_line_color=None,location = (0,0), orientation = 'horizontal', major_label_overrides = tick_labels)

#Create figure object.
p = figure(title = 'Casualities due to Terror activities', plot_height = 600 , plot_width = 950, toolbar_location = None, tools = [hover])
p.xgrid.grid_line_color = None
p.ygrid.grid_line_color = None
#Add patch renderer to figure. 
p.patches('xs','ys', source = geosource,fill_color = {'field' :'Attacks', 'transform' : color_mapper},
          line_color = 'black', line_width = 0.25, fill_alpha = 1)
#Specify layout
p.add_layout(color_bar, 'below')
# Define the callback function: update_plot
def update_plot(attr, old, new):
    yr = slider.value
    new_data = json_data(yr)
    geosource.geojson = new_data
    p.title.text = 'Terrorist activities over the year, %d' %yr
    
# Make a slider object: slider 
slider = Slider(title = 'Year',start = 1970, end = 2018, step = 1, value = 2001)
slider.on_change('value', update_plot)
# Make a column layout of widgetbox(slider) and plot, and add it to the current document
layout = column(p,widgetbox(slider))
curdoc().add_root(layout)
# #Display plot inline in Jupyter notebook
# output_notebook()
# #Display plot
# show(layout)