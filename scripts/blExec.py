import os
import sys

import bpy

# Добавляем директорию скрипта в sys.path
script_dir = os.path.dirname(os.path.abspath(__file__))
if script_dir not in sys.path:
    sys.path.append(script_dir)

from utils_reg import UNregister


# Существование путей ранее проверено в extension.ts при передаче
# Путь непосредственно запущенного *.py файла
run_file = None
# Путь текущего воркспейса, в котором где-то находится run_file
path_workspace = None
# print('ARGV 1:', run_file)
# print('ARGV 2:', path_workspace)


# С точки зрения Blender нужно указать не папку с проектом,
# а root каталог в котором находится каталог проекта
def add_path_package(path_dir_root):
    path_to_add = os.path.dirname(path_dir_root)
    if path_to_add not in sys.path:
        # .../DevCave/my_project
        sys.path.append(path_to_add)

    # Пока бесполезный вывод, на будущее путь для удаления из sys.path
    return path_to_add


# Путь к непосредственно запущенному файлу в VS Code (__init__ или script)
# path/to/folder and name_file.py
path_dir, name_file = os.path.split(run_file)
# print('path_dir:', path_dir)
# print('name_file', name_file)

# Полученное имя является именем пакета для exec_variables,
# Учитывает вложенный запуск проекта
path_package = os.path.basename(path_dir)
# print('path_package:', path_package)




# Определение типа запуска - скрипт/аддон
if name_file == '__init__.py' and path_dir == path_workspace:
    print('Это __init__.py основного пакета')

    # Разрегистрация старой версии аддона
    UNregister(path_package)

    # Потом можно удалять старый путь из sys.path
    # add_sys_path = add_path_package(path_workspace)

    # Добавляем root каталог проекта в sys.path
    add_path_package(path_workspace)

elif name_file.endswith('.py'):

    if name_file == '__init__.py':
        print('Обрабатываем __init__.py подмодуля как обычный скрипт')
    else:
        print(f'Это самостоятельный скрипт: {name_file}')
    # print('Это самостоятельный скрипт или __init__.py подмодуля')
    # Здесь не добавляем путь в sys.path, т.к. у скриптов нет относительных импортов
    # Относиительные импорты работают только с пакетами
else:
    print('Ошибка: Это не *.py файл')
    sys.exit(1)




# Словарь переменных для эмуляции переменных скрипта/аддона
exec_variables = {
    '__file__'   : run_file,
    '__name__'   : '__main__',
    '__package__': path_package,
    # 'DEBUG_MODE' : None,
}
# print(*[f'{key}: {value}' for key, value in exec_variables.items()], sep='\n')


with open(run_file) as f:
    code = f.read()
    # init_path типо имя файла на случай вызова ошибки 
    # codepile = compile(code, 'init_path', 'exec')
# exec(codepile, exec_variables)

# Запуск/перезапуск проекта
print('Запуск проекта')
exec(code, exec_variables)

# После выполнения exec, функция register должна быть доступна в exec_variables
if 'register' in exec_variables:
    register_func = exec_variables['register']
    register_func()
else:
    print('Функция register не найдена')