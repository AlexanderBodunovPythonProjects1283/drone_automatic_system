import socket
import time
import os

#dir_read_1="/home/pi/share/"
dir_read_1="/mnt/share/"

sock=socket.socket()

sock.bind(("",12))
sock.listen(1)

conn,addr=sock.accept()

print("connected")
while True:
    for i in os.listdir(dir_read_1):
        if i=="report.txt":
            with open (dir_read_1+"report.txt","r") as file:
                msg=file.read()
            conn.send(b"00000000"+b"1"+ msg.encode("utf-8")+b"11111111")
            #conn.send(b"00000000")    
    time.sleep(0.3)
    #print(data)
    print(time.time())
    print(msg)
    print("\n")
    
con.close()
    
