# command = `${pathExecPython} "${scriptPath}" "${pathPyFile}" "${pathWorkspace}"`;

# sys.argv[0] - scriptPath    - это путь к текущему скрипту при его запуске
# ...\BlendPyBridge\scripts\socketSendCommand.py

# sys.argv[1] - pathPyFile    - целевой скрипт-проект, который будет запускаться blender-ом
# ...\DevCave\VS_Code_Addons\EXPorter\testomizer.py

# sys.argv[2] - workspacePath - папка проекта
# ...\DevCave\VS_Code_Addons\EXPorter


import os
import sys
import socket


class ColTerm:
    HEADER = '\033[95m'      # Цвет текста: Розовый
    OKBLUE = '\033[94m'      # Цвет текста: Синий
    OKGREEN = '\033[92m'     # Цвет текста: Зеленый
    WARNING = '\033[93m'     # Цвет текста: Желтый
    ORANGE = '\033[38;5;208m'# ANSI код для оранжевого цвета
    FAIL = '\033[91m'        # Цвет текста: Красный
    ENDC = '\033[0m'         # Сброс цвета к стандартному
    BG_BLUE = '\033[44m'     # Фон: Синий
    BG_GREEN = '\033[42m'    # Фон: Зеленый
    BG_YELLOW = '\033[43m'   # Фон: Желтый


# Установка кодировки stdout и stderr на UTF-8
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')


# Отправляем код на указанный адрес и порт
def send_command(command, host='localhost', port=3264):
    # command = b'TEXT:' + command.encode('utf-8')
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((host, port))
        s.sendall(command.encode('utf-8'))


# Формируем путь к файлу, который отправится и выполнится в Blender,
# чтобы запустит требуемый проект в пространстве Blender

# Путь к папке с текущим файлом этого скрипта
work_dir = os.path.dirname(__file__)
# Путь к файлу blExec.py лежашего рядом с текущим скриптом
path_module = os.path.join(work_dir, 'blExec.py')


# На всякий случай проверяем наличие отправляемого скрипта
if os.path.exists(path_module):
    # Чтение blExec.py файла, не забываем указывать кодировку
    with open(path_module, 'r', encoding='utf-8') as file:
        module_code = file.read()
else:
    print(f'{ColTerm.FAIL}Скрипта blExec.py нет в папке{ColTerm.ENDC}')
    sys.exit(1)


# Подменяем переменные путей в blExec.py на пути запускаемого проекта
try:
    # Замена строк
    module_code = module_code.replace(
        "run_file = None",
        f"run_file = r'{sys.argv[1]}'"
    ).replace(
        "path_workspace = None",
        f"path_workspace = r'{sys.argv[2]}'"
    )
    # print(module_code)

    # Функция отправки кода на сервер
    send_command(module_code)

except Exception as e:
    print(f'\tОшибка отправке blExec.py в Blender: {e}')
else:
    print(f'{ColTerm.ORANGE}Файл {ColTerm.OKGREEN}blExec.py {ColTerm.ORANGE}отправлен успешно{ColTerm.ENDC}')