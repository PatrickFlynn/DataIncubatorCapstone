# -*- coding: utf-8 -*-
"""
Created on Sun Nov  1 12:15:20 2020

@author: Patrick Flynn
"""
import pandas as pd
import geopandas as gp
import matplotlib.pyplot as plt
import shapely
import requests
from sqlalchemy import create_engine
from sklearn.preprocessing import MultiLabelBinarizer
import re
import os
import sqlite3



yelpkey = 'cBtu43sa9qo4ITijqcYxBP5xpEyxMywLfUgDa1NSzbrbpd_gLlkEyVEc4_781I8v7jmehAxfEOKwyboFlHYfxEgiMVlr6Dg3vcEjl_wuMMXggc-tuSbEZuxFnBTWW3Yx'

zip_codes = gp.GeoDataFrame.from_file(r'zip_shapefile\Political_Boundaries.shp')
zip_codes = zip_codes.loc[~zip_codes['ZIP'].isin([
        89124, 89007, 89025, 89046, 89019, 89029, 89040, 
        89018, 89039, 89021, 89027, 89034])]
zip_codes.plot(column='ZIP', legend=True)

boundaries = zip_codes.total_bounds
maxy = boundaries[3]
maxx = boundaries [2]
miny = boundaries[1]
minx = boundaries[0]

xdelta =maxx-minx
ydelta = maxy-miny


gridpoints = []

startx = minx
starty = miny
xdelta = xdelta/49
ydelta = ydelta/49

for y in range (0, 50):
    
    gridpoints.append(shapely.geometry.Point(startx, starty))
    
    for x in range(0, 50):
        
        gridpoints.append(shapely.geometry.Point(startx, starty))
        
        startx += xdelta
        
    startx = minx
    
    starty += ydelta

gridpoints = gp.GeoDataFrame(gridpoints)
gridpoints.rename(columns={0:'Geometry'}, inplace=True)
gridpoints = gridpoints.set_geometry('Geometry')
gridpoints = gp.sjoin(gridpoints, zip_codes)


fig, ax = plt.subplots(1,1, figsize=(10,20))
zip_codes.plot(ax=ax)   
gridpoints.plot(ax=ax, color='red')
plt.show()     

locations = pd.DataFrame()

def requestyelp(api_key, url_params=None):
    url_params = url_params or {}
    url = r'https://api.yelp.com/v3/businesses/search'
    headers = {
        'Authorization': 'Bearer %s' % api_key,
    }
    response = requests.request('GET', url, headers=headers, 
                                params=url_params, verify=False)
    return response.json()

if not os.path.exists(r'yelp_data.db'):
    
    engine = create_engine('sqlite:///yelp_data.db', echo=True)
    sqlite_connection = engine.connect()

    for x in gridpoints['Geometry']:
        
        i = x.coords[0]
        
        temp = requestyelp(yelpkey, {'latitude':i[1],'longitude':i[0], 
                                     'radius':1750, 'limit':50})
        temp = pd.io.json.json_normalize(temp['businesses'])
        if not temp.empty:
                        types = []
                        for index, row in temp.iterrows():
                            types.append([i['alias'] for i in row['categories']])
                        temp['types'] = types 
        locations = locations.append(temp)
        
    locations = locations.drop_duplicates(subset='id')
    locations = locations.drop(columns=['alias', 'categories', 
                                        'location.display_address', 
                                        'transactions'])
    
    saved = locations.copy()

#locations = saved.copy().reset_index(drop=True)

    mlb = MultiLabelBinarizer(sparse_output=True)
    
    categories = pd.DataFrame.sparse.from_spmatrix(
                   mlb.fit_transform(locations['types']),
                   index=locations.index,
                   columns=mlb.classes_)
    
    #locations = locations.join(categories)
    
    locations['types'] = locations['types'].apply(lambda x: ', '.join(x))
    locations['price'] = locations['price'].fillna('').apply(
            lambda x: len(re.findall('\$', x))).astype(int)
    
    locations.to_sql('Locations', sqlite_connection, if_exists='replace', 
                     index=False)
    categories.to_sql('categories', sqlite_connection, if_exists='replace', 
                      index=False)

else:
    
    con = sqlite3.connect("yelp_data.db")
    
    locations = pd.read_sql_query("SELECT * from Locations", con)
    categories = pd.read_sql_query("SELECT * from categories", con)
    
location_counts = locations.groupby('location.zip_code').count(
        )['name']
location_stats = pd.DataFrame(location_counts).join(locations.groupby(
        'location.zip_code').mean()[['rating', 'price']]).reset_index(
        ).rename(columns={'name':'count', 'location.zip_code':'ZIP'})
location_stats.drop(location_stats.loc[location_stats['ZIP'] == ''].index, 
                    inplace=True)
location_stats['ZIP'] = location_stats['ZIP'].astype(int)
stats_mappable = pd.merge(zip_codes, location_stats, left_on='ZIP', right_on='ZIP', how='inner')

stats_mappable.plot('count', legend=True)