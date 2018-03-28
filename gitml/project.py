from tinydb import TinyDB, Query, where
from os.path import (
	join as _path_join, 
	exists as _path_exists, 
	dirname as _path_dirname
)
from os import getcwd, remove as _rmfile
from shutil import rmtree as _rmdir
from codecs import open
from sys import exit
from json import dumps as _json_dump

from .db import DataModel
from .scm import Git
from .util import *


class Project(object):

	VML_FILE_NAME = "gitml.json"

	VML_DIR_NAME = ".gitml"

	CONFIRM_QUESTIONS = ["git"]

	ORDER_OF_QUESTIONS = ["name", "author"]

	INIT_QUESTIONS = {
		"name": "Name of the project : ",
		"author": "Name of the author : "
	}

	DEFAULT_ANSWERS = {
		"name": "Project X",
		"author": "Anonymous"
	}

	GIT_IGNORES = [
		".gitml/.data/*",
		"!.gitml/.data/commits.json",
		".gitml/.iterations"
	]

	def __init__(self, base_path=None):
		if not base_path:
			base_path = getcwd()
		self._file_path = _path_join(base_path,
			self.VML_FILE_NAME)
		self._dir_path = _path_join(base_path,
			self.VML_DIR_NAME)
		self._base_path = base_path


	def _ask_init_questions(self):
		answers = {}
		for key in self.ORDER_OF_QUESTIONS:
			question = self.INIT_QUESTIONS[key]
			if key in self.CONFIRM_QUESTIONS: 
				answer = confirm(question)
			else: 
				answer = raw_input(question).strip()
			if not answer and key in self.DEFAULT_ANSWERS:
				answer = self.DEFAULT_ANSWERS[key]
			answers[key] = answer
		return answers


	def _create_file_with_config(self, config):
		with open(self._file_path, "w+", "utf-8") as project_file:
			project_file.write(_json_dump(config, indent=2))
		return self._file_path


	def _create_dir(self):
		dir_path = create_dir_if_not_exist(self._dir_path, 0755)
		# .keep folder for initial commit of .gitml dir.
		# touch(_path_join(dir_path, ".keep"))
		return dir_path


	@classmethod
	def exists_file_dir(cls, path):
		file_path = _path_join(path, cls.VML_FILE_NAME)
		dir_path = _path_join(path, cls.VML_DIR_NAME)
		return (_path_exists(file_path)
			and _path_exists(dir_path))


	@classmethod
	def confirm_initialize(cls):
		question = "Do you want to create a new project?"
		if not confirm(question): 
			exit()
		else: 
			return Project().initialize()


	@classmethod
	def closest(cls, quiet=True):
		_path = getcwd()
		if cls.exists_file_dir(_path): 
			return _path
		else:
			while(True):
				parent = _path_dirname(_path)
				if parent == _path:
					if quiet: return None
					log_message("No project found.")
					return cls.confirm_initialize()
				_path = parent
				if(cls.exists_file_dir(_path)): 
					return _path


	def exists(self):
		return self.exists_file_dir(self._base_path)


	def create(self):
		show_banner() # Displays banner.
		config = self._ask_init_questions()
		# Config file, Directory, Git init if not exist.
		self._create_file_with_config(config)
		self._create_dir()
		# Creates local db files.
		DataModel.setup(self._base_path)
		# Create git repository with ignores, if not exist.
		Git.init(self._base_path, self.GIT_IGNORES)


	def remove(self):
		if _path_exists(self._file_path): 
			_rmfile(self._file_path)
		if _path_exists(self._dir_path):
			_rmdir(self._dir_path)


	def replace(self):
		question = "A project already exists. "+ \
		"Do you want to replace it?"
		if not confirm(question): exit()
		self.remove(); self.create()


	def delete(self):
		_closest = self.closest()
		question = "Deleting gitml on project:"+ \
			" %s. Are you sure?" % _closest
		if not confirm(question): exit()
		Project(_closest).remove()


	def initialize(self):
		if self.exists(): self.replace()
		else: self.create()
		exit_with_message("Project initiated with GitML. Visit "+ \
			"http://gitml.com for more info.")
		return self._base_path

