import os
import paramiko
import socket

def check_sharing_on_nfs(host,user,password,port,host_client,user_client,password_client,port_client,input,output):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    # Подключение
    client.connect(hostname=host, username=user, password=password, port=port)
    stdin, stdout, stderr = client.exec_command('touch '+input+'/file_test')
    client.close()
    ###########################################
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    # Подключение
    client.connect(hostname=host_client, username=user_client, password=password_client, port=port_client)
    stdin, stdout, stderr = client.exec_command('ls -l '+output)
    # Читаем результат
    data = stdout.read()  # +stderr.read()
    print(data)
    client.close()
    ###########################################
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    # Подключение
    client.connect(hostname=host, username=user, password=password, port=port)
    stdin, stdout, stderr = client.exec_command('rm ' + input + '/file_test')
    client.close()


    if data.find(b"file_test"):
        print("соединение есть")
        return True
    else:
        print(":( нет соединения")
        return False

def network_check():
    result={"is_network":[],
            "is_socket":[],
            "is_NFS":[]}
    list_devices=[["router","192.168.1.101"],
          ["rpi_server","192.168.1.105"],
          ["rpi1_client","192.168.1.106"]
          ]

    for i in list_devices:
        response=os.system("ping -n 1 "+i[1])

        result["is_network"].append([response==0,response==0])
        #if response==0:
            #print ("{0} is up :)".format(i[0]))
        #else:
            #print ("{0} is down :(".format(i[0]))

    with open ("hosts_passwords.txt") as file:
        content=file.read().split("\n\n")
    server = content[0]
    server_arr=server.split("\n")
    host = server_arr[0].split("=")[1]
    user = server_arr[1].split("=")[1]
    password = server_arr[2].split("=")[1]
    port = server_arr[3].split("=")[1]
    inputs=[i for i in  server_arr[4].split("=")[1].split(",")]
    outputs = [i for i in  server_arr[5].split("=")[1].split(",")]

    for i in range(len(content[1:])):
        client_info_arr=content[i].split("\n")
        host_client = client_info_arr[0].split("=")[1]
        user_client = client_info_arr[1].split("=")[1]
        password_client = client_info_arr[2].split("=")[1]
        port_client = client_info_arr[3].split("=")[1]
        input_client = server_arr[4].split("=")[1]
        output_client =server_arr[5].split("=")[1]
        up=check_sharing_on_nfs(host, user, password, port, host_client, user_client, password_client,port_client, inputs[i],output_client)
        down=check_sharing_on_nfs(host_client, user_client, password_client,port_client,host, user, password, port, input_client,outputs[i])
        result["is_NFS"].append([up,down])
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    # Подключение
    client.connect(hostname=host, username=user, password=password, port=port)
    client.exec_command('sudo python3 /home/pi/object_detection/test_socket.py')
    client.close()

    conn=socket.socket()
    conn.connect(("192.168.1.105",10))

    count_=0
    while True:
        count_+=1
        print(count_)
        data = conn.recv(1024).decode("utf-8")
        print(count_)
        if data.startswith("010101"):
            #print("Успех")
            result["is_socket"].append([True,True])
            print(data)
            break
        if count_==10:
            result["is_socket"].append([False, False])
            break
    print ("Конец функции проверки сети")
    return result





#print (network_check())


