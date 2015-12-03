from flask import Flask
from flask.ext.restful import Api
from flask.ext.sqlalchemy import SQLAlchemy

application = Flask(__name__)
application.config.from_object('config')

# Restful api
api = Api(application)

# Database
db = SQLAlchemy(application)

# import controllers
import app.controllers
