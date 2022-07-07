from bureaucrat.SmarterBureaucrat import SmarterBureaucrat
from pathlib import Path
from process_measurement_at_constant_variable import script_core as process_measurement_at_constant_variable

def script_core(path, force=False):
	Paul = SmarterBureaucrat(
		measurement_base_path = path,
		_locals = locals(),
	)

	if force==False and Paul.script_was_applied_without_errors():
		print(f'Script was already applied successfully on measurement {Paul.measurement_name}, nothing will be done...')
		return
	
	Paul.check_required_scripts_were_run_before('measure_sweeping_variable.py')
	
	with Paul.do_your_magic():
		submeasurements_dict = Paul.find_submeasurements('measure_sweeping_variable.py')
		values_of_variable = []
		for submeasurement_name in sorted(submeasurements_dict):
			process_measurement_at_constant_variable(path = submeasurements_dict[submeasurement_name])
			with open(submeasurements_dict[submeasurement_name]/Path('process_measurement_at_constant_variable/processed_data.txt'),'r') as ifile:
				for line in ifile:
					values_of_variable.append(int(line))
					break
		with open(Paul.path_to_default_output_directory/Path('values_of_variable.txt'), 'w') as ofile:
			print(values_of_variable, file=ofile)

if __name__=='__main__':
	script_core(
		Path.home()/Path.home()/Path('Desktop/measurements_data')/Path('20220707195708_measurement_sweeping_the_variable'),
		force = True,
	)
