import gc
import sys
import inspect

import bpy


# Разрегистрация старой версии
#### Анализ запускаемого файла для поиска классов для разрегистрации
def UNregister(package_name):
    print(f'\033[38;5;208m  def UNregister(package_name)  \033[0m')

    class_registered = []

    for cls_name in dir(bpy.types):
        # Получаем ссылку на элемент в bpy.types
        cls = getattr(bpy.types, cls_name)
        # Если ссылка является классом
        if isinstance(cls, type):
            # И начинается с имени модуля пользователя
            if cls.__module__.startswith(package_name):
                print(' + ', cls)
                class_registered.append(cls.__name__)

                try:
                    bpy.utils.unregister_class(cls)
                    print(f'\t- {class_registered[-1]} разрегистрирован')
                except Exception as e:
                    print(f'\t- Ошибка при разрегистрации {class_registered[-1]}: {e}')

    print(class_registered)


    addon_modules = [mod for mod in sys.modules if mod.startswith(package_name)]

    for module_name in addon_modules:
        module = sys.modules[module_name]
        print(f'\n* Обработка модуля: {module_name}')
        
        # Удаляем модуль из sys.modules
        del sys.modules[module_name]
        print(f'* Модуль {module_name} удалён из sys.modules')

    print('\n')
