from app import application

if __name__ == '__main__':
    application.run(debug=True)

 #curl http://localhost:5000/gateways/001/sensors/data/2015-12-20T13:40:15+1000 -d "data={\"voltage\":12}" -X PUT
