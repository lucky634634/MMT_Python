from os import curdir, sep
import socket

hostName = 'localhost'
serverPort = 8080

def sendFile(client, path):
    f = open(path, 'rb').read()
    client.sendall(f)
    client.close()

def sendHeader200(client, path):
    header = 'HTTP/1.1 200 OK\r\nAccept-Ranges: bytes\r\n'
    if ('.html' in path):
        header += 'Content-Type: text/html; charset=UTF-8\r\n'
    if ('.txt' in path):
        header += 'Content-Type: text/plain\r\n'
    if ('.jpg' in path):
        header += 'Content-Type: image/jpeg\r\n'
    if ('.png' in path):
        header += 'Content-Type: image/png\r\n'
    if ('.css' in path):
        header += 'Content-Type: text/css\r\n'
    header += '\r\n'
    client.sendall(header.encode())   

def handleGET(request, client):
    path = request[4::].split()[0][1::]
    try:
        if (path == ''):
            path = 'index.html'
        sendHeader200(client, path)
        sendFile(client, path)
    except:
        sendFile(client, '404.html')

def handlePOST(request, client):
    try:
        uname, psw, _ = request[request.index('uname')::].split()[0].split('&')
        uname = uname[6::]
        psw = psw[4::]
        if (uname == 'admin' and psw == '123456'):
            sendHeader200(client, 'images.html')
            sendFile(client, 'images.html')
        else:
            sendFile(client, '401.html')
    except:
        sendFile(client, '404.html')

def handleRequest(request, client):
    # print(request)
    if (request.startswith('GET')):
        handleGET(request, client)
    if (request.startswith('POST')):
        handlePOST(request, client)

def socketServer():
    print("Start Server - %s:%s"%(hostName,serverPort))
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((hostName, serverPort))
    s.listen()

    while True:
        client, addr = s.accept()
        print("Success!")
        try:
            print("Connected by", addr)
            request = client.recv(1024).decode()# 1024
            handleRequest(request, client)
        except KeyboardInterrupt:
            print("Server closed")
            s.close()
            return

if __name__ == "__main__":
    socketServer()