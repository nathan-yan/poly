
import socket

 

msgFromClient       = "Hello UDP Server"

bytesToSend         = str.encode(msgFromClient)

serverAddressPort   = ("127.0.0.1", 20001)

bufferSize          = 1024

 

# Create a UDP socket at client side

UDPClientSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
UDPClientSocket2 = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

 

# Send to server using created UDP socket

UDPClientSocket.sendto(bytesToSend, serverAddressPort)
UDPClientSocket2.sendto(bytesToSend, serverAddressPort)
print('sent message1')
UDPClientSocket.sendto(bytesToSend, serverAddressPort)
UDPClientSocket2.sendto(bytesToSend, serverAddressPort)
print('sent message2')
 

msgFromServer = UDPClientSocket.recvfrom(bufferSize)

print(msg)

msg = "Message from Server {}".format(msgFromServer[0])


msgFromServer = UDPClientSocket2.recvfrom(bufferSize)

 

msg = "Message from Server {}".format(msgFromServer[0])

print(msg)