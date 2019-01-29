import os
import time
import datetime
import math
import numpy as np
import sys
sys.path.append("..")
from network import push_to_rpi_server

from PyQt5 import QtGui
from PyQt5 import QtCore
import sys
from PyQt5.Qt import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *


# Инициализируем важные константы
dir_write = "/media/pi/USB DISK1/five_metka_proceed/"
rect_radius_new = 5
number_of_led = 2
const_width_window = 30

with open("time_log.txt","w")as file:
    pass

with open("results_log.txt","w")as file1:
    pass

resently_used={"func":"","number_of_times":"","sum_time":""}


def time_of_functions(level_hierarchy):
    def inner_(func_):
        def wrapper(*args,**kwargs):
            global resently_used
            start =time.time()
            result=func_(*args,**kwargs)
            time_=time.time()-start
            if resently_used["func"]!=func_.__name__:
                with open("time_log.txt", "a+")as file:
                    file.write("{0}[{1}] Функция {2} обработана за {3} милисекунд\n".format("    "*level_hierarchy,resently_used["number_of_times"],resently_used["func"],resently_used["sum_time"]))
                resently_used["number_of_times"]=1
                resently_used["func"]=func_.__name__
                resently_used["sum_time"]=time_
            else:
                resently_used["number_of_times"]+=1
                resently_used["sum_time"]+=time_
            #print("Функция {0} обработана за {1} милисекунд\n".format(func_.__name__,time_))
            #print("Function {0} proceed in {1} milliseconds\n".format(func_.__name__,time_))
            return result
        return wrapper
    return inner_


def result_printer(func_):
    def wraper(*args,**kwargs):
        result_=func_(*args,**kwargs)
        with open("results_log.txt", "a+")as file1:
            file1.write("Функция: {0}\nс аргументами {1}\n вернула результат :{2}\n\n".format(func_.__name__,*args,result_))
        return result_
    return wraper



@time_of_functions(1)
def find_points_x0_y0(a1, a2, b1, b2):
    x = int((b2 - b1) / (a1 - a2))
    y = int(a1 * x + b1)
    return [x, y]

@time_of_functions(0)
def visualize(img, i, j):
    # cv2.line(img,(i[0],i[1]),(j[0],j[1]),(255,0,255),4)
    try:
        a = (i[1] - j[1]) / (i[0] - j[0])
    except:
        a = (i[1] - j[1]) / 0.0001

    b = i[1] - a * i[0]

    try:
        a_inv = -1 / a
    except:
        a_inv = 1e6
    b1_inv = i[1] - a_inv * i[0]
    b2_inv = j[1] - a_inv * j[0]

    # cv2.line(img,(int(-b1_inv/a_inv),0),(0,int(b1_inv)),(255,0,255),4)
    # cv2.line(img,(int(-b2_inv/a_inv),0),(0,int(b2_inv)),(255,0,255),4)
    # print(str(int(-b1_inv/a_inv))," 0"," 0",str(int(b1_inv)))

    p1 = find_points_x0_y0(a, a_inv, b + const_width_window, b1_inv)
    p2 = find_points_x0_y0(a, a_inv, b - const_width_window, b1_inv)
    p4 = find_points_x0_y0(a, a_inv, b + const_width_window, b2_inv)
    p3 = find_points_x0_y0(a, a_inv, b - const_width_window, b2_inv)
    # print(p1,p2,p3,p4)
    cv2.line(img, (p1[0], p1[1]), (p2[0], p2[1]), (255, 0, 255), 4)
    cv2.line(img, (p2[0], p2[1]), (p3[0], p3[1]), (255, 0, 255), 4)
    cv2.line(img, (p3[0], p3[1]), (p4[0], p4[1]), (255, 0, 255), 4)
    cv2.line(img, (p4[0], p4[1]), (p1[0], p1[1]), (255, 0, 255), 4)

    cv2.putText(img, "a=" + str(a), (p2[0], p2[1] + 100), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 255, 0), 4)
    return img

@time_of_functions(3)
def calc_distance(x, y):
    return int(math.sqrt((x[0] - y[0]) ** 2 + (x[1] - y[1]) ** 2))

