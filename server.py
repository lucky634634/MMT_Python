from os import curdir, sep
import socket

hostName = "0.0.0.0"
serverPort = 8080

def combineFile(path):
    f = open('200.html', 'r')
    newF = open('tmp.html', 'w')
    newF.write(f.read())
    if ('.html' in path):
        newF.write(r'Content-Type: text/html; charset=UTF-8\r\n')
    if ('.txt' in path):
        newF.write(r'Content-Type: text/plain\r\n')
    if ('.jpg' in path):
        newF.write(r'Content-Type: image/jpeg\r\n')
    if ('.png' in path):
        newF.write(r'Content-Type: image/png\r\n')
    if ('.css' in path):
        newF.write(r'Content-Type: text/css\r\n')
    newF.write('\n')
    f = open(path, 'r')
    newF.write(f.read())

def handleGET(request, client):
    path = request[4::].split()[0][1::]
    try:
        if (path == ''):
            path = 'index.html'
        combineFile(path)
        f = open('tmp.html')
        client.sendall(f.read().encode())
        client.close()
    except:
        f = open('404.html')
        client.sendall(f.read().encode())
        client.close()

def handlePOST(request, client):
    try:
        uname, psw, _ = request[request.index('uname')::].split()[0].split('&')
        uname = uname[6::]
        psw = psw[4::]
        if (uname == 'admin' and psw == '123456'):
            combineFile('images.html')
            f = open('tmp.html').read()
            client.sendall(f.encode())
            client.close()
        else:
            f = open('401.html')
            client.sendall(f.read().encode())
            client.close()
    except:
        f = open('404.html')
        client.sendall(f.read().encode())
        client.close()


def handleRequest(request, client):
    print(request)
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
    # combineFile('index.html', '.html')   