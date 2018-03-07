"""Usage:

## How to record an iteration with the state on the code?

Code: model.py

from versionml import state

with state() as _state:
	_state.set(model=<MODEL-OBJECT>, params=<PARAMETERS>,
		metrics=<METRICS>, remarks="Added.")

# The below command will record an iteration with the state.

Command: `python model.py serve`

"""


from shutil import (copy2 as _file_copy, 
	copytree as _dir_copy, ignore_patterns,
	rmtree as _rmdir, move)
from tinydb import TinyDB, Query, where
from os.path import join as _path_join, exists as _path_exists
from pickle import dump as model_dump, load as model_load
from os import remove, listdir
from distutils.dir_util import copy_tree as _dir_copy_contents


from .exceptions import VersionMLException
from .project import Project
from .db import DataModel
from .scm import Git
from .util import *


class InvalidIterationException(VersionMLException):
	pass


class ProjectNotFoundException(VersionMLException):
	pass

class Iteration(object):

	DIR_NAME = ".iterations"

	COMMIT_DIR = ".commits"

	MODEL_FILE_NAME = "model.pkl"

	DISPLAY_COLS = ["id", "params", "metrics", "remarks"]

	CODE_ARCHIVE_IGNORE = [
		".git", ".versionml", 
		".gitignore", "versionml.json"
	]


	def __init__(self, project_path=None):

		# If not project path given, find the closest.
		if not project_path:
			project_path = Project.closest()

		# If no Project found on scan. 
		if not project_path: exit_with_message(
			"No versionml project found. Use 'versionml init' " + \
			"command to create one.", tag=True)

		self.project_path = project_path

		self.git = Git(self.project_path)
		self.workspace = Workspace(self.project_path, 
			self.CODE_ARCHIVE_IGNORE)

		self.db = DataModel(self.project_path, "iteration")()
		self.commit_db = DataModel(self.project_path, "commit")()
		self.query = Query()

		self.dir = _path_join(self.project_path, 
			Project.VML_DIR_NAME, self.DIR_NAME)

		self.commit_dir = _path_join(self.project_path,
			Project.VML_DIR_NAME, self.COMMIT_DIR)


	def _create_record(self, unique_id, params, metrics, remarks):

		record = {
			"id": unique_id, 
			"params": params, 
			"metrics": metrics, 
			"remarks": remarks, 
			"timestamp": timestamp() 
		}

		if not self.db.insert(record):
			return None
		return record


	def _delete_record_by_id(self, unique_id):
		return self.db.remove(where("id") == unique_id)


	def _create_commit_record(self, attributes):
		return self.commit_db.insert(attributes)


	def _unique_dir(self, unique_id):
		return _path_join(self.dir, unique_id)


	def _unique_commit_dir(self, unique_id):
		return _path_join(self.commit_dir, unique_id)


	def _find_by_id(self, unique_id, selected="iterations"):
		# Choosing db.
		if selected == "iterations": _db = self.db
		elif selected == "commits": _db = self.commit_db

		_records = _db.search(self.query.id == unique_id)
		if len(_records) > 0:
			return _records[0]
		return None


	def _model_path(self, unique_id):
		return _path_join(self.dir, unique_id, self.MODEL_FILE_NAME)		


	def _sort_by_timestamp(self, records):
		return sorted(records, 
			key=lambda record: record["timestamp"], reverse=True)


	def _code_archival_path(self, unique_id, selected="iteration"):
		# Returns code_path based on selected.
		if selected == "commit":
			return _path_join(self._unique_commit_dir(unique_id), "code")
		return _path_join(self._unique_dir(unique_id), "code")


	def _code_ignores(self):
		return set(self.git.get_ignores() + self.CODE_ARCHIVE_IGNORE)


	def _archive_code(self, code_path):
		_project_path = self.project_path
		ignores = self._code_ignores()
		try:
			_dir_copy(_project_path, code_path, 
				ignore=ignore_patterns(*ignores))
		except OSError as e:
			if e.errno == errno.ENOTDIR:
				_file_copy(_project_path, code_path)
			else:
				log_message("Code archival failed on save.")


	def _iteration_or_commit(self, unique_id):
		# Figuring out iteration or commit.
		_iteration = self._find_by_id(unique_id)
		if _iteration: return "iteration"
		_commit = self._find_by_id(unique_id, selected="commits")
		if not _commit: return None
		return "commit"


	def save(self, params={}, metrics={}, remarks="", model=None):
		unique_id = generate_unique_id()
		unique_dir = create_dir_if_not_exist(
			self._unique_dir(unique_id))

		model_path = self._model_path(unique_id)
		code_path = self._code_archival_path(unique_id)

		if not model:
			log_message("No model given for saving. Try command"+ \
				" 'versionml save -h'.")

		if not _path_exists(model_path):
			# Saving the model object as pickle file.
			model_dump(model, open(model_path, "wb"))

		if not _path_exists(code_path):
			self._archive_code(code_path)

		# Adding state to db. 
		self._create_record(unique_id=unique_id, 
			remarks=remarks, params=params, metrics=metrics)

		log_message("Iteration saved : %s" % unique_id, tag=True)


	def commit(self, unique_id):
		iteration_dir = self._unique_dir(unique_id)
		if not _path_exists(iteration_dir):
			raise InvalidIterationException(
				"No such iteration %s" % unique_id)

		_commit_dir = self._unique_commit_dir(unique_id)
		if _path_exists(_commit_dir):
			exit_with_message("Iteration is committed already.")

		# Moving iteration to commit.
		_dir_copy(iteration_dir, _commit_dir)

		# Moving iteration record to commit db.
		_iteration_record = self._find_by_id(unique_id)
		self._create_commit_record(_iteration_record)

		# Clearing iteration.
		_rmdir(iteration_dir)
		self._delete_record_by_id(unique_id)

		self.git.commit_all("Iteration %s" % unique_id)

		exit_with_message("Iteration committed : %s" % unique_id)


	def reuse(self, unique_id):

		# Code path of iteration by unique id.
		_object = self._iteration_or_commit(unique_id)

		if not _object: exit_with_message("No iterations found.")
		
		# Returns code path of object which can be an iteration
		# or a commit.
		code_path = self._code_archival_path(unique_id, _object)

		if not _path_exists(code_path):
			exit_with_message("Not able restore code for iteration.")

		if not self.workspace.is_empty():
			exit_with_message("Workspace is not empty. Please stash your " + \
				"changes using 'versionml stash'")

		# Copies code contents to workspace.
		_dir_copy_contents(code_path, self.project_path)


	def list(self, selected="iterations"):
		display_title = "--- List of %s ---" % selected

		if selected == "iterations": _records = self.db.all()
		elif selected == "commits": _records = self.commit_db.all()
		
		if len(_records) > 0:
			_records = self._sort_by_timestamp(_records)
			return log_dicts_as_tables(_records, 
				display_title, self.DISPLAY_COLS)

		exit_with_message("No %s found." % selected)	


	def show(self, uid, selected="iterations"):
		_record = self._find_by_id(uid, selected)
		if not _record:
			return exit_with_message("Invalid %s id %s." % (selected.strip("s"), uid))

		return log_dict_as_table(_record, self.DISPLAY_COLS)	


	def load_model(self, unique_id):
		unique_id = unique_id.strip()

		if not unique_id:
			raise ValueError("[VersionML] Invalid id.")

		model_path = self._model_path(unique_id)
		if not _path_exists(model_path):
			error_msg = "[VersionML] Failed loading model." + \
				" Invalid iteration id %s." % str(unique_id) 
			raise ValueError(error_msg)

		# Return model by reading the pickle.
		return model_load(open(model_path, "rb"))


