from bureaucrat.SmarterBureaucrat import SmarterBureaucrat
from pathlib import Path
from time import sleep

def script_core(path, some_variable:int):
	Rick = SmarterBureaucrat(
		measurement_base_path = path,
		_locals = locals(),
		new_measurement = True,
	)
	sleep(1) # This is to avoid multiple measurements with the same timestamp.
	with Rick.do_your_magic():
		with (Rick.path_to_default_output_directory/Path('measured_data.txt')).open('w') as ofile:
			print('Rick measured this!', file=ofile)
			print(f'The variable value is {some_variable}', file=ofile)

if __name__=='__main__':
	variable = 4
	script_core(
		path = Path.home()/Path('Desktop/measurements_data')/Path(f'variable_is_{variable}'),
		some_variable = variable,
	)
	