@time_of_functions(0)
def calc_fit_points(i, j, different):
    try:
        a = (i[1] - j[1]) / (i[0] - j[0])
    except:
        a = (i[1] - j[1]) / 0.0001

    b = i[1] - a * i[0]

    try:
        a_inv = 1 / a
    except:
        a_inv = 1e6
    b1_inv = i[1] + a_inv * i[0]
    b2_inv = j[1] + a_inv * j[0]
    count = 0
    for i in different:
        s = i[1] - a * i[0] - b
        s1 = i[1] + a_inv * i[0]

        if s < const_width_window and s > -const_width_window and (s1 - b1_inv) * (s1 - b2_inv) <= 0:
            count += 1
    abs_alph = abs(a)
    # if abs_alph >0.7 and abs_alph<1.3:
    # return count
    # else:
    # return 0
    return count

@time_of_functions(1)
def calc_dist(different):
    result = []
    for i in different:
        row = []
        for j in different:
            row.append(calc_distance(i, j))
        result.append(row)
    return result


@time_of_functions(2)
def find_points_in_radius(arr_dist1, radius):
    index = 0
    for i in arr_dist1:
        arr_in_radius = []
        for j in range(len(i)):
            if i[j] <= radius:
                arr_in_radius.append(j)
        if len(arr_in_radius) >= 5:
            # return arr_in_radius
            radius1 = radius + 100
            arr_in_radius = []
            for j in range(len(i)):
                if i[j] <= radius1:
                    arr_in_radius.append(j)
            return [arr_in_radius, index]
        index += 1

    return [[], 0]

@time_of_functions(2)
def devide_by_2(arr):
    result_1 = []
    result_2 = []
    arr_x = []
    for i in arr:
        arr_x.append(i[0])

    avg_ = int(np.mean(arr_x))
    for i in arr:
        if i[0] > avg_:
            result_2.append(i)
        else:
            result_1.append(i)
    return [result_1, result_2]


@time_of_functions(2)
def find_center_1(arr):
    distances = calc_dist(arr)
    for r in range(1, 50):
        r1 = r * 10
        for i in range(len(distances)):
            if max(distances[i]) <= r1:
                return arr[i]
    return [0, 0]

@time_of_functions(5)
def find_p1(arr):
    # x>0,y>0
    result = []
    for i in arr:
        if i[0] > 0 and i[1] > 0:
            result.append(i)
    if len(result) > 1:
        return [max(result), 1]
    else:
        return [max(result), 0]

@time_of_functions(5)
def find_p2(arr):
    # x>0,y<0
    result = []
    for i in arr:
        if i[0] > 0 and i[1] < 0:
            result.append(i)
    if len(result) > 1:
        return [max(result), 1]
    else:
        return [max(result), 0]

@time_of_functions(5)
def find_p3(arr):
    # x<0,y>0
    result = []
    for i in arr:
        if i[0] < 0 and i[1] > 0:
            result.append(i)
    if len(result) > 1:
        return [min(result), 1]
    else:
        return [min(result), 0]

@time_of_functions(5)
def find_p4(arr):
    # x<0,y<0
    result = []
    for i in arr:
        if i[0] < 0 and i[1] < 0:
            result.append(i)
    if len(result) > 1:
        return [min(result), 1]
    else:
        return [min(result), 0]

@result_printer
@time_of_functions(2)
def find_points_2_shreres_2(arr_distances):
    coords = [[0, 52], [119, 0], [0, 175], [], [], [], [], [], [0, 300]]
    r1 = int(arr_distances[0][0])
    point1 = arr_distances[0][1]
    coo = coords[point1]
    x01 = coo[0]
    y01 = coo[1]
    r2 = arr_distances[1][0]
    point2 = arr_distances[1][1]
    coo = coords[point2]
    x02 = coo[0]
    y02 = coo[1]
    if x01 > x02:
        buf_x = x02
        buf_y = y02
        buf_r = r2
        x02 = x01
        y02 = y01
        r2 = r1
        x01 = buf_x
        y01 = buf_y
        r1 = buf_r
    phi = math.atan((y02 - y01) / (x02 - x01))
    transform_matrix = np.array([[math.cos(phi), math.sin(phi)], [-math.sin(phi), math.cos(phi)]])
    D = math.sqrt((x01 - x02) ** 2 + (y01 - y02) ** 2)
    if D == 0:
        return False
    x1 = (r1 ** 2 - r2 ** 2 + D ** 2) / (2 * D)
    y10 = math.sqrt(r1 ** 2 - x1 ** 2)
    y11 = -y10
    R1 = np.dot(np.array([x1, y10]), transform_matrix) + np.array([x01, y01])
    R2 = np.dot(np.array([x1, y11]), transform_matrix) + np.array([x01, y01])
    return [R1, R2]


@result_printer
@time_of_functions(2)
def find_points_2_shreres(arr_distances):
    coords = [[0, 52], [119, 0], [0, 175], [], [], [], [], [], [0, 300]]
    d1 = int(arr_distances[0][0])
    point1 = arr_distances[0][1]
    coo = coords[point1]
    c_x_1 = coo[0]
    c_y_1 = coo[1]
    d2 = arr_distances[1][0]
    point2 = arr_distances[1][1]
    coo = coords[point2]
    c_x_2 = coo[0]
    c_y_2 = coo[1]

    d = (math.sqrt((c_x_1 - c_x_2) ** 2 + (c_y_1 - c_y_2) ** 2))
    if d == 0:
        return False
    a = int((d1 ** 2 - d2 ** 2 + d ** 2) / (2 * d))
    # print(d1,d2,d,a)
    h = math.sqrt(d1 ** 2 - a ** 2)

    Pox = c_x_1 + (a / d) * (c_x_2 - c_x_1)
    Poy = c_y_1 + (a / d) * (c_y_2 - c_y_1)

    P3x = Pox - (c_y_2 - c_y_1) * (h / d)
    P3y = +Poy + (c_x_2 - c_x_1) * (h / d)

    P4x = Pox + (c_y_2 - c_y_1) * (h / d)
    P4y = Poy - (c_y_2 - c_y_1) * (h / d)

    return [[P3x, P3y], [P4x, P4y]]

@time_of_functions(1)
def calculate_x_y(arr_distances, x0, y0, num):
    coords = [[0, 52], [119, 0], [0, 175], [], [], [], [], [], [0, 300]]
    if len(arr_distances) == 0:
        return [x0, y0]
    if len(arr_distances) == 1:
        distance = arr_distances[0][0]
        point = arr_distances[0][1]
        coo = coords[point]
        c_x = coo[0]
        c_y = coo[1]
        lambd = (distance / math.sqrt((c_x - x0) ** 2 + (c_y - y0) ** 2))
        # print(lambd)
        #with open("result/" + str(num) + ".txt", "a+") as file:
            #file.write("lambd= " + str(lambd) + "\n")
            #file.write("x0= " + str(x0) + " " + str(c_x) + " " + str(y0) + " " + str(c_y) + "\n")
        return [(x0 * lambd) + (c_x * (1 - lambd)), (y0 * lambd) + (c_y * (1 - lambd))]
    if len(arr_distances) == 2:
        P_s = find_points_2_shreres_2(arr_distances)
        P3x = P_s[0][0]
        P3y = P_s[0][1]
        P4x = P_s[1][0]
        P4y = P_s[1][1]

        with open("result/" + str(num) + ".txt", "a+") as file:
            file.write("points= " + str(P3x) + " " + str(P3y) + " " + str(P4x) + " " + str(P4y) + "\n")

        if (P3x < 0) or (P3y < 0):
            return [P4x, P4y]
        if (P4x < 0) or (P4y < 0):
            return [P3x, P3y]

        if (P3x - x0) ** 2 + (P3y - y0) ** 2 < (P4x - x0) ** 2 + (P4y - y0) ** 2:
            return [P3x, P3y]
        else:
            return [P4x, P4y]
    if len(arr_distances) == 3:
        P_s = find_points_2_shreres([arr_distances[0], arr_distances[1]])
        P3x1 = P_s[0][0]
        P3y1 = P_s[0][1]
        P4x1 = P_s[1][0]
        P4y1 = P_s[1][1]

        P_s = find_points_2_shreres([arr_distances[0], arr_distances[2]])
        P3x2 = P_s[0][0]
        P3y2 = P_s[0][1]
        P4x2 = P_s[1][0]
        P4y2 = P_s[1][1]

        A1 = P3y1 - P4y1  # P3y1,P4y1
        B1 = P4x1 - P3x1  # P4x1,P3x1
        C1 = P3x1 * P4y1 - P4x1 * P3y1  # P3x1,P4y1,P4x1,P3y1
        A2 = P3y2 - P4y2  # P3y2,P4y2
        B2 = P4x2 - P3x2  # P4x2,P3x2
        C2 = P3x2 * P4y2 - P4x2 * P3y2  # P3x2,P4y2,P4x2,P3y2
        # решаем систему двух уравнений
        if B1 * A2 - B2 * A1 != 0:
            y = (C2 * A1 - C1 * A2) / (B1 * A2 - B2 * A1)
            x = (-C1 - B1 * y) / A1

        # решаем систему двух уравнений
        if B1 * A2 - B2 * A1 == 0:
            y = (C2 * A1 - C1 * A2) / (0.000001)
            x = (-C1 - B1 * y) / A1

        return [x, y]

    if len(arr_distances) == 4:
        pass


x0 = 100
y0 = 300

index = 0

@time_of_functions(0)
def get_position(num,x0,y0):
    print("yess")

    different=push_to_rpi_server.read_and_push()
    count_ = 0
    for i in different:
        count_ += 1
    index__ = 1
    arr_groups = []
    arr_dist = calc_dist(different)

    indexes_was = []

    for r in range(1, 30):
        points = find_points_in_radius(arr_dist, r * 10)
        arr_coords_detected = []
        for i in points[0]:
            arr_coords_detected.append(different[i])
            indexes_was.append(i)
        arr_coords_detected = [arr_coords_detected, different[points[1]]]
        arr_groups.append(arr_coords_detected)

        for i in range(len(points[0])):
            for j in range(len(arr_dist)):
                for k in range(len(arr_dist)):
                    arr_dist[points[0][i]][j] = 10000
                    arr_dist[k][points[0][i]] = 10000
    arr_other = []

    for i in range(len(different)):
        if i not in indexes_was:
            arr_other.append(different[i])

    if len(arr_other) >= 10:
        arrs_other = devide_by_2(arr_other)
        first = arrs_other[0]
        second = arrs_other[1]
        center_1 = find_center_1(first)
        center_2 = find_center_1(second)
        arr_groups.append([first, center_1])
        arr_groups.append([second, center_2])
    else:
        center = find_center_1(arr_other)
        arr_other = [arr_other, center]
        arr_groups.append(arr_other)

    arr_dist = []
    for different2 in arr_groups:
        center = different2[1]
        center_x = center[0]
        center_y = center[1]
        different1 = different2[0]
        if len(different1) > 0:
            if not isinstance(different1[0], int) and different1[0]:
                for i in range(len(different1)):
                    different1[i][0] = different1[i][0] - center_x
                    different1[i][1] = different1[i][1] - center_y
                try:
                    p1 = find_p1(different1)
                    p2 = find_p2(different1)
                    p3 = find_p3(different1)
                    p4 = find_p4(different1)

                    mark = 8 * p1[1] + 4 * p2[1] + 2 * p3[1] + p4[1]
                    size = int(math.sqrt((p1[0][0] + abs(p4[0][0])) ** 2 + (p1[0][1] + abs(p4[0][1])) ** 2)) + int(
                        math.sqrt((p2[0][0] + abs(p3[0][0])) ** 2 + (abs(p2[0][1]) + p3[0][1]) ** 2))
                    #distance = 108800 / size # BV7000
                    distance = 50000 / size # rpi3 camera
                    arr_dist.append([distance, mark])
                except:
                    pass
    arr_dist_0 = []
    was = []
    for i in arr_dist:
        if i[1] in [0, 1, 8]:
            if i[1] not in was:
                arr_dist_0.append(i)
                was.append(i[1])
    arr_dist = arr_dist_0
    result = calculate_x_y(arr_dist, x0, y0, num)
    x1 = result[0]
    y1 = result[1]
    print("result  ",result)
    x0 = x1
    y0 = y1
    return [arr_dist, x0, y0]


