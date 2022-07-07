from pathlib import Path
import datetime
import warnings
import inspect
import tempfile
from shutil import rmtree

class SmarterBureaucrat:
	"""Let a `SmartBureaucrat` ease your life by doing all the boring stuff
	while you focus on the important things.
	"""
	def __init__(self, measurement_base_path:Path, _locals:dict=None, new_measurement=False):
		"""Create an instance of `Bureaucrat`.
		
		Parameters
		----------
		measurement_base_path: Path
			If `new_measurement` is `True`, this must be a Path to the 
			directory that contains your measurement.
		_locals: ATTENTION HERE!
			This is in some sense a hack for creating a backup of the script
			that called this method including the variables values. You 
			always have to use this parameter in the following way:
			```
			_locals = locals()
			```
			I found no way to automatize and hide this, sorry.
		new_measurement: bool, default `False`
			If `False` then `measurement_base_path` must exist beforehand,
			i.e. you will run this script on a measurement that was already
			created in the past, for example you will now analyze this 
			data with another script. If `True` then a new directory
			will be created as the root directory for a new measurement.
		"""
		if _locals is None: # Explain how to use this workaround thing...
			raise ValueError(f'''When you create your bureaucrat please do it in this way:
bureaucrat = Bureaucrat(
	measurement_base_path = blah blah blah,
	_locals = locals(),
)
''')
		if not isinstance(measurement_base_path, Path):
			raise TypeError(f'`measurement_base_path` must be an instance of {Path}, received object of type {type(measurement_base_path)}.')
		if not isinstance(new_measurement, bool):
			raise TypeError(f'`new_measurement` must be `True` or `False`.')
		
		if ' ' in str(measurement_base_path):
			warnings.warn(f'The `measurement_base_path` contains blank spaces. I can handle this, but it is always better to aviod them.')
		
		self._datetime_bureaucrat_was_born = datetime.datetime.now()
		
		self._path_to_the_script_that_created_this_bureaucrat = Path.cwd()/Path(inspect.currentframe().f_back.f_code.co_filename)
		
		self._new_measurement = new_measurement
		
		if new_measurement == True:
			self._measurement_base_path = measurement_base_path.parent/Path(f'{self.birth_datetime.strftime("%Y%m%d%H%M%S")}_{measurement_base_path.parts[-1]}')
		else: # if not a new measurement...
			if not measurement_base_path.is_dir():
				raise FileNotFoundError(f'Directory {measurement_base_path} does not exist.')
			self._measurement_base_path = measurement_base_path
		
		self._backup_script_file_name = f'backup.{self._path_to_the_script_that_created_this_bureaucrat.parts[-1]}'
		self._make_backup_of_calling_script_file(
			_locals = _locals, 
			fpath = self.path_to_temporary_directory/Path(self._backup_script_file_name),
		)
	
	def do_your_magic(self, clean_default_output_directory:bool=True):
		"""Use this method to enter into a `with` statement (with the
		bureaucrat as the context manager). For example
		```
		with my_bureaucrat.do_your_magic(...):
			do_stuff()
		```
		
		Parameters
		----------
		clean_default_output_directory: bool, default `True`
			If `True`, all the contents in the output directory are deleted
			when the bureaucrat starts doing its magic. Otherwise they
			are not changed. This is useful when you may run a script that
			processes data more than once (because your are testing stuff
			or so) and you want to remove all the previous products of such
			script, or maybe for some reason you don't want to remove such
			old data.
		"""
		if clean_default_output_directory not in {True, False}:
			raise ValueError(f'`clean_default_output_directory` must be `True` or `False`, received {clean_default_output_directory}.')
		
		if not hasattr(self, '_do_your_magic_parameters'):
			self._do_your_magic_parameters = locals() # All the arguments of the function will be catched here.
		else:
			raise RuntimeError('Your bureaucrat has already done his magic, the idea is that you call it only once in your program!')
		return self
	
	def __enter__(self):
		if not hasattr(self, '_do_your_magic_parameters'):
			raise RuntimeError(f'Before doing `with your_bureaucrat:` you have to call `your_bureaucrat.do_your_magic`. A one liner is `with your_bureaucrat.do_your_magic(...):`')
		if hasattr(self, '_already_did_my_job'):
			raise RuntimeError(f'You can only request your bureaucrats to do their job once. This one has already finished.')
		if self._new_measurement:
			if self.path_to_measurement_base_directory.is_dir():
				raise RuntimeError(f'You told your bureaucrat that this is a new measurement, but the directory {self.path_to_measurement_base_directory} already exists...')
			self.path_to_measurement_base_directory.mkdir(parents=True)
		self.path_to_default_output_directory.mkdir(exist_ok=True)
		if self._do_your_magic_parameters['clean_default_output_directory'] == True:
			self.clean_default_output_directory()
		return self
	
	def __exit__(self, exc_type, exc_val, exc_tb):
		self._already_did_my_job = True
		(self.path_to_temporary_directory/Path(self._backup_script_file_name)).rename(self.path_to_default_output_directory/Path(self._backup_script_file_name)) # Move the backup script to the output directory.
		with open(self.path_to_default_output_directory/Path('SmarterBureaucrat_errors_report.txt'), 'w') as ofile:
			if all([exc is None for exc in [exc_type, exc_val, exc_tb]]): # This means there was no error, see https://docs.python.org/3/reference/datamodel.html#object.__exit__
				print('run_status: no errors', file=ofile)
				print(f'The sole purpose of this file is to indicate that this job was completed with no errors on {datetime.datetime.now()}.', file=ofile)
			else: # If there was any kind of error...
				print('run_status: there were errors', file=ofile)
				print(f'If you are reading this it means that this script ended with errors on {datetime.datetime.now()}', file=ofile)
	
	@property
	def path_to_measurement_base_directory(self) -> Path:
		"""Returns the path to the directory where all data concerning this
		measurement (this and other scripts) should be.
		"""
		return self._measurement_base_path
	
	@property
	def measurement_name(self) -> str:
		"""Returns a string with the measurement name."""
		return self.path_to_default_output_directory.parts[-1]
	
	@property
	def birth_datetime(self) -> datetime.datetime:
		"""Returns a `datetime.datetime` object with with the time when 
		the bureaucrat was created.
		"""
		return self._datetime_bureaucrat_was_born
	
	@property
	def path_to_default_output_directory(self) -> Path:
		"""Returns the full path to the directory where you should place
		the data produced by your current script.
		
		Returns
		-------
		path_to_directory: Path
			A `pathlib.Path` object to the directory.
		"""
		if not hasattr(self, '_path_to_default_output_directory'):
			self._path_to_default_output_directory = self.path_to_measurement_base_directory/Path(self._path_to_the_script_that_created_this_bureaucrat.parts[-1].replace(".py",""))
		return self._path_to_default_output_directory
	
	@property
	def path_to_temporary_directory(self) -> Path:
		"""Path to a temporary directory to store temporary stuff. It will
		be lost after Python ends."""
		if not hasattr(self, '_temporary_directory'):
			self._temporary_directory = tempfile.TemporaryDirectory()
		return Path(self._temporary_directory.name)
	
	def script_was_applied_without_errors(self, script_name:str=None) -> bool:
		"""Checks whether a script named `script_name` was run on the 
		measurement being handled by the bureaucrat and if it ended
		without errors.
		
		Parameters
		----------
		script_name: str, optional
			Name of the script that you want to check for. If not specified
			then the name of the current script is used.
		
		Returns
		-------
		did_it_run_without_errors: bool
			If the script ended without errors, `True` is returned, otherwise
			(either ended with errors or was not run at all) `False`. 
		"""
		if script_name is None:
			script_name = self._path_to_the_script_that_created_this_bureaucrat.parts[-1]
		errors_report_file_path = self.path_to_output_directory_of_script_named(script_name)/Path('SmarterBureaucrat_errors_report.txt')
		
		script_was_applied_without_errors = False
		
		try:
			with open(errors_report_file_path, 'r') as ifile:
				for line in ifile:
					if 'run_status: no errors' in line:
						script_was_applied_without_errors = True
		except FileNotFoundError:
			pass
		
		for fname in {'script_successfully_applied','.script_successfully_applied'}: # Compatibility with older bureaucrats...
			script_was_applied_without_errors |= (self.path_to_default_output_directory(script_name)/Path(fname)).is_file()
		
		return script_was_applied_without_errors
	
	def path_to_output_directory_of_script_named(self, script_name:str) -> Path:
		"""Returns the path to the directory where another script named 
		`script_name` that was run before on the same measurement was 
		supposed to store its output data.
		
		Parameters
		----------
		script_name: str
			The name of the other script.
		"""
		return self.path_to_measurement_base_directory/Path(script_name.replace(".py",""))
	
	def clean_default_output_directory(self):
		"""Deletes all content in the default output directory."""
		for p in self.path_to_default_output_directory.iterdir():
			if p.is_file():
				p.unlink()
			elif p.is_dir():
				rmtree(p)
	
	def _make_backup_of_calling_script_file(self, _locals:dict, fpath:Path):
		"""Creates a backup of the script in which this bureaucrat was
		created, and stores it in the default output directory.
		"""
		with fpath.open('w') as ofile:
			print(f'# This is an automatic copy of the script that processed the data in this directory.', file = ofile)
			print(f'# The script original location was {self._path_to_the_script_that_created_this_bureaucrat}', file = ofile)
			print(f'# This backup was created on {datetime.datetime.now()}.', file = ofile)
			print(f'# The local variables in the script at the moment this copy was made were:', file = ofile)
			for key in _locals:
				print(f'# {key}: {repr(_locals[key])}', file = ofile)
			print(f'# -----------------------------------', file = ofile)
			with self._path_to_the_script_that_created_this_bureaucrat.open('r') as ifile:
				for line in ifile:
					line = line.replace("\n","").replace("\r","")
					print(line, file = ofile)