class Workspace(object):

	def __init__(self, path, ignore=[]):
		self.path = path
		self.ignores = ignore
		self.stash_path = _path_join(path, Project.VML_DIR_NAME, 
			".stash")
		# Creates stash path if not available already.
		create_dir_if_not_exist(self.stash_path);


	def list(self):
		return list(set(listdir(self.path)) - set(self.ignores))


	def is_empty(self):
		return (len(self.list()) == 0)


	def stash(self):
		if self.is_empty():
			exit_with_message("Empty workspace. Nothing to stash.")

		_list = self.list()

		for l in _list:
			move(_path_join(self.path, l), 
				_path_join(self.stash_path, l))

		exit_with_message("Stashed successfully.")


	def restore(self):
		if not _path_exists(self.stash_path):
			exit_with_message("No stash found.")

		contents = listdir(self.stash_path)

		if len(contents) == 0:
			exit_with_message("Nothing to restore. Stash is empty.")

		for content in contents:
			move(_path_join(self.stash_path, content), 
				self.path)

		exit_with_message("Stash restored.")


class State(object):

	def __init__(self):
		self.model = None
		self.params = {}
		self.metrics = {}
		self.remarks = ""


	@classmethod
	def action(cls, name):
		return Action(name)


	def set(self, model=None, params={}, metrics={}, remarks=""):
		# Iteration attributes.
		self.model = model
		self.params = params
		self.metrics = metrics
		self.remarks = remarks
		return self


class Action(object):

	SUPPORT = [
		"save",
		"run"
	]

	DEFAULT = "run"

	def __init__(self, name):
		
		# Setting default action if not given.
		if not name: name = self.DEFAULT

		name = name.strip()
		if name not in self.SUPPORT:
			raise Exception("Unsupported versionml action.")
		self.name = name
		# Creates an instance of empty state.
		self.state = State()


	def __enter__(self):
		return self.state


	def run(self):
		# Run actions based on name.

		if self.name == "run":
			log_message("Building your model..", tag=True)

		elif self.name == "save":
			# Saving the state on iteration.
			Iteration().save(
				params=self.state.params,
				metrics=self.state.metrics,
				model=self.state.model,
				remarks=self.state.remarks)


	def __exit__(self, type, value, traceback):
		self.run()


def load(iteration_id):
	# Load model by iteration.
	model = Iteration().load_model(iteration_id)
	return model


