#Long
import socket
import threading
import os

HOST = "localhost"
PORT = 8080
PATH = "web_src"  # Thư mục lưu các file của web
FORMAT = "utf-8"
SIZE = 1024
#Minh
address_login = []  # lưu các client đã đăng nhập thành công

#Nhật
def readFile(srcfile):
    file = open(srcfile, 'rb')
    data = file.read()
    file.close()
    return (data)


def ReadRequest(Client, addr):  # Hàm đọc Request từ Client
    dataRequest = ""
    while True:
        if "GET" in dataRequest and "\r\n\r\n" in dataRequest:
           break
        if "POST" in dataRequest and "remember=on" in dataRequest:
           break
        data = Client.recv(SIZE).decode(FORMAT)
        if data == "": 
            return transferRequest("")
        dataRequest = dataRequest + data
    print("Request from "+str(addr)+":\n"+dataRequest) #Long
    return (transferRequest(dataRequest))


class transferRequest:  # Tạo class chứa thông tin Request từ Client.
    def __init__(self, request):
        # Phân tách Request theo từng dòng.
        requestArray = request.split("\r\n")
        if request == "":
            self.empty = True
        else:
            self.empty = False
            self.method = requestArray[0].split()[0]
            self.path = requestArray[0].split()[1]
            self.connection = requestArray[2].split()[1]
            if(self.path == '/'):
                self.path += "index.html"    
            if self.method == "POST":
                self.uname = request.split("\r\n\r\n")[1].split("&")[0].split("=")[1]
                self.psw = request.split("\r\n\r\n")[1].split("&")[1].split("=")[1]

def getHeader(typeRequest: transferRequest, sizeFile, address):
    data = ""
    data += "HTTP/1.1 200 OK\r\n" + "Content-Type: "
    buff = typeRequest.path.split('.')[1]
    if buff == "html" or buff == "htm":
        data += "text"
        buff = "html"  # chuẩn hóa về html
    elif buff == "txt":
        data += "text"
        buff = "plain"  # chuyển về tag chuẩn của txt
    elif buff == "jpg" or buff == "jpeg":
        data += "image"
        buff = "jpeg"  # chuẩn hóa tất cả về jpeg
    elif buff == "gif" or buff == "png":
        data += "image"
    elif buff == "css":
        data += "text"
    else:
        data += "application"
        buff = "octet-stream"
    data += "/" + buff + "\r\n"
    data += "Content-Length: " + str(sizeFile) + "\r\n"
    data += "Connection: "+typeRequest.connection+"\r\n"
    data += "\r\n"
    return (data)

# Nhật
def handleClient(client, address, address_login):
    print("Connected to "+str(address))
    # liên tục đọc request cho đến khi client đóng
    
    # Long
    while True:
        try: 
            
            #Nhật
            # Đọc Request từ Client.
            dataRequest = ReadRequest(client, address)
            
            #Long
            if dataRequest.empty:
                print(str(address)+": return 0 and close!") 
                client.close()
                return
                
            # Nhật 
            else:  # Phần xử lí yêu cầu nếu như không có bất kì lỗi nào xảy ra. Nếu như dataRequest không có lỗi.
                if dataRequest.method == "GET":  # Nếu method là GET.
                    
                    # Văn Minh
                    try:  # Tiến hành đọc file body, xác định header, kích thước file body và gửi cho Client.
                        # không nằm trong danh sách đăng nhập khi cố tình truy cập vào image.html    
                        if dataRequest.path == "/images.html" and address[0] not in address_login:  # ko nằm trong danh sách đăng nhập
                            print("\n"+str(address)+" trying to access the private area without Login\n") # Long
                            dataRequest.path = "/index.html"    
                        
                        # Nhật
                        # Đọc thông tin phần body.
                        dataFile = readFile(PATH + dataRequest.path)
                        # Xác định kích thước phần body phía trên.
                        sizeBody = os.path.getsize(PATH + dataRequest.path)
                        # Chèn phần Header phù hợp với phần body.
                        dataFile = getHeader(dataRequest, sizeBody, address).encode(FORMAT) + dataFile
                        client.sendall(dataFile)
                        continue # Long
                    
                    # Văn Minh
                    except:  # request để truy xuất page không thấy
                        print("Send 404 to "+str(address)+" for not found "+dataRequest.path) # Long | có sửa thêm hiện file
                        data = "HTTP/1.1 404 Not Found\r\n"
                        data += "Content-Type: text/html\r\n"
                        data += "Connection: close\r\n"
                        data += "\r\n" + "<!DOCTYPE html><html><head>"
                        data += "<title> 404 Not Found </title></head><body>"
                        data += "<p> The requested file cannot be found. </p>"
                        data += "</body></html>"
                        client.sendall(data.encode(FORMAT))
                        continue # Long
                
                # Văn Minh     
                elif dataRequest.method == "POST":  # Xét trường hợp là POST method.
                    # Kiểm tra uname và psw, sau đó tiến hành đọc file body, xác định header và kích thước rồi gửi cho Client.
                    if dataRequest.uname == "admin" and dataRequest.psw == "123456":
                        address_login.append(address[0])
                        dataFile = readFile(PATH + dataRequest.path)
                        sizeBody = os.path.getsize(PATH + dataRequest.path)
                        dataFile = getHeader(dataRequest, sizeBody, address).encode(FORMAT) + dataFile
                        client.sendall(dataFile)
                        continue # Long
                    else:  # đăng nhập sai
                        print("Send 401 to "+str(address)) #Long
                        data = "HTTP/1.1 401 Unauthorized\r\n"
                        data += "Content-Type: text/html\r\n"
                        data += "Connection: close\r\n"
                        data += "\r\n" + "<!DOCTYPE html>"
                        data += "<h1>401 Unauthorized</h1>"
                        data += "<p>This is a private area.</p>"
                        client.sendall(data.encode(FORMAT))
                        continue #Long
                break
        # Long
        except: # đóng khi gặp lỗi hoặc ngắt kết nối, hay timeout
            print(str(address)+": ST went wrong! This connection will be closed\n")
            client.close()
            return
# Long
try:
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen()
    print(f"*Server running on http://{HOST}:{PORT}")
    while True:
        client, address = server.accept()
        thr = threading.Thread(target=handleClient, args=(client, address, address_login))
        thr.start()
except socket.error as error:
    print("Error: ", error)
