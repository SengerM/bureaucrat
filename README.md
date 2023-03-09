# bureaucrat

### DEPRECATED, use [this one](https://github.com/SengerM/the_bureaucrat)!!!

Package for easy, standard, safe and OS independent handling of directories with my measurements and data processing. This should ensure that things are automatically kept in order without my intervention.

## Installation

```
pip install git+https://github.com/SengerM/bureaucrat
```

## Usage

There are examples in the [examples directory](examples). For reference look at [the source code](bureaucrat/SmarterBureaucrat.py).

Creating a new measurement:
```python
from bureaucrat.SmarterBureaucrat import SmarterBureaucrat
from pathlib import Path

Rick = SmarterBureaucrat(
	measurement_base_path = path,
	_locals = locals(), # This is a workaround to backup the variables together with the script, it must be here... Sorry.
	new_measurement = True,
)
with Rick.do_your_magic(): # Here Rick creates the directory for the new measurement, does the backup of this script, etc.
	with (Rick.path_to_default_output_directory/Path('measured_data.txt')).open('w') as ofile:
		# Do whatever you like here...
		print('Rick measured this!', file=ofile)
		print(f'The variable value is {some_variable}', file=ofile)
		# raise RuntimeError('Ops!') # Any error that happens here will be reported in the output directory. Uncoment this line to test it.
```
Running an analysis script on an already existing measurement:
```python
from bureaucrat.SmarterBureaucrat import SmarterBureaucrat
from pathlib import Path

Paul = SmarterBureaucrat(
	measurement_base_path = path,
	_locals = locals(),
)

if force==False and Paul.script_was_applied_without_errors():
	print(f'Script was already applied successfully on measurement {Paul.measurement_name}, nothing will be done...')
	return

Paul.check_required_scripts_were_run_before('measure_at_constant_variable.py') # If this script did not end successfully previously on this measurement, an error will be raised.

with Paul.do_your_magic():
	print(f'Processing measurement {Paul.measurement_name}...')
	with open(Paul.path_to_output_directory_of_script_named('measure_at_constant_variable.py')/Path('measured_data.txt'), 'r') as ifile:
		for line in ifile:
			if 'The variable value is' in line:
				variable_value_was = int(line.replace('The variable value is ',''))
	with open(Paul.path_to_default_output_directory/Path('processed_data.txt'), 'w') as ofile:
		print(variable_value_was, file=ofile)
```
