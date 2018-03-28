from os.path import join as _path_join, exists as _path_exists
from codecs import open
from tinydb import TinyDB

from .util import *

class DataModel(object):

	MODELS = [
		"iteration",
		"commit"
	]

	DATA_DIR = _path_join(".gitml", ".data")

	@classmethod
	def setup(cls, project_path):
		"""Setup task for creating db files for all model.
		"""
		# Create data directory if not exist.
		data_dir = _path_join(project_path, cls.DATA_DIR)
		create_dir_if_not_exist(data_dir)
		# Create db file if not exist.
		for model_name in cls.MODELS:
			db_path = _path_join(data_dir, "%s.json" % model_name)
			if not _path_exists(db_path):
				open(db_path, "a", "utf-8").close()
		return data_dir		


	def db_path(self, project_path, model_name):
		model_name = model_name.strip().lower()
		return _path_join(project_path, 
			self.DATA_DIR, "%s.json" % model_name)


	def __init__(self, project_path, model_name):
		self.model = model_name.strip().lower()
		self.project = project_path
		# TinyDB instance using db file.
		self.path = self.db_path(self.project, self.model)
		self.db = TinyDB(self.path)


	def __call__(self):
		return self.db

