import pandas as pd
pd.set_option('display.float_format', lambda x: '%.3f' % x)

import numpy as np
from math import pi

from bokeh.layouts import gridplot, row, column, widgetbox
from bokeh.plotting import figure, show, output_file, output_notebook
from bokeh.models import ColumnDataSource, HoverTool, BasicTicker, ColorBar, ColumnDataSource, LinearColorMapper, PrintfTickFormatter, Slider
from bokeh.plotting import figure
from bokeh.transform import dodge, transform, cumsum
from bokeh.io import export_png, curdoc
from bokeh.models import Range1d
from bokeh.palettes import Category20c, Inferno256, Category10

GTD_full = pd.read_pickle("/Users/poonamarora/Desktop/Aleph/Datasets/GTD_Dataset.pkl")

Country = GTD_full.groupby(['country_txt']).agg({'eventid' : 'count', 'nkill' :'sum', 'nwound' :'sum'}).reset_index()
Country = Country.rename(columns = {'country_txt' : 'Country',
                                    'eventid' : 'Attacks'})
Country['CN_Attacks_Percent'] = Country['Attacks']*100/Country['Attacks'].sum()
Country = Country[Country.CN_Attacks_Percent >= 2.0]

# Country
Troubled_countries = Country.Country.tolist()

City = GTD_full[['eventid', 'city','country_txt','iyear','attacktype1_txt','targtype1_txt']]
City = City[(City.country_txt.isin(Troubled_countries)) & (City.attacktype1_txt != 'Unknown')]
# City.shape

City_CN = City.groupby(['country_txt', 'attacktype1_txt', 'iyear']).agg({'eventid' : 'count'}).reset_index()
City_CN = City_CN.rename(columns = {'country_txt' : 'Country',
                             'eventid' : 'Attacks'})
City_CN['Attacks'] = np.log(City_CN['Attacks'])


# GTD_full.shape
def data(selectedYear):
    yr= selectedYear
    city_data = City_CN[City_CN.iyear == yr]
    return(city_data)

# Troubled_countries


# City_CN

### HeatMap
source = ColumnDataSource(City_CN)

# this is the colormap from the original NYTimes plot
colors = ["#75968f", "#a5bab7", "#c9d9d3", "#e2e2e2", "#dfccce", "#ddb7b1", "#cc7878", "#933b41", "#550b1d"]
mapper = LinearColorMapper(palette=colors, low=City_CN.Attacks.min(), high=City_CN.Attacks.max())

p = figure(plot_width=800, plot_height=300, title="Terrorist Activities in most troubled countries",
           x_range=list(City_CN.Country.unique()), y_range=list(City_CN.attacktype1_txt.unique()),
           toolbar_location=None, tools="", x_axis_location="above")

rec = p.rect(x="Country", y="attacktype1_txt", width=1, height=1, source=source,
       line_color=None, fill_color=transform('Attacks', mapper))

color_bar = ColorBar(color_mapper=mapper, location=(0, 0),
                     ticker=BasicTicker(desired_num_ticks=len(colors)),
                     formatter=PrintfTickFormatter(format="%.1f"))

p.add_layout(color_bar, 'right')
p.xgrid.grid_line_color = None
p.ygrid.grid_line_color = None
p.axis.axis_line_color = None
p.axis.major_tick_line_color = None
p.axis.major_label_text_font_size = "7pt"
p.axis.major_label_standoff = 0
p.xaxis.major_label_orientation = 1.0
hover = HoverTool(tooltips = [
    ('Year', '@iyear'),
    ('Country', '@Country'),
    ('Attack Type', '@attacktype1_txt'),
    ('Global Events', '@Attacks')])

p.add_tools(hover)

def update_plot(attr, old, new):
    new_data = data(new)
    rec.data_source.data = new_data
    p.title.text = 'Terror, %d' %new
    
    
slider = Slider(title = 'Year',start = 1970, end = 2018, step = 1, value = 2001)
slider.on_change('value', update_plot)

layout = column(p,widgetbox(slider))
curdoc().add_root(layout)
# #Display plot inline in Jupyter notebook
# output_notebook()
# # #Display plot
# show(layout)