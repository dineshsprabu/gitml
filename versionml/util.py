from sys import exit
from os.path import dirname, abspath, exists as _path_exists
from os import makedirs
from uuid import uuid1
from terminaltables import AsciiTable, SingleTable
from datetime import datetime
from fnmatch import translate as _fn_translate
from re import compile as _re_compile


def log_message(message, tag=False):
	if tag: message = "[VersionML] %s" % message
	print("\n%s\n" % message)


def exit_with_message(message, tag=False):
	log_message(message, tag)
	exit()


def tabulate(rows, headers=None):
	if len(rows) == 0: 
		exit_with_message("No entries found.")

	if not headers:
		headers = rows[0].keys()

	table = [headers] # Headers.
	for row in rows:
		table.append([row[col] for col in headers])

	table = AsciiTable(table)
	log_message(table.table)
	return table.table


def printable_dict(_dict):
	dict_string = ""
	for k, v in _dict.items():
		dict_string = (dict_string 
			+ ("%s: %s, " % (k, v)))
	# Removing trailing space and comma.
	dict_string = dict_string.strip().strip(",")
	return dict_string


def tabulate_dict(tdict, headers=None):
	if len(tdict) == 0: return None

	if not headers:
		headers = tdict.keys()

	_table = []
	for head in headers:
		if head in tdict and tdict[head]:
			if isinstance(tdict[head], dict):
				# i.e For parameters and metrics.
				tdict[head] = printable_dict(tdict[head])
			_table.append([head, tdict[head]])

	_table = AsciiTable(_table)
	# _table.inner_heading_row_border = False
	return _table.table


def log_dict_as_table(tdict, headers=None):
	table = tabulate_dict(tdict, headers)
	if not table:
		log_message("No entries found.")
	return log_message(table)


def log_dicts_as_tables(tdicts, title, headers=None):
	log_message(title)
	for tdict in tdicts:
		log_dict_as_table(tdict, headers)
	return


def show_banner():
	print("\n")
	print("############################################")
	print("############ VersionML (v0.1) ##############")
	print("############################################")
	print("\n")
	return


def confirm(question):
	question = "%s [Y/n] : " % question.strip()
	answer = raw_input(question)
	answer = answer.strip().lower()
	return (answer == "y" or answer == "yes")


def generate_unique_id():
	return str(uuid1()).replace("-", "")


def root_dir():
	return dirname(abspath(__file__))


def create_dir_if_not_exist(dir_path, privilege=0755):
	if not _path_exists(dir_path):
		makedirs(dir_path, privilege)
	return dir_path


def timestamp():
	return datetime.now().strftime("%Y%m%d%H%M%S")


def match_path_by_pattern(pattern, path):
	# Match file path by pattern. i.e pattern : "/root/*.txt" 
	# path : "/root/model.txt"
	regex = _fn_translate(pattern)
	reobj = _re_compile(regex)
	return reobj.match(path)


def touch(path):
	if not _path_exists(path):
		open(path, "w+").close()
	return path


