import socket
import time
import os

#dir_read_1="/home/pi/share/"

sock=socket.socket()
sock.bind(("",10))
sock.listen(1)

conn,addr=sock.accept()

print("connected")
while True:
    conn.send(b"01010101") 
    time.sleep(0.3)
    #print(data)
    print(time.time())
    print(msg)
    print("\n")
    
con.close()
