import gc
import sys
import inspect

import bpy


# Разрегистрация старой версии
#### Анализ запускаемого файла для поиска классов для разрегистрации
def UNregister(package_name):
    addon_modules = [mod for mod in sys.modules if mod.startswith(package_name)]

    # Множество для хранения имен обработанных классов
    # processed_classes = set()

    # Используем копию списка, так как будем изменять sys.modules
    for module_name in list(addon_modules):
        module = sys.modules[module_name]
        print(f'\n* Обработка модуля: {module_name}')

        # Перебираем все атрибуты модуля, для поиска классов, их регистрации и удаления
        for name in dir(module):
            obj = getattr(module, name)

            # Проверяем, является ли атрибут классом
            if isinstance(obj, type):
                # Если это не базовый класс и у класса есть bl_rna(определяет зарегистрированность класса)
                # if not is_bpy_base_class and hasattr(obj, "bl_rna"):
                if not obj.__module__.startswith("bpy.types") and hasattr(obj, "bl_rna"):
                    # processed_classes.add(name)
                    # Пытаемся разрегистрировать класс
                    try:
                        # По идее если есть bl_rna, то класс точно зареган и это нет смысла проверять
                        bpy.utils.unregister_class(obj)
                        print(f'\t- {name} разрегистрирован')
                    except Exception as e:
                        print(f'\t- {name} ошибка разрегистрации: {e}')
        
        # Удаляем модуль из sys.modules
        del sys.modules[module_name]
        print(f'* Модуль {module_name} удалён из sys.modules')

    print('\n')
