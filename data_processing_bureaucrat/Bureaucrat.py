from pathlib import Path
import datetime
import __main__
from shutil import copyfile
import warnings

class Bureaucrat:
	"""
	Naming convention:
	- Stuff that ends in "path" is supposed to be/return an instance of Path.
	- Stuff that ends in "name" are strings.
	"""
	PROCESSED_DATA_DIRECTORY_PREFIX = 'processed_by_script_'
	def __init__(self, measurement_base_path: str):
		if ' ' in measurement_base_path:
			warnings.warn(f'The <measurement_base_path> = "{measurement_base_path}" contains blank spaces. I can handle this, but it is better to aviod them.')
		self._timestamp = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
		self._measurement_base_path =  Path(measurement_base_path)
		self._processing_script_absolute_path = Path.cwd()/Path( __main__.__file__)
		self._processed_data_subdir_name = f'{self.PROCESSED_DATA_DIRECTORY_PREFIX}{self._processing_script_absolute_path.parts[-1].replace(".py","")}'
		
		if not self._measurement_base_path.is_dir():
			raise ValueError(f'Directory "{self._measurement_base_path}" does not exist.')
		
	@property
	def measurement_base_path(self):
		return self._measurement_base_path
	
	@property
	def measurement_name(self):
		return self.measurement_base_path.parts[-1]
	
	@property
	def this_run_timestamp(self):
		return self._timestamp
	
	@property
	def raw_data_dir_path(self):
		raw_path = self._measurement_base_path/Path('raw')
		if not raw_path.is_dir():
			warnings.warn(f'Directory with raw data "{raw_path}" does not exist.')
		return raw_path
	
	@property
	def processed_data_dir_path(self):
		_ = self._measurement_base_path/Path(self._processed_data_subdir_name)
		_.mkdir(exist_ok=True)
		return _
	
	def processed_by_script_dir_path(self, script_name: str):
		_ = self._measurement_base_path/Path(f'{self.PROCESSED_DATA_DIRECTORY_PREFIX}{script_name.replace(".py","")}')
		if not _.is_dir():
			warnings.warn(f'Directory with the output of script <{script_name}> "{_}" does not exist.')
		return _
