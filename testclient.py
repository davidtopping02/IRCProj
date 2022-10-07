import socket

HOST = "127.0.0.1" 
PORT = 4443  
SEPERATOR = " : ".encode()

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:

    print("Enter Username")
    user = input().encode()

    print("Enter Message")
    string = input().encode() 
    s.connect((HOST, PORT))
    s.sendall(user +SEPERATOR+ string)

    while(True):
        string = input().encode() 
        s.send(user +SEPERATOR+ string)
        data = s.recv(1024)
        print(data.decode('utf-8'))



print(f"Received {data!r}")
