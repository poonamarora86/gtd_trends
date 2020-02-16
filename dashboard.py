import pandas as pd
import geopandas as gpd
pd.set_option('display.float_format', lambda x: '%.3f' % x)

import numpy as np
from math import pi

from bokeh.layouts import gridplot, row, column, widgetbox
from bokeh.plotting import figure, show, output_file, output_notebook
from bokeh.models import ColumnDataSource, HoverTool, BasicTicker, ColorBar, ColumnDataSource, LinearColorMapper, PrintfTickFormatter, GeoJSONDataSource, ColorBar
from bokeh.plotting import figure
from bokeh.transform import dodge, transform, cumsum
from bokeh.io import export_png, curdoc
from bokeh.models import Range1d
from bokeh.palettes import Category20c, Inferno256, Category10
from bokeh.layouts import gridplot
from bokeh.plotting import figure, show, output_file
from bokeh.plotting import figure
from bokeh.transform import dodge, transform
from bokeh.palettes import brewer
from bokeh.io import curdoc, output_notebook, show, output_file
from bokeh.models import Slider, HoverTool
from bokeh.layouts import widgetbox, row, column
from bokeh.models.widgets import Tabs, Panel 
from bokeh.palettes import Inferno10, Spectral6

import numpy as np
import math
import json

output_file("Pictures/html/dashboard.html")

start_year = 2018
GTD_full = pd.read_pickle("Datasets/GTD_Dataset.pkl")

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
def heat_data(selectedYear):
    yr= selectedYear
    city_data = City_CN[City_CN.iyear == yr]
    return(city_data)


# Troubled_countries


# City_CN

### HeatMap

def create_heat_map():
  source_heat = ColumnDataSource(heat_data(start_year))
  colors = ["#75968f", "#a5bab7", "#c9d9d3", "#e2e2e2", "#dfccce", "#ddb7b1", "#cc7878", "#933b41", "#550b1d"]
  mapper = LinearColorMapper(palette=colors, low=City_CN.Attacks.min(), high=City_CN.Attacks.max())
  p_heat = figure(plot_width=600, plot_height=430, title="Type of attacks by country",
             x_range=list(City_CN.Country.unique()), y_range=list(City_CN.attacktype1_txt.unique()),
             toolbar_location=None, tools="", x_axis_location="below")
  rec = p_heat.rect(x="Country", y="attacktype1_txt", width=1, height=1, source=source_heat,
         line_color=None, fill_color=transform('Attacks', mapper))
  color_bar = ColorBar(color_mapper=mapper, location=(0, 0),
                       ticker=BasicTicker(desired_num_ticks=len(colors)),
                       formatter=PrintfTickFormatter(format="%.1f"))
  p_heat.add_layout(color_bar, 'right')
  p_heat.xgrid.grid_line_color = None
  p_heat.ygrid.grid_line_color = None
  p_heat.axis.axis_line_color = None
  p_heat.axis.major_tick_line_color = None
  p_heat.axis.major_label_text_font_size = "7pt"
  p_heat.axis.major_label_standoff = 0
  p_heat.xaxis.major_label_orientation = 1.0
  hover = HoverTool(tooltips = [
      ('Year', '@iyear'),
      ('Country', '@Country'),
      ('Attack Type', '@attacktype1_txt'),
      ('Global Events', '@Attacks')])
  p_heat.add_tools(hover)
  return (p_heat, rec)


def create_map_data(): 
  shapefile = 'Datasets/ne_110m_admin_0_countries/ne_110m_admin_0_countries.shp'
  gdf = gpd.read_file(shapefile)[['ADMIN', 'ADM0_A3', 'geometry']]
  gdf.columns = ['country', 'country_code', 'geometry']
  map_data = GTD_full.groupby(['iyear', 'country_txt']).agg({'nkill':'sum'})
  map_data = map_data.groupby(level=0).apply(lambda x:
                                                 100 * x / float(x.sum()))
  map_data = map_data.reset_index()
  map_data = map_data.rename(columns= {'iyear' :'Year',
                                    'country_txt' :'Country',
                                    'nkill':'Attacks'})
  map_data["Country"].replace({"United States": "United States of America"}, inplace=True)
  return (map_data, gdf)

(map_data, gdf) = create_map_data()

def json_data(selectedYear):
    yr = selectedYear
    df_yr = map_data[map_data['Year'] == yr]
    merged = gdf.merge(df_yr, left_on = 'country', right_on = 'Country', how = 'left')
#     merged.fillna('No data', inplace = True)
    merged_json = json.loads(merged.to_json())
    json_data = json.dumps(merged_json)
    return json_data


