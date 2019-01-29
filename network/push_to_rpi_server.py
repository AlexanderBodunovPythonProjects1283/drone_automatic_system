import os
import time
import shutil
import socket
import time

#path=os.chdir(r'Z:\\')
dir="Z:\\"

count_=0
#os.remove()
print(os.listdir(dir))
def read_and_push_1():
    result=[]
    for i in os.listdir(dir):
        if i=="report.txt":

            #for j in os.listdir(dir):
                #os.remove(dir + str(j))
            with open(dir+i,"r") as file:
                for string_ in file.read().split("\n")[:-1]:
                    x_y=string_.split(" ")
                    print("x_y",x_y)
                    try:
                        x=int(x_y[0])
                        y=int(x_y[1])
                        result.append([x,y])
                    except:
                        pass
            #shutil.copy("command.txt",dir+"command.txt")
            print (result)
            if len(result)==0:
                result=[[0,0]]
            return result



conn = socket.socket()

conn.connect(("192.168.1.105", 12))

def read_and_push():
                result = []
                data = conn.recv(1024).decode("utf-8")
                print("recieved")
                if data[0:8] == "00000000" and data[-8:] == "11111111":
                    sender = int(data[8])
                    msg = data[9:-9]
                    print(sender, msg)
                else:
                    print(data[0:8], data[-8:])
                    return [[0, 0]]
                for string_ in msg.split("\n"):
                    x_y = string_.split(" ")
                    print("x_y", x_y)
                    try:
                        x = int(x_y[0])
                        y = int(x_y[1])
                        result.append([x, y])
                    except:
                        pass
                print(result)
                if len(result) == 0:
                    result = [[0, 0]]
                return result


#while True:
    #time.sleep(1)
    #read_and_push()

print("yes")
#conn.close()