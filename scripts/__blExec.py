import os
import sys

addon_path = 'D:\LIB_SVN\BRANCH_Personal_Use\DevCave\EXPorter'
addons_folder, addon_name = os.path.split(addon_path)

init_path = '__init__.py'

if addons_folder not in sys.path:
    sys.path.append(addons_folder)

exec_code_path = os.path.join(addon_path, init_path)

exec_variables = {
    '__file__'   : exec_code_path,
    '__name__'   : '__main__',
    '__package__': 'EXPorter',
    'DEBUG_MODE' : None,
}

with open(exec_code_path) as f:
    code = compile(f.read(), init_path, 'exec')

exec(code, exec_variables)
