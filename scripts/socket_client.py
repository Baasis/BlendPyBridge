import time
import socket

def send_command(command, host='localhost', port=12345):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((host, port))
        s.sendall(command.encode('utf-8'))

#command = ""
#send_command(command)

time.sleep(4)
send_command("bpy.ops.mesh.primitive_monkey_add()")

time.sleep(4)
send_command("print('\\n')")

time.sleep(4)
send_command("print(list(bpy.data.objects))")

time.sleep(4)
send_command(r"print('\\n')")
send_command(r"print('\n')")

time.sleep(4)
send_command("print(list(bpy.data.objects))")

