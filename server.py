from os import curdir, sep
import socket

hostName = "0.0.0.0"
serverPort = 8080

def handleGET(request, client):
    path = request[4::].split()[0][1::]
    print(path)
    try:
        if (path == ''):
            path = 'index.html'
        f = open(path)
        client.sendall('HTTP/1.1 200 OK\r\n'.encode())
        client.sendall(f.read().encode())
        client.close()
    except:
        f = open('404.html')
        client.sendall('HTTP/1.1 404 Not Found\r\n'.encode())
        client.sendall(f.read().encode())
        client.close()

def handlePOST(request, client):
    try:
        uname, psw, _ = request[request.index('uname')::].split()[0].split('&')
        uname = uname[6::]
        psw = psw[4::]
        if (uname == 'admin' and psw == '123456'):
            client.sendall('HTTP/1.1 200 OK\r\n'.encode())
            client.close()
        else:
            f = open('401.html')
            client.sendall(f.read().encode())
            client.close()
    except:
        f = open('404.html')
        client.sendall('HTTP/1.1 404 Not Found\r\n'.encode())
        client.sendall(f.read().encode())
        client.close()


def handleRequest(request, client):
    if (request.startswith('GET')):
        handleGET(request, client)
    if (request.startswith('POST')):
        handlePOST(request, client)
        
        


def socketServer():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((hostName, serverPort))
    s.listen()

    while True:
        client, addr = s.accept()
        print("Success!")
        try:
            print("Connected by", addr)
            request = client.recv(1024).decode()
            handleRequest(request, client)
        except KeyboardInterrupt:
            print("Server closed")
            s.close()
            return

if __name__ == "__main__":
    socketServer()
    