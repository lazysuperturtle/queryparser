from flask import Blueprint, flash, g, \
				  redirect, render_template, request,\
				  session, url_for, jsonify
from datapi.db import get_app_db
from datapi.url_parser import url_to_query

bp = Blueprint("api", __name__, url_prefix="/api")


def get_db_data(db):

	db_name = "dataset"
	db_cols_types = {"TEXT": str, "INTEGER": int, "REAL": float}
	db_sample = db.execute(f"PRAGMA TABLE_INFO({db_name})")
	db_cols_info = [list(data) for data in db_sample.fetchall()]
	db_data = {col[1]:db_cols_types[col[2]] for col in db_cols_info} # col[1] = colmn name, col[2] = colmn_type 

	return db_name, db_data

#/api/getdata?show=channel+country+impressions+clicks&group=channel+country&sort=clicks-&tdate=<=2017-06-01
@bp.route("/getdata", methods=("GET", "POST"))
def get_data():

	json_dict = {}

	if request.method == "GET" or request.method == "POST":
		request_data = request.args.items() if request.method == "GET" \
											else request.form.items() 
		db = get_app_db()
		db_data = get_db_data(db)
		# try:
		new_query = url_to_query(request_data, db_data)
		print(new_query)
		cursor = db.execute(new_query)
		result = cursor.fetchall()
		clmn_names = [description[0] for description in cursor.description]
		query_list = [list(x) for x in result]
		dict_res = [{clmn_names[n]:list_res[n] for n in range(len(clmn_names))} \
											   for list_res in query_list]
		
		json_dict["result"] = dict_res
		# except Exception as exc:
			# json_dict["result"] = str(exc)

		return jsonify(json_dict)





