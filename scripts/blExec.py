import os
import sys

import bpy


run_file = None
path_workspace = None
print('ARGV 1:', run_file)
print('ARGV 2:', path_workspace)

if not os.path.exists(run_file):
    print(f'Путь недопустим или не существует')
    sys.exit(1)


# Вот тут неправильно с точки зрения Blender
# Blender ищет все пакеты и скрипты в папке addons
# Нужно добавить папку не к самому аддону, а к root каталогу текущего пакета
def add_package_path(path_dir_or_file):
    if path_dir_or_file not in sys.path:
        # sys.path.append(path_dir_or_file)
        # .../DevCave/VS_Code_Addons
        # sys.path.append(os.path.dirname(path_dir_or_file))
        sys.path.append(path_dir_or_file)
    print('path_dir_or_file:', path_dir_or_file)



# Это файл, но какой ...
path_dir, name_file = os.path.split(run_file)
    
# Имя файла, сам себе имя пакета?
path_package = os.path.basename(path_dir)
print('run_file:', run_file)

# Определение типа скрипта
# Если *.py либо __init__.py
# Бля __init__ может быть в подмодулях и я их неправильно обработаю !!!!!!!!!!!!!!!
if name_file == '__init__.py':
    print('Это __init__.py пакета')
    # Это пакет и нужно добавить путь к воркспейсу
    add_package_path(path_workspace)

elif name_file.endswith('.py'):
    print('Это самостоятельный скрипт')
    # Для файла тоже нужно добавлять путь __file__ каталога в sys.path
    print('ХУУУУУ', os.path.dirname(path_dir))
    add_package_path(os.path.dirname(path_dir))
else:
    print('Ошибка: Это не *.py файл')
    sys.exit(1)


exec_variables = {
    '__file__'   : run_file,
    '__name__'   : '__main__',
    '__package__': path_package,
    'DEBUG_MODE' : None,
}

# print(*[f'{key}: {value}' for key, value in exec_variables.items()], sep='\n')

with open(run_file) as f:
    code = f.read()
    # init_path типо имя файла на случай вызова ошибки 
    # codepile = compile(code, 'init_path', 'exec')


#### Анализ запускаемого файла для поиска классов для разрегистрации
addon_modules = [mod for mod in sys.modules if mod.startswith(path_package)]

# Множество для хранения имен обработанных классов
processed_classes = set()

# Используем копию списка, так как будем изменять sys.modules
for module_name in list(addon_modules):
    module = sys.modules[module_name]
    print(f'Обработка модуля: {module_name}')

    for name in dir(module):
        obj = getattr(module, name)
        if isinstance(obj, type) and name not in processed_classes and not issubclass(obj, bpy.types.PropertyGroup):
            # Проверяем, есть ли у класса атрибут bl_rna
            if hasattr(obj, "bl_rna"):
                print(f'\tПациент для разрегистрации: {name}')
                processed_classes.add(name)

                if hasattr(bpy.utils, 'unregister_class'):
                    try:
                        bpy.utils.unregister_class(obj)
                        print(f'\nКласс {name} успешно разрегистрирован')
                    except Exception as e:
                        print(f'\tОшибка при разрегистрации класса {name}: {e}')
                else:
                    print(f'\tbpy.utils.unregister_class не доступен для класса {name}')
    
    # Удаляем модуль из sys.modules
    del sys.modules[module_name]
    print(f'\tМодуль {module_name} удалён из sys.modules')


# Запуск/перезапуск проекта
# exec(codepile, exec_variables)
exec(code, exec_variables)







# # Путь - каталог, ищем __init__
# if os.path.isdir(path_dir_or_file):
#     # Это папка, при запуске скрипта напрямую
#     run_file = os.path.join(path_dir_or_file, '__init__.py')
#     # Если __init__ есть в каталоге это пакет
#     if os.path.isfile(run_file):
#         print('Это пакет')
#         # add_package_path(path_dir_or_file)
#         # Добавляем мета-каталог
#         add_package_path(os.path.dirname(path_dir_or_file))
#         print('run_file:', run_file)
#     else:
#         print('Ошибка: Это папка, но в ней нет файла __init__.py')
#         sys.exit(1)
# else: