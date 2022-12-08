from os import curdir, sep
import socket
import threading

HOST_NAME = 'localhost'
SERVER_PORT = 8080
BUFFER_SIZE = 1024
FORMAT = "utf8"

def sendFile(client, path, header = ''):
    l = open(path, 'rb').read()
    
    if header != '':
        header = header + 'Content-Length: ' + str(len(l)) + '\r\n'
        header += '\r\n'
    
    # print(header)
    f = header.encode()
    f += l
    
    client.sendall(f)
    # client.close()

def sendHeader200(client, path):
    header = 'HTTP/1.1 200 OK\r\nAccept-Ranges: bytes\r\n'
    header += 'Connection: Keep-Alive\r\n'
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

    ###
    header += 'Keep-Alive: timeout=5, max=1000\r\n'
    ###
    # header += '\r\n'

    # client.sendall(header.encode())
    return header

def handleGET(request, client):
    path = request[4::].split()[0][1::]
    try:
        if (path == ''):
            path = 'index.html'
        # sendHeader200(client, path)
        sendFile(client, path, sendHeader200(client, path))
    except:
        sendFile(client, '404.html')

def handlePOST(request, client):
    try:
        uname, psw, _ = request[request.index('uname')::].split()[0].split('&')
        uname = uname[6::]
        psw = psw[4::]
        if (uname == 'admin' and psw == '123456'):
            # sendHeader200(client, 'images.html')
            sendFile(client, 'images.html', sendHeader200(client, 'images.html'))
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

        
def _handle(client, addr):
    while True:
        try:
            print("Connected by", addr)
            request = client.recv(BUFFER_SIZE).decode()# 1024
            if not request: 
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
    #     request = client.recv(1024).decode()# 1024
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
