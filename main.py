import json
from flask import Flask, render_template, request, jsonify
from initalize import initialise
from give_data import given_data
from v2_parallel import v2_parallel_point
from timeit import default_timer as timer
import ee
import logging

app_logger = logging.getLogger('main.py')
app_logger.setLevel(logging.DEBUG)

file_handler = logging.FileHandler('app.log', mode='a')
file_handler.setLevel(logging.DEBUG)

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
file_handler.setFormatter(formatter)

app_logger.addHandler(file_handler)

initialise()

app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False # This usage is warned in flask documentation

# Home page of the App

# This is the home page of the app where the user can choose their input method
@app.route("/")
def index():
    return render_template('index.html')

# This is the page of the app where the user can get data of an area by selecting the area on the map
@app.route("/map")
def map():
    return render_template('new-google-map.html')

# This is the page of the app where the user can input coordinates and get data at that coordinates
@app.route("/coordinates")
def coordinates():
    return render_template('coordinates.html')

# This is the page of the app where the user can input diagonal coordinates and get data at that coordinates
@app.route("/diagonal-coordinates")
def diagonalcoordinates():
    return render_template('diagonal-coordinates.html')

@app.route("/oldmap")
def aa():
    return render_template('old-map.html')

@app.route("/oldway")
def neway():
    return render_template('old-coordinates.html')

@app.route("/form")
def enterdata():
    return render_template('form.html')

# This function takes in user input(boundary coordinates) and returns a JSON object with the calculated data

# @app.route("/calculate", methods=['POST'])
# def calculate():
#     # initialise() # Initialize the Earth Engine API
#     input = request.get_json()
#     app_logger.info("Request arg type: ", type(input))
#     app_logger.info(input)
#     result = json.loads(input) # Load the JSON input into a Python object
#     app_logger.info("\n Type of input: ", type(result))
#     app_logger.info("\n Input: ", result)
#     app_logger.info("\n length of input: ",len(result))
#     app_logger.info(result[0])
#     inputlength = len(result)
    #Check whether the input is apoint or a polygon
    # if(inputlength > 2):
        # #region = ee.Geometry.Polygon(result)
        # app_logger.info("Input region is polygon")
    # else: 
        # #region = ee.Geometry.Point(result)
        # app_logger.info("Input region is a Point")
    # ans = given_data(region) # Calculate the data for the region using the Earth Engine API
    # app_logger.info("In calculate method :")
    # return jsonify(ans)  # Return a JSON object instead of a JSON string


@app.route("/newcalculate", methods=['POST'])
def newcalculate():
    start =timer()
    # initialise() # Initialize the Earth Engine API
    input = request.get_json()
    # app_logger.info("Request arg type: ", type(input))
    # app_logger.info(input)
    result = json.loads(input) # Load the JSON input into a Python object
    app_logger.info("Input is : %s",result)
    app_logger.info("Type of input: %s ", type(result))
    app_logger.info("Input: %s ", result)
    app_logger.info("Length of input: %s ",str(len(result)))
    app_logger.info("First element in input is: %s",result[0])
    inputlength = len(result)
    #Check whether the input is apoint or a polygon
    if(inputlength > 2):
        region = ee.Geometry.Polygon(result)
        app_logger.info("Input region is polygon")
        # ans = v2_parallel_point(region)
    else: 
        region = ee.Geometry.Point(result)
        app_logger.info("Input region is a Point")
    ans = v2_parallel_point(region)    
    app_logger.info("time until main passing : %s ",round(timer()-start,5))
     # Calculate the data for the region using the Earth Engine API
    # app_logger.info("In calculate method :")
    end = timer()
    app_logger.info("Time for calculate %s", round(end-start,5))
    return jsonify(ans)  # Return a JSON object instead of a JSON string

if __name__ == "__main__":
    app.run(host="0.0.0.0",port=5000, debug=True)
