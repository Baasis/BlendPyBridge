import sys

import bpy


# Разрегистрация старой версии
#### Анализ запускаемого файла для поиска классов для разрегистрации
def UNregister(package_name):
    addon_modules = [mod for mod in sys.modules if mod.startswith(package_name)]

    # Множество для хранения имен обработанных классов
    processed_classes = set()

    # Используем копию списка, так как будем изменять sys.modules
    for module_name in list(addon_modules):
        module = sys.modules[module_name]
        print(f'\n* Обработка модуля: {module_name}')

        for name in dir(module):
            obj = getattr(module, name)
            if isinstance(obj, type) and name not in processed_classes and not issubclass(obj, bpy.types.PropertyGroup):
                # Проверяем, есть ли у класса атрибут bl_rna
                if hasattr(obj, "bl_rna"):
                    processed_classes.add(name)
                    message = f'\t- Пациент {name} - '

                    if hasattr(bpy.utils, 'unregister_class'):
                        try:
                            bpy.utils.unregister_class(obj)
                            message += 'разрегистрирован'
                        except Exception as e:
                            message += f'ошибка: {e}'
                    else:
                        message += 'bpy.utils.unregister_class не доступен'
                    
                    print(message)
        
        # Удаляем модуль из sys.modules
        del sys.modules[module_name]
        print(f'* Модуль {module_name} удалён из sys.modules')
    
    print('\n')
    