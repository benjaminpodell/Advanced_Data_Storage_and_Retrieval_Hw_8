# Importing dependencies 
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify
import numpy as np
import pandas as pd
import datetime as dt

# Variable that stores created engine referencing the `hawaii.sqlite` database file from the resources folder
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# Variable reflecting an existing database into a new model
Base = automap_base()

# Reflects the tables
Base.prepare(engine, reflect=True)

# Variables storing the Reflect Database into object relational mapping classes
Measurement = Base.classes.measurement
Station = Base.classes.station

# Creates session link from Python to the database
session = Session(engine)

# Setting up flask
app = Flask(__name__)

# Building First Homepage flask route that lists all other available routes
@app.route("/")
def homepage():
    return (
        f"Here is a list of all available api routes!<br/>"
        f"------------------------------------------------"
        f"<br/>"
        
        f"Previous year rain totals from every station<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"<br/>"

        f"Station numbers along with their respective names<br/>"
        f"/api/v1.0/stations<br/>"
        f"<br/>"
        
        f"Previous year temperatures across all stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"<br/>"
        
        f"From a start date this calculates the min, avg, and max temperature of all dates >= to the start date<br/>"
        f"/api/v1.0/start<br/>"
        f"<br/>"
        
        f"From a start and an end date this calculates min, avg, and max temperature of all dates between the start and end date<br/>"
        f"/api/v1.0/start/end<br/>"   
    )

# Builds the second flask route that opens the precipitation information    
@app.route("/api/v1.0/precipitation")
def precipitation():
    
    # Variables that build a query for the dates and precipitation observations from the last year
    lowest_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    previous_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    rain_measurement = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date > previous_year).order_by(Measurement.date).all()

    # For loop that creates a list of dictionarys with `date` and `prcp` as the keys and values
    rain_holder = []
    for x in rain_measurement:
        capture = {}
        capture["date"] = rain_measurement[0]
        capture["prcp"] = rain_measurement[1]
        rain_holder.append(capture)
    
    # Returns the json representation of the dictionary
    return jsonify(rain_holder)

# Builds the third flask route that opens all of the station information specifically the name and station id
@app.route("/api/v1.0/stations")
def stations():
    active_station = session.query(Station.name, Station.station)
    station_reader = pd.read_sql(active_station.statement, active_station.session.bind)
    return jsonify(station_reader.to_dict())

# Builds the fourth flask route that opens all of the 'tobs' information
@app.route("/api/v1.0/tobs")
def tobs():

    # Variables that build a query for the dates and temperature observations from the last year
    lowest_date1 = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    previous_year1 = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    temp_measurement = session.query(Measurement.date, Measurement.tobs).filter(Measurement.date > previous_year1).order_by(Measurement.date).all()

    # For loop that creates a list of dictionarys with `date` and `tobs` as the keys and values
    temperature_list = []
    for x in temp_measurement:
        capture = {}
        capture["date"] = temp_measurement[0]
        capture["tobs"] = temp_measurement[1]
        temperature_list.append(capture)
    
    # Returns the json representation of the dictionary    
    return jsonify(temperature_list)

# Builds the fifth flask route that opens all of the 'start' information 
@app.route("/api/v1.0/<start>")
def Start(start):

    # Using datetime function .strptime to pull the very first starting time to subtract from the previous year which then querys the min, avg, and max tobs data by filtering based on when the data began and finished
    # The 'begin_date' variable is not parsing through the '%Y-%m-%d' and I'm not sure why...?
    begin_date = dt.datetime.strptime(start, '%Y-%m-%d')
    previous_year = dt.timedelta(days=365)
    
    start = begin_date - previous_year
    finish =  dt.date(2017, 8, 23)
    
    start_data = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).filter(Measurement.date >= start).filter(Measurement.date <= finish).all()
    list_start_data = list(np.ravel(start_data))
    
    return jsonify(list_start_data)

# Builds the sixth flask route that opens all of the 'start' to 'end' information
@app.route("/api/v1.0/<start>/<end>")
def Start_End(start_2,end):
    

    # Using datetime function .strptime to pull the very first starting time to subtract from the previous year and ending time to subtract from the previous year which then querys the min, avg, and max tobs data by filtering based on when the data began and finished
    # The 'begin_date' and 'finish_date_2 variables are not parsing through the '%Y-%m-%d' and I'm not sure why...?
    begin_date_2 = dt.datetime.strptime(start_2, '%Y%m-%d')
    finish_date_2 = dt.datetime.strptime(end,'%Y-%m-%d')
    previous_year_2 = dt.timedelta(days=365)
    
    start_2 = begin_date_2 - previous_year_2
    end = finish_date_2 - previous_year_2
    
    start_end_data = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).filter(Measurement.date >= start_2).filter(Measurement.date <= end).all()
    list_start_end_data = list(np.ravel(start_end_data))
    
    return jsonify(list_start_end_data)

if __name__ == "__main__":
    app.run(debug=True)