from pathlib import Path
import datetime
import warnings
import inspect

class Bureaucrat:
	"""
	A class to normalize and ease the handling of directories with data.
	
	Naming convention
	-----------------
	- Stuff that ends in "path" is supposed to return an instance of Path.
	- Stuff that ends in "name" are strings.
	"""
	PROCESSED_DATA_DIRECTORY_PREFIX = ''
	SCRIPT_SUCCESSFULLY_FINISHED_WITHOUT_ERRORS_FILE_FLAG_NAME = '.script_successfully_applied'
	
	def __init__(self, measurement_base_path: Path, variables: dict = None, new_measurement=False):
		"""Create an instance of `Bureaucrat`.
		
		Parameters
		----------
		measurement_base_path: Path
			Path to the directory that contains your measurement. Example:
			```
			measurement_base_path = Path('/path/to/my_measurement')
			```
		variables: ATTENTION HERE!
			This is in some sense a hack for creating a backup of the script
			that called this method. You always have to use this parameter
			in the following way:
			```
			variables = locals()
			```
			I found no way to automatize and hide this, sorry.
		new_measurement: bool, default `False`
			If `False` then `measurement_base_path` must exist beforehand,
			i.e. you will run this script on a measurement that was already
			performed in the past, for example you will now analyze this 
			data with another script. If `True` then a new directory
			will be created.
		"""
		if variables is None:
			raise ValueError(f'''<variables> must be a dictionary with the variables names and their values, so the Bureaucrat can keep a record in the processed data directory. The easy way is to call
bureaucrat = Bureaucrat(
	measurement_base_path = "path/to/the/measurement"
	variables = locals()
)
using locals() which does exactly that.''')
		if not isinstance(measurement_base_path, Path):
			raise TypeError(f'`measurement_base_path` must be an instance of {Path}, received object of type {type(measurement_base_path)}.')
		if ' ' in str(measurement_base_path):
			warnings.warn(f'The `measurement_base_path` = {repr(measurement_base_path)} contains blank spaces. I can handle this, but it is better to aviod them.')
		self._timestamp = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
		self._measurement_base_path =  measurement_base_path
		self._processing_script_absolute_path = Path.cwd()/Path(inspect.currentframe().f_back.f_code.co_filename)
		self._processed_data_subdir_name = f'{self.PROCESSED_DATA_DIRECTORY_PREFIX}{self._processing_script_absolute_path.parts[-1].replace(".py","")}'
		
		if new_measurement == False:
			if not self._measurement_base_path.is_dir():
				raise FileNotFoundError(f'Directory "{self._measurement_base_path}" does not exist.')
		else:
			self._measurement_base_path = self._measurement_base_path.parent/Path(f'{self._timestamp}_{self._measurement_base_path.parts[-1]}')
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
		
		self.this_script_job_succesfully_completed_flag_file_path = self.processed_data_dir_path/Path(self.SCRIPT_SUCCESSFULLY_FINISHED_WITHOUT_ERRORS_FILE_FLAG_NAME)
		self._this_script_job_successfully_completed_before_flag = False
		if self.this_script_job_succesfully_completed_flag_file_path.is_file():
			self._this_script_job_successfully_completed_before_flag = True
	
	@property
	def measurement_base_path(self):
		"""Returns the path to the directory where all data concerning this
		measurement (this and other scripts) should be."""
		return self._measurement_base_path
	
	@property
	def measurement_name(self):
		"""Returns a string with the measurement name."""
		return self.measurement_base_path.parts[-1]
	
	@property
	def this_run_timestamp(self):
		"""Returns a string with a timestamp for the current run. This means
		the timestamp when the current bureaucrat was created."""
		return self._timestamp
	
	@property
	def timestamp(self):
		"""Same as `this_run_timestamp`."""
		return self._timestamp
	
	@property
	def current_script_output_directory_path(self) -> Path:
		"""Returns the full path to the directory where you should place
		the data produced by your current script.
		
		Returns
		-------
		path_to_directory: Path
			A `pathlib.Path` object to the directory.
		"""
		return self.processed_data_dir_path
	
	@property
	def processed_data_dir_path(self):
		"""Same as `current_script_output_directory_path`."""
		_ = self._measurement_base_path/Path(self._processed_data_subdir_name)
		_.mkdir(exist_ok=True)
		return _
	
	def other_script_output_directory_path(self, script_name: str) -> Path:
		"""Returns the full path to the directory where another script that
		was run for the current measurement should have stored it's data.
		
		Parameters
		----------
		script_name: str
			The name of the other script.
		
		Returns
		-------
		path_to_directory: Path
			A `pathlib.Path` object to the directory.
		"""
		return self.processed_by_script_dir_path(script_name)
	
	def processed_by_script_dir_path(self, script_name: str):
		"""Same as `other_script_output_directory_path`."""
		_ = self._measurement_base_path/Path(f'{self.PROCESSED_DATA_DIRECTORY_PREFIX}{script_name.replace(".py","")}')
		return _
	
	def job_successfully_completed_by_script(self, script_name: str) -> bool:
		"""Returns `True` if the script `script_name` was applied before 
		to the current measurement AND the `verify_no_errors_context` method
		was used AND such script ended without errors.
		If `script_name` is `'this script'` (case unsensitive) then it 
		checks for the current script without the need to hardcode its 
		name.
		
		Parameters
		----------
		script_name: str
			Name of the script you want to check if it was run (and if it
			was whether it was without errors) on the current measurement.
		"""
		if script_name.lower() == 'this script':
			script_name = str(self._processing_script_absolute_path.parts[-1])
		if script_name == str(self._processing_script_absolute_path.parts[-1]):
			return self._this_script_job_successfully_completed_before_flag
		else:
			return (self.processed_by_script_dir_path(script_name)/Path(self.SCRIPT_SUCCESSFULLY_FINISHED_WITHOUT_ERRORS_FILE_FLAG_NAME)).is_file()
	
	def verify_no_errors_context(self):
		"""Call with a context manager to create a hidden file if the job
		is completed without errors so later on other scripts can verify 
		this. Example:
		```
		with buraucrat.veriry_no_errors_context:
			very_important_function()
		```
		If no errors occur within the `with` block, a file will be created
		indicating the completion of the tasks with no errors. Later on
		you can call `job_successfully_completed_by_script` and it will
		tell you if there were errors or not."""
		return _MarkJobWithNoErrors(self.this_script_job_succesfully_completed_flag_file_path)
	
class _MarkJobWithNoErrors:
	def __init__(self, file_path: Path):
		self.file_path = file_path
	
	def __enter__(self):
		self.file_path.unlink(missing_ok=True)
	
	def __exit__(self, exc_type, exc_val, exc_tb):
		if all([exc is None for exc in [exc_type, exc_val, exc_tb]]): # This means there was no error, see https://docs.python.org/3/reference/datamodel.html#object.__exit__
			with open(self.file_path, 'w') as ofile:
				print(f'Job completed with no errors on {datetime.datetime.now()}.', file=ofile)
