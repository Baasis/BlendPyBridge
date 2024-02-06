# Файл запускается Blender-ом при старте
# blender --python self_script.py

import os
import sys
import time
import socket
import importlib
import threading

import bpy


# Добавляем директорию скрипта в sys.path
script_dir = os.path.dirname(os.path.abspath(__file__))
if script_dir not in sys.path:
    sys.path.append(script_dir)

from utils_reg import UNregister




class Color:
    RED     = '\033[91m'        # Цвет текста: Красный
    GREEN   = '\033[92m'        # Цвет текста: Зеленый
    YELLOW  = '\033[93m'        # Цвет текста: Желтый
    ORANGE  = '\033[38;5;208m'  # ANSI код для оранжевого цвета
    MAGENTA = '\033[95m'        # Цвет текста: Розовый
    RESET   = '\033[0m'         # Сброс цвета к стандартному

    # BLUE = '\033[94m'
    # CYAN = '\033[96m'
    # WHITE = '\033[97m'

    BG_BLUE = '\033[44m'      # Фон: Синий
    BG_GREEN = '\033[42m'     # Фон: Зеленый
    BG_YELLOW = '\033[43m'    # Фон: Желтый




# Запуск/перезапуск проекта
def start_project(package_name):
    print(f'{Color.YELLOW}Запуск проекта{Color.RESET}')

    # Запускаем проект через его Import
    module = importlib.import_module(package_name)
    
    # __name__ пакета будет именем пакета, __name__ != "__main__"
    # Вызываем функцию 'register' из импортированного модуля
    if hasattr(module, 'register'):
        module.register()
    else:
        print("Функция 'register' не найдена в модуле")

    print(f'{Color.YELLOW}Отработано{Color.RESET}')



# Пока не создан полный разрегистратор, без перезапуска, то нет смысла удалять путь из sys.path
# Так как я только при запуске могу могу использовать и посути выгружу и тут же загружу
# Это бессмысленно и я буду меша логику перезапускатора с разрегистратором
def path_append_to_syspath(added_path):
    if added_path not in sys.path:
        sys.path.append(added_path)


def blExec(message):
    print(f'\n{Color.GREEN}#### Вжух вжух, это магия ####{Color.RESET}')
    print(f'\n{Color.ORANGE} * def blExec(message){Color.RESET}')
    # Полученные от клиента пути для запуска проекта
    pathWorkspace, pathPyFile = message.split('\n')
    
    # Путь к непосредственно запущенному файлу в VS Code (__init__ или script)
    # path/to/folder and name_file.py
    path_dir, name_file = os.path.split(pathPyFile)


    # Определение типа запуска - скрипт/аддон
    if path_dir == pathWorkspace and name_file == '__init__.py':
        print('Это __init__.py основного пакета')
        
        # Полученное имя является именем пакета для,
        # Для учитывания вложенности запускаемого файла относительно корня
        module_name = os.path.basename(path_dir)
        
        # Разрегистрация старой версии аддона
        UNregister(module_name)

        # Добавляем root каталог проекта в sys.path
        # С точки зрения Blender нужно указать не папку с проектом,
        # а root каталог в котором находится каталог проекта
        path_to_add = os.path.dirname(pathWorkspace)
        path_append_to_syspath(path_to_add)
        # print(*sys.path, sep='\n')

        # Старт проекта
        start_project(module_name)


    elif name_file.endswith('.py'):
        print(f'Это самостоятельный скрипт: {name_file}')

        # Имя файла без расширения
        module_name = os.path.splitext(name_file)[0]

        # Разрегистрация старой версии аддона
        UNregister(module_name)
        
        # Добавляем путь к директории скрипта
        # path_append_to_syspath(path_dir)
        path_append_to_syspath(path_dir)
        # print(*sys.path, sep='\n')

        # Старт скрипта
        start_project(module_name)

    else:
        print('Ошибка: Это не *.py файл')
        sys.exit(0)




def handle_client(client_sock):
    try:
        # Собираем все части кода по 4096 байт
        data_parts = []
        while True:
            # Получает данные от клиента
            part = client_sock.recv(1024)
            # Если часть пустая, значит все данные получены
            if not part:
                break
            data_parts.append(part)
            
        # Склеиваем бинарные данные
        data = b''.join(data_parts)

        if data:
            # Декодирует полученные байты данных
            message = data.decode('utf-8')
            
            # Разграничивающая линия перед запуском полученного кода
            print('*'*50)
            
            # Особая проверка чтобы пользователь не мог прервать помимо своего аддона еще и сервер
            try:
                # exec в своем собственном локальном контексте и не видит глобальные переменные
                # exec(command, globals())
                blExec(message)
                # pass
            except SystemExit:
                print(f'{Color.ORANGE}Вызван {Color.RED}sys.exit(){Color.ORANGE}, но сервер продолжит работу{Color.RESET}')
            except Exception as e:
                print(f"Ошибка при выполнении команды: {e}")
        else:
            print('Нет данных для получения')

        # Обновляет текущий видовой слой в Blender, если необходимо
        # bpy.context.view_layer.update()

    except Exception as e:
        print(f'Ошибка обработки соединения: {e}')
    finally:
        # После получения всех частей кода и его заупска - закрываем соединение
        client_sock.close()
        print(f'{Color.YELLOW}Соединение закрыто{Color.RESET}')




# Собственно сам слушайющий сервер
# Если быстро перезапустить Blender, сервер не успеет остановится и ругнется на двойной запуск
def start_server(port=3264):
    # Создает сокет, AF_INET - сетевой сокет (IPv4), SOCK_STREAM - сокет TCP
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # Привязывает сокет к адресу localhost и порту
    server.bind(('localhost', port))
    # Максимальное количество входящих соединений, которые ожидают обработки, помещенные в очередь
    server.listen(1)
    print(f'{Color.YELLOW}Сервер запущен на порту {Color.GREEN}{port}{Color.RESET}')

    while True:
        # Ожидает входящее соединение от клиента, весь потом останавливается в ожидании сообщения
        client_sock, address = server.accept()
        print(f'{Color.YELLOW}Подключено к {Color.GREEN}{address}{Color.RESET}')
        # Сборка получаемого пакета и его запуск
        handle_client(client_sock)




# Аварийная самовырубалка процесса, на случай зависания или специфического вылета Blender
# Оно же проверялка текущего состояния сервера с обратным откликом
def check_blender_status():
    start_time = time.time()
    while True:
        try:
            count = len(bpy.data.scenes)
            if count == 0:
                raise Exception(f'Blender перестал отвечать\nCODE: {count}')

            elapsed_time = time.time() - start_time
            print(f'{Color.MAGENTA}RUN: {int(elapsed_time)} секунд{Color.RESET}')
        except Exception as e:
            print(f'{Color.YELLOW}Остановка сервера:{Color.RESET}', e)
            sys.exit(0)
        time.sleep(8)


# Господа демоны-процессы
def server_run():
    # Процесс слушающего сервера
    server_thread = threading.Thread(target=start_server, daemon=True)
    server_thread.start()
    # Процесс обратного отклика и статуса
    check_thread = threading.Thread(target=check_blender_status, daemon=True)
    check_thread.start()

# Запуск всей это эпопеи
server_run()
