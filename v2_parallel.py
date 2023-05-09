import ee
from timeit import default_timer as timer
import concurrent.futures
import cProfile
import logging

app_logger = logging.getLogger('v2_parallel.py')
app_logger.setLevel(logging.DEBUG)

file_handler = logging.FileHandler('app.log', mode='a')
file_handler.setLevel(logging.DEBUG)

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
file_handler.setFormatter(formatter)

app_logger.addHandler(file_handler)

# start1 = timer()
# # Add the service account mail ID from Google Cloud
# service_account = 'project-xyz@project-xyz-383203.iam.gserviceaccount.com'
# # Give the location of the privatekey file of the service account
# credentials = ee.ServiceAccountCredentials(
#     service_account, 'project-xyz-383203.json')
# ee.Initialize(credentials)
# end1 = timer()
# app_logger.info("Time for initialisation : ", end1-start1)


def population(population_image,region,centroid):
            start = timer()
            scale = 927.6624232772793
            is_larger = population_image.reduceRegion(ee.Reducer.count(), region,scale).get('population_density_mean')
            roi = ee.Algorithms.If(is_larger, region, centroid)
            population_density_data = population_image.reduceRegion(ee.Reducer.mean(), roi,scale).getInfo()['population_density_mean']
            if population_density_data is not None:
                population_density_data = round(population_density_data)
                population_density_data = str(population_density_data) + " per Sq. Km"
            else:
                population_density_data = 'Data is not available'
            end = timer()
            app_logger.info("time for population : %s",round(end-start,5))    
            # app_logger.info("PPD :", population_density_data)
            return population_density_data

def organic_soil(soil_image,region,centroid):
    start = timer()

    is_larger = soil_image.reduceRegion(ee.Reducer.count(),region).get('b0')

    app_logger.info("time for is_larger : %s ",round(timer()-start,5))


    # app_logger.info("islarger",is_larger)
    
    roi = ee.Algorithms.If(is_larger, region, centroid)

    app_logger.info("time for reg check : %s ",round(timer()-start,5))
    
    soil_data = soil_image.reduceRegion(ee.Reducer.mean(),roi).getInfo()
    
    for key in soil_data:
        if soil_data[key] is not None:
            soil_data[key] = '{:.3f}'.format(round(soil_data[key]/2,3))
        else:
            soil_data[key] = 'Data is not available'

    # app_logger.info(soil_data)

    soilkey_list = ['Soil organic carbon content at 0 cm depth', 'Soil organic carbon content at 10 cm depth', 'Soil organic carbon content at 30 cm depth',
                'Soil organic carbon content at 60 cm depth', 'Soil organic carbon content at 100 cm depth', 'Soil organic carbon content at 200 cm depth']
    soilvalue_list = [soil_data['b0'],soil_data['b10'],soil_data['b30'],soil_data['b60'],soil_data['b100'],soil_data['b200']]

    new_soil_value_list = []
    for i in range (len(soilvalue_list)):
        new_soil_value_list.append(str(soilvalue_list[i])+" %")
    modified_soil_data = dict(
        zip(soilkey_list, new_soil_value_list))
    end = timer()
    app_logger.info("Time taken for organic_carbon : %s ",round(end-start,5))
    # app_logger.info("Soil Data: ", modified_soil_data)
    return modified_soil_data

