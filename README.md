# Patrick S. Flynn - Data Incubator Capstone 

## Summary
The purpose goal of this project is to analyze the importance of a given yelp restaurant's geographic location in the greater Las Vegas valley (Las Vegas, Henderson, North Las Vegas, Green Valley, and Boulder City). In addition to geographic location we will also analyze any particular types of restaurant (i.e. Korean BBQ, Chinese, Italian) to determine if we can say with some degree of certainty that planning a new restaurant in a given zip code will be more likely to fail or succeed.

## Scenario: 
*Imagine you are an entrepreneur looking to open a new restaurant in the Las Vegas valley. You want to locate your establishment in an area that the cost-point and type of food your restaurant serves will be most likely to succeed.* 

## Hypothesis:
While overall quality of food and service are paramount to a restaurant's success - does the location and socioeconomic/demographic factors within that area impact the impact the restaurants success metric? The success metric for this project will defined as Yelp rating for a business (1-5 stars).

## Analytical Goals
- Identify trends regarding what restaurants/restaurant types do well in a given zip code in the greater Las Vegas area
- Reject or accept project hypothesis
  

## Project/Model Goals
- Be able to recommend a restaurant type (or combination of types) given a particular zip code that will be more likely to succeed (i.e. high number of "good" ratings)

- Inversely, be able to reccommend a given zip code to establish a restaurant within based on the price and type of food that will be served



## Datasets
### Greater Las Vegas Area Zip Code Shapefile
<img src="images/vegas_zipcodes.png" alt="drawing" width="1080"/>

Source: [ESRI Arcgis](https://hub.arcgis.com/datasets/ccgismo::zip-codes)
</br>
In order to be able to visually identify zip codes in the greater Las Vegas area we need the corresponding shapefiles provided by the Clark County GISMO team via ESRI ArcGIS hub technology. We are able to then ingest this information into Python via Geopandas and visualize the zip codes as seen above.

### Yelp API
Source: [Yelp API](https://www.yelp.com/developers/documentation/v3/get_started)


## Methodology
#### Requirements
- Python 3.X
- Package/Environment:
  - Anaconda Environment (Numpy, Pandas, SKlearn, etc.)
  - Geopandas/Shapely/Descartes

### Steps
1. Ingest the zip code shapefile as a Geopandas DataFrame
   - We also remove some zip codes that are essentially vast open desert
2. We obtain the latitude/longitude boundaries (minimum, maximums) and we construct a fishnet grid comprised of coordinates centroid points. (see below image)
<img src="images/zip_centroids.png" alt="drawing" width="1080"/>

3. We spatially join ALL of the centroids to the zip code shapefile and we remove any centroids that are not within the selected zip codes, resulting in over 1000 (1117 to be exact) coordinate pairs.
4. We iterate through each centroid coordinate pair passing in the coordinate to the yelp API as a HTTP request, receiving back a dataset of 50 or less business for each centroid.
5. We remove any duplicate business IDs that may have been retrieved in low density areas.
6. We apply a SKlearn multilabel binarizer to turn all of the individual categories of a business (such as "Seafood" or "Burger") into a unique one-hot-encoded set of columns
7. In order to stay under our allotted API requests, we cache the results of our API requests into a SQLite database stored within the repository allowing us to easily access the almost 5000 businesses without having to send an API request for each of the centroids again
## Exploratory Data Analysis
<img src="images/choropleth_maps.png" alt="drawing" width="1080"/>
As a proof of concept and viability assessment for this project we do some transformations of our data and plot them geographically as seen above. The results are perhaps not what I was expecting to see, I expected that the higher the prices, the better the ratings would be. After plotting the results we can see that this is in fact not the case and instead we see a high concentration of businesses along the Las Vegas strip which is to be expected, however most of the well rated restaurants are on the West side of the valley or in Boulder City (South East). The prices are located centrally in the valley which makes sense as this is where many of the high-end luxury restaurants are located on the Las Vegas Strip. 



## Next Steps
Our initial EDA serves as a good first step but there is much work to be done! In order to understand at a deeper level what is going on we need to obtain some economic data to see how economic status is distributed across the zip codes as well as some qualitative data in the form of written user reviews to better understand what is going on.

- Locate socioeconomic information for potential use in ML training model
  - US Census Bureau has an open data portal with the required economic and demographic information. Although these are estimates (due to the 2020 US census data not being available) they should provide a solid dataset for use in predictions and recommendations.
- Query Yelp API for more in-depth location about each business such as hours of operation or written user reviews.

## Machine Learning Model Considerations
- Target Variable(s): 
  - If provided a zip code -> predict the best price and type of food
  - if provided a price/type of food -> predict the best zip code(s) to locate in

- Some analysis will need to be performed to ensure that our model does not over-saturate an area with an already existing type of food. For example, in Las Vegas' Chinatown area - there are many highly rated Chinese restaurants, but is that necessarily the best recommendation to make in an area that already has many of the same type of high-performing restaurant?
  
- Ensuring that our model does not just always suggest the highest scoring zip code or type of food is important to having a model that is useful and practical. 

## Taking the Project to the Next Level
Depending on the results of our analysis and performance of our model - can the lessons learned in this analysis be taken to a broader country or even global level? Perhaps our model can be commercialized into an application that future restaurant owners can use to best determine where to locate their business. 