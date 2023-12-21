# command = `${pathExecPython} "${scriptPath}" "${pathPyFile}" "${pathWorkspace}"`;

# sys.argv[0] - scriptPath    - это путь к текущему скрипту при его запуске
# ...\BlendPyBridge\scripts\socketSendCommand.py

# sys.argv[1] - pathPyFile      - целевой скрипт-проект, который запускается в blender-ом
# ...\DevCave\VS_Code_Addons\EXPorter\testomizer.py

# sys.argv[2] - workspacePath - папка проекта
# ...\DevCave\VS_Code_Addons\EXPorter


import os
import sys
import socket

from TerminalTextColer import ColTerm


# Установка кодировки stdout и stderr на UTF-8
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')


# Отправляем код на указанный адрес и порт
def send_command(command, host='localhost', port=3264):
    # command = b'TEXT:' + command.encode('utf-8')
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((host, port))
        s.sendall(command.encode('utf-8'))


work_dir = os.path.dirname(__file__)
# print(work_dir)

# Ищем файл, который отправится и выполнится в Blender, который запустит проект в пространстве Blender
# Путь к файлу текущего модуля в расширении VS Code
path_module = os.path.join(work_dir, 'blExec.py')

# На всякий случай проверяем наличие отправляемого скрипта
if os.path.exists(path_module):
    # print(f'{ColTerm.OKGREEN}Валидненько:{ColTerm.ENDC}', path_module)

    # Чтение blExec.pyфайла, не забываем указывать кодировку
    with open(path_module, 'r', encoding='utf-8') as file:
        module_code = file.read()
else:
    print(f'{ColTerm.FAIL}НЕВалидненько - Скрипта нет !!!{ColTerm.ENDC}')
    sys.exit(1)


# Подменяем переменные путей в скрипте на пути проекта
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
    send_command(module_code)

except Exception as e:
    print(f'\tОшибка отправке blExec.py в Blender: {e}')
else:
    print(f'{ColTerm.ORANGE}Файл {ColTerm.OKGREEN}blExec.py {ColTerm.ORANGE}отправлен успешно{ColTerm.ENDC}')