from flask import Flask, render_template,request,redirect,url_for
from initalize import initialise
from give_data import given_data
import ee

app = Flask(__name__)

#Home page of the App
@app.route("/")
def index():
      return render_template('index.html')
     

      
@app.route("/result",methods=['GET','POST'])
def ans():
      print('submit button clicked')
      initialise()
      if request.method == 'POST':
            print("post inititated")
            dd_long = float(request.form['longitude'])
            dd_lat = float(request.form['latitude'])   
            print(dd_lat,dd_long)
            coordinates=ee.Geometry.Point([float(dd_long),float(dd_lat)])
            print(coordinates.getInfo())
            output = given_data(coordinates)
            print(output)
      return render_template('result.html',output=output,dd_long=dd_long,dd_lat = dd_lat,population = output.get('population'),rainfall=output.get('rainfall'))

# if __name__ == "__main__":
#     app.run(host="127.0.0.1", port=8080, debug=True)  


