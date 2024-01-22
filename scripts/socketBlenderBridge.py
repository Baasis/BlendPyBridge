# Файл запускается Blender-ом при старте
# blender --python self_script.py

import sys
import time
import socket
import threading

import bpy


class Color:
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    ORANGE = '\033[38;5;208m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    RESET = '\033[0m'


def handle_client(client_sock):
    try:
        # Собираем все части кода по 4096 байт
        data_parts = []
        while True:
            # Получает данные от клиента
            part = client_sock.recv(4096)
            # Если часть пустая, значит все данные получены
            if not part:
                break
            data_parts.append(part)
            
        # Склеиваем бинарные данные
        data = b''.join(data_parts)

        if data:
            # Декодирует полученные байты данных
            command = data.decode('utf-8')
            
            # Разграничивающая линия перед запуском полученного кода
            # print('*'*50)
            
            # Особая проверка чтобы пользователь не мог прервать помимо своего аддона еще и сервер
            try:
                # exec в своем собственном локальном контексте и не видит глобальные переменные
                exec(command, globals())
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
