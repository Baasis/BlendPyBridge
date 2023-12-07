# Помог второй вариант
# https://ru.stackoverflow.com/questions/1025858/Иероглифы-вместо-русского-языка-в-vscode-в-окне-output
# https://help-komp.ru/kak-ustanovit-russkij-yazyk-v-windows-11#:~:text=Административные%20языковые%20параметры%20(Administrative%20Language,от%20языка%20системы%20других%20пользователей


import time 

print('Zapuskatr готов к бою')

time.sleep(10)



# import os
# import inspect

# def transmit_func(path_folder, path_run):
#     return os.path.join(path_folder, path_run)

# print('*'*50, '\n', transmit_func('pupa', 'lupa'))

# fGet = inspect.getsource(transmit_func)

# print(fGet)

# print('*'*50)
# fGet += """
# a = 'afgan'
# b = 'pip'
# print(transmit_func(a, b))
# """
# print(fGet)
# print('*'*50)

# exec(fGet)



# import os
# import sys
# import pickle
# import inspect
# import functools

# def transmit_func(path_folder, path_run, addon_path):
#     return os.path.join(path_folder, path_run, addon_path)

# # Получите значение addon_path из sys.argv
# addon_path = sys.argv[2]
# print('\n')
# print(addon_path)
# print('\n')
# # Аргументы для функции
# arg1 = 'pupa'
# arg2 = 'LuPa'

# # Создаем частичную функцию, фиксируя аргументы arg1 и arg2
# partial_function = functools.partial(transmit_func, arg1, arg2, addon_path)
# print(partial_function)
# print('\n')
# # Сериализуем частичную функцию
# serialized_function = pickle.dumps(partial_function)
# print(serialized_function)
# print('\n')

# print('=+=')
# deserialized_function = pickle.loads(serialized_function)

# result = deserialized_function()
# print(result)

# Теперь можно передать serialized_function на сервер
