import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, inspect
import datetime as dt
from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite", connect_args={'check_same_thread': False})
inspector = inspect(engine)
print(f" tables are: {inspector.get_table_names()}")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################

@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end><br/>"
    )


@app.route("/api/v1.0/precipitation")
def Precipitation():
    """Return a list of all Precipitation values"""
    # Determine latest date in data set
    last_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    last_date_str = ''.join(last_date)
    print(last_date_str)
   
    #Determine date 1 year ago from today
    year_ago_date = dt.datetime.strptime(last_date_str,"%Y-%m-%d") - dt.timedelta(days=365)
    year_ago_date = year_ago_date.strftime('%Y-%m-%d')
    print(year_ago_date)
    #Determine the precipitation data for the last 1 year
    prcp_results = session.query(Measurement.date, Measurement.prcp).\
    filter(Measurement.date >= year_ago_date).all()
    #Unpacking the tuples and storing date and precipitation data in separate lists
    prcp_date = [result[0] for result in prcp_results[:]]
    prcp = [result[1] for result in prcp_results[:]]

    
    prcp_list = []

    #Iterating through the tuples and unpacking them 
    #for result in prcp_results:
    prcp_dict = {}
    prcp_dict["date"] = prcp_date
    prcp_dict["prcp"] = prcp
    #prcp_list.append(prcp_dict)
    #print(prcp_list)
    return jsonify(prcp_dict)


@app.route("/api/v1.0/stations")
def stations():
    """Return a list of stations"""
    # Query all stations
    stations_result = session.query(Station.station, Station.name).all()

    # Create a dictionary from the row data and append to a list of all_stations
    all_stations = []
    for result in stations_result:
        station_dict = {}
        station_dict["ID"] = result.station
        station_dict["Name"] = result.name
        
        all_stations.append(station_dict)

    return jsonify(all_stations)


@app.route("/api/v1.0/tobs")
def tobs():
    """query for the dates and temperature observations from a year from the last data point"""

    # Determine latest date in data set
    last_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    last_date_str = ''.join(last_date)
    print(last_date_str)
   
    #Determine date 1 year ago from today
    year_ago_date = dt.datetime.strptime(last_date_str,"%Y-%m-%d") - dt.timedelta(days=365)
    year_ago_date = year_ago_date.strftime('%Y-%m-%d')
    print(year_ago_date)
    # Query all stations
    tobs_result = session.query(Measurement.date, Measurement.tobs).\
        filter(Measurement.date >= year_ago_date).all()

    # Create a dictionary from the row data and append to a list of all_stations
    all_tobs = []
    for result in tobs_result:
        tob_dict = {}
        tob_dict["Date"] = result.date
        tob_dict["Tobs"] = result.tobs
        
        all_tobs.append(tob_dict)

    return jsonify(all_tobs)

@app.route("/api/v1.0/<start>")
def start_func(start):
        startDate = dt.datetime.strptime(start,"%Y-%m-%d")
        start_tobs_result = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs),\
        func.max(Measurement.tobs)).\
        filter(Measurement.date >= startDate).all()
        print (startDate)
        print(start_tobs_result)
        
        t_min = [result[0] for result in start_tobs_result[:]]
        t_avg = [result[1] for result in start_tobs_result[:]]
        t_max = [result[2] for result in start_tobs_result[:]]
        
        start_tobs_list = []
        
        
        start_tobs_dict = {}
        start_tobs_dict["Min Temp"] = t_min
        start_tobs_dict["Avg Temp"] = t_avg
        start_tobs_dict["Max Temp"] = t_max
        start_tobs_list.append(start_tobs_dict)
        return jsonify(start_tobs_list) 
    

@app.route("/api/v1.0/<start>/<end>")
def startend(start,end):
    startDate = dt.datetime.strptime(start,"%Y-%m-%d")
    endDate = dt.datetime.strptime(end,"%Y-%m-%d")
    startend_tobs_result = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= startDate).filter(Measurement.date <= endDate).all()
    print(startend_tobs_result)
    t_min = [result[0] for result in startend_tobs_result[:]]
    t_avg = [result[1] for result in startend_tobs_result[:]]
    t_max = [result[2] for result in startend_tobs_result[:]]
    startend_tobs_list = []
   
    startend_tobs_dict = {}
    startend_tobs_dict["Min Temp"] = t_min
    startend_tobs_dict["Avg Temp"] = t_avg
    startend_tobs_dict["Max Temp"] = t_max
    startend_tobs_list.append(startend_tobs_dict)
    return jsonify(startend_tobs_list) 
    
if __name__ == '__main__':
    app.run(debug=True)
