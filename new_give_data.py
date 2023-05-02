import ee
from timeit import default_timer as timer

def new_given_data(region):
    start = timer()
    print("\n main code execution started")
    print("executing in new_give_data.py")
    try:
        

        # Input year (this can be taken as an inpput from UI)
        year = '2020'
        # print(" \n Showing Data for the year: ", year)

        # Load the imagecollection of global population density

        population_coll = ee.ImageCollection(
            "CIESIN/GPWv411/GPW_Population_Density")  # Temporal Res = 5 years
        # Load the image of Soil Organic Carbon content
        soil_image = ee.Image(
            "OpenLandMap/SOL/SOL_ORGANIC-CARBON_USDA-6A1C_M/v02")
        
        sand_fraction = ee.Image("OpenLandMap/SOL/SOL_SAND-WFRACTION_USDA-3A1A1A_M/v02")

        soil_bulk_density = ee.Image("OpenLandMap/SOL/SOL_BULKDENS-FINEEARTH_USDA-4A1H_M/v02") 

        soil_ph = ee.Image("OpenLandMap/SOL/SOL_PH-H2O_USDA-4C1A2A_M/v02")

        soil_water_content = ee.Image("OpenLandMap/SOL/SOL_WATERCONTENT-33KPA_USDA-4B1C_M/v01")

        soil_texture_class = ee.Image("OpenLandMap/SOL/SOL_TEXTURE-CLASS_USDA-TT_M/v02")

        soil_great_group = ee.Image("OpenLandMap/SOL/SOL_GRTGROUP_USDA-SOILTAX_C/v01")
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

        # For the time duration we can sum, take average etc of the data
        # Here we are taking sum for rainfall data and average for Population and climate data
        
        def get_value(image_collection, timereducer,spacereducer, region, year):
            
            if isinstance(image_collection, ee.image.Image):
                    image = image_collection
                    # print("\n The input is an Image.")
                    projection = image.projection()
                    scale = projection.nominalScale().getInfo()
                    # print("\n Scale: ", scale)

            elif isinstance(image_collection, ee.imagecollection.ImageCollection):
                    # print("\n The input is an ImageCollection.")
                    projection = image_collection.first().projection()
                    # print("\n  Projection: ",projection.getInfo())
                    
                    scale = projection.nominalScale().getInfo()
                    # print("\n  Scale: ", scale)
                    
                    # Filter the image collection for the given year
                    filtered_collection = image_collection.filterDate(str(year)+'-01-01', str(year)+'-12-31')

                    # Reduce the image collection to a single image using mean()
                    image = filtered_collection.reduce(reducer=timereducer)
            # else:   print("The input is neither an Image nor an ImageCollection.")
            
            # Check if the region is a point or a polygon
            if region.type().getInfo() == 'Point':
                # If the region is a point, use reducer.first() at original scale of the image
                # print("\n Region is a Point")
                value = image.reduceRegion(ee.Reducer.first(), region, scale).getInfo()

            else:
                # If the region is a polygon, check if the region is larger than an pixel at original resolution of image
                # print("\n Region is a Polygon")
                first_band = image.select(0)
                band_name = first_band.bandNames().getInfo()
                is_larger = image.reduceRegion(ee.Reducer.anyNonZero(), region, scale).getInfo()[band_name[0]]
                
                # print("\n is larger",is_larger)

                if is_larger:
                    # print("region is larger than original pixel")
                    # print(band_name[0])
                    # If the region is larger than an pixel at original resolution of image, use reducer.mean() at original scale of the image
                    value = image.reduceRegion(reducer=spacereducer, geometry = region, scale=scale).getInfo()
                else:
                    # If the region is smaller than an pixel at original resolution of image, take the centroid of region and output using reducer.first() at original scale of the image
                    # print("\n region is smaller than the original pixel")
                    centroid = region.centroid()
                    value = image.reduceRegion(ee.Reducer.first(), centroid, scale).getInfo()
                    

            return value

        population_density_data = get_value(population_coll, ee.Reducer.mean(),ee.Reducer.mean(), region, year)['population_density_mean']
        climate_data = get_value(climate_coll,ee.Reducer.mean(),ee.Reducer.mean(),region,year)
        rainfall_data = get_value(rainfall_coll,ee.Reducer.sum(),ee.Reducer.mean(),region,year)['precipitation_sum']
        cloud_cover_data = get_value(cloud_cover_coll, ee.Reducer.mean(),ee.Reducer.mean(),region,year)['probability_mean']
        max_temp_data = get_value(max_temp_coll,ee.Reducer.max(),ee.Reducer.mean(),region,year)['tmmx_max']
        min_temp_data = get_value(min_temp_coll,ee.Reducer.min(),ee.Reducer.mean(),region,year)['tmmn_min']    
        soil_data = get_value(soil_image,ee.Reducer.mean(),ee.Reducer.mean(),region,year)
        sand_fraction_data = get_value(sand_fraction,ee.Reducer.mean(),ee.Reducer.mean(),region,year)
        soil_bulk_density_data = get_value(soil_bulk_density,ee.Reducer.mean(),ee.Reducer.mean(),region,year)
        soil_ph_data = get_value(soil_ph,ee.Reducer.mean(),ee.Reducer.mean(),region,year)
        soil_water_content_data = get_value(soil_water_content,ee.Reducer.mean(),ee.Reducer.mean(),region,year)
        soil_texture_class_data = get_value(soil_texture_class,ee.Reducer.mean(),ee.Reducer.mode(),region,year)
        soil_great_group_data = get_value(soil_great_group,ee.Reducer.mean(),ee.Reducer.mode(),region,year)['grtgroup']

        soil_great_group_value_ref_list = [
            [0, "ffffff", "NODATA"],
            [1, "adff2d", "Albaqualfs"],
            [2, "adff22", "Cryaqualfs"],
            [4, "a5ff2f", "Durixeralfs"],
            [6, "87ff37", "Endoaqualfs"],
            [7, "baf019", "Epiaqualfs"],
            [9, "87ff19", "Fragiaqualfs"],
            [10, "96f03d", "Fragiudalfs"],
            [11, "a3f52f", "Fragixeralfs"],
            [12, "aff319", "Fraglossudalfs"],
            [13, "91ff37", "Glossaqualfs"],
            [14, "9cf319", "Glossocryalfs"],
            [15, "9bff37", "Glossudalfs"],
            [16, "91ff19", "Haplocryalfs"],
            [17, "71ff37", "Haploxeralfs"],
            [18, "86ff19", "Hapludalfs"],
            [19, "a9d42d", "Haplustalfs"],
            [25, "aff519", "Natraqualfs"],
            [26, "9bff19", "Natrixeralfs"],
            [27, "9af024", "Natrudalfs"],
            [28, "a5fd2f", "Natrustalfs"],
            [29, "88ff37", "Palecryalfs"],
            [30, "afed19", "Paleudalfs"],
            [31, "71ff19", "Paleustalfs"],
            [32, "aff026", "Palexeralfs"],
            [38, "8cf537", "Rhodustalfs"],
            [39, "b7ff19", "Vermaqualfs"],
            [41, "7177c0", "Eutroboralfs"],
            [42, "9a85ec", "Ochraqualfs"],
            [43, "f5f5e1", "Glossoboralfs"],
            [44, "52cf5a", "Cryoboralfs"],
            [45, "e42777", "Natriboralfs"],
            [46, "4ef76d", "Paleboralfs"],
            [50, "ff00fb", "Cryaquands"],
            [58, "eb05eb", "Fulvicryands"],
            [59, "fa04fa", "Fulvudands"],
            [61, "fc04f5", "Haplocryands"],
            [63, "f50df0", "Haploxerands"],
            [64, "f118f1", "Hapludands"],
            [74, "fa0cfa", "Udivitrands"],
            [75, "fc05e1", "Ustivitrands"],
            [76, "f100d5", "Vitraquands"],
            [77, "eb09e6", "Vitricryands"],
            [80, "fa22fa", "Vitrixerands"],
            [82, "ffdab9", "Aquicambids"],
            [83, "f5d2bb", "Aquisalids"],
            [85, 'e8c9b8', 'Argidurids'],
            [86, 'ffddc4', 'Argigypsids'],
            [87, 'e7cbc0', 'Calciargids'],
            [89, 'ffd2c3', 'Calcigypsids'],
            [90, 'f5d6bb', 'Gypsiargids'],
            [92, 'd5d3b9', 'Haplargids'],
            [93, 'e8d4b8', 'Haplocalcids'],
            [94, 'e7cdc0', 'Haplocambids'],
            [96, 'f3eac8', 'Haplodurids'],
            [97, 'a0c4ba', 'Haplogypsids'],
            [98, 'ffd2b9', 'Haplosalids'],
            [99, 'f5dabb', 'Natrargids'],
            [100, 'f5d5b9', 'Natridurids'],
            [101, 'e8ebb8', 'Natrigypsids'],
            [102, 'ffddc2', 'Paleargids'],
            [103, 'e7ffc0', 'Petroargids'],
            [104, 'f3e6c8', 'Petrocalcids'],
            [105, 'ffdab9', 'Petrocambids'],
            [107, 'f5cdb9', 'Petrogypsids'],
            [110, 'a91d30', 'Calciorthids'],
            [111, '796578', 'Camborthids'],
            [112, 'd8ff6e', 'Paleorthids'],
            [113, '177548', 'Durorthids'],
            [114, '43efd6', 'Durargids'],
            [115, '8496a9', 'Gypsiorthids'],
            [116, '296819', 'Nadurargids'],
            [118, '73ffd4', 'Cryaquents'],
            [119, '6fffc8', 'Cryofluvents'],
            [120, '75fbc9', 'Cryopsamments'],
            [121, '86f5d1', 'Cryorthents'],
            [122, '82ffd2', 'Endoaquents'],
            [123, '88eec8', 'Epiaquents'],
            [124, '80ffd4', 'Fluvaquents'],
            [126, '6bffc9', 'Frasiwassents'],
            [131, '88eec8', 'Hydraquents'],
            [133, '7fffc8', 'Psammaquents'],
            [134, '81ffd2', 'Psammowassents'],
            [135, '86f0d4', 'Quartzipsamments'],
            [136, '67ffc8', 'Sulfaquents'],
            [137, '88eec8', 'Sulfiwassents'],
            [138, '7ffbcb', 'Torrifluvents'],
            [139, '87ffd2', 'Torriorthents'],
            [140, '8af5ce', 'Torripsamments'],
            [141, '6bfad2', 'Udifluvents'],
            [142, '78f0d4', 'Udipsamments'],
            [143, '88eec8', 'Udorthents'],
            [144, '7ffbd4', 'Ustifluvents'],
            [145, '73f5cd', 'Ustipsamments'],
            [146, '88c8d2', 'Ustorthents'],
            [147, '91f0cd', 'Xerofluvents'],
            [148, '73cdd2', 'Xeropsamments'],
            [149, '88eec8', 'Xerorthents'],
            [153, 'fb849b', 'Udarents'],
            [154, 'dd4479', 'Torriarents'],
            [155 ,'61388b' ,'Xerarents'],
            [179 ,'a52a30' ,'Cryofibrists'],
            [180, '722328' ,'Cryofolists'],
            [181 ,'d81419' ,'Cryohemists'],
            [182 ,'a42828' ,'Cryosaprists'],
            [183 ,'82f5cd' ,'Frasiwassists'],
            [184 ,'a54c2e' ,'Haplofibrists'],
            [185 ,'c11919' ,'Haplohemists'],
            [186 ,'b91419' ,'Haplosaprists'],
            [189 ,'21b199' ,'Sphagnofibrists'],
            [190 ,'702028' ,'Sulfihemists'],
            [191 ,'b41919' ,'Sulfisaprists'],
            [196 ,'b22328' ,'Udifolists'],
            [201 ,'a2c7eb' ,'Borosaprists'],
            [202 ,'36ba79' ,'Medisaprists'],
            [203 ,'806797' ,'Borohemists'],
            [206 ,'cb5b5f' ,'Calcicryepts'],
            [207 ,'cd5c5c' ,'Calciustepts'],
            [208 ,'d94335' ,'Calcixerepts'],
            [209 ,'d35740' ,'Cryaquepts'],
            [210 ,'e05a5d' ,'Durixerepts'],
            [212 ,'cf5b5c' ,'Durustepts'],
            [213 ,'ca5964' ,'Dystrocryepts'],
            [215 ,'ca5d5f' ,'Dystroxerepts'],
            [216 ,'cd5e5a' ,'Dystrudepts'],
            [217 ,'ca5969' ,'Dystrustepts'],
            [218 ,'d95a35' ,'Endoaquepts'],
            [219 ,'d36240', 'Epiaquepts'],
            [220 ,'e05c43' ,'Eutrudepts'],
            [221 ,'d64755' ,'Fragiaquepts'],
            [222 ,'cf595c' ,'Fragiudepts'],
            [225 ,'ff5f5f', 'Halaquepts'],
            [226 ,'cd6058' 'Haplocryepts'],
            [228 ,'d95f35' ,'Haploxerepts'],
            [229 ,'d35140' ,'Haplustepts'],
            [230 ,'d65a55' ,'Humaquepts'],
            [231 ,'e05c59' ,'Humicryepts'],
            [233 ,'cf525e' ,'Humixerepts'],
            [234 ,'c65978' ,'Humudepts'],
            [235 ,'f5615f' ,'Humustepts'],
            [245 ,'826f9a' ,'Ustochrepts'],
            [246 ,'cff41a' ,'Eutrochrepts'],
            [247 ,'4a6f31' ,'Dystrochrepts'],
            [248 ,'a96989' ,'Eutrocryepts'],
            [249 ,'e16438' ,'Haplaquepts'],
            [250 ,'24f640' ,'Xerochrepts'],
            [251 ,'88c1f9' ,'Cryochrepts'],
            [252 ,'f5d25c' ,'Fragiochrepts'],
            [253 ,'d74322' ,'Haplumbrepts'],
            [254 ,'7f939e' ,'Cryumbrepts'],
            [255 ,'41a545' ,'Dystro'],
            [246, 'cff41a', 'Eutrochrepts'],
            [247, '4a6f31', 'Dystrochrepts'],
            [248, 'a96989', 'Eutrocryepts'],
            [249, 'e16438', 'Haplaquepts'],
            [250, '24f640', 'Xerochrepts'],
            [251, '88c1f9', 'Cryochrepts'],
            [252, 'f5d25c', 'Fragiochrepts'],
            [253, 'd74322', 'Haplumbrepts'],
            [254, '7f939e', 'Cryumbrepts'],
            [255, '41a545', 'Dystropepts'],
            [256, '8f8340', 'Vitrandepts'],
            [268, '09fe03', 'Argialbolls'],
            [269, '0aff00', 'Argiaquolls'],
            [270, '0ff30f', 'Argicryolls'],
            [271, '02f00a', 'Argiudolls'],
            [272, '0fc903', 'Argiustolls'],
            [273, '17f000', 'Argixerolls'],
            [274, '0cff00', 'Calciaquolls'],
            [275, '0ac814', 'Calcicryolls'],
            [276, '0cfe00', 'Calciudolls'],
            [277, '0aff0a', 'Calciustolls'],
            [278, '03ff05', 'Calcixerolls'],
            [279, '1cf31c', 'Cryaquolls'],
            [280, '24f000', 'Cryrendolls'],
            [283, '00ff0c', 'Durixerolls'],
            [284, '14c814', 'Durustolls'],
            [285, '00fe4c', 'Endoaquolls'],
            [286, '14ff96', 'Epiaquolls'],
            [287, '44d205', 'Haplocryolls'],
            [289, '05f305', 'Haploxerolls'],
            [290, '62f00a', 'Hapludolls'],
            [291, '0fcd03', 'Haplustolls'],
            [292, '00d20f', 'Haprendolls'],
            [294, '1add11', 'Natraquolls'],
            [296, '09ff0c', 'Natrixerolls'],
            [297, '03ff05', 'Natrudolls'],
            [298, '05e700', 'Natrustolls'],
            [299, '02f00a', 'Palecryolls'],
            [300, '0fea03', 'Paleudolls'],
            [301, '00f000', 'Paleustolls'],
            [302, '0ccb0c', 'Palexerolls'],
            [303, '14dd14', 'Vermudolls'],
            [306, '6a685d', 'Haploborolls'],
            [307, 'fae6b9', 'Argiborolls'],
            [308, '769a34', 'Haplaquolls'],
            [309, '6ff2df', 'Cryoborolls'],
            [310, 'ca7fc6', 'Natriborolls'],
            [311, 'd8228f', 'Calciborolls'],
            [312, 'c01bf0', 'Paleborolls'],
            [342, 'd2bad3', 'Alaquods'],
            [343, 'd8c3cb', 'Alorthods'],
            [345, 'd4c6d4', 'Duraquods'],
            [348, 'd5bed5', 'Durorthods'],
            [349, 'ddb9dd', 'Endoaquods'],
            [350, 'd8d2d8', 'Epiaquods'],
            [351, 'd4c9d4', 'Fragiaquods'],
            [353, 'd2bad5', 'Fragiorthods'],
            [354, 'd5bad5', 'Haplocryods'],
            [356, 'd5b2d5', 'Haplohumods'],
            [357, 'd8c8d2', 'Haplorthods'],
            [358, 'd4cbd4', 'Humicryods'],
            [367, '552638', 'Haplaquods'],
            [368, '2571eb', 'Cryorthods'],
            [370, 'ffa514', 'Albaquults'],
            [371, 'f3a502', 'Endoaquults'],
            [372, 'fb7b00', 'Epiaquults'],
            [373, 'f0b405', 'Fragiaquults'],
            [374, 'f7a80f', 'Fragiudults'],
            [375, 'fb9113', 'Haplohumults'],
            [376, 'ffa519', 'Haploxerults'],
            [377, 'f3a702', 'Hapludults'],
            [378, 'fbba07', 'Haplustults'],
            [381, 'f7970f', 'Kandiudults'],
            [385, 'f3a702', 'Kanhapludults'],
            [387, 'fb5a00', 'Paleaquults'],
            [388, 'f0c005', 'Palehumults'],
            [389, 'f7810f', 'Paleudults'],
            [390, 'ff9c00', 'Paleustults'],
            [391, 'f3b002', 'Palexerults'],
            [396, 'f0b005', 'Rhodudults'],
            [399, 'f7980f', 'Umbraquults'],
            [401, '4d7cfc', 'Ochraquults'],
            [403, 'ffff00', 'Calciaquerts'],
            [405, 'fafa05', 'Calciusterts'],
            [406, 'ebeb22', 'Calcixererts'],
            [409, 'ffff14', 'Dystraquerts'],
            [410, 'f1f10a', 'Dystruderts'],
            [412, 'fafa05', 'Endoaquerts'],
            [413, 'ebeb1e', 'Epiaquerts'],
            [414, 'f5eb0c', 'Gypsitorrerts'],
            [415, 'eef506', 'Gypsiusterts'],
            [417, 'f1f129', 'Haplotorrerts'],
            [418, 'fafa05', 'Haploxererts'],
            [419, 'ebeb0c', 'Hapluderts'],
            [420, 'f5d202', 'Haplusterts'],
            [422, 'ffd700', 'Natraquerts'],
            [424, 'f1f12b', 'Salitorrerts'],
            [429, 'a91fac', 'Chromusterts'],
            [430, "2da468", "Pellusterts"],
            [431, "9a8b71", "Chromoxererts"],
            [432, "76b989", "Pelluderts"],
            [433, "713959", "Torrerts"]
            ]



        soil_texture_class_value_ref_list = [[1, 'd5c36b', 'Cl','Clay'],
                                    [2, 'b96947', 'SiCl','Silty Clay'],
                                    [3, '9d3706', 'SaCl','Sandy Clay'],
                                    [4, 'ae868f', 'ClLo','Clay Loam'],
                                    [5, 'f86714', 'SiClLo','Silty Clay Loam'],
                                    [6, '46d143', 'SaClLo','Sandy Clay Loam'],
                                    [7, '368f20', 'Lo','Loam'],
                                    [8, '3e5a14', 'SiLo','Silty Loam'],
                                    [9, 'ffd557', 'SaLo','Sandy Loam'],
                                    [10, 'fff72e', 'Si','Silt'],
                                    [11, 'ff5a9d', 'LoSa','Loamy Sand'],
                                    [12, 'ff005b', 'Sa','Sand']]





        # print("Cloud cover data",cloud_cover_mean.getInfo())

        # print("cloud cover",cloud_cover_data)
        
        if cloud_cover_data is not None:
            cloud_cover_data = round(cloud_cover_data)
            cloud_cover_data = str(cloud_cover_data) + " %"
            # print('rainfall_data', type(rainfall_data))
        else:
            cloud_cover_data = 'Data is not available'

        # print("max temp",max_temp_data)
        
        if max_temp_data is not None:
            max_temp_data = round(max_temp_data)
            max_temp_data = str(round(max_temp_data * 0.1)) + " ℃"
        else:
            max_temp_data = 'Data is not available'
    
        # print("min temp",min_temp_data)
        
        if min_temp_data is not None:
            min_temp_data = round(min_temp_data)
            min_temp_data = str(round(min_temp_data * 0.1)) + " ℃"
        else:
            min_temp_data = 'Data is not available'
        
       
        # print("rainfall",rainfall_data)
        
        if rainfall_data is not None:
            rainfall_data = round(rainfall_data)
            rainfall_data = str(rainfall_data) + " mm per year"
        else:
            rainfall_data = 'Data is not available'
        
        if population_density_data is not None:
            population_density_data = round(population_density_data)
            population_density_data = str(population_density_data) + " per Sq. Km"
        else:
            population_density_data = 'Data is not available'

        
        for key in climate_data:
            if climate_data[key] is not None:
                climate_data[key] = round(climate_data[key], 5)
            else:
                climate_data[key] = 'Data is not available'

        for key in soil_data:
            if soil_data[key] is not None:
                soil_data[key] = round(soil_data[key]/2,3)
            else:
                soil_data[key] = 'Data is not available'

        # print(soil_data)

        soilkey_list = ['Soil organic carbon content at 0 cm depth', 'Soil organic carbon content at 10 cm depth', 'Soil organic carbon content at 30 cm depth',
                        'Soil organic carbon content at 60 cm depth', 'Soil organic carbon content at 100 cm depth', 'Soil organic carbon content at 200 cm depth']
        
        sand_fraction_key_list = ['Sand content at 0 cm depth', 'Sand content at 10 cm depth', 'Sand content at 30 cm depth', 
                                        'Sand content at 60 cm depth', 'Sand content at 100 cm depth', 'Sand content at 200 cm depth']
            
        soil_bulk_density_key_list = ['Soil bulk density at 0 cm depth', 'Soil bulk density at 10 cm depth', 'Soil bulk density at 30 cm depth', 
                                        'Soil bulk density at 60 cm depth', 'Soil bulk density at 100 cm depth', 'Soil bulk density at 200 cm depth']
            
        soil_ph_key_list = ['Soil pH in H2O at 0 cm depth', 'Soil pH in H2O at 10 cm depth', 'Soil pH in H2O at 30 cm depth', 
                                        'Soil pH in H2O at 60 cm depth', 'Soil pH in H2O at 100 cm depth', 'Soil pH in H2O at 200 cm depth']
            
        soil_water_content_key_list = ['Soil water content at 33kPa (field capacity) at 0 cm depth', 'Soil water content at 33kPa (field capacity) at 10 cm depth', 'Soil water content at 33kPa (field capacity) at 30 cm depth', 
                                        'Soil water content at 33kPa (field capacity) at 60 cm depth', 'Soil water content at 33kPa (field capacity) at 100 cm depth', 'Soil water content at 33kPa (field capacity) at 200 cm depth']
            
        soil_texture_class_key_list = ['Soil texture class (USDA system) at 0 cm depth', 'Soil texture class (USDA system) at 10 cm depth', 'Soil texture class (USDA system) at 30 cm depth', 
                                        'Soil texture class (USDA system) at 60 cm depth', 'Soil texture class (USDA system) at 100 cm depth', 'Soil texture class (USDA system) at 200 cm depth']
                    
            
            
            
        climatekey_list = ['Evapotranspiration ', 'Downward longwave radiation flux ', 'Net longwave radiation flux ', 'Surface pressure', 'Specific humidity', 'Soil heat flux ', 'Sensible heat net flux', 'Latent heat net flux', 'Storm surface runoff', 'Baseflow-groundwater runoff', 'Surface radiative temperature', 'Total precipitation rate', 'Snow cover fraction', 'Snow depth', 'Snowfall rate', 'Soil moisture (0 - 10 cm underground)',
                            'Soil moisture (10 - 40 cm underground)', 'Soil moisture (40 - 100 cm underground)', 'Soil moisture (100 - 200 cm underground)', 'Soil temperature (0 - 10 cm underground)', 'Soil temperature (10 - 40 cm underground)', 'Soil temperature (40 - 100 cm underground)', 'Soil temperature (100 - 200 cm underground)', 'Surface downward shortwave radiation', 'Snow water equivalent', 'Net shortwave radiation flux', 'Near surface air temperature', 'Near surface wind speed']
        climatevalue_unit_list = ['Kg/㎡/s',  'W/㎡', 'W/㎡', 'Pa', '1(mass fraction)', 'W/㎡', 'W/㎡', 'W/㎡', 'Kg/㎡/s', 'Kg/㎡/s', 'K', 'Kg/㎡/s', '', 'm', 'Kg/㎡/s', '1(volume fraction)',
                            '1(volume fraction)', '1(volume fraction)', '1(volume fraction)', 'K', 'K', 'K', 'K', 'W/㎡', 'Kg/㎡', 'W/㎡', 'K', 'm/s']


        climatevalue_unit_list = ['Kg/m*m/s',  'W/m*m', 'W/m*m', 'Pa', '1(mass fraction)', 'W/m*m', 'W/m*m', 'W/m*m', 'Kg/m*m/s', 'Kg/m*m/s', 'K', 'Kg/m*m/s', '', 'm', 'Kg/m*m/s', '1(volume fraction)',
                            '1(volume fraction)', '1(volume fraction)', '1(volume fraction)', 'K', 'K', 'K', 'K', 'W/m*m', 'Kg/m*m/s', 'W/m*m', 'K', 'm/s']
        climatevalue_list = [climate_data['Evap_tavg_mean'],climate_data['LWdown_f_tavg_mean'],climate_data['Lwnet_tavg_mean'],climate_data['Psurf_f_tavg_mean'],climate_data['Qair_f_tavg_mean'],climate_data['Qg_tavg_mean'],climate_data['Qh_tavg_mean'],climate_data['Qle_tavg_mean'],climate_data['Qs_tavg_mean'],climate_data['Qsb_tavg_mean'],climate_data['RadT_tavg_mean'],climate_data['Rainf_f_tavg_mean'],climate_data['SnowCover_inst_mean'],climate_data['SnowDepth_inst_mean'],climate_data['Snowf_tavg_mean'],climate_data['SoilMoi00_10cm_tavg_mean'],climate_data['SoilMoi10_40cm_tavg_mean'],climate_data['SoilMoi40_100cm_tavg_mean'],climate_data['SoilMoi100_200cm_tavg_mean'],climate_data['SoilTemp00_10cm_tavg_mean'],climate_data['SoilTemp10_40cm_tavg_mean'],climate_data['SoilTemp40_100cm_tavg_mean'],climate_data['SoilTemp100_200cm_tavg_mean'],climate_data['SWdown_f_tavg_mean'],climate_data['SWE_inst_mean'],climate_data['Swnet_tavg_mean'],climate_data['Tair_f_tavg_mean'],climate_data['Wind_f_tavg_mean']]
        soilvalue_list = [soil_data['b0'],soil_data['b10'],soil_data['b30'],soil_data['b60'],soil_data['b100'],soil_data['b200']]
        sand_fraction_value_list = [sand_fraction_data['b0'],sand_fraction_data['b10'],sand_fraction_data['b30'],sand_fraction_data['b60'],sand_fraction_data['b100'],sand_fraction_data['b200']]
        soil_bulk_density_value_list = [soil_bulk_density_data['b0'],soil_bulk_density_data['b10'],soil_bulk_density_data['b30'],soil_bulk_density_data['b60'],soil_bulk_density_data['b100'],soil_bulk_density_data['b200']]
        soil_ph_value_list = [soil_ph_data['b0'],soil_ph_data['b10'],soil_ph_data['b30'],soil_ph_data['b60'],soil_ph_data['b100'],soil_ph_data['b200']]
        soil_water_content_value_list = [soil_water_content_data['b0'],soil_water_content_data['b10'],soil_water_content_data['b30'],soil_water_content_data['b60'],soil_water_content_data['b100'],soil_water_content_data['b200']]
        soil_texture_class_value_list = [soil_texture_class_data['b0'],soil_texture_class_data['b10'],soil_texture_class_data['b30'],soil_texture_class_data['b60'],soil_texture_class_data['b100'],soil_texture_class_data['b200']]

        # print(soil_texture_class_value_list )
        
        for i in range (len(sand_fraction_value_list)):
            if sand_fraction_value_list[i] is None: sand_fraction_value_list[i] = 'Data is not available'
            else: sand_fraction_value_list[i] = str(round(sand_fraction_value_list[i],5))+ "% (kg / kg)"

        for i in range (len(soil_bulk_density_value_list)):
            if soil_bulk_density_value_list[i] is None: soil_bulk_density_value_list[i] = 'Data is not available'
            else : soil_bulk_density_value_list[i] = str(round(soil_bulk_density_value_list[i],5))+" (10 x kg / m-cubic)"
        

        for i in range(len(soil_ph_value_list)):
            if soil_ph_value_list[i] is None: soil_ph_value_list[i] = 'Data is not available'
            else : soil_ph_value_list[i]=str(round(soil_ph_value_list[i]/10,5))
        
        for i in range(len(soil_water_content_value_list)):
            if soil_water_content_value_list[i] is None: soil_water_content_value_list[i] = 'Data is not available'
            else : soil_water_content_value_list[i] = str(round(soil_water_content_value_list[i],5))+" (volumetric) %"
        
        new_soil_value_list = []
        for i in range (len(soilvalue_list)):
            new_soil_value_list.append(str(soilvalue_list[i])+" %")

        for i in range (len( soil_texture_class_value_list)):
            if soil_texture_class_value_list[i] is not None:
                for item in soil_texture_class_value_ref_list:
                    if item[0] == soil_texture_class_value_list[i] :  soil_texture_class_value_list[i] = item[3]
            else: soil_texture_class_value_list[i] = 'Data is not available'            
        

        new_climate_valuelist = []
        for i in range(len(climatevalue_list)):
            new_climate_valuelist.append(str(climatevalue_list[i])+" "+climatevalue_unit_list[i])  
        

        modified_climate_key_data = dict(
            zip(climatekey_list, new_climate_valuelist))

        modified_soil_data = dict(
            zip(soilkey_list, new_soil_value_list))
        
        modified_sand_fraction_data = dict(
            zip(sand_fraction_key_list,sand_fraction_value_list)
        )
        
        modified_soil_bulk_density_data = dict(
            zip(soil_bulk_density_key_list,soil_bulk_density_value_list)
        )

        modified_soil_ph_data = dict(
            zip(soil_ph_key_list,soil_ph_value_list)
        )

        modified_soil_water_content_data = dict(
            zip(soil_water_content_key_list,soil_water_content_value_list)
        )

        modified_soil_texture_class_data = dict(
                zip(soil_texture_class_key_list, soil_texture_class_value_list)
        )

        if soil_great_group_data is not None :
            soil_group = soil_great_group_data
            for item in soil_great_group_value_ref_list:
                if item[0] == soil_great_group_data :
                    # print(item)
                    soil_group = item[2]
        else : soil_group = 'Data is not available'



        out_dict = {
            'Climate': modified_climate_key_data,
            'Cloud': {'Cloud Cover Probability':cloud_cover_data},
            'Temperature': {'Maximum Temperature':max_temp_data,'Minimum Temperature': min_temp_data},
            'Population': {'Population': population_density_data},
            'Soil': modified_soil_data,
            'Rainfall':{'Total Rainfall': rainfall_data,},
            'Sand Fraction': modified_sand_fraction_data,
            'Soil Bulk Density': modified_soil_bulk_density_data,
            'Soil pH': modified_soil_ph_data,
            'Soil Water Content':modified_soil_water_content_data,
            'Soil Texture Class': modified_soil_texture_class_data,
            'Soil Great Group': {"Soil Great Group":soil_group}
        }
        # print(out_dict)
        print("execution done")
        end = timer()
        print("\n Time for main code", round(end-start,5))
        return (out_dict)

    except ValueError:
        return "Invalid Input"
