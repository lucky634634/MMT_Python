from os import curdir, sep
import socket
import threading

HOST_NAME = 'localhost'
SERVER_PORT = 8080
BUFFER_SIZE = 1024
FORMAT = "utf8"

def sendFile(client, path, header):
    l = open(path, 'rb').read()
    
    if header != '':
        header = header + 'Content-Length: ' + str(len(l)) + '\r\n'
        header += '\r\n'
    
    # print(header)
    f = header.encode()
    f += l
    
    # print('Res: ', header.split('\r\n')[0])
    client.sendall(f)
    # client.close()

def _get_content_type(path):
    re = 'Content-Type: '

    if ('.html' in path or '.htm' in path):
        re += 'text/html; charset=UTF-8\r\n'
    elif ('.txt' in path):
        re += 'text/plain\r\n'
    elif ('.jpg' in path or '.jpeg' in path):
        re += 'image/jpeg\r\n'
    elif ('.png' in path):
        re += 'image/png\r\n'
    elif ('.css' in path):
        re += 'text/css\r\n'
    else:
        re += 'application/octet-stream\r\n'

    return re

def sendHeader200(client, path):
    header = 'HTTP/1.1 200 OK\r\nAccept-Ranges: bytes\r\n'
    header += 'Connection: Keep-Alive\r\n'
    header += _get_content_type(path)
    header += 'Keep-Alive: timeout=5, max=1000\r\n'
    # header += '\r\n'
    # client.sendall(header.encode())
    return header

def sendHeader404(client, path):
    header = 'HTTP/1.1 404 Not Found\r\nAccept-Ranges: bytes\r\n'
    header += 'Connection: Keep-Alive\r\n'
    header += 'Content-Type: text/html\r\n'
    header += 'Keep-Alive: timeout=5, max=1000\r\n'
    # header += '\r\n'
    return header

def sendHeader401():
    header = 'HTTP/1.1 401 Unauthorized\r\nAccept-Ranges: bytes\r\n'
    header += 'Connection: Keep-Alive\r\n'
    header += 'Content-Type: text/html\r\n'
    header += 'Keep-Alive: timeout=5, max=1000\r\n'
    # header += '\r\n'
    return header

def handleGET(request, client):
    path = request[4::].split()[0][1::]
    print('path: ',path)
    try:
        if (path == ''):
            path = 'index.html'
        sendFile(client, path, sendHeader200(client, path))
    except:
        sendFile(client, '404.html',sendHeader404(client,path))

def handlePOST(request, client):
    try:
        uname, psw, _ = request[request.index('uname')::].split()[0].split('&')
        uname = uname[6::]
        psw = psw[4::]
        if (uname == 'admin' and psw == '123456'):
            sendFile(client, 'images.html', sendHeader200(client, 'images.html'))
        else:
            sendFile(client, '401.html', sendHeader401())
    except:
        sendFile(client, '404.html',sendHeader401())


def handleRequest(request, client):
    if not request:
        print('No request')
    print('Req: ', request.split('\r\n')[0])
    # print(request)
    if (request.startswith('GET')):
        handleGET(request, client)
    if (request.startswith('POST')):
        handlePOST(request, client)


def _read_request(client, addr):
    result = ""
    client.settimeout(60)# sec
    try:
        result = client.recv(BUFFER_SIZE).decode()
        while (result):
            result = result + client.recv(BUFFER_SIZE).decode()
    except socket.timeout:
        if not result:
            print("Didn't receive data! [Timeout] from ", {addr})
    finally:
        return result


def _handle(client, addr):
    while True:
        try:
            print("Connected by", addr)
            request = client.recv(BUFFER_SIZE).decode()# 1024
            # request = _read_request(client, addr)
            if not request or request == ' ': 
                print("Client closed: ", addr)
                client.close()
                return
            handleRequest(request, client)
        except KeyboardInterrupt:
            print("Client closed: ", addr)
            client.close()
            return

    # try:
    #     print("Connected by", addr)
    #     request = client.recv(BUFFER_SIZE).decode()# 1024
    #     if not request: 
    #         print("Client closed: ", addr)
    #         client.close()
    #         return
    #     handleRequest(request, client)
    # except KeyboardInterrupt:
    #     print("Client closed: ", addr)
    #     client.close()
    #     return


def socketServer():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((HOST_NAME, SERVER_PORT))
    s.listen()
    print("Start Server - %s:%s"%(HOST_NAME,SERVER_PORT))

    while True:
        client, addr = s.accept()
        print("Success!")
        try:
            thr = threading.Thread(target=_handle,args=(client, addr))
            thr.daemon = False# TRUE
            thr.start()
        except KeyboardInterrupt:
            print("Server closed")
            s.close()
            return

if __name__ == "__main__":
    socketServer()
    # combineFile('index.html', '.html')   
