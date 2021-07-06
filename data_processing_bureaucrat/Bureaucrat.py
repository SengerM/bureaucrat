from pathlib import Path
import datetime
import warnings
import inspect

class Bureaucrat:
	"""
	Naming convention:
	- Stuff that ends in "path" is supposed to be/return an instance of Path.
	- Stuff that ends in "name" are strings.
	"""
	PROCESSED_DATA_DIRECTORY_PREFIX = ''
	def __init__(self, measurement_base_path: str, variables: dict = None, new_measurement=False):
		if variables is None:
			raise ValueError(f'''<variables> must be a dictionary with the variables names and their values, so the Bureaucrat can keep a record in the processed data directory. The easy way is to call
bureaucrat = Bureaucrat(
	measurement_base_path = "path/to/the/measurement"
	variables = locals()
)
using locals() which does exactly that.''')
		measurement_base_path = str(measurement_base_path)
		if ' ' in measurement_base_path:
			warnings.warn(f'The <measurement_base_path> = "{measurement_base_path}" contains blank spaces. I can handle this, but it is better to aviod them.')
		self._timestamp = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
		self._measurement_base_path =  Path(measurement_base_path)
		self._processing_script_absolute_path = Path.cwd()/Path(inspect.currentframe().f_back.f_code.co_filename)
		self._processed_data_subdir_name = f'{self.PROCESSED_DATA_DIRECTORY_PREFIX}{self._processing_script_absolute_path.parts[-1].replace(".py","")}'
		
		if new_measurement == False:
			if not self._measurement_base_path.is_dir():
				raise ValueError(f'Directory "{self._measurement_base_path}" does not exist.')
		else:
			self._measurement_base_path = Path('/'.join(list(self._measurement_base_path.parts[:-1]) + [f'{self._timestamp}_{self._measurement_base_path.parts[-1]}']))
			self._measurement_base_path.mkdir()
		
		with (self.processed_data_dir_path/Path(f'backup.{self._processing_script_absolute_path.parts[-1]}')).open('w') as ofile:
			print(f'# This is an automatic copy of the script that processed the data in this directory.', file = ofile)
			print(f'# The script original location was {self._processing_script_absolute_path}', file = ofile)
			print(f'# The timestamp for this processing is {self._timestamp}.', file = ofile)
			print(f'# The local variables in the script at the moment this copy was made were:', file = ofile)
			for key in variables:
				print(f'# {key}: {variables[key]}', file = ofile)
			print(f'# -----------------------------------', file = ofile)
			with self._processing_script_absolute_path.open('r') as ifile:
				for line in ifile:
					line = line.replace("\n","").replace("\r","")
					if 'locals()' in line:
						print(f'{line} # <-- Variables were registered at this point: {variables}', file = ofile)
					else:
						print(line, file = ofile)
		
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
	def timestamp(self):
		return self._timestamp
	
	@property
	def raw_data_dir_path(self):
		warnings.warn(f'<raw_data_dir_path> is deprecated. It is better to store everything in the script processed data dir path.')
		raw_path = self._measurement_base_path/Path('raw')
		raw_path.mkdir(exist_ok=True)
		# ~ if not raw_path.is_dir():
			# ~ warnings.warn(f'Directory with raw data "{raw_path}" does not exist.')
		return raw_path
	
	@property
	def processed_data_dir_path(self):
		_ = self._measurement_base_path/Path(self._processed_data_subdir_name)
		_.mkdir(exist_ok=True)
		return _
	
	def processed_by_script_dir_path(self, script_name: str):
		_ = self._measurement_base_path/Path(f'{self.PROCESSED_DATA_DIRECTORY_PREFIX}{script_name.replace(".py","")}')
		return _

class TelegramReportingInformation:
	apples = '1689568059:AAFkl3e0hsHBKfYF65VDxqbvIiahhbdjChY'
	strawberries = '164530575'
	
	@property
	def token(self):
		return self.apples
	
	@property
	def chat_id(self):
		return self.strawberries
