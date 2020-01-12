from flask import Flask, render_template, flash, request, url_for
from flask_uploads import UploadSet, configure_uploads, IMAGES
from wtforms import Form, TextField, TextAreaField, validators, StringField, SubmitField
from urllib.request import urlopen
import requests
import os
import cvrp
import urllib.request
from werkzeug import secure_filename
# App config.
app = Flask(__name__)
if not os.path.isdir('./static/img') :
	os.makedirs('./static/img')

@app.route("/", methods=['GET', 'POST'])
def upload():
	dataSend=False
	if request.method=='POST' and 'sendFile' in request.files:
		dataSend=True
		file_string = request.files['sendFile'].read()
		file_string = file_string.decode('utf-8')
		vehicle_distance, vehicle_load, text, filename = cvrp.cvrp_fun(file_string)
		name, capacity, dimension, point_int, demand_int, trucks = cvrp.parse_file(file_string)
		return render_template('index.html', dataSend=dataSend, file_string=text, filename=filename, customers=dimension, vehicles=trucks, capacity=capacity[0], opt_distance=sum(vehicle_distance))
	if request.method=='POST':
		dataSend=True
		url=request.form['url']
		output = urlopen(url).read()
		file_string = (output.decode('utf-8'))
		vehicle_distance, vehicle_load, text, filename = cvrp.cvrp_fun(file_string)
		name, capacity, dimension, point_int, demand_int, trucks = cvrp.parse_file(file_string)
		return render_template('index.html', dataSend=dataSend, file_string=text, filename=filename, customers=dimension, vehicles=trucks, capacity=capacity[0], opt_distance=sum(vehicle_distance))
	return render_template('index.html')

if __name__ == "__main__":
	app.run(debug=True)