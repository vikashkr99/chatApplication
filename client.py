import socket,sys,base64,subprocess,time

def __endConversation__():
    message = 'BYE'
    print('\033[31m[!] Connection closed\033[00m')
    connection.sendall(message.encode())
    connection.close()
    exit()

def __conversationEnded__():
    __clearConsole__(1)
    print('\033[31m[!] Connection Closed By The Server.\033[00m')
    connection.close()
    exit()

def __recvFile__(file_name, file_size):
    print('[!] Connection is sendign a file...')
    print(f'[!] File name: {file_name}')
    print(f'[!] File size: {file_size}')
    getFile = input('Accept file (Y?N) ?: ')
    if getFile.lower() == "y":
        message = '1'
        connection.sendall(message.encode())
        __clearConsole__(1)
        print('[!] Downloading File...')
        file_parts = int(file_size)/1024
        file=''
        for j in range(0,int(file_parts)):
            file+=connection.recv(1024).decode()
        file+=connection.recv(1024).decode()
        write_file = open(file_name, 'wb')
        write_file.write(base64.b64decode(file))
        __clearConsole__(4)
        print('[!] File received')
        return
    elif getFile.lower() == 'n':
        message = '0'
        connection.sendall(message.encode())
        __clearConsole__(1)
        __sendMessage__()
        return
    
def __sendFile__():
    message = 'SF'
    file_name = input('Enter file name: ')
    whoAmI = '/home/'
    whoAmI+= subprocess.check_output(['whoami'], text=True)
    find_file = subprocess.check_output(['find', whoAmI.strip(), '-type', 'f', '-name', file_name], text=True)
    fileList = find_file.strip().split('\n')
    if len(find_file) == 0:
        print('\033[31m[!] File not found\033[00m')
    else:
        if len(fileList) > 1:
            num = 0
            for file in fileList:
                num+=1
                print(f'[{num}] : {file}')
            selectedFile = int(input('Select File Index Number : '))
            find_file = fileList[selectedFile-1]
            print(find_file)     
        else:
            find_file = fileList[0]
        file = open(find_file.strip(), 'rb')
        file = file.read()
        b64_encoded = base64.b64encode(file)
        b64_string = b64_encoded.decode('ascii')
        file_length = str(len(b64_string))
        connection.send(message.encode())
        time.sleep(0.5)
        connection.send(file_name.encode())
        time.sleep(0.5)
        connection.send(file_length.encode())
        reply = connection.recv(1024).decode()
        if reply == '1':
            print('[!] Sending File...')
            while len(b64_string) > 1024:
                file_part = b64_string[:1024]
                connection.send(file_part.encode())
                b64_string = b64_string[1024:]
                time.sleep(0.1)
            connection.send(b64_string.encode())
            __clearConsole__(3)
            print('[!] File Sent.')
            return
        elif reply == '0':
            print('[!] File Transfer Denied..')
            return
    
def __sendMessage__():
    message = ''
    print('\033[32m',end='')
    message = input('You: ')
    print('\033[00m',end='')
    if message == "BYE":
        __endConversation__()
    elif message == "SF":
        __sendFile__()
    else:
        connection.sendall(message.encode())
        print('\033[32;5;51mWait for reply.....\033[00m')

def __getMessage__():
    reply = connection.recv(1024).decode()
    if reply == "BYE":
        __conversationEnded__()
    elif reply == "SF":
        file_name = connection.recv(1024).decode()
        file_size = connection.recv(1024).decode()
        __recvFile__(file_name, file_size)
    else:
        __clearConsole__(1)
        print(f'Connection: {reply}')

def __clearConsole__(nLines):
    sys.stdout.write("\033["+str(nLines)+"F")
    sys.stdout.write("\033[J")

connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
CONNECTIONPORT = int(input('[!] Connection port number: '))
connection.connect(('0.tcp.in.ngrok.io', CONNECTIONPORT))

__clearConsole__(1)
print('\033[32m[+] Connection Established\033[00m')
print('\033[32;5;51mWaiting for message.....\033[00m')

while True:
    __getMessage__()
    __sendMessage__()
    