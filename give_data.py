import ee
from timeit import default_timer as timer

def given_data(region):
    start = timer()
    print("\n main code execution started")
    try:
        # Method 1: Defining the region with coordinates obtianed manually ,
        # Mumbai_Coordinates are the boundary coordinates of Mumbai Suburban
        Mumbai_Coordinates = ee.Geometry.Polygon([[83.1193749999224,18.112857087514755],[83.11929284890783,18.11251282490663],
                                                  [83.12000980321545,18.112498628495658],[83.12034214141096,18.112544766825977],
                                                  [83.12052884826153,18.112651239851033],[83.12055872135807,18.112796752879916],
                                                  [83.12052884826153,18.112974207628938],[83.12036081209516,18.113002600372653],
                                                  [83.11999860080425,18.112928069411723],[83.1193749999224,18.112857087514755]])

        # Method 2: Defining region with single pair of coordinates, in this case we can give a radis(in meters)
        # and can calculate the values of a circular region

        dd_long = 83.395551
        dd_lat = 18.106658

        # Method 3 : Defining the region from the features of an existing feature collection by FAO.(Food and Agricultural Organisation)
        # We have Level 2 Administrative regions's(Districts) features from the FeatureCollection("FAO/GAUL/2015/level2")
        # Import the featurecollection
        # boundarycoll = ee.FeatureCollection("FAO/GAUL/2015/level2")

        # district_features = region

        # Input year (this can be taken as an inpput from UI)
        year = '2020'
        # print(" \n Showing Data for the year: ", year)
        number = ee.Number(int(year))

        # Load the imagecollection of global population density

        population_coll = ee.ImageCollection(
            "CIESIN/GPWv411/GPW_Population_Density")  # Temporal Res = 5 years
        # Load the image of Soil Organic Carbon content
        soil_image = ee.Image(
            "OpenLandMap/SOL/SOL_ORGANIC-CARBON_USDA-6A1C_M/v02")
        # Load the climate data
        # Temporal Resolution = 1 Month
        climate_coll = ee.ImageCollection("NASA/FLDAS/NOAH01/C/GL/M/V001")
        # Load the rainfall data
        rainfall_coll = ee.ImageCollection(
            "UCSB-CHG/CHIRPS/DAILY")  # Temporal Resolution = 1 Day
        
        #load cloud cover data

        cloud_cover_coll = ee.ImageCollection("COPERNICUS/S2_CLOUD_PROBABILITY") # temporal resolution = 1 Day

        #load temperature data 

        temperature_coll = ee.ImageCollection("IDAHO_EPSCOR/TERRACLIMATE") # temporal resolution = 1 Month

        #Selecting maximum and minimum temperature bands from the collection
        max_temp_coll = temperature_coll.select('tmmx')
        min_temp_coll = temperature_coll.select('tmmn')


        # Get the Scale(Resolution) of the data
        rainfall_projection = rainfall_coll.first().projection()
        # print(" \n Rainfall data Projection: ",rainfall_projection.getInfo())
        rainfall_scale = int(rainfall_projection.nominalScale().getInfo())
        # print(" \n Rainfall Scale : ",rainfall_scale)

        cloud_cover_projection  = cloud_cover_coll.first().projection()
        # print("\n Cloud Cover Projection: ", cloud_cover_projection.getInfo())
        cloud_cover_scale = int(cloud_cover_projection.nominalScale().getInfo())
        # print("\n cloud_cover_scale: ", cloud_cover_scale)
        
        population_projection = population_coll.first().projection()
        # print("\n Population Projection: ",population_projection.getInfo())
        population_scale = int(population_projection.nominalScale().getInfo())
        # print("\n Population Scale: ", population_scale)
        
        climate_projection = climate_coll.first().projection()
        # print("\n Climate Projection: ",climate_projection.getInfo())
        climate_scale = int(climate_projection.nominalScale().getInfo())
        # print(" \n Climate Scale: ",climate_scale)

        soil_projection = soil_image.projection()
        # print("\n Soil Projection: ",soil_projection.getInfo())
        soil_scale = int(soil_projection.nominalScale().getInfo())
        # print(" \n Soil Scale: ",soil_scale)

        temperature_projection = temperature_coll.first().projection()
        # print("\n Temperature Projection: ",temperature_projection.getInfo())
        temperature_scale = int(temperature_projection.nominalScale().getInfo())
        # print(" \n Tempearture Scale: ",temperature_scale)

        reducerr = ee.Reducer.first()
        #The below method checks the input and if it is a polygon,gets the length of the sides and takes the median of them and sets the scale of the projection to this median value.
        coords = region.coordinates().getInfo()
        # print("coordinates are",coords)
        if(len(coords)==1):
            
            # print(coords[0])

            # Get the length of each side of the polygon
            sides = []
            for i in range(len(coords[0]) - 1):
                side = ee.Geometry.LineString([coords[0][i], coords[0][i+1]])
                length = side.length().getInfo()
                sides.append(length)

            # Calculate the median length of the sides
            sides_sorted = sorted(sides)
            n = len(sides_sorted)
            if n % 2 == 0:
                median_scale = (sides_sorted[n//2 - 1] + sides_sorted[n//2]) / 2
            else:
                median_scale = sides_sorted[n//2]
            climate_scale = median_scale
            soil_scale = median_scale
            population_scale = median_scale 
            rainfall_scale  = median_scale
            cloud_cover_scale = median_scale
            temperature_scale = median_scale
            reducerr = ee.Reducer.mean()
            # print("The median length of the sides is:", median_scale)

        # print("Reducer is",reducerr.getInfo())

        all_coll = [population_coll, climate_coll, rainfall_coll,cloud_cover_coll,max_temp_coll,min_temp_coll]

        filtered_coll = [None]*6

        # Filtering the collection for a period of one year

        def year_filter(number):

            start_date = ee.Date.fromYMD(number, 1, 1)
            end_date = start_date.advance(1, 'year')

            for i in range(0, len(all_coll)):
                filtered_coll[i] = all_coll[i].filterDate(start_date, end_date)

        year_filter(number)

        # For the time duration we can sum, take average etc of the data
        # Here we are taking sum for rainfall data and average for Population and climate data

        min_temp_mean = filtered_coll[5].reduce(ee.Reducer.min()).clip(region)
        max_temp_mean = filtered_coll[4].reduce(ee.Reducer.max()).clip(region)
        cloud_cover_mean = filtered_coll[3].reduce(ee.Reducer.mean()).clip(region)
        rainfall_sum = filtered_coll[2].reduce(ee.Reducer.sum()).clip(region)
        cli_mean = filtered_coll[1].reduce(ee.Reducer.mean()).clip(region)
        popul_mean = filtered_coll[0].reduce(ee.Reducer.mean()).clip(region)
        soil_image = soil_image.clip(region)

        # print("Cloud cover data",cloud_cover_mean.getInfo())

        cloud_cover_data = cloud_cover_mean.reduceRegion(
            reducer = reducerr,
            geometry =  region,
            scale= cloud_cover_scale,
            # bestEffort =True
        ).getInfo()['probability_mean']

        # print("cloud cover",cloud_cover_data)
        
        if cloud_cover_data is not None:
            cloud_cover_data = round(cloud_cover_data)
            cloud_cover_data = str(cloud_cover_data) + " %"
        # print('rainfall_data', type(rainfall_data))
        else:
            cloud_cover_data = 'Data is not available'

        
        max_temp_data = max_temp_mean.reduceRegion(
            reducer = reducerr,
            geometry =  region,
            scale= temperature_scale,
            # bestEffort =True
        ).getInfo()['tmmx_max']

        # print("max temp",max_temp_data)
        
        if max_temp_data is not None:
            max_temp_data = round(max_temp_data)
            max_temp_data = str(round(max_temp_data * 0.1)) + " ℃"
        # print('rainfall_data', type(rainfall_data))
        else:
            max_temp_data = 'Data is not available'

        
        min_temp_data = min_temp_mean.reduceRegion(
            reducer = reducerr,
            geometry =  region,
            scale= temperature_scale,
            # bestEffort =True
        ).getInfo()['tmmn_min']

        # print("min temp",min_temp_data)
        
        if min_temp_data is not None:
            min_temp_data = round(min_temp_data)
            min_temp_data = str(round(min_temp_data * 0.1)) + " ℃"
        # print('rainfall_data', type(rainfall_data))
        else:
            min_temp_data = 'Data is not available'
        
        
        rainfall_data = rainfall_sum.reduceRegion(

            # For given region we are taking the mean value of the pixels to
            # output the data, again here also we can perform sum
            # or take maximum/minimum values as per our requirement.
            reducer=reducerr,
            geometry=region,
            scale=rainfall_scale,
            # bestEffort =True


        ).getInfo()['precipitation_sum']
        # print("rainfall",rainfall_data)
        
        if rainfall_data is not None:
            rainfall_data = round(rainfall_data)
            rainfall_data = str(rainfall_data) + " mm per year"
        # print('rainfall_data', type(rainfall_data))
        else:
            rainfall_data = 'Data is not available'



        population_density_data = popul_mean.reduceRegion(

            reducer=reducerr,
            geometry=region,
            scale=population_scale,
            # bestEffort =True

        ).getInfo()['population_density_mean']

        
        if population_density_data is not None:
            population_density_data = round(population_density_data)
            population_density_data = str(population_density_data) + " per Sq. Km"
        else:
            population_density_data = 'Data is not available'

        climate_data = cli_mean.reduceRegion(

            reducer=reducerr,
            geometry=region,
            scale=climate_scale,
            # bestEffort =True


        ).getInfo()
        for key in climate_data:
            if climate_data[key] is not None:
                climate_data[key] = round(climate_data[key], 5)
            else:
                climate_data[key] = 'Data is not available'

        soil_data = soil_image.reduceRegion(
            reducer=reducerr,
            geometry=region,
            scale=soil_scale,
            # bestEffort =True
        ).getInfo()

        for key in soil_data:
            if soil_data[key] is not None:
                soil_data[key] = round(soil_data[key]/2,3)
            else:
                soil_data[key] = 'Data is not available'

        # print(soil_data)

        soilkey_list = ['Soil organic carbon content at 0 cm depth', 'Soil organic carbon content at 10 cm depth', 'Soil organic carbon content at 30 cm depth',
                        'Soil organic carbon content at 60 cm depth', 'Soil organic carbon content at 100 cm depth', 'Soil organic carbon content at 200 cm depth']
        climatekey_list = ['Evapotranspiration ', 'Downward longwave radiation flux ', 'Net longwave radiation flux ', 'Surface pressure', 'Specific humidity', 'Soil heat flux ', 'Sensible heat net flux', 'Latent heat net flux', 'Storm surface runoff', 'Baseflow-groundwater runoff', 'Surface radiative temperature', 'Total precipitation rate', 'Snow cover fraction', 'Snow depth', 'Snowfall rate', 'Soil moisture (0 - 10 cm underground)',
                           'Soil moisture (10 - 40 cm underground)', 'Soil moisture (40 - 100 cm underground)', 'Soil moisture (100 - 200 cm underground)', 'Soil temperature (0 - 10 cm underground)', 'Soil temperature (10 - 40 cm underground)', 'Soil temperature (40 - 100 cm underground)', 'Soil temperature (100 - 200 cm underground)', 'Surface downward shortwave radiation', 'Snow water equivalent', 'Net shortwave radiation flux', 'Near surface air temperature', 'Near surface wind speed']
        # climatevalue_unit_list = ['Kg/㎡/s',  'W/㎡', 'W/㎡', 'Pa', '1(mass fraction)', 'W/㎡', 'W/㎡', 'W/㎡', 'Kg/㎡/s', 'Kg/㎡/s', 'K', 'Kg/㎡/s', '', 'm', 'Kg/㎡/s', '1(volume fraction)',
        #                    '1(volume fraction)', '1(volume fraction)', '1(volume fraction)', 'K', 'K', 'K', 'K', 'W/㎡', 'Kg/㎡', 'W/㎡', 'K', 'm/s']


        climatevalue_unit_list = ['Kg/m*m/s',  'W/m*m', 'W/m*m', 'Pa', '1(mass fraction)', 'W/m*m', 'W/m*m', 'W/m*m', 'Kg/m*m/s', 'Kg/m*m/s', 'K', 'Kg/m*m/s', '', 'm', 'Kg/m*m/s', '1(volume fraction)',
                           '1(volume fraction)', '1(volume fraction)', '1(volume fraction)', 'K', 'K', 'K', 'K', 'W/m*m', 'Kg/m*m/s', 'W/m*m', 'K', 'm/s']
        climatevalue_list = [climate_data['Evap_tavg_mean'],climate_data['LWdown_f_tavg_mean'],climate_data['Lwnet_tavg_mean'],climate_data['Psurf_f_tavg_mean'],climate_data['Qair_f_tavg_mean'],climate_data['Qg_tavg_mean'],climate_data['Qh_tavg_mean'],climate_data['Qle_tavg_mean'],climate_data['Qs_tavg_mean'],climate_data['Qsb_tavg_mean'],climate_data['RadT_tavg_mean'],climate_data['Rainf_f_tavg_mean'],climate_data['SnowCover_inst_mean'],climate_data['SnowDepth_inst_mean'],climate_data['Snowf_tavg_mean'],climate_data['SoilMoi00_10cm_tavg_mean'],climate_data['SoilMoi10_40cm_tavg_mean'],climate_data['SoilMoi40_100cm_tavg_mean'],climate_data['SoilMoi100_200cm_tavg_mean'],climate_data['SoilTemp00_10cm_tavg_mean'],climate_data['SoilTemp10_40cm_tavg_mean'],climate_data['SoilTemp40_100cm_tavg_mean'],climate_data['SoilTemp100_200cm_tavg_mean'],climate_data['SWdown_f_tavg_mean'],climate_data['SWE_inst_mean'],climate_data['Swnet_tavg_mean'],climate_data['Tair_f_tavg_mean'],climate_data['Wind_f_tavg_mean']]
        soilvalue_list = [soil_data['b0'],soil_data['b10'],soil_data['b30'],soil_data['b60'],soil_data['b100'],soil_data['b200']]

        new_soil_value_list = []
        for i in range (len(soilvalue_list)):
            new_soil_value_list.append(str(soilvalue_list[i])+" %")

        new_climate_valuelist = []
        for i in range(len(climatevalue_list)):
            new_climate_valuelist.append(str(climatevalue_list[i])+" "+climatevalue_unit_list[i])  
        

        modified_climate_key_data = dict(
            zip(climatekey_list, new_climate_valuelist))

        modified_soil_key_data = dict(
            zip(soilkey_list, new_soil_value_list))
        
        out_dict = {
            'Climate': modified_climate_key_data,
            'Cloud': {'Cloud Cover Probability':cloud_cover_data},
            'Temperature': {'Maximum Temperature':max_temp_data,'Minimum Temperature': min_temp_data},
            'Population': {'Population': population_density_data},
            'Soil': modified_soil_key_data,
            'Rainfall':{'Total Rainfall': rainfall_data,},
        }
        # print(out_dict)
        print("execution done")
        end = timer()
        print("\n ", round(end-start,5))
        return (out_dict)

    except ValueError:
        return "Invalid Input"
