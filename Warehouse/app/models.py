import json
from app import db

class SensorySnapshot(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    device_id = db.Column(db.String(16), unique=False)
    utc_timestamp = db.Column(db.DateTime, unique=False)
    string_data = db.Column(db.String, unique=False) # TODO: see if LargeBinary is better than string

    def __init__(self, device_id, utc_timestamp, string_data):
        self.device_id = device_id
        self.utc_timestamp = utc_timestamp
        self.string_data = string_data

    def __repr__(self):
        return  '<Gateway {0} data snapshot - {1}>'.format(self.device_id, self.utc_timestamp)

    def json(self):
    	return json.loads(self.string_data)