######################## Geo ##################################################

def create_geo(): 
  geosource = GeoJSONDataSource(geojson = json_data(start_year))
  palette = brewer['YlGnBu'][8]
  palette = palette[::-1]
  color_mapper = LinearColorMapper(palette = palette, low = 0, high = 40, nan_color = '#d9d9d9')
  tick_labels = {'0': '0%', '5': '5%', '10':'10%', '15':'15%', '20':'20%', '25':'25%', '30':'30%','35':'35%', '40': '>40%'}
  hover = HoverTool(tooltips = [ ('Country/region','@country'),('Fatalities', '@Attacks')])
  color_bar = ColorBar(color_mapper=color_mapper, label_standoff=8,width = 500, height = 20,
                       border_line_color=None,location = (0,0), orientation = 'horizontal', major_label_overrides = tick_labels)
  p = figure(title = 'Casualities due to Terror activities', plot_height = 550 , plot_width = 1000, toolbar_location = None, tools = [hover])
  p.xgrid.grid_line_color = None
  p.ygrid.grid_line_color = None
  p.patches('xs','ys', source = geosource,fill_color = {'field' :'Attacks', 'transform' : color_mapper},
            line_color = 'black', line_width = 0.25, fill_alpha = 1)
  p.add_layout(color_bar, 'below')
  return (p, geosource)



gtd_without_uk = GTD_full[GTD_full['country_txt'] != 'United Kingdom']
only_uk = GTD_full[GTD_full['country_txt'] == 'United Kingdom']

def prepare_line_data_impl(input, label):
  yearly_events = input.groupby(["iyear"]).count()['eventid'].reset_index()
  yearly_events= yearly_events.rename(columns = {'iyear' : 'Year',
                                                  'eventid' : label})
  yearly_events = yearly_events.sort_values(by=['Year'], ascending = True )
  yearly_events['Formatted_Date'] = pd.to_datetime(yearly_events.Year, format='%Y')
  yearly_events[label] = np.log(yearly_events[label])
  return yearly_events


def prepare_line_data():
  dfG = prepare_line_data_impl(gtd_without_uk, 'Attacks')
  dfUK = prepare_line_data_impl(only_uk, 'Attacks_UK')
  merged = dfG.merge(dfUK, left_on = 'Year', right_on = 'Year', how= 'inner')
  return merged [['Year','Attacks', 'Attacks_UK', 'Formatted_Date_x']]

def create_line_region_data():
  region_year_data = GTD_full.groupby(["iyear", "region_txt"]).count()['eventid'].reset_index()
  region_year_data= region_year_data.rename(columns = {'iyear' : 'Year',
                                                           'region_txt' :'Region',
                                                            'eventid' : 'Attacks'})
  region_year_data = region_year_data.sort_values(by=['Year'], ascending = True )
  region_year_data['Formatted_Date'] = pd.to_datetime(region_year_data.Year, format='%Y')
  region_year_data = pd.pivot_table(region_year_data, values='Attacks', index=['Year', 'Formatted_Date'],
                      columns=['Region'], aggfunc=np.sum).reset_index()
  region_year_data = region_year_data.fillna(0)
  return region_year_data

def create_region_line():
  src_R = ColumnDataSource(create_line_region_data())
  p2 = figure(x_axis_type="datetime", title="Terrorism activities over the years(1970-2018) in different regions")
  p2.grid.grid_line_alpha=0.3
  p2.xaxis.axis_label = 'Year'
  p2.yaxis.axis_label = 'Number of Terrorist Events'


  p2.line('Formatted_Date', 'Australasia & Oceania', line_color='#081d58', source = src_R, legend = '1.Australia & Oceania')
  p2.line('Formatted_Date', 'Central America & Caribbean', line_color='#253494', source = src_R, legend = '2.Central America & Caribbean')
  p2.line('Formatted_Date', 'Central Asia', line_color='#225ea8', source = src_R, legend = '3.Central Asia')
  p2.line('Formatted_Date', 'East Asia', line_color='#1d91c0', source = src_R, legend = '4.East Asia')
  p2.line('Formatted_Date', 'Eastern Europe', line_color='#41b6c4', source = src_R, legend = '5.Eastern Europe')
  p2.line('Formatted_Date', 'Middle East & North Africa', line_color='red', source = src_R, legend = '6.Middle East & North Africa', line_width = 2.0)
  p2.line('Formatted_Date', 'North America', line_color='#c7e9b4', source = src_R, legend = '7.North America')
  p2.line('Formatted_Date', 'South America', line_color='#edf8b1', source = src_R, legend = '8.South America')
  p2.line('Formatted_Date', 'South Asia', line_color='green', source = src_R, legend = '9.South Asia', line_width = 2.0)
  p2.line('Formatted_Date', 'Southeast Asia', line_color='#CD4247', source = src_R, legend = '10.Southeast Asia')
  p2.line('Formatted_Date', 'Sub-Saharan Africa', line_color='blue', source = src_R, legend = '11.Sub-Saharan Africa', line_width = 2.0)
  p2.line('Formatted_Date', 'Western Europe', line_color='#000003', source = src_R, legend = '12.Western Europe')

  p2.legend.label_text_font_size = "9pt"
  p2.legend.click_policy='hide'
  p2.legend.location = "top_left"
  p2.axis.major_label_text_font_size = "7pt"
  hover = HoverTool(tooltips = [('Year', '@Year')])
  p2.add_tools(hover)
  return p2


def create_line():
  src = ColumnDataSource(prepare_line_data())
  p1 = figure(x_axis_type="datetime", title="")
  p1.grid.grid_line_alpha=0.3
  p1.xaxis.axis_label = 'Year'
  p1.yaxis.axis_label = 'Number of Terrorist Events (Log scaled)'
  p1.y_range = Range1d(0,10)

  p1.line('Formatted_Date_x', 'Attacks', line_color='red', source = src, legend = 'Global', line_width = 2.0)
  p1.line('Formatted_Date_x', 'Attacks_UK', line_color='green', source = src, legend = 'UK', line_width = 2.0)

  p1.axis.major_label_text_font_size = "7pt"
  p1.legend.label_text_font_size = "9pt"
  p1.legend.location = 'top_left'
  hover = HoverTool(tooltips = [
      ('Year', '@Year'),
      ('Global Events', '@Attacks'),
      ('United Kingdom', '@Attacks_UK')])
  p1.add_tools(hover)
  return p1

def year_filter_gtd(year, group, finalcol):
  gtd_for_year = GTD_full[GTD_full.iyear == year]
  ATT = gtd_for_year.groupby([group]).agg({'eventid':'count', 'nkill' :'sum', 'nwound' : 'sum'}).reset_index()
  ATT = ATT.rename(columns= {
                          group : finalcol,
                          'eventid' :'Attacks',
                          'nkill' : 'Fatalities',
                          'nwound' : 'Wounded'})

  ATT['Attacks_Percent'] = ATT['Attacks']*100/ATT['Attacks'].sum()
  ATT = ATT[ATT.Attacks_Percent > 2.0]

  ATT['angle'] = ATT['Attacks_Percent']/ATT['Attacks_Percent'].sum() * 2*pi
  x=ATT[finalcol].value_counts()

  ATT['color'] = Category20c[len(x)]
  ATT['Fatalities_Percent'] = ATT['Fatalities']*100/ATT['Fatalities'].sum()
  ATT['Wounded_Percent'] = ATT['Wounded']*100/ATT['Wounded'].sum()
  return ATT


######
def create_bar_data(year, group, finalcol):
  by_year = GTD_full[GTD_full.iyear == year]
  Casualities = by_year.groupby(group).agg({'eventid' :'count', 'nkill' : 'sum', 'nwound' : 'sum'}).reset_index()
  Casualities = Casualities.rename(columns = {group : finalcol,
                                              'eventid' : 'Attacks',
                                              'nkill' : 'Fatalities',
                                              'nwound' : 'Wounded'})
  Casualities['Attacks_Percent'] = Casualities['Attacks']*100/Casualities['Attacks'].sum()
  Casualities['Fatalities_Percent'] = Casualities['Fatalities']*100/Casualities['Fatalities'].sum()
  Casualities['Wounded_Percent'] = Casualities['Wounded']*100/Casualities['Wounded'].sum()
  Casualities = Casualities.sort_values(by=['Attacks_Percent', 'Fatalities_Percent', 'Wounded_Percent'], ascending=False)

  return Casualities.head(11)

