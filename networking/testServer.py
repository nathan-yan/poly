
import socket

 

localIP     = "127.0.0.1"

localPort   = 20001

bufferSize  = 1024

 

msgFromServer       = "Hello UDP Client"

bytesToSend         = str.encode(msgFromServer)

 

# Create a datagram socket

UDPServerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

 

# Bind to address and ip

UDPServerSocket.bind((localIP, localPort))

 

print("UDP server up and listening")

 
UDPServerSocket.setblocking(False)

# Listen for incoming datagrams

while(True):
    a = input(">>>")
    if (str(a) == 'q'):
        break;
    
    try:
        bytesAddressPair = UDPServerSocket.recvfrom(bufferSize)

        message = bytesAddressPair[0]

        address = bytesAddressPair[1]

        clientMsg = "Message from Client:{}".format(message)
        clientIP  = "Client IP Address:{}".format(address)
        
        print(clientMsg)
        print(clientIP)

    

        # Sending a reply to client

        UDPServerSocket.sendto(bytesToSend, address)
    except BlockingIOError:
        print('no message recieved')
    except ConnectionResetError:
        print("client dropped")