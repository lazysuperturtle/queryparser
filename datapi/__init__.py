from flask import Flask, request
from . import db
from . import api
import os


def create_app(test_config=None):


	app = Flask(__name__, instance_relative_config=True)
	config = {
				"SECRET_KEY":"dev", 
				"DATABASE":os.path.join(app.instance_path, "datapi.sqlite"),
			 }
	app.config.from_mapping(**config)


	try:
		os.makedirs(app.instance_path)
	except OSError:
		pass

	db.init_app(app)

	app.register_blueprint(api.bp)
	
	return app