A simple data warehouse
=======================

## To run
- Install dependencies:
```bash
pip install flask flask_restful flask_sqlalchemy
```

- Create database
```bash
python create_db.py
```

- Run server:
```bash
python run.py
```

## API

`/gateways/<gateway_id>/sensors/data/<timestamp>`
- gateway_id = A string
- timestamp = A timestamp in ISO 8601 format. Supports timezones
- data = any json string.

`/gateways/<gateway_id>/sensors/data_table`
- gateway_id = A string
- timestamp = A timestamp in ISO 8601 format. Supports timezones
- start = start of query timestamp
- end = end of query timestamp
- res = aggregation resolution

### Using curl

To store data for gateway 001, measured at 2015-12-20 13:40:20 AEST:

```bash
curl http://localhost:5000/gateways/001/sensors/data/20151220T134020+1000 -d "data={\"voltage\":14}" -X PUT
```
or
```bash
curl http://localhost:5000/gateways/001/sensors/data/2015-12-20T13:40:20+1000 -d "data={\"voltage\":14}" -X PUT
```



To retrieve data:

```bash
curl http://localhost:5000/gateways/001/sensors/data/20151220T134020+1000
```

it returns:
```json
{
    "data": {
        "voltage": 14
    },
    "gateway_id": "001",
    "timestamp": "2015-12-20T03:40:20+00:00"
}
```
