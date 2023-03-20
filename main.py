
import ee
service_account = 'helpful-aurora-380816@appspot.gserviceaccount.com'
credentials = ee.ServiceAccountCredentials(service_account, 'private-key.json')
ee.Initialize(credentials)
from flask import Flask, render_template
from flask import request 

app = Flask(__name__)

@app.route("/")
def index():
      district = request.args.get("district", "")
    #   year = request.args.get("year","")
      output = give_data(district)
      return render_template('index.html',district=district,output=output,population = output.get('population'),rainfall=output.get('rainfall'))



def give_data(district):
    try:
        organic_carbon = ee.Image("OpenLandMap/SOL/SOL_ORGANIC-CARBON_USDA-6A1C_M/v02")
        
        # Method 1: Defining the region with coordinates obtianed manually , 
        # Mumbai_Coordinates are the boundary coordinates of Mumbai Suburban 
        Mumbai_Coordinates = ee.Geometry.Polygon([[72.820578,19.044863],[72.788306,19.265397],[72.830191,19.249840],
                                                  [72.852851,19.268638],[72.934562,19.194729],[72.978507,19.156464],[72.955848,19.081207],
                                                  [72.956534,19.029285],[72.885810,18.996826],[72.878257,19.047460],[72.820578,19.044863]])
        
        # Method 2: Defining region with single pair of coordinates, in this case we can give a radis(in meters)
        # and can calculate the values of a circular region 
        
        dd_long = 83.395551
        dd_lat = 18.106658
        coordinates=ee.Geometry.Point(dd_long,dd_lat)
        circular_region = coordinates.buffer(100000)

        # Method 3 : Defining the region from the features of an existing feature collection by FAO.(Food and Agricultural Organisation)
        # We have Level 2 Administrative regions's(Districts) features from the FeatureCollection("FAO/GAUL/2015/level2")
        # Import the featurecollection
        boundarycoll = ee.FeatureCollection("FAO/GAUL/2015/level2")

        district_features = boundarycoll.filter(ee.Filter.eq('ADM2_NAME',district))
        # district_features = circular_region

        #Input year (this can be taken as an inpput from UI)
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
        
        
        #Get the Scale(Resolution) of the data
        rainfall_projection = rainfall_coll.first().projection()
        rainfall_scale = rainfall_projection.nominalScale()
        population_projection = population_coll.first().projection()
        population_scale = population_projection.nominalScale()
        climate_projection = climate_coll.first().projection()
        climate_scale = climate_projection.nominalScale()




        all_coll = [population_coll,climate_coll,rainfall_coll]

        filtered_coll = [None]*3

        # Filtering the collection for a period of one year 
        
        def year_filter(number):
                
                start_date = ee.Date.fromYMD(number, 1, 1)
                end_date = start_date.advance(1, 'year')
                
                for i in range(0,len(all_coll)):
                    filtered_coll[i] = all_coll[i].filterDate(start_date, end_date)

        year_filter(number)



        # For the time duration we can sum, take average etc of the data
        # Here we are taking sum for rainfall data and average for Poulation and climate data  
        
        rainfall_sum = filtered_coll[2].reduce(ee.Reducer.sum())
        popul_mean = filtered_coll[0].reduce(ee.Reducer.mean())
        cli_mean = filtered_coll[1].reduce(ee.Reducer.mean())



       

        rainfall_data = rainfall_sum.reduceRegion(
                                                    
                                                    reducer= ee.Reducer.mean(), #For given region we are taking the mean value of the pixels to 
                                                                                #output the data, again here also we can perform sum 
                                                                                # or take maximum/minimum values as per our requirement.
                                                    geometry=district_features,
                                                    scale= rainfall_scale
                                                    
                                                    ).getInfo()['precipitation_sum']
        
        population_density_data = popul_mean.reduceRegion(
                                                    
                                                    reducer= ee.Reducer.mean(),
                                                    geometry=district_features,
                                                    scale=population_scale
                                                    
                                                    ).getInfo()['population_density_mean']
        
        
        climate_data = cli_mean.reduceRegion(
                                                    
                                                    reducer= ee.Reducer.mean(),
                                                    geometry=district_features,
                                                    scale=climate_scale
                                                    
                                                    ).getInfo()
        soil_data = organic_carbon.reduceRegion('mean', district_features).getInfo()



        soilkey_list = ['Soil organic carbon content at 0 cm depth', 'Soil organic carbon content at 10 cm depth', 'Soil organic carbon content at 100 cm depth', 'Soil organic carbon content at 200 cm depth','Soil organic carbon content at 30 cm depth','Soil organic carbon content at 60 cm depth']
        climatekey_list =['Evapotranspiration(kg m-2 s-1)','Downward longwave radiation flux(W m-2)','Net longwave radiation flux(W m-2)','Surface pressure(Pa)','Specific humidity(1(mass fraction))','Soil heat flux(W m-2)','Sensible heat net flux(W m-2)','Latent heat net flux(W m-2)','Storm surface runoff(Kg m-2 s-1)','Baseflow-groundwater runoff(Kg m-2 s-1)','Surface radiative temperature(K)','Total precipitation rate(Kg m-2 s-1)','Snow cover fraction','Snow depth(m)','Snowfall rate(Kg m-2 s-1)','Soil moisture (0 - 10 cm underground)','Soil moisture (10 - 40 cm underground)(1(volume fraction))','Soil moisture (100 - 200 cm underground)(1(volume fraction))','Soil moisture (40 - 100 cm underground)(1(volume fraction))','Soil temperature (0 - 10 cm underground)(K)','Soil temperature (10 - 40 cm underground)(K)','Soil temperature (100 - 200 cm underground)(K)','Soil temperature (40 - 100 cm underground)(K)','Surface downward shortwave radiation(W m-2)','Snow water equivalent(Kg m-2)','Net shortwave radiation flux(W m-2)','Near surface air temperature)(K)','Near surface wind speed(m/s)']


        modified_climate_key_data = dict(zip(climatekey_list,list(climate_data.values())))
        modified_soil_key_data = dict(zip(soilkey_list, list(soil_data.values())))

        out_dict = {
             'rainfall' : rainfall_data,
             'population' : population_density_data,    
             'climate': modified_climate_key_data,
             'soil': modified_soil_key_data
             }
        print(out_dict)
        
        return (out_dict)

    except ValueError:
        return "Invalid Input"
    




if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8080, debug=True)