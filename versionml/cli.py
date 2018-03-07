"""VersionML (v0.1) - Git for Data Scientists.\n
  Usage:
	versionml
	versionml -h | --help
	versionml -v | --version
	versionml init
	versionml ls | list
	versionml show <ITERATION-ID>
	versionml commit <ITERATION-ID>
	versionml commit ls | commit list
	versionml commit show <ITERATION-ID>
	versionml delete
	versionml stash
	versionml restore
	versionml reuse <ITERATION-ID>


  Options:
	-h | --help		Shows the usage details.
	-v | --version		Shows the version of your versionml installation.
	init			Initializes a versionml project on your current directory.
	ls | list		Lists all iterations.
	show			Shows the details of the iteration for the ITERATION_ID passed.
	commit			Commits the iteration available by ITERATION_ID
	commit ls | list	Lists all commited iterations.
	commit show 	Shows the selected commit by ITERATION_ID.
	delete			Deletes the versionml project.
"""


from docopt import docopt
from . import __version__ as VERSION

from .project import Project
from .iteration import Iteration
from .util import exit_with_message, show_banner
from os.path import exists as _path_exists
from json import loads as _json_loads


PRIMARY_COMMANDS = [
	"save",
	"commit",
	"reuse",
	"show",
	"ls",
	"stash",
	"list",
	"-h",
	"--help",
	"-v",
	"--version"
]

def help():
	exit_with_message(__doc__)

def _validate(req):
	_primary_commands = set(PRIMARY_COMMANDS).intersection(
		req.keys())

	if len(_primary_commands) != 1:
		exit_with_message("Unknown command. %s" % __doc__)

	return True


def _get_user_selected(req):
	_commands = []
	for k, v in req.items(): 
		if str(v) == "True": 
			_commands.append(k)
	return _commands


def _check_mandatory_opt(req, opt):
	if opt not in req or not req[opt]:
		exit_with_message("Option %s is missing. Try" % opt + \
			" versionml -h for help.")


def _opt_to_arg(opt):
	"""
	i.e opt : --model-file -> arg : model_file
	"""
	return opt.replace("--","").replace("-","_")


def _print_version():
	exit_with_message("VersionML %s" % VERSION)


def _parse_if_json(jstring):
	if isinstance(jstring, dict):
		return jstring
	try: return _json_loads(jstring)
	except ValueError: return jstring


def dispatch(req):
	user_selected = _get_user_selected(req)

	if not len(user_selected): help()

	if user_selected[0] == "init": Project().initialize()

	# Scanning for a project.
	project_path = Project.closest(quiet=True)
	
	# if not found ask for an init.
	if not project_path: Project.confirm_initialize()
	_iteration = Iteration(project_path=project_path)

	# Actions on existing project.
	if user_selected[0] == "delete": Project(project_path).delete()

	elif "commit" in user_selected:
		if "show" in user_selected and "<ITERATION-ID>" in req:
			_iteration.show(req["<ITERATION-ID>"], selected="commits")
		elif "<ITERATION-ID>" in req:
			# Fix for ls or list as iteration is.
			if req["<ITERATION-ID>"] == "ls" or  req["<ITERATION-ID>"] == "list":
				_iteration.list(selected="commits")
			else:
				_iteration.commit(req["<ITERATION-ID>"])

	elif user_selected[0] == "show":
		if "<ITERATION-ID>" in req and req["<ITERATION-ID>"]:
			_iteration.show(req["<ITERATION-ID>"])

	elif user_selected[0] == "ls" or user_selected[0] == "list":
		_iteration.list()

	elif user_selected[0] == "stash":
		_iteration.workspace.stash()

	elif user_selected[0] == "restore":
		_iteration.workspace.restore()

	elif user_selected[0] == "reuse":
		if not req["<ITERATION-ID>"]:
			exit_with_message("Please provide an iteration id. For help 'versionml -h'. ")
		_iteration.reuse(req["<ITERATION-ID>"])

	elif (user_selected[0] == "-v" 
		or user_selected[0] == "--version"): 
		_print_version()

	elif (user_selected[0] == "-h" 
		or user_selected[0] == "--help"):
		help()

	else: help()


def main(): dispatch(docopt(__doc__, version=VERSION))

