import sys
import socket

sys.stdout.reconfigure(encoding='utf-8')


if len(sys.argv) > 1:
    print("Переданные аргументы:")
    # sys.argv[0] - это путь к самому скрипту
    for arg in sys.argv[1:]:
        print(arg)
        



def send_command(command, host='localhost', port=12345):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((host, port))
        s.sendall(command.encode('utf-8'))




# print('Client запускается')

send_command("print('+'*50)")
# send_command("print(bpy.data.objects)")
# send_command("bpy.ops.mesh.primitive_monkey_add()")


