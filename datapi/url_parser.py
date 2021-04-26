from collections import defaultdict
from dateutil.parser import parse

import re

def is_date(string):
	try:
		parse(string, fuzzy=True)
		return True
	except:
		return False

def is_int(string):
	int_string = re.findall(r"(\d+)", string)
	if int_string: return True


def sql_function(sql_function):

	def parse_wrapper(parser_function):

		def wrapper(*url_data):
			parsed_data = parser_function(*url_data)
			return "%s %s" % (sql_function, parsed_data) 

		return wrapper

	return parse_wrapper


@sql_function("order by")
def parse_sort(*url_data):
	val_data, grouped = url_data
	val, data = list(val_data.items())[0]
	args = list(data.keys())
	arg = args[0]
	direction = "desc" if '-' in arg else "asc"
	arg = ''.join(x for x in filter(lambda x: x!="-", arg)) #only one possible value
	return f"{arg} {direction}" # hope you use python >= 3.6

@sql_function("where")
def parse_filter(*url_data):
	val_data, grouped = url_data
	val, data = list(val_data.items())[0]
	arg = list(data.keys())[0]
	get_sql_operator = lambda data : list(filter(lambda x: x!='', re.findall(r"[<=>]*", data)))
	sql_operator = None
	sql_value = None

	if is_date(arg):
		dates = list(filter(lambda x: x!='', re.split(r"\_", arg)))
		datetime_dates = [parse(date, fuzzy=True) for date in dates]
		datetime_dates.sort()
		datetime_dates_sql_format = [date.strftime("%Y-%m-%d") for date in datetime_dates]
		if len(datetime_dates_sql_format) > 1: #have a range here
			return f"{val} >= '%s' and {val} <= '%s'" % (datetime_dates_sql_format[0], datetime_dates_sql_format[1],)
		sql_value = "'%s'" % datetime_dates_sql_format[0]
	
	elif is_int(arg):
		sql_value = re.findall(r"(\d+)", arg)


	else: #string data, only = operator
		sql_value = "'%s'" % arg

	operator_symbol = get_sql_operator(arg)
	sql_operator = operator_symbol[0] if len(operator_symbol) > 0 else "="		
	return f"{val} {sql_operator} %s" % sql_value


@sql_function("group by")
def parse_groups(*url_data):
	val_data, grouped = url_data
	val, data = list(val_data.items())[0]
	args = data.keys()
	return ", ".join(group for group in args) 


@sql_function("select")
def parse_show(*url_data):
	sum_func_pattern = "sum({col_name}) as {col_name}"
	val_data, grouped = url_data
	val, data = list(val_data.items())[0]
	args = data.keys()
	if grouped: args = list(map(lambda arg: sum_func_pattern.format(col_name=arg) if data[arg] == int or data[arg] == float else arg, args))
	return ", ".join(col for col in args)

def parse_cpi(*url_data):
	sum_func_pattern = "sum({})"
	val_data, grouped = url_data
	val, data = list(val_data.items())[0]
	arg = list(data.keys())[0]
	print(arg)
	if arg.lower() in ("true", "1"):
		cols = ['spend', 'installs']
		if grouped: cols = [sum_func_pattern.format(col_name) for col_name in cols]
		cpi_query_func = " ,{spend}/{installs} as cpi".format(spend=cols[0], installs=cols[1])
		return cpi_query_func
	return ""

functions = {
			 "show": parse_show, 
			 "group": parse_groups,
			 "sort": parse_sort,
			 "filter": parse_filter,
			 "cpi": parse_cpi,
			 }



def url_to_query(request_data, db_data):
	db_name, db_colmns = db_data
	query="{show}{cpi} from %s {filter} {group} {sort}" % db_name
	

	url_dict = {val:{arg:db_colmns.get(arg, "undefined") for arg in args.split()} for val, args in request_data}
	grouped = True if "group" in url_dict.keys() else False 
	
	url_data = defaultdict(str)
	url_data["show"] = "select *" # select all clmns by default, if url didn't contains query
	for val, args in url_dict.items():
		if val in functions.keys():
			fnc = val
		elif val in db_colmns.keys():
			fnc = "filter"
		else: continue
		parser = functions[fnc]
		parse_data = {val:url_dict[val]}
		url_data[fnc] = parser(parse_data, grouped)
	return query.format_map(url_data)
