import json
from flask import Flask, render_template, request, jsonify
from initalize import initialise
from give_data import given_data
import ee

app = Flask(__name__)

# Home page of the App

# This is the home page of the app where the user can choose their input method
@app.route("/")
def index():
    return render_template('index.html')


# This is the page of the app where the user can get data of an area by selecting the area on the map
@app.route("/map")
def map():
    return render_template('map.html')

# This is the page of the app where the user can input coordinates and get data at that coordinates
@app.route("/coordinates")
def coordinates():
    return render_template('coordinates.html')

# This is the page of the app where the user can input diagonal coordinates and get data at that coordinates
@app.route("/diagonal-coordinates")
def diagonalcoordinates():
    return render_template('diagonal-coordinates.html')


# This function takes in user input(boundary coordinates) and returns a JSON object with the calculated data

@app.route("/calculate", methods=['POST'])
def calculate():
    initialise() # Initialize the Earth Engine API
    output = request.get_json()
    print("Request arg type: ", type(output))
    print(output)
    result = json.loads(output) # Load the JSON input into a Python object
    print("JSON loaded input: ", type(result))
    print("After JSON loads: ", result)
    print(result[0])
    region = ee.Geometry.Polygon(result) # Create a region object from the input coordinates
    ans = given_data(region) # Calculate the data for the region using the Earth Engine API
    # print("In calculate method :")
    return jsonify(ans)  # Return a JSON object instead of a JSON string


# This route takes the latitude and longitude values from the form and outputs the values at that location
@app.route("/result", methods=['POST'])
def ans():
    print('submit button clicked')
    initialise()
    if request.method == 'POST':
        print("post inititated")
        dd_long = float(request.form['longitude'])
        dd_lat = float(request.form['latitude'])
        print(dd_lat, dd_long)
        coordinates = ee.Geometry.Point([float(dd_long), float(dd_lat)])
        print(coordinates.getInfo())
        output = given_data(coordinates)
        print(output)
    return render_template('result.html', output=output, dd_long=dd_long, dd_lat=dd_lat, population=output.get('population'), rainfall=output.get('rainfall'))


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8080, debug=True)
