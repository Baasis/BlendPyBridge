# command = `${pathPythonExe} "${scriptPath}" "${filePath}" "${workspacePath}" "${initFilePath}"`;

# sys.argv[0] - scriptPath    - это путь к самому скрипту
# d:\LIB_SVN\BRANCH_Personal_Use\DevCave\BlendPyBridge\scripts\socketSendCommand.py

# sys.argv[1] - filePath      - скрипт, который запускается blender-ом
# d:\LIB_SVN\BRANCH_Personal_Use\DevCave\BlenToTanki\vi\tester.py

# sys.argv[2] - workspacePath - папка проекта
# d:\LIB_SVN\BRANCH_Personal_Use\DevCave\BlenToTanki\vi

# sys.argv[3] - initFilePath  - __init__ полный путь, если есть
# undefined
# d:\LIB_SVN\BRANCH_Personal_Use\DevCave\BlenToTanki\vi\__init__.py

import os
import sys
import socket


sys.stdout.reconfigure(encoding='utf-8')

def send_command(command, host='localhost', port=3264):
    # command = b'TEXT:' + command.encode('utf-8')
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((host, port))
        s.sendall(command.encode('utf-8'))


print('/*'*20)

# print(sys.path)
print(sys.executable)

# current_file_path = os.path.abspath(__file__)

# base_path = os.getcwd()
# Получаем каталог, в котором находится текущий файл
work_dir = os.path.dirname(__file__)
print(work_dir)

# Путь к файлу модуля
path_module = os.path.join(work_dir, 'blExec.py')
if os.path.exists(path_module):
    print('Валидненько:', path_module)
    # Чтение исходного кода модуля
    with open(path_module, 'r') as file:
        module_code = file.read()
    
    # print(module_code)

else:
    print('НЕВалидненько!!!')
    sys.exit(1)


# Замена строки
module_code = module_code.replace(
    "path_dir_or_file = sys.argv[1]",
    f"path_dir_or_file = r'{sys.argv[1]}'"
)

# print(module_code)
send_command(module_code)

print('Отправлено')