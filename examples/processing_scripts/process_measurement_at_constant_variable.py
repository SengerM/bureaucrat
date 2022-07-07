from bureaucrat.SmarterBureaucrat import SmarterBureaucrat
from pathlib import Path

def script_core(path, force=False):
	Paul = SmarterBureaucrat(
		measurement_base_path = path,
		_locals = locals(),
	)

	if force==False and Paul.script_was_applied_without_errors():
		print(f'Script was already applied successfully on measurement {Paul.measurement_name}, nothing will be done...')
		return
	
	Paul.check_required_scripts_were_run_before('measure_at_constant_variable.py')
	
	with Paul.do_your_magic():
		print(f'Processing measurement {Paul.measurement_name}...')
		with open(Paul.path_to_output_directory_of_script_named('measure_at_constant_variable.py')/Path('measured_data.txt'), 'r') as ifile:
			for line in ifile:
				if 'The variable value is' in line:
					variable_value_was = int(line.replace('The variable value is ',''))
		with open(Paul.path_to_default_output_directory/Path('processed_data.txt'), 'w') as ofile:
			print(variable_value_was, file=ofile)

if __name__=='__main__':
	script_core(
		Path.home()/Path.home()/Path('Desktop/measurements_data')/Path('20220707195708_measurement_sweeping_the_variable/measure_sweeping_variable/submeasurements/20220707195708_variable_value_0')
	)
