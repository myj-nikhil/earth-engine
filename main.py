import json
from flask import Flask, render_template, request, jsonify
from initalize import initialise
from give_data import given_data
from v2_parallel import v2_parallel_point
from timeit import default_timer as timer
import ee

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


# This function takes in user input(boundary coordinates) and returns a JSON object with the calculated data

# @app.route("/calculate", methods=['POST'])
# def calculate():
#     # initialise() # Initialize the Earth Engine API
#     input = request.get_json()
#     print("Request arg type: ", type(input))
#     print(input)
#     result = json.loads(input) # Load the JSON input into a Python object
#     print("\n Type of input: ", type(result))
#     print("\n Input: ", result)
#     print("\n length of input: ",len(result))
#     print(result[0])
#     inputlength = len(result)
    #Check whether the input is apoint or a polygon
    # if(inputlength > 2):
        # #region = ee.Geometry.Polygon(result)
        # print("Input region is polygon")
    # else: 
        # #region = ee.Geometry.Point(result)
        # print("Input region is a Point")
    # ans = given_data(region) # Calculate the data for the region using the Earth Engine API
    # print("In calculate method :")
    # return jsonify(ans)  # Return a JSON object instead of a JSON string


@app.route("/newcalculate", methods=['POST'])
def newcalculate():
    start =timer()
    # initialise() # Initialize the Earth Engine API
    input = request.get_json()
    print("Request arg type: ", type(input))
    print(input)
    result = json.loads(input) # Load the JSON input into a Python object
    print("\n Type of input: ", type(result))
    print("\n Input: ", result)
    print("\n length of input: ",len(result))
    print(result[0])
    inputlength = len(result)
    #Check whether the input is apoint or a polygon
    if(inputlength > 2):
        region = ee.Geometry.Polygon(result)
        print("Input region is polygon")
        # ans = v2_parallel_point(region)
    else: 
        region = ee.Geometry.Point(result)
        print("Input region is a Point")
    ans = v2_parallel_point(region)    
    print("time until main passing :",round(timer()-start,5))
     # Calculate the data for the region using the Earth Engine API
    # print("In calculate method :")
    end = timer()
    print("\n time for calculate", round(end-start,5))
    return jsonify(ans)  # Return a JSON object instead of a JSON string

if __name__ == "__main__":
    app.run(host="0.0.0.0",port=5000, debug=True)
