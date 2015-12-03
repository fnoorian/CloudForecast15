#/gateways/<gateway_id>/sensors/data/<timestamp>
#/gateways/<gateway_id>/sensors/data_table&start=YYYYMMDDThhmmssZ&end=YYYYMMDDThhmmssZ&res=5min

#<timestamp>: 
#YYYYMMDDThhmmssZ
#YYYY-MM-DDThh:mm:ssZ
#YYYY-MM-DDThh:mm:ss+1000

import json
import datetime
import dateutil.parser

from flask import request
from flask.ext.restful import Resource

from app import api, db
from app.models import SensorySnapshot as Snapshot

# The gateway URL handlers
class GatewayData(Resource):
    def get(self, gateway_id, timestamp):

        timestamp = dateutil.parser.parse(timestamp)
        timestamp_utc = timestamp.astimezone(datetime.timezone.utc)

        # query data
        sensor_data = Snapshot.query.filter(Snapshot.device_id == gateway_id, Snapshot.utc_timestamp == timestamp_utc).first()

        if sensor_data is None:
            # No object found
            return {'error': 'snapshot not found'}, 404
        else:
            return {'gateway_id': gateway_id, 
                    'timestamp': timestamp_utc.isoformat('T'),
                    'data': sensor_data.json()}

    def put(self, gateway_id, timestamp):
        
        # Get data from HTTP session
        data = request.form['data']
        timestamp = dateutil.parser.parse(timestamp)
        timestamp_utc = timestamp.astimezone(datetime.timezone.utc)

        # check if data already exists
        sensor_data = Snapshot.query.filter(Snapshot.device_id == gateway_id, Snapshot.utc_timestamp == timestamp_utc).first()

        if sensor_data is None:
            # create new object
            print("No object found")
            sensor_data = Snapshot(gateway_id, 
                                   timestamp_utc,
                                   data)
            db.session.add(sensor_data)
        else:
            # only update data
            print("Object exists, updating")
            print(sensor_data)
            sensor_data.string_data = data

        db.session.commit()

        json_return = {'gateway_id': gateway_id, 
                       'timestamp': timestamp_utc.isoformat('T'),
                       'data': sensor_data.json()}

        return json_return, 201

class GatewayDatatable(Resource):
    def get(self, gateway_id):
        from_date = request.form['start']
        to_date = request.form['end']
        time_resolution = request.form['res']

        return {'error': 'not implemented'}, 500 

api.add_resource(GatewayData,      '/gateways/<gateway_id>/sensors/data/<timestamp>')
api.add_resource(GatewayDatatable, '/gateways/<gateway_id>/sensors/data_table')
