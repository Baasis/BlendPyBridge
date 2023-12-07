import os
import sys


path_dir_or_file = sys.argv[1]
print('input:', path_dir_or_file)

if not os.path.exists(path_dir_or_file):
    print(f'Путь недопустим или не существует')
    sys.exit(1)


run_file = None
path_package = None


def add_package_path(path_dir_or_file):
    if path_dir_or_file not in sys.path:
        sys.path.append(path_dir_or_file)
    print('path_dir_or_file:', path_dir_or_file)


if os.path.isdir(path_dir_or_file):
    # Это папка, при запуске скрипта напрямую
    run_file = os.path.join(path_dir_or_file, '__init__.py')
    if os.path.isfile(run_file):
        print('Это пакет')
        add_package_path(path_dir_or_file)
        print('run_file:', run_file)
    else:
        print('Ошибка: Это папка, но в ней нет файла __init__.py')
        sys.exit(1)
else:
    # Это файл, при запуске *.py либо __init__.py через exec()
    path_dir, name_file = os.path.split(path_dir_or_file)
    run_file = path_dir_or_file
    path_package = os.path.basename(path_dir)
    print('run_file:', run_file)
    # if path_dir_or_file.endswith('__init__.py'):
    if name_file == '__init__.py':
        print('Это __init__.py пакета')
        add_package_path(path_dir)
    # Может и для файла нужно добавлять в sys.path путь к директории запуска
    elif name_file.endswith('.py'):
        print('Это самостоятельный скрипт')
    else:
        print('Ошибка: Это файл, но не *.py')
        sys.exit(1)
    
    
exec_variables = {
    '__file__'   : run_file,
    '__name__'   : '__main__',
    '__package__': path_package,
    'DEBUG_MODE' : None,
}

print(*[f'{key}: {value}' for key, value in exec_variables.items()], sep='\n')

with open(run_file) as f:
    code = f.read()
    # init_path типо имя файла на случай вызова ошибки 
    codepile = compile(code, 'init_path', 'exec')

print('Экзешим')

# exec(codepile, exec_variables)
exec(code, exec_variables)

print('ОтЭкзешено')