from pathlib import Path
import datetime
import warnings
import inspect
import requests

class Bureaucrat:
	"""
	Naming convention:
	- Stuff that ends in "path" is supposed to be/return an instance of Path.
	- Stuff that ends in "name" are strings.
	"""
	PROCESSED_DATA_DIRECTORY_PREFIX = 'processed_by_script_'
	def __init__(self, measurement_base_path: str, variables: dict = None, new_measurement=False):
		if variables is None:
			raise ValueError(f'''<variables> must be a dictionary with the variables names and their values, so the Bureaucrat can keep a record in the processed data directory. The easy way is to call
bureaucrat = Bureaucrat(
	measurement_base_path = "path/to/the/measurement"
	variables = locals()
)
using locals() which does exactly that.''')
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
		if not _.is_dir():
			warnings.warn(f'Directory with the output of script <{script_name}> "{_}" does not exist.')
		return _

class TelegramProgressBar:
	"""
	Usage example
	-------------
	
	from data_processing_bureaucrat.Bureaucrat import Bureaucrat, TelegramProgressBar
	import time

	bureaucrat = Bureaucrat(
		measurement_base_path = 'testing_the_bureaucrat',
		variables = locals(),
		new_measurement = True,
	)

	with TelegramProgressBar(99, bureaucrat) as pbar:
		for k in range(99):
			time.sleep(1)
			pbar.update(1)
	"""
	def __init__(self, total: int, bureaucrat: Bureaucrat, telegram_token='923059887:AAGW18jNJOshNi83r0Y6JsfizCdrCi8ytZQ', telegram_chat_id='164530575', **kwargs):
		self._telegram_token = telegram_token
		self._telegram_chat_id = telegram_chat_id
		self._bureaucrat = bureaucrat
		if not isinstance(total, int):
			raise TypeError(f'<total> must be an integer number, received {total} of type {type(total)}.')
		self._total = total

	def __enter__(self):
		try:
			response = self.send_message(f'Starting {self._bureaucrat.measurement_name}...')
			self._message_id = response['result']['message_id']
		except:
			warnings.warn(f'Could not establish connection with Telegram to send the progress status.')
		self._count = 0
		self._start_time = datetime.datetime.now()
		return self
		
	def update(self, count: int):
		if not hasattr(self, '_count'):
			raise RuntimeError(f'Before calling to <update> you should create a context using "with TelegramProgressBar(...) as pbar:".')
		if not isinstance(count, int):
			raise TypeError(f'<count> must be an integer number, received {count} of type {type(count)}.')
		self._count += count
		if hasattr(self, '_message_id'):
			message_string = f'{self._bureaucrat.measurement_name}\n\n'
			message_string += f'Started: {self._start_time.strftime("%Y-%m-%d %H:%M")}\n'
			message_string += f'Expexted finish: {(self._start_time + (datetime.datetime.now()-self._start_time)/self._count*self._total).strftime("%Y-%m-%d %H:%M")}\n'
			message_string += '\n'
			message_string += f'{self._count}/{self._total} | {self._count/self._total*100:.2f} %'
			try:
				self.edit_message(
					message_text = message_string,
					message_id = self._message_id,
				)
			except KeyboardInterrupt:
				raise KeyboardInterrupt()
			except:
				warnings.warn(f'Could not establish connection with Telegram to send the progress status.')
	
	def __exit__(self, exc_type, exc_value, exc_traceback):
		now = datetime.datetime.now()
		if hasattr(self, '_message_id'):
			message_string = f'{self._bureaucrat.measurement_name}\n\n'
			if self._count != self._total:
				message_string += f'FINISHED WITHOUT REACHING 100 %\n\n'
			message_string += f'Finished on {now.strftime("%Y-%m-%d %H:%M")}\n'
			message_string += f'Total elapsed time: {(now-self._start_time)}\n'
			try:
				self.edit_message(
					message_text = message_string,
					message_id = self._message_id,
				)
			except:
				warnings.warn(f'Could not establish connection with Telegram to send the progress status.')
	
	def send_message(self, message_text):
		# https://core.telegram.org/bots/api#sendmessage
		response = requests.get(
			f'https://api.telegram.org/bot{self._telegram_token}/sendMessage',
			data = {
				'chat_id': self._telegram_chat_id,
				'text': message_text,
			}
		)
		return response.json()

	def edit_message(self, message_text, message_id):
		# https://core.telegram.org/bots/api#editmessagetext
		requests.post(
			f'https://api.telegram.org/bot{self._telegram_token}/editMessageText',
			data = {
				'chat_id': self._telegram_chat_id,
				'text': message_text,
				'message_id': str(message_id),
			}
		)
