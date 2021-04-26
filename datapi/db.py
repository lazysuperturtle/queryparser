from flask import current_app, g
from flask.cli import with_appcontext

import sqlite3
import click
import pandas


def get_app_db():
	#add db instance to flask g (global)
	if "db" not in g:
		g.db = sqlite3.connect( current_app.config["DATABASE"],
								detect_types = sqlite3.PARSE_DECLTYPES)
		g.db.row_factory = sqlite3.Row

	return g.db

def close_db(e=None):
	db = g.pop("db", None)
	if db is not None:
		db.close()

def init_db():
	db = get_app_db()

	with current_app.open_resource("csv_schema.sql") as f:
		db.executescript(f.read().decode('utf8'))

	click.echo("Database was initialized")

def csv_to_db():

	filename = "dataset.csv"
	db = get_app_db()

	with current_app.open_resource(filename) as csv:
		csv_data = pandas.read_csv(csv)
		dt_frame = pandas.DataFrame(csv_data)
		for idx, data_elem in dt_frame.iterrows():
			print(data_elem.array)
			query = "INSERT INTO dataset VALUES ( ?, ?, ?, ?, ?, ?, ?, ?, ?);"
			db.execute(query, data_elem.array)
		db.commit()

	click.echo("File %s converted to a relational database" % filename)

@click.command("init-db")
@with_appcontext
def initialize():
	init_db()
	csv_to_db()

def init_app(app):
	app.teardown_appcontext(close_db)
	app.cli.add_command(initialize)