class Window(QMainWindow):
    def __init__(self):
        super().__init__()

        self.title="Pyqt5 Qgraphics view"
        self.top=100
        self.left=100
        self.width=1000
        self.height=1000

        self.prev=[]

        self.readThread=ReadThread()
        self.readThread.start()

        self.readThread.readthread.connect(self.change_state)



        self.initWindow()


    def initWindow(self):
        self.minutes=5
        self.coords = [[0, 52], [119, 0], [0, 175], [], [], [], [], [], [0, 300]]
        scene=QGraphicsScene()
        #pic = QtGui.QPixmap("triangle.png")
        #scene.addItem(QtGui.QGraphicsPixmapItem(pic))
        scene.addPixmap(QtGui.QPixmap("my_room.png"))
        redBrush=QBrush(Qt.red)
        blueBrush = QBrush(Qt.blue)
        blackPen=QPen(Qt.black)
        redPen = QPen(Qt.red)
        green_pen=QPen(Qt.green)
        blackPen.setWidth(7)

        for i in range(1,6):
            scene.addLine(i*100, 0, i*100, 600, green_pen)
            scene.addLine(0,i * 100, 600,i * 100, green_pen)
        scene.addLine(0, 0, 0, 500, redPen)
        scene.addLine(0, 500, 500, 500, redPen)
        scene.addLine(500, 0, 500, 500, redPen)
        scene.addLine(0, 0, 500, 0, redPen)
        for i in [0,1,2,8]:
            scene.addEllipse(500-self.coords[i][1], self.coords[i][0], 10, 10, blackPen, redBrush)



        view=QGraphicsView(scene,self)
        view.setGeometry(0,0,500,500)

        #################################
        self.scene1 = QGraphicsScene()
        self.scene1.addPixmap(QtGui.QPixmap("my_room.png"))
        for i in range(1,10):
            self.scene1.addLine(i*100, 0, i*100, 1000, green_pen)
            self.scene1.addLine(0,i * 100, 1000,i * 100, green_pen)
            self.scene1.addLine(0, 0, 0, 500, redPen)
            self.scene1.addLine(0, 500, 500, 500, redPen)
            self.scene1.addLine(500, 0, 500, 500, redPen)
            self.scene1.addLine(0, 0, 500, 0, redPen)

        for i in [0,1,2,8]:
            self.scene1.addEllipse(500-self.coords[i][1], self.coords[i][0], 10, 10, blackPen, redBrush)

        view1 = QGraphicsView(self.scene1, self)
        view1.setGeometry(501, 0, 500, 500)
        ###################################
        scene2 = QGraphicsScene()

        for i in range(self.minutes*60):
            scene2.addLine(i*20, 0, i*20, 150, green_pen)

        for i in range(self.minutes):
            scene2.addLine(i*1200, 0, i*1200, 150, redPen)
        view2 = QGraphicsView(scene2, self)
        view2.setGeometry(0, 550, 1000, 150)
        ######################################

        self.setWindowTitle(self.title)
        self.setGeometry(self.top,self.left,self.width,self.height)

    def change_state(self,arr_all):
        try:
            for i in self.prev:
                self.scene1.removeItem(i)

            redBrush = QBrush(Qt.red)
            transperentBrush=QBrush(Qt.transparent)
            blueBrush = QBrush(Qt.blue)
            blackPen = QPen(Qt.black)
            redPen = QPen(Qt.red)
            green_pen = QPen(Qt.green)


            arr=arr_all[0]
            x1=arr_all[1]
            y1=arr_all[2]
            x0=arr_all[3]
            y0=arr_all[4]
            coords = [[0, 52], [119, 0], [0, 175], [], [], [], [], [], [0, 300]]
            for i in arr:
                d1 = int(i[0])
                point1 = i[1]
                coo = coords[point1]
                c_x_1 = coo[1]
                c_y_1 = coo[0]
                delt=-d1
                #rad1=d1*2
                x_curr=500-c_x_1+delt
                y_curr =c_y_1 + delt
                self.prev.append(self.scene1.addEllipse(x_curr,y_curr, d1*2, d1*2, blackPen, transperentBrush))
                self.prev.append(self.scene1.addEllipse(c_x_1, c_y_1, 5,5, blackPen, transperentBrush))
            self.prev.append(self.scene1.addEllipse(500-y1,x1,10,10,blackPen, redBrush))
            self.prev.append(self.scene1.addEllipse(500-y0,x0, 10, 10, blackPen, blueBrush))
            (self.scene1.addLine(500 - y1 + 5, x1 + 5, 500 - y0 + 5, x0 + 5, redPen))

        except:
            (type, value, traceback) = sys.exc_info()
            sys.excepthook(type, value, traceback)



# поток для получения координат через TCP socket
class ReadThread(QtCore.QThread):
    readthread = pyqtSignal(list)
    def __init__(self,parent=None):
        super(ReadThread,self).__init__(parent)

    def run (self):
        self.x0 = 100
        self.y0 = 300
        while True:
            t1 = time.time()
            num="00"
            try:
                positions=get_position(num,self.x0,self.y0)
            except:
                (type,value,traceback)=sys.exc_info()
                sys.excepthook(type,value,traceback)
                break
            positions.append(self.x0)
            positions.append(self.y0)
            self.x0 = positions[1]
            self.y0 = positions[2]
            print(positions)
            time.sleep(0.1)
            self.readthread.emit(positions)

x0 = 100
y0 = 300

# бесконечный цикл отрисовки окна
App=QApplication(sys.argv)
window=Window()
window.show()
sys.exit(App.exec())


