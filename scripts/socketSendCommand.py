import sys
import socket
import marshal

sys.stdout.reconfigure(encoding='utf-8')

# print('/\\'*25)
# print(sys.executable)
# print('-'*50)

def send_command(command, host='localhost', port=3264):
    command = b'TEXT:' + command.encode('utf-8')
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((host, port))
        s.sendall(command)

def send_byteCode(code, host='localhost', port=3264):
    marshaled_code = marshal.dumps(code)
    marshaled_code = b'MARSHAL:' + marshaled_code
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((host, port))
        s.sendall(marshaled_code)
        
        
# command = `${pathPythonExe} "${scriptPath}" "${filePath}" "${workspacePath}" "${initFilePath}"`;
# scriptPath
# d:\LIB_SVN\BRANCH_Personal_Use\DevCave\BlendPyBridge\scripts\socketSendCommand.py
# filePath
# d:\LIB_SVN\BRANCH_Personal_Use\DevCave\BlenToTanki\vi\tester.py

# d:\LIB_SVN\BRANCH_Personal_Use\DevCave\BlenToTanki\vi
# undefined
    
# if len(sys.argv) > 1:
#     print("Переданные аргументы:")
#     # sys.argv[0] - это путь к самому скрипту
#     for arg in sys.argv[1:]:
#         print(arg)

# print('pathPythonExe:', sys.argv[0])
# print('scriptPath:', sys.argv[1])
# print('filePath', sys.argv[1])
# print('workspacePath', sys.argv[3])
# print('initFilePath', sys.argv[4])
        

# Путь к исполняемому файлу
exec_code_path = sys.argv[1]

with open(exec_code_path) as f:
    script_content = f.read()
    code = compile(script_content, 'init_path', 'exec')

print('Компайлюшка:', code)


# Выводит текст скрипта
# print(script_content)

# send_command(marshaled_code)
# print(script_content)
# send_command(script_content)
# send_byteCode(script_content)
send_byteCode(code)

# send_command("import sys")
# send_command("print(sys.executable)")
# send_command("print(sys.version)")
# send_command("print(bpy.data.objects)")
# send_command("bpy.ops.mesh.primitive_monkey_add()")