def sand_fraction(sand_fraction_image,region,centroid):
    start = timer()

    is_larger = sand_fraction_image.reduceRegion(ee.Reducer.count(), region).get('b0')

    roi = ee.Algorithms.If(is_larger, region, centroid)
    
    sand_fraction_data = sand_fraction_image.reduceRegion(ee.Reducer.mean(), roi).getInfo()
    
    sand_fraction_key_list = ['Sand content at 0 cm depth', 'Sand content at 10 cm depth', 'Sand content at 30 cm depth', 
                                'Sand content at 60 cm depth', 'Sand content at 100 cm depth', 'Sand content at 200 cm depth']
    sand_fraction_value_list = [sand_fraction_data['b0'],sand_fraction_data['b10'],sand_fraction_data['b30'],sand_fraction_data['b60'],sand_fraction_data['b100'],sand_fraction_data['b200']]
    
    for i in range (len(sand_fraction_value_list)):
        if sand_fraction_value_list[i] is None: sand_fraction_value_list[i] = 'Data is not available'
        else: sand_fraction_value_list[i] = '{:.3f}'.format(round(sand_fraction_value_list[i],3))+ "% (kg / kg)"
    
    modified_sand_fraction_data = dict(zip(sand_fraction_key_list,sand_fraction_value_list))
    end = timer()
    app_logger.info("TIme taken for sand_fraction : %s ",round(end-start,5))
    return modified_sand_fraction_data

def soil_bulk_density(soil_bulk_density_image,region,centroid):
            start = timer()

            is_larger = soil_bulk_density_image.reduceRegion(ee.Reducer.count(), region).get('b0')

            roi = ee.Algorithms.If(is_larger, region, centroid)

            soil_bulk_density_data = soil_bulk_density_image.reduceRegion(ee.Reducer.mean(),roi).getInfo()
            soil_bulk_density_key_list = ['Soil bulk density at 0 cm depth', 'Soil bulk density at 10 cm depth', 'Soil bulk density at 30 cm depth', 
                                'Soil bulk density at 60 cm depth', 'Soil bulk density at 100 cm depth', 'Soil bulk density at 200 cm depth']
            soil_bulk_density_value_list = [soil_bulk_density_data['b0'],soil_bulk_density_data['b10'],soil_bulk_density_data['b30'],soil_bulk_density_data['b60'],soil_bulk_density_data['b100'],soil_bulk_density_data['b200']]
            for i in range (len(soil_bulk_density_value_list)):
                if soil_bulk_density_value_list[i] is None: soil_bulk_density_value_list[i] = 'Data is not available'
                else : soil_bulk_density_value_list[i] = '{:.3f}'.format(round(soil_bulk_density_value_list[i],3))+" (10 x kg / m-cubic)"
            modified_soil_bulk_density_data = dict(zip(soil_bulk_density_key_list,soil_bulk_density_value_list))
            end = timer()
            app_logger.info("Time taken for soil_bulk_density : %s ",round(end-start,5))
            return modified_soil_bulk_density_data

def soil_ph(soil_ph_image,region,centroid):
    start = timer()
    is_larger = soil_ph_image.reduceRegion(ee.Reducer.count(),region).get('b0')
    roi = ee.Algorithms.If(is_larger, region, centroid)
    soil_ph_data = soil_ph_image.reduceRegion(ee.Reducer.mean(),roi).getInfo()
    soil_ph_key_list = ['Soil pH in H2O at 0 cm depth', 'Soil pH in H2O at 10 cm depth', 'Soil pH in H2O at 30 cm depth', 
                                    'Soil pH in H2O at 60 cm depth', 'Soil pH in H2O at 100 cm depth', 'Soil pH in H2O at 200 cm depth']
    soil_ph_value_list = [soil_ph_data['b0'],soil_ph_data['b10'],soil_ph_data['b30'],soil_ph_data['b60'],soil_ph_data['b100'],soil_ph_data['b200']]
    for i in range(len(soil_ph_value_list)):
        if soil_ph_value_list[i] is None: soil_ph_value_list[i] = 'Data is not available'
        else : soil_ph_value_list[i]='{:.3f}'.format(round(soil_ph_value_list[i]/10,3))
    modified_soil_ph_data = dict(zip(soil_ph_key_list,soil_ph_value_list))
    end = timer()
    app_logger.info("Time for soil_pH : %s ",round(end-start,5))
    return modified_soil_ph_data

def soil_water_content(soil_water_content_image,region,centroid):
    start=timer()
    roi =  region
    is_larger = soil_water_content_image.reduceRegion(ee.Reducer.count(),region).get('b0')
    roi = ee.Algorithms.If(is_larger, region, centroid)
    soil_water_content_data = soil_water_content_image.reduceRegion(ee.Reducer.mean(),roi).getInfo()
    soil_water_content_key_list = ['Soil water content at 33kpa - 0cm', 'Soil water content at 33kpa - 10cm', 'Soil water content at 33kpa - 30cm', 
                                    'Soil water content at 33kpa - 60cm', 'Soil water content at 33kpa - 100cm', 'Soil water content at 33kpa - 200cm']
    soil_water_content_value_list = [soil_water_content_data['b0'],soil_water_content_data['b10'],soil_water_content_data['b30'],soil_water_content_data['b60'],soil_water_content_data['b100'],soil_water_content_data['b200']]
    for i in range(len(soil_water_content_value_list)):
        if soil_water_content_value_list[i] is None: soil_water_content_value_list[i] = 'Data is not available'
        else : soil_water_content_value_list[i] = '{:.3f}'.format(round(soil_water_content_value_list[i],3))+" (volumetric) %"
    
    modified_soil_water_content_data = dict(zip(soil_water_content_key_list,soil_water_content_value_list))
    end = timer()
    app_logger.info("Time for soil_water_content : %s ",round(end-start,5))

    return modified_soil_water_content_data 

def soil_texture(soil_texture_class_image,region,centroid):
    start=timer()
    is_larger = soil_texture_class_image.reduceRegion(ee.Reducer.count(),region).get('b0')
    roi = ee.Algorithms.If(is_larger, region, centroid)
    soil_texture_class_data = soil_texture_class_image.reduceRegion(ee.Reducer.mode(),roi).getInfo()
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
    soil_texture_class_key_list = ['Soil texture class (USDA system) at 0 cm depth', 'Soil texture class (USDA system) at 10 cm depth', 'Soil texture class (USDA system) at 30 cm depth', 
                                'Soil texture class (USDA system) at 60 cm depth', 'Soil texture class (USDA system) at 100 cm depth', 'Soil texture class (USDA system) at 200 cm depth']
    
    soil_texture_class_value_list = [soil_texture_class_data['b0'],soil_texture_class_data['b10'],soil_texture_class_data['b30'],soil_texture_class_data['b60'],soil_texture_class_data['b100'],soil_texture_class_data['b200']]

    for i in range (len( soil_texture_class_value_list)):
        if soil_texture_class_value_list[i] is not None:
            for item in soil_texture_class_value_ref_list:
                if item[0] == soil_texture_class_value_list[i] :  soil_texture_class_value_list[i] = item[3]
        else: soil_texture_class_value_list[i] = 'Data is not available'

    modified_soil_texture_class_data = dict(zip(soil_texture_class_key_list, soil_texture_class_value_list))

    end = timer()
    app_logger.info("Time taken for soil_texture : %s ",round(end-start,5))
    return modified_soil_texture_class_data
        

def soil_great_group(soil_great_group_image,region,centroid):
    start = timer()
    is_larger = soil_great_group_image.reduceRegion(ee.Reducer.count(),region).get('grtgroup')
    roi = ee.Algorithms.If(is_larger, region, centroid)
    soil_great_group_data = soil_great_group_image.reduceRegion(ee.Reducer.mode(),roi).getInfo()['grtgroup']
    app_logger.info("soil_great_group_data: %s ",soil_great_group_data)
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
    if soil_great_group_data is not None :
        soil_group = soil_great_group_data
        for item in soil_great_group_value_ref_list:
            if item[0] == soil_great_group_data :
                # app_logger.info(item)
                soil_group = item[2]
    else : soil_group = 'Data is not available'
    end = timer()
    app_logger.info("Time for soil_group :  %s ", round(end-start,5))
    
    return soil_group

def climate(climate_image,region,centroid):
    start  = timer()
    scale = 11131.949079327358
    is_larger = climate_image.reduceRegion(ee.Reducer.count(),region,scale).get('Evap_tavg_mean')
    roi = ee.Algorithms.If(is_larger, region, centroid)
    climate_data = climate_image.reduceRegion(ee.Reducer.mean(),roi,scale).getInfo()
    for key in climate_data:
        if climate_data[key] is not None:
            climate_data[key] = '{:.5f}'.format(round(climate_data[key], 5))
        else:
            climate_data[key] = 'Data is not available'
    climatekey_list = ['Evapotranspiration ', 'Downward longwave radiation flux ', 'Net longwave radiation flux ', 'Surface pressure', 'Specific humidity', 'Soil heat flux ', 'Sensible heat net flux', 'Latent heat net flux', 'Storm surface runoff', 'Baseflow-groundwater runoff', 'Surface radiative temperature', 'Total precipitation rate', 'Snow cover fraction', 'Snow depth', 'Snowfall rate', 'Soil moisture (0 - 10 cm underground)',
                    'Soil moisture (10 - 40 cm underground)', 'Soil moisture (40 - 100 cm underground)', 'Soil moisture (100 - 200 cm underground)', 'Soil temperature (0 - 10 cm underground)', 'Soil temperature (10 - 40 cm underground)', 'Soil temperature (40 - 100 cm underground)', 'Soil temperature (100 - 200 cm underground)', 'Surface downward shortwave radiation', 'Snow water equivalent', 'Net shortwave radiation flux', 'Near surface air temperature', 'Near surface wind speed']
    climatevalue_unit_list = ['Kg/m*m/s',  'W/m*m', 'W/m*m', 'Pa', '1(mass fraction)', 'W/m*m', 'W/m*m', 'W/m*m', 'Kg/m*m/s', 'Kg/m*m/s', 'K', 'Kg/m*m/s', '', 'm', 'Kg/m*m/s', '1(volume fraction)',
                            '1(volume fraction)', '1(volume fraction)', '1(volume fraction)', 'K', 'K', 'K', 'K', 'W/m*m', 'Kg/m*m/s', 'W/m*m', 'K', 'm/s']
    climatevalue_list = [climate_data['Evap_tavg_mean'],climate_data['LWdown_f_tavg_mean'],climate_data['Lwnet_tavg_mean'],climate_data['Psurf_f_tavg_mean'],climate_data['Qair_f_tavg_mean'],climate_data['Qg_tavg_mean'],climate_data['Qh_tavg_mean'],climate_data['Qle_tavg_mean'],climate_data['Qs_tavg_mean'],climate_data['Qsb_tavg_mean'],climate_data['RadT_tavg_mean'],climate_data['Rainf_f_tavg_mean'],climate_data['SnowCover_inst_mean'],climate_data['SnowDepth_inst_mean'],climate_data['Snowf_tavg_mean'],climate_data['SoilMoi00_10cm_tavg_mean'],climate_data['SoilMoi10_40cm_tavg_mean'],climate_data['SoilMoi40_100cm_tavg_mean'],climate_data['SoilMoi100_200cm_tavg_mean'],climate_data['SoilTemp00_10cm_tavg_mean'],climate_data['SoilTemp10_40cm_tavg_mean'],climate_data['SoilTemp40_100cm_tavg_mean'],climate_data['SoilTemp100_200cm_tavg_mean'],climate_data['SWdown_f_tavg_mean'],climate_data['SWE_inst_mean'],climate_data['Swnet_tavg_mean'],climate_data['Tair_f_tavg_mean'],climate_data['Wind_f_tavg_mean']]

    new_climate_valuelist = []
    for i in range(len(climatevalue_list)):
        new_climate_valuelist.append(str(climatevalue_list[i])+" "+climatevalue_unit_list[i])

    modified_climate_data = dict(zip(climatekey_list, new_climate_valuelist))   

    end = timer()   
    app_logger.info("Time taken for climate : %s ", round(end-start,5))

    return modified_climate_data


def rainfall(filtered_rainfall_coll,rainfall_yearly_image,region,centroid):
    start =  timer()
    scale = 5565.974539663679
    
    def getMonthlyAverages(img_coll):
  # Define a list of months to loop through
        months = ee.List.sequence(1, 12)

        # Define a function to get the monthly averages
        def getMonthlyAverage(month):
            # Filter the collection by the current month
            filtered_month = img_coll.filter(ee.Filter.calendarRange(month, month, 'month'))

            # Calculate the mean for the current month
            monthly_mean = filtered_month.reduce(ee.Reducer.sum())
            is_larger = monthly_mean.reduceRegion(ee.Reducer.count(),region,scale).get('precipitation_sum')
            roi = ee.Algorithms.If(is_larger, region, centroid)
            # Clip the image to the region of interest
            clipped_mean = monthly_mean

            # Get the average rainfall value for the region of interest
            rainfall_value = clipped_mean.reduceRegion(ee.Reducer.mean(), geometry=roi, scale=5565.974539663679).get('precipitation_sum')

            # Return the month and the average rainfall value
            return rainfall_value

            # Map the function over the list of months
        monthly_averages = months.map(getMonthlyAverage)

        # Return the monthly averages as a list
        return monthly_averages.getInfo()
    is_larger = rainfall_yearly_image.reduceRegion(ee.Reducer.count(),region,scale).get('precipitation_sum')
    roi = ee.Algorithms.If(is_larger, region, centroid)
    # Clip the image to the region of interest
    # Get the average rainfall value for the region of interest
    rainfall_sum_yearly = rainfall_yearly_image.reduceRegion(ee.Reducer.mean(), geometry=roi, scale=5565.974539663679).getInfo()['precipitation_sum']
    if rainfall_sum_yearly is not None:
        rainfall_sum_yearly = round(rainfall_sum_yearly)
        rainfall_sum_yearly = str(rainfall_sum_yearly) + " mm per year"
    else:
        rainfall_sum_yearly = 'Data is not available'

    # Get the monthly averages for the filtered collection
    monthly_averages = getMonthlyAverages(filtered_rainfall_coll)
    rounded_values = []
    for value in monthly_averages:
        if value is not None:
            rounded_value = "{:.3f}".format(value)
            rounded_values.append(rounded_value)
    output = [value + " mm" if value is not None else None for value in rounded_values]
    month_list = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
    rainfall_sum_monthly  = dict(zip(month_list,output))
   
    end = timer()
    app_logger.info("Time taken for rainfall : %s ", round(end-start,5))

    return [rainfall_sum_monthly,rainfall_sum_yearly]


def cloud(cloud_image,region,centroid):
    start = timer()
    scale  = 10
    new_cloud_image = cloud_image.clip(region)
    is_larger = new_cloud_image.reduceRegion(reducer= ee.Reducer.count(),geometry = region,scale=scale).get('probability_mean')
    # app_logger.info("is_larger in cloud : ",is_larger)
    # app_logger.info("time for islarger in cloud : ",round(timer()-start,5))
    roi = ee.Algorithms.If(is_larger, region, centroid)
    cloud_cover_data = new_cloud_image.reduceRegion(reducer= ee.Reducer.mean(),geometry = roi,scale=scale).getInfo()['probability_mean']
    # app_logger.info(cloud_cover_data)
    if cloud_cover_data is not None:
        cloud_cover_data = round(cloud_cover_data,2)
        cloud_cover_data = str(cloud_cover_data) + " %"
    else:
        cloud_cover_data = 'Data is not available'
    end = timer()
    app_logger.info("Time taken for cloud : %s ", round(end-start,5))

    return cloud_cover_data

def max_temp(max_temp_image,region,centroid):
    start = timer()
    scale = 4638.312116386398
    is_larger = max_temp_image.reduceRegion(ee.Reducer.count(),region,scale).get('tmmx_max')
    roi = ee.Algorithms.If(is_larger, region, centroid)
    max_temp_data = max_temp_image.reduceRegion(ee.Reducer.mean(),roi,scale).getInfo()['tmmx_max']
    if max_temp_data is not None:
        max_temp_data = round(max_temp_data,2)
        max_temp_data = str(round(max_temp_data * 0.1)) + " ℃"
    else:
        max_temp_data = 'Data is not available'
    end = timer()
    app_logger.info("Time for max_temp : %s ",round(end-start,5))

    return max_temp_data


def min_temp(min_temp_image,region,centroid):
    start = timer()

    # Determine if the minimum temperature image covers the entire region
    is_larger = min_temp_image.reduceRegion(reducer=ee.Reducer.count(),geometry=region,scale=4638.312116386398).get('tmmn_min')

    # Choose the region of interest based on whether the image covers the entire region
    roi = ee.Algorithms.If(is_larger, region, centroid)

    # Reduce the minimum temperature image within the region of interest and get the minimum temperature value
    min_temp_data = min_temp_image.reduceRegion(
    reducer=ee.Reducer.mean(),
    geometry=roi,
    scale=4638.312116386398
    ).get('tmmn_min').getInfo()

    # Convert the minimum temperature value to Celsius and round to the nearest degree
    if min_temp_data is not None:
        min_temp_data = round(min_temp_data * 0.1,2)
        min_temp_data = str(min_temp_data) + " ℃"
    else:
        min_temp_data = 'Data is not available'

    # End the timer and app_logger.info the time elapsed and the minimum temperature value
    end = timer()
    app_logger.info(f"Time for min_temp: {round(end-start,5)}")

    return min_temp_data 



