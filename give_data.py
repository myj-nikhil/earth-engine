import ee


def given_data(region):
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
        year = '2010'
        print("Showing Data for the year: ", year)
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

        # Get the Scale(Resolution) of the data
        rainfall_projection = rainfall_coll.first().projection()
        print(" \n Rainfall data Projection: ",rainfall_projection.getInfo())
        rainfall_scale = int(rainfall_projection.nominalScale().getInfo())
        print(" \n Rainfall Scale : ",rainfall_scale)
        
        population_projection = population_coll.first().projection()
        print("\n Population Projection: ",population_projection.getInfo())
        population_scale = int(population_projection.nominalScale().getInfo())
        print("\n Population Scale: ", population_scale)
        
        climate_projection = climate_coll.first().projection()
        print("\n Climate Projection: ",climate_projection.getInfo())
        climate_scale = int(climate_projection.nominalScale().getInfo())
        print(" \n Climate Scale: ",climate_scale)

        soil_projection = soil_image.projection()
        print("\n Soil Projection: ",soil_projection.getInfo())
        soil_scale = int(soil_projection.nominalScale().getInfo())
        print(" \n Soil Scale: ",soil_scale)

#The below method checks the input and if it is a polygon,gets the length of the sides and takes the median of them and sets the scale of the projection to this median value.
        coords = region.coordinates().getInfo()
        if(len(coords)==1):
            
            print(coords[0])

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
            print("The median length of the sides is:", median_scale)



        all_coll = [population_coll, climate_coll, rainfall_coll]

        filtered_coll = [None]*3

        # Filtering the collection for a period of one year

        def year_filter(number):

            start_date = ee.Date.fromYMD(number, 1, 1)
            end_date = start_date.advance(1, 'year')

            for i in range(0, len(all_coll)):
                filtered_coll[i] = all_coll[i].filterDate(start_date, end_date)

        year_filter(number)

        # For the time duration we can sum, take average etc of the data
        # Here we are taking sum for rainfall data and average for Population and climate data

        rainfall_sum = filtered_coll[2].reduce(ee.Reducer.sum()).clip(region)
        popul_mean = filtered_coll[0].reduce(ee.Reducer.mean()).clip(region)
        cli_mean = filtered_coll[1].reduce(ee.Reducer.mean()).clip(region)
        soil_image = soil_image.clip(region)

        rainfall_data = rainfall_sum.reduceRegion(

            # For given region we are taking the mean value of the pixels to
            # output the data, again here also we can perform sum
            # or take maximum/minimum values as per our requirement.
            reducer=ee.Reducer.mean(),
            geometry=region,
            scale=rainfall_scale

        ).getInfo()['precipitation_sum']

        

        print(rainfall_data)
        
        if rainfall_data is not None:
            rainfall_data = round(rainfall_data)
            rainfall_data = str(rainfall_data) + " mm"
        # print('rainfall_data', type(rainfall_data))
        else:
            rainfall_data = 'Data is not available'

        population_density_data = popul_mean.reduceRegion(

            reducer=ee.Reducer.mean(),
            geometry=region,
            scale=population_scale,
            bestEffort =True

        ).getInfo()['population_density_mean']

        
        if population_density_data is not None:
            population_density_data = round(population_density_data)
            population_density_data = str(population_density_data) + " per Sq. Km"
        else:
            population_density_data = 'Data is not available'

        climate_data = cli_mean.reduceRegion(

            reducer=ee.Reducer.mean(),
            geometry=region,
            scale=climate_scale,
            bestEffort =True


        ).getInfo()
        for key in climate_data:
            if climate_data[key] is not None:
                climate_data[key] = round(climate_data[key], 5)
                print(key)
            else:
                climate_data[key] = 'Data is not available'

        soil_data = soil_image.reduceRegion(
            reducer=ee.Reducer.mean(),
            geometry=region,
            scale=soil_scale,
            bestEffort =True
        ).getInfo()

        for key in soil_data:
            if soil_data[key] is not None:
                soil_data[key] = round(soil_data[key]/2)
            else:
                soil_data[key] = 'Data is not available'

        soilkey_list = ['Soil organic carbon content at 0 cm depth', 'Soil organic carbon content at 10 cm depth', 'Soil organic carbon content at 100 cm depth',
                        'Soil organic carbon content at 200 cm depth', 'Soil organic carbon content at 30 cm depth', 'Soil organic carbon content at 60 cm depth']
        climatekey_list = ['Evapotranspiration ', 'Downward longwave radiation flux ', 'Net longwave radiation flux ', 'Surface pressure', 'Specific humidity', 'Soil heat flux ', 'Sensible heat net flux', 'Latent heat net flux', 'Storm surface runoff', 'Baseflow-groundwater runoff', 'Surface radiative temperature', 'Total precipitation rate', 'Snow cover fraction', 'Snow depth', 'Snowfall rate', 'Soil moisture (0 - 10 cm underground)',
                           'Soil moisture (10 - 40 cm underground)', 'Soil moisture (100 - 200 cm underground)', 'Soil moisture (40 - 100 cm underground)', 'Soil temperature (0 - 10 cm underground)', 'Soil temperature (10 - 40 cm underground)', 'Soil temperature (100 - 200 cm underground)', 'Soil temperature (40 - 100 cm underground)', 'Surface downward shortwave radiation', 'Snow water equivalent', 'Net shortwave radiation flux', 'Near surface air temperature', 'Near surface wind speed']

        climatevalue_unit_list = ['Kg/㎡/s',  'W/㎡', 'W/㎡', 'Pa', '1(mass fraction)', 'W/㎡', 'W/㎡', 'W/㎡', 'Kg/㎡/s', 'Kg/㎡/s', 'K', 'Kg/㎡/s', '', 'm', 'Kg/㎡/s', '1(volume fraction)',
                           '1(volume fraction)', '1(volume fraction)', '1(volume fraction)', 'K', 'K', 'K', 'K', 'W/㎡', 'Kg/㎡', 'W/㎡', 'K', 'm/s']
        climatevalue_list = list(climate_data.values())
        soilvalue_list = list(soil_data.values())

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
            'Rainfall': rainfall_data,
            'Population': population_density_data,
            'Climate': modified_climate_key_data,
            'Soil': modified_soil_key_data
        }
        print(out_dict)

        return (out_dict)

    except ValueError:
        return "Invalid Input"
