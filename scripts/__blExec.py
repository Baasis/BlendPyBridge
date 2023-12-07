import os
import sys

addon_path = 'D:\WORK\GAYAPyProject\GAYA_Generators'
addons_folder, addon_name = os.path.split(addon_path)

init_path = '__init__.py'

if addons_folder not in sys.path:
    sys.path.append(addons_folder)

exec_code_path = os.path.join(addon_path, init_path)

exec_variables = {
    '__file__'   : exec_code_path,
    '__name__'   : '__main__',
    '__package__': 'Blender_EXEC',
    'DEBUG_MODE' : None,
}

with open(exec_code_path) as f:
    # init_path типо имя файла на случай вызова ошибки 
    code = compile(f.read(), init_path, 'exec')

exec(code, exec_variables)