def v2_parallel_point(region):

    try :
        # pr = cProfile.Profile()
        # pr.enable()
        start = timer()
        # app_logger.info("\n main code execution started")
        year = '2020'
        # dd_long = 83.395551
        # dd_lat = 18.106658
        # #region = ee.Geometry.Polygon([[70.57762138834659,28.43379607099714],[70.57762138834659,28.43330075366702],[70.57898395052615,28.433296036347983],[70.57899467936221,28.433852678544397],[70.57762138834659,28.43386211313265],[70.57762138834659,28.43379607099714]])
        # #region = ee.Geometry.Point([dd_long,dd_lat])
        # app_logger.info(" \n Showing Data for the year: ", year)

        # Load the imagecollection of global population density

        centroid  = region.centroid()
        population_coll = ee.ImageCollection(
            "CIESIN/GPWv411/GPW_Population_Density")  # Temporal Res = 5 years
        
        filtered_pop_collection = population_coll.filterDate(str(year)+'-01-01', str(year)+'-12-31')

        population_image = filtered_pop_collection.reduce(ee.Reducer.mean())
        # Load the image of Soil Organic Carbon content
        soil_image = ee.Image(
            "OpenLandMap/SOL/SOL_ORGANIC-CARBON_USDA-6A1C_M/v02")

        sand_fraction_image= ee.Image("OpenLandMap/SOL/SOL_SAND-WFRACTION_USDA-3A1A1A_M/v02")

        soil_bulk_density_image = ee.Image("OpenLandMap/SOL/SOL_BULKDENS-FINEEARTH_USDA-4A1H_M/v02") 

        soil_ph_image = ee.Image("OpenLandMap/SOL/SOL_PH-H2O_USDA-4C1A2A_M/v02")

        soil_water_content_image = ee.Image("OpenLandMap/SOL/SOL_WATERCONTENT-33KPA_USDA-4B1C_M/v01")

        soil_texture_class_image = ee.Image("OpenLandMap/SOL/SOL_TEXTURE-CLASS_USDA-TT_M/v02")

        soil_great_group_image = ee.Image("OpenLandMap/SOL/SOL_GRTGROUP_USDA-SOILTAX_C/v01")

        climate_coll = ee.ImageCollection("NASA/FLDAS/NOAH01/C/GL/M/V001")

        filtered_cli_collection = climate_coll.filterDate(str(year)+'-01-01', str(year)+'-12-31')

        climate_image = filtered_cli_collection.reduce(ee.Reducer.mean())

        rainfall_coll = ee.ImageCollection("UCSB-CHG/CHIRPS/DAILY")
        
        filtered_rainfall_coll = rainfall_coll.filterDate(str(year)+'-01-01', str(year)+'-12-31')

        rainfall_yearly_image = filtered_rainfall_coll.reduce(ee.Reducer.sum())


        cloud_cover_coll = ee.ImageCollection("COPERNICUS/S2_CLOUD_PROBABILITY") # temporal resolution = 1 Day

        filtered_cloud_collection = cloud_cover_coll.filterDate(str(year)+'-01-01', str(year)+'-12-31')

        cloud_image = filtered_cloud_collection.reduce(ee.Reducer.mean())


        temperature_coll = ee.ImageCollection("IDAHO_EPSCOR/TERRACLIMATE") # temporal resolution = 1 Month

        temperature_coll = ee.ImageCollection("IDAHO_EPSCOR/TERRACLIMATE") # temporal resolution = 1 Month
        temperature_projection = temperature_coll.first().projection()
        # app_logger.info("\n Temperature Projection: ",temperature_projection.getInfo())
        temperature_scale = temperature_projection.nominalScale().getInfo()
        # app_logger.info(" \n Tempearture Scale: ",temperature_scale)

        filtered_temp_collection = temperature_coll.filterDate(str(year)+'-01-01', str(year)+'-12-31')


        #Selecting maximum and minimum temperature bands from the collection
        max_temp_coll = filtered_temp_collection.select('tmmx')

        max_temp_image = max_temp_coll.reduce(ee.Reducer.max())

        min_temp_coll = temperature_coll.select('tmmn')

        min_temp_image = min_temp_coll.reduce(ee.Reducer.min())




        # def get_value(input, timereducer,spacereducer, region, year):
            
        #     if isinstance(input, ee.image.Image):
        #             image = input
        #             # app_logger.info("\n The input is an Image.")
        #             projection = image.projection()
        #             scale = projection.nominalScale().getInfo()
        #             # app_logger.info("\n Scale: ", scale)

        #     elif isinstance(input, ee.imagecollection.ImageCollection):
        #             # app_logger.info("\n The input is an ImageCollection.")
        #             image_collection  = input
        #             projection = image_collection.first().projection()
        #             # app_logger.info("\n  Projection: ",projection.getInfo())
                    
        #             scale = projection.nominalScale().getInfo()
        #             # app_logger.info("\n  Scale: ", scale)
                    
        #             # Filter the image collection for the given year
        #             filtered_collection = image_collection.filterDate(str(year)+'-01-01', str(year)+'-12-31')

        #             # Reduce the image collection to a single image using mean()
        #             image = filtered_collection.reduce(reducer=timereducer)
        #     # else:   app_logger.info("The input is neither an Image nor an ImageCollection.")
            
        #     # Check if the region is a point or a polygon
        #     if region.type().getInfo() == 'Point':
        #         # If the region is a point, use reducer.first() at original scale of the image
        #         # app_logger.info("\n Region is a Point")
        #         value = image.reduceRegion(ee.Reducer.first(), region, scale).getInfo()

        #     else:
        #         # If the region is a polygon, check if the region is larger than an pixel at original resolution of image
        #         # app_logger.info("\n Region is a Polygon")
        #         first_band = image.select(0)
        #         band_name = first_band.bandNames().getInfo()
        #         is_larger = image.reduceRegion(ee.Reducer.anyNonZero(), region, scale).getInfo()[band_name[0]]
                
        #         # app_logger.info("\n is larger",is_larger)

        #         if is_larger:
        #             # app_logger.info("region is larger than original pixel")
        #             # app_logger.info(band_name[0])
        #             # If the region is larger than an pixel at original resolution of image, use reducer.mean() at original scale of the image
        #             value = image.reduceRegion(reducer=spacereducer, geometry = region, scale=scale).getInfo()
        #         else:
        #             # If the region is smaller than an pixel at original resolution of image, take the centroid of region and output using reducer.first() at original scale of the image
        #             # app_logger.info("\n region is smaller than the original pixel")
        #             centroid = region.centroid()
        #             value = image.reduceRegion(ee.Reducer.first(), centroid, scale).getInfo()
                    

        #     return value

        
        with concurrent.futures.ThreadPoolExecutor(max_workers=13) as executor:
            future1 = executor.submit(climate,climate_image,region,centroid)
            future2 = executor.submit(organic_soil,soil_image,region,centroid)
            future3 = executor.submit(sand_fraction,sand_fraction_image,region,centroid)
            future4 = executor.submit(soil_bulk_density,soil_bulk_density_image,region,centroid)
            future5 = executor.submit(soil_ph,soil_ph_image,region,centroid)
            future6 = executor.submit(soil_water_content,soil_water_content_image,region,centroid)
            future7 = executor.submit(soil_texture,soil_texture_class_image,region,centroid)
            future8 = executor.submit(soil_great_group,soil_great_group_image,region,centroid)
            future9 = executor.submit(population,population_image,region,centroid)
            future10 = executor.submit(rainfall,filtered_rainfall_coll,rainfall_yearly_image,region,centroid)
            future11 = executor.submit(cloud,cloud_image,region,centroid)
            future12 = executor.submit(max_temp,max_temp_image,region,centroid)
            future13 = executor.submit(min_temp,min_temp_image,region,centroid)

            # app_logger.info(future1)
            # app_logger.info(future2)
            # try:
            #     app_logger.info(future2.result())
            # except Exception:
            #     traceback.app_logger.info_exc()

            # app_logger.info(future9)
            # try:
            #     app_logger.info(future9.result())
            # except Exception:
            #     traceback.app_logger.info_exc()

        wait = timer()
        app_logger.info("Time elapesed until before wait line : %s ",round(wait-start,5))

        concurrent.futures.wait([future1,future2 ,future3,future4,future5,future6,future7,future8,future9,future10,future11,future12,future13])

        app_logger.info("Time elapesed until after wait line : %s ",round(timer()-wait,5))

        out_dict = {
            'Climate': future1.result(),
            'Cloud': {'Cloud Cover Probability':future11.result()},
            'Temperature': {'Maximum Temperature': future12.result(),'Minimum Temperature': future13.result()},
            'Population': {'Population': future9.result()},
            'Soil': future2.result(),
            'Rainfall':{'Total Rainfall':future10.result()[1]},
            'Sand Fraction':future3.result(),
            'Soil Bulk Density': future4.result(),
            'Soil pH': future5.result(),
            'Soil Water Content':future6.result(),
            'Soil Texture Class': future7.result(),
            'Soil Great Group': {"Soil Great Group":future8.result()}, 
            'monthly_rainfall': future10.result()[0]  
        }
        # app_logger.info("execution done")
        end = timer()
        app_logger.info(" Time for main code :%s ", round(end-start,5))
        # app_logger.info(out_dict)
        # stop profiling
        # pr.disable()

        # app_logger.info the profiling results
        # pr.app_logger.info_stats()
        # import pstats

# create a Stats object from the cProfile object
        # stats = pstats.Stats(pr)

        # app_logger.info the top 10 functions by cumulative time
        # stats.strip_dirs().sort_stats('cumulative').app_logger.info_stats(10)
        return (out_dict)
    
    except ValueError:
        app_logger.error('%s raised an error', ValueError)
        return "Invalid Input"


