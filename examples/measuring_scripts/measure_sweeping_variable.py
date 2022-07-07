from bureaucrat.SmarterBureaucrat import SmarterBureaucrat
from pathlib import Path
from measure_at_constant_variable import script_core as measure_at_constant_variable

John = SmarterBureaucrat(
	measurement_base_path = Path.home()/Path('Desktop/measurements_data')/Path(f'measurement_sweeping_the_variable'),
	_locals = locals(), # This will make John to store all the variables
	new_measurement = True,
)

with John.do_your_magic():
	with open(John.path_to_default_output_directory/Path('output_data.txt'), 'w') as ofile:
		print('Some stuff...', file=ofile)
	for k in range(22):
		measure_at_constant_variable(
			John.path_to_submeasurements_directory/Path(f'variable_value_{k}'),
			some_variable = k,
		)