def create_bar(group, finalcol, y_scale=(0,60)):
  source = ColumnDataSource(data=create_bar_data(start_year, group, finalcol))

  listOf = source.data[finalcol].tolist()

  p3 = figure(x_range=listOf, y_range=y_scale, plot_height=500, title=f"By {finalcol}")

  attacks_bar = p3.vbar(x=dodge(finalcol, -0.25, range=p3.x_range), top='Attacks_Percent', width=0.2, source=source,
         color="darkturquoise", legend="Total Incidents")

  fatalities_bar =p3.vbar(x=dodge(finalcol,  0.01,  range=p3.x_range), top='Fatalities_Percent', width=0.2, source=source,
         color="indianred", legend="Casualities")

  wounded_bar = p3.vbar(x=dodge(finalcol,  0.27,  range=p3.x_range), top='Wounded_Percent', width=0.2, source=source,
         color="forestgreen", legend="Injured")

  # p3.xaxis.axis_label = 'Region'
  p3.yaxis.axis_label = 'Percentage'

  p3.x_range.range_padding = 0.1
  p3.xgrid.grid_line_color = None
  p3.legend.location = "top_left"
  p3.legend.orientation = "vertical"
  p3.xaxis.major_label_orientation = math.pi/4
  p3.axis.major_label_text_font_size = "7pt"
  p3.legend.label_text_font_size = "9pt"

  hover = HoverTool(tooltips = [('Terrorist Incidents', '@Attacks_Percent%'),
                               ('Casualties', '@Fatalities_Percent'),
                               ('Injured', '@Wounded_Percent')])
  p3.add_tools(hover)

  return (p3, attacks_bar, fatalities_bar, wounded_bar)



def create_pie(typ, orig):
    tooltip = "@AttackType: @Attacks_Percent{0.2f} %"
    p7 = figure(plot_height=440, plot_width = 700, toolbar_location=None,
               tools="hover", tooltips=f"@{typ}: @Attacks_Percent %", x_range=(-.5, .5),
               title = typ)

    pie = p7.annular_wedge(x=0, y=1,  inner_radius=0.15, outer_radius=0.25, direction="anticlock",
                    start_angle=cumsum('angle', include_zero=True), end_angle=cumsum('angle'),
            line_color="white", fill_color='color', legend=typ,source=year_filter_gtd(start_year, orig, typ))

    p7.legend.label_text_font_size = "6pt"
    p7.axis.axis_label=None
    p7.axis.visible=False
    p7.grid.grid_line_color = None
    p7.legend.location = "top_left"
    p7.legend.orientation = "vertical"
    p7.legend.click_policy='mute'
    return (p7, pie)

####################################################################
(p7, attack_types) = create_pie('AttackType', 'attacktype1_txt')
(target, target_types) = create_pie('TargetType', 'targtype1_txt')
(weapon, weapon_types) = create_pie('WeaponType', 'weaptype1_txt')
(bar_region, attacks_bar, fatalities_bar, wounded_bar) = create_bar('region_txt', 'Region')
(bar_region_city, attacks_bar_city, fatalities_bar_city, wounded_bar_city) = create_bar('city', 'City', y_scale=(0, 15))
(geo, geosource) = create_geo()
(p_heat, rec) = create_heat_map()
general_line = create_line()
region_year_line = create_region_line()
####################################################################


######


def update_plot(attr, old, new):
    new_data = heat_data(new)
    new_data_map = json_data(new)
    rec.data_source.data = new_data
    attacks_bar.data_source.data = create_bar_data(new, 'region_txt', 'Region')
    fatalities_bar.data_source.data = create_bar_data(new, 'region_txt', 'Region')
    wounded_bar.data_source.data = create_bar_data(new, 'region_txt', 'Region')
    attacks_bar_city.data_source.data = create_bar_data(new, 'city', 'City')
    fatalities_bar_city.data_source.data = create_bar_data(new, 'city', 'City')
    wounded_bar_city.data_source.data = create_bar_data(new, 'city', 'City')
    attack_types.data_source.data = year_filter_gtd(new, 'attacktype1_txt', 'AttackType')
    weapon_types.data_source.data = year_filter_gtd(new, 'weaptype1_txt', 'WeaponType')
    target_types.data_source.data = year_filter_gtd(new, 'targtype1_txt', 'TargetType')
    geosource.geojson = new_data_map



slider = Slider(title = 'Year',start = 1970, end = 2018, step = 1, value = start_year)
slider.on_change('value', update_plot)

panel1 = Panel(child=gridplot([[geo], [widgetbox(slider), None]]), title='Geo')
panel2 = Panel(child=gridplot([[bar_region, bar_region_city], [widgetbox(slider), None]]), title='Region')
panel3 = Panel(child=gridplot([[p7, p_heat], [widgetbox(slider), None]]), title='Attack types')
panel4 = Panel(child=gridplot([[target, weapon], [widgetbox(slider), None]]), title='Weapon/Target types')
panel5 = Panel(child=gridplot([[general_line, region_year_line]]), title='General trends')
layout = Tabs(tabs=[panel1, panel2, panel3, panel4, panel5])
## layout = gridplot([[p_heat, p], [p7, None], [widgetbox(slider), None]])

curdoc().add_root(layout)
# #Display plot inline in Jupyter notebook
# output_notebook()
# # #Display plot
# show(layout)