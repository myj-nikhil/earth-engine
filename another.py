import ee
service_account = 'helpful-aurora-380816@appspot.gserviceaccount.com'
credentials = ee.ServiceAccountCredentials(service_account, 'private-key.json')
ee.Initialize(credentials)

organic_carbon = ee.Image("OpenLandMap/SOL/SOL_ORGANIC-CARBON_USDA-6A1C_M/v02")
Mumbai_Coordinates = ee.Geometry.Polygon([[72.820578,19.044863],[72.788306,19.265397],[72.830191,19.249840],[72.852851,19.268638],[72.934562,19.194729],[72.978507,19.156464],[72.955848,19.081207],[72.956534,19.029285],[72.885810,18.996826],[72.878257,19.047460],[72.820578,19.044863]])
        # dd_long = 83.395551
        # dd_lat = 18.106658
        # coordinates=ee.Geometry.Point(dd_long,dd_lat)
        # circular_region = coordinates.buffer(100000)

            # Method 2 : Defining the region from the features of an existing feature collection by FAO.(Food and Agricultural Organisation)
            # We have Level 2 Administrative regions's(Districts) features from the FeatureCollection("FAO/GAUL/2015/level2")
            # Import the featurecollection
boundarycoll = ee.FeatureCollection("FAO/GAUL/2015/level2")

district_features = boundarycoll.filter(ee.Filter.eq('ADM2_NAME','Vizianagaram'))
        # district_features = circular_region

year='2010'
number = ee.Number(int(year))

        # Load the imagecollection of global population density

population_coll = ee.ImageCollection("CIESIN/GPWv411/GPW_Population_Density")  # Temporal Res = 5 years
        # Load the image of Soil Organic Carbon content
organic_carbon = ee.Image("OpenLandMap/SOL/SOL_ORGANIC-CARBON_USDA-6A1C_M/v02") 
            #Load the climate data
climate_coll = ee.ImageCollection("NASA/FLDAS/NOAH01/C/GL/M/V001") #Temporal Resolution = 1 Month
            #Load the rainfall data
rainfall_coll = ee.ImageCollection("UCSB-CHG/CHIRPS/DAILY")# Temporal Resolution = 1 Day
        
        
rainfall_projection = rainfall_coll.first().projection()
rainfall_scale = rainfall_projection.nominalScale()
population_projection = population_coll.first().projection()
population_scale = population_projection.nominalScale()
climate_projection = climate_coll.first().projection()
climate_scale = climate_projection.nominalScale()




all_coll = [population_coll,climate_coll,rainfall_coll]

filtered_coll = [None]*3

def year_filter(number):
                
        start_date = ee.Date.fromYMD(number, 1, 1)
        end_date = start_date.advance(1, 'year')
                
        for i in range(0,len(all_coll)):
                    filtered_coll[i] = all_coll[i].filterDate(start_date, end_date)

year_filter(number)



rainfall_sum = filtered_coll[2].reduce(ee.Reducer.sum())
popul_mean = filtered_coll[0].reduce(ee.Reducer.mean())
cli_mean = filtered_coll[1].reduce(ee.Reducer.mean())




rainfall_data = rainfall_sum.reduceRegion(
                                                    
                                                    reducer= ee.Reducer.mean(),
                                                    geometry=district_features,
                                                    scale= rainfall_scale
                                                    
                                                    ).getInfo()['precipitation_sum']
        # if (rainfall_data is not None):
        #     final_rainfall_data = round(rainfall_data['precipitation_sum'])
        
population_density_data = popul_mean.reduceRegion(
                                                    
                                                    reducer= ee.Reducer.mean(),
                                                    geometry=district_features,
                                                    scale=population_scale
                                                    
                                                    ).getInfo()['population_density_mean']
        
         
        
        # if (population_density_data is not None): 
            
        #     final_population_density_data =  round(population_density_data)
        
climate_data = cli_mean.reduceRegion(
                                                    
                                     reducer= ee.Reducer.mean(),
                                     geometry=district_features,
                                     scale=climate_scale
     
                                    ).getInfo()

print(climate_data)
soil_data = organic_carbon.reduceRegion('mean', district_features).getInfo()



soilkey_list = ['Soil organic carbon content at 0 cm depth', 'Soil organic carbon content at 10 cm depth', 'Soil organic carbon content at 100 cm depth', 'Soil organic carbon content at 200 cm depth','Soil organic carbon content at 30 cm depth','Soil organic carbon content at 60 cm depth']
climatekey_list =['Evapotranspiration','Downward longwave radiation flux','Net longwave radiation flux','Surface pressure','Specific humidity','Soil heat flux','Sensible heat net flux','Latent heat net flux','Storm surface runoff','Baseflow-groundwater runoff','Surface radiative temperature','Total precipitation rate','Snow cover fraction','Snow depth','Snowfall rate','Soil moisture (0 - 10 cm underground)','Soil moisture (10 - 40 cm underground)','Soil moisture (100 - 200 cm underground)','Soil moisture (40 - 100 cm underground)','Soil temperature (0 - 10 cm underground)','Soil temperature (10 - 40 cm underground)','Soil temperature (100 - 200 cm underground)','Soil temperature (40 - 100 cm underground)','Surface downward shortwave radiation','Snow water equivalent','Net shortwave radiation flux','Near surface air temperature','Near surface wind speed']


modified_climate_key_data = dict(zip(climatekey_list,list(climate_data.values())))
modified_soil_key_data = dict(zip(soilkey_list, list(soil_data.values())))

out_dict = {
             'rainfall' : rainfall_data,
             'population' : population_density_data,    
             'climate': modified_climate_key_data,
             'soil': modified_soil_key_data
             }
# print(modified_climate_key_data)