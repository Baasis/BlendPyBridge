import os
import sys
import time
import platform
import subprocess

from TerminalTextColer import ColTerm, terminal_print_header, highlight_last_path_component


# Проверка, выполняется ли скрипт в Windows
if platform.system() == 'Windows':
    # Изменение кодировки терминала на UTF-8
    subprocess.run(["chcp", "65001"], shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


terminal_print_header('__START_BRIDGE__', ColTerm.HEADER, s='\n')


# Получение и вывод текущего рабочего каталога
path_curr = os.path.dirname(os.path.realpath(__file__))
path_hl = highlight_last_path_component(path_curr, ColTerm.ORANGE)
print(f'{ColTerm.WARNING}Текущий рабочий каталог:{ColTerm.ENDC}\n{path_hl}')


# Путь к Blender, передаётся первым аргмуентом
if len(sys.argv) > 1:
    # print('*'*50)
    # print(sys.argv[1])
    path_blender = sys.argv[1]
    # Используйте path_blender в вашем скрипте
else:
    print("Путь к Blender не был предоставлен")
    sys.exit(1)
# Скрипт сокет сервера
path_server = "socketBlenderBridge.py"


# Проверка наличия файла blender.exe
if not os.path.isfile(path_blender):
    print(f'{ColTerm.FAIL}Blender не найден по указанному пути{ColTerm.ENDC}\n')
    sys.exit(1)
else:
    path_hl = highlight_last_path_component(path_blender, ColTerm.ORANGE)
    print(f'{ColTerm.WARNING}Blender EXE:{ColTerm.ENDC}\n{path_hl}')

# Проверка наличия серверного скрипта
full_path_server = os.path.join(path_curr, path_server)
if not os.path.isfile(full_path_server):
    print(f'{ColTerm.FAIL}Серверный скрипт не найден{ColTerm.ENDC}\n')
    sys.exit(1)
else:
    path_hl = highlight_last_path_component(full_path_server, ColTerm.ORANGE)
    print(f'{ColTerm.WARNING}Серверный скрипт:{ColTerm.ENDC}\n{path_hl}')


# Запуск Blender как подпроцесса
process_blender = subprocess.Popen([path_blender, "--python", full_path_server], stdout=None, stderr=None)
# process_blender = subprocess.Popen(path_blender, stdout=None, stderr=None)

# Вариант с перехватом и форматированием вывода Blender, он глючит из-за буфера
# process_blender = subprocess.Popen([path_blender, "--python", full_path_server], stdout=subprocess.PIPE)


terminal_print_header('__START_BLENDER__', ColTerm.HEADER, s='\n')

# Проверяет завершился ли процесс открытый в Popen, если нет, то код не идет дальше
while True:
    # Проверка состояния подпроцесса Blender
    if process_blender.poll() is not None:
        terminal_print_header('Blender завершил работу', ColTerm.OKGREEN)
        break
    time.sleep(1)
    
terminal_print_header('__FINISH__', ColTerm.OKGREEN, s='\n', f='\n')


# Считалка от 3 до 1 с паузой 1 секунда между числами
for i in range(3, 0, -1):
    print(f'До закрытия - {i} сек')
    time.sleep(1)

print('До встречи!')