# Это сокет клиент, для отправки кода на слушающий сокет сервер в Blender
# Файл запускается строкой ниже в extension.ts
# command = `${pathExecPython} "${pathSocketSendMessage}" "${pathWorkspace}" "${pathPyFile}"`;

# sys.argv[0] - pathSocketSendMessage      - это путь к текущему скрипту при его запуске
# ...\BlendPyBridge\scripts\socketSendCommand.py

# sys.argv[1] - доп.аргумент pathWorkspace - папка проекта
# ...\DevCave\EXPorter

# sys.argv[2] - доп.аргумент pathPyFile    - целевой скрипт-проект, который будет запускаться blender-ом
# ...\DevCave\EXPorter\testomizer.py


import sys
import socket


# Установка кодировки stdout и stderr на UTF-8
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')


# Отправляем код на указанный адрес и порт
def send_command(command, host='localhost', port=3264):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((host, port))
        s.sendall(command.encode('utf-8'))


# Отправляем переменные путей workspacePath + pathPyFile на сервер
send_command(f'{sys.argv[1]}\n{sys.argv[2]}')


