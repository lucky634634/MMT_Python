from os import curdir, sep
import socket
import threading
import time

HOST_NAME = 'localhost'
SERVER_PORT = 8080
BUFFER_SIZE = 4096#4096
FORMAT = "utf8"

ADDR_LIST = []
queue = []
# ------------------- 
def sendFile(client, path, header, request):
    # Đọc dữ liệu từ file dưới dạng bytes
    l = open(path, 'rb').read()

    # Xác dịnh Content-Length của file tương ứng
    if header != '':
        header = header + 'Content-Length: ' + str(len(l)) + '\r\n'
        header += '\r\n'# Kết thúc phần header

    # Thêm header và nội dung của file vào response
    f = header.encode()
    f += l

    # Gửi toàn bộ response đến client
    try:
        client.sendall(f)
        if(len(queue) > 0):
           queue.pop(0)
    except socket.timeout: 
        pass

def _get_content_type(path):
    re = 'Content-Type: '

    # Tùy vào mỗi định dạng file
    # mà ta có các xử lý tương ứng
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
    else:# (unknown)
        re += 'application/octet-stream\r\n'

    return re

def sendHeader200(path):
    header = 'HTTP/1.1 200 OK\r\nAccept-Ranges: bytes\r\n'
    header += 'Connection: Keep-Alive\r\n'
    header += _get_content_type(path)
    header += 'Keep-Alive: timeout=60, max=1000\r\n'#10000
    return header

def sendHeader404():
    header = 'HTTP/1.1 404 Not Found\r\nAccept-Ranges: bytes\r\n'
    header += 'Connection: close\r\n'
    header += 'Content-Type: text/html\r\n'
    return header

def sendHeader401():
    header = 'HTTP/1.1 401 Unauthorized\r\nAccept-Ranges: bytes\r\n'
    header += 'Connection: close\r\n'
    header += 'Content-Type: text/html\r\n'
    return header

def handleGET(request, client):
    path = request[4::].split()[0][1::]
    # print('path: ',path)
    try:
        if (path == ''):
            path = 'index.html'
        sendFile(client, path, sendHeader200(path), request)
    except:
        sendFile(client, '404.html',sendHeader404(), request)

def handlePOST(request, client):
    try:
        uname, psw, _ = request[request.index('uname')::].split()[0].split('&')
        uname = uname[6::]
        psw = psw[4::]
        if (uname == 'admin' and psw == '123456'):
            sendFile(client, 'images.html', sendHeader200('images.html'), request)
        else:
            sendFile(client, '401.html', sendHeader401(), request)
    except:
        sendFile(client, '404.html',sendHeader401(), request)

def handleRequest(request, client, addr):
    if not request:
        print('No request')
    # print(request)
    # print('>> From', _modify_addr(addr), 'request:', request.split('\r\n')[0])
    print('>> From', addr, 'request:', request.split('\r\n')[0])
    if (request.startswith('GET')):
        handleGET(request, client)
    if (request.startswith('POST')):
        handlePOST(request, client)

# Server đọc request từ phía client
def _read_request(Client):
	re = ""
	Client.settimeout(1)# 1
	try:
		re = Client.recv(BUFFER_SIZE).decode()
		while (re):
			re = re + Client.recv(BUFFER_SIZE).decode()
	except socket.timeout: # fail after 1 second of no activity
		pass
	finally:
		return re

def _modify_addr(addr):
    addrStr = str(addr)
    addrStr = addrStr[1::].split(',')[0]
    return addrStr

def _thr_get_req(client, addr):
    with client:
        while True:
            try:
                # request = _read_request(client)
                request = client.recv(BUFFER_SIZE).decode()# 1024
                queue.append(request)
            except KeyboardInterrupt:
                break

def recvall3(sock, size):
    result = b''
    remaining = size
    while remaining > 0:
        data = sock.recv(remaining)
        result += data
        remaining -= len(data)
    return result.decode()

def _handle(client, addr):
    with client:
        # time.sleep(0)
        # t1 = threading.Thread(target=_thr_get_req,args=(client, addr))
        # t1.start()
        while True:
            try:
                request = ''
                
                # request = _read_request(client)
                request = client.recv(BUFFER_SIZE).decode()# 1024
                # print(request)
                # request = recvall3(client, 10000)# 1024
                
                # queue.append(request)
                # if len(request) > 0:
                    # if request not in queue:
                        # queue.append(request)
                if len(queue) > 0:
                    request = queue[0]
                if not request:
                    break
                handleRequest(request, client, addr)
            except socket.timeout:
                break
            except KeyboardInterrupt:
                break

        # t1.join()
        print("Client closed: ", addr)
        print("------------------------------")
        client.close()
        # ADDR_LIST.remove(_modify_addr(addr))

def socketServer():
    # khởi tạo socket sử dụng IPv4 và TCP
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # socket bind với name: localhost trên port: 8080
    s.bind((HOST_NAME, SERVER_PORT))
    # sau đó server sẽ chờ để listen 
    # và accept connection từ browser
    s.listen(1)
    print("Start Server - %s:%s"%(HOST_NAME,SERVER_PORT))

    # try:
    #     client, addr = s.accept()
    #     # client.settimeout(1)
    #     print(addr, "- Xin mo ket noi")
    #     thr = threading.Thread(target=_handle,args=(client, addr))
    #     thr.daemon = False# TRUE
    #     thr.start()
    # except KeyboardInterrupt:
    #     print("Server closed")
    #     s.close()
    #     return

    while True:
        try:
            client, addr = s.accept()
            addrStr = _modify_addr(addr)
            if(addrStr in ADDR_LIST):
                continue
            # ADDR_LIST.append(addrStr)

            print(addr, "- Xin mo ket noi")
            thr = threading.Thread(target=_handle,args=(client, addr))
            thr.daemon = False# TRUE
            thr.start()
        except KeyboardInterrupt:
            print("Server closed")
            s.close()
            return

if __name__ == "__main__":
    socketServer()
