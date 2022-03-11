# bureaucrat

Small package for easy, uniform and OS independent handling of directories with my measurements. This should ensure that things are automatically kept in order.

## Installation

```
pip install git+https://github.com/SengerM/bureaucrat
```

## Usage

Suppose you have a script `do_something_with_my_data.py` with this content:
```python
from bureaucrat.Bureaucrat import Bureaucrat
from pathlib import Path

# Create `John`, a `Bureaucrat` object that will help you organize everything
John = Bureaucrat(
	measurement_base_path = '/path/to/my_measurement_main_directory',
	variables = locals(),
)

print(f'Working with {John.measurement_name}')
print(f"The full path to this measurement's folder is {John.measurement_base_path}")
print(f"The path to save data produced by this script is {John.current_script_output_directory_path}")

# Now let's create a file and store some text.
path_to_file = John.current_script_output_directory_path/Path('file_name.txt')
with open(path_to_file, 'w') as output_file:
	print('John helps you to organize your data :)', file=output_file)

```
You can see that the first thing we do is to create `John`, and then when we need to know the path to any directory we just ask him. In this way all the code becomes independent of the name of the measurement or where it is stored, you only have to tell John where it is and he will do the rest for you.

When you run the previous script, John will automatically create a new folder with the name of the script inside the measurement's folder, in this case `/path/to/my_measurement_main_directory/do_something_with_my_data`. Then you can ask John `John.current_script_output_directory_path` where to save your data.
