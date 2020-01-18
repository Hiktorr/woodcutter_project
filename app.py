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
	first_solution_strategies = ['AUTOMATIC', 'PATH_CHEAPEST_ARC', 'PATH_MOST_CONSTRAINED_ARC', 'SAVINGS', 'CHRISTOFIDES', 'PARALLEL_CHEAPEST_INSERTION', 'LOCAL_CHEAPEST_INSERTION', 'GLOBAL_CHEAPEST_ARC', 'LOCAL_CHEAPEST_ARC', 'FIRST_UNBOUND_MIN_VALUE']
	times = [{'name':'10s', 'value':'10'}, {'name':'30s', 'value':'30'}, {'name':'5m', 'value':'300'}, {'name':'10m', 'value':'600'}]
	local_search_options = ['AUTOMATIC', 'GREEDY_DESCENT', 'GUIDED_LOCAL_SEARCH', 'SIMULATED_ANNEALING', 'TABU_SEARCH']
	if request.method=='POST' and 'sendFile' in request.files:
		ffs = request.form['first_solution_strategies']
		time = request.form['times']
		lso = request.form['local_search_options']
		dataSend=True
		file_string = request.files['sendFile'].read()
		file_string = file_string.decode('utf-8')
		vehicle_distance, vehicle_load, text, filename = cvrp.cvrp_fun(file_string, ffs, time, lso)
		name, capacity, dimension, point_int, demand_int, trucks, optimal_value = cvrp.parse_file(file_string)
		percentage = 100 * (optimal_value - sum(vehicle_distance)) / optimal_value
		return render_template('index.html', dataSend=dataSend, file_string=text, filename=filename,
							   customers=dimension, vehicles=trucks, capacity=capacity[0],
							   first_solution_strategies=first_solution_strategies, times=times,
							   local_search_options=local_search_options,
							   ffs=ffs, time=time, lso=lso, opt_distance=sum(vehicle_distance),
							   optimal_value=optimal_value, change_percent=percentage)
	if request.method == 'POST':
		ffs = request.form['first_solution_strategies']
		time = request.form['times']
		lso = request.form['local_search_options']
		dataSend=True
		url=request.form['url']
		output = urlopen(url).read()
		file_string = (output.decode('utf-8'))
		vehicle_distance, vehicle_load, text, filename = cvrp.cvrp_fun(file_string, ffs, time, lso)
		name, capacity, dimension, point_int, demand_int, trucks, optimal_value = cvrp.parse_file(file_string)
		percentage = 100 * (optimal_value - sum(vehicle_distance))/optimal_value
		return render_template('index.html', dataSend=dataSend, file_string=text, filename=filename,
							   customers=dimension, vehicles=trucks, capacity=capacity[0],
							   first_solution_strategies=first_solution_strategies, times=times,
							   local_search_options=local_search_options,
							   ffs=ffs, time=time, lso=lso, opt_distance=sum(vehicle_distance), optimal_value=optimal_value, change_percent = percentage)
	return render_template('index.html', first_solution_strategies=first_solution_strategies, times=times, local_search_options=local_search_options)

if __name__ == "__main__":
	app.run(debug=True)