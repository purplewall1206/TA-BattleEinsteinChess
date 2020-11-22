import pygame
import os
import sys
import time
import random
import copy
import socket
import logging
from pygame.locals import *
from sys import exit
from time import sleep
import logging
import threading
from threading import Lock
from tkinter import ttk,messagebox, Tk, VERTICAL, Label, Entry, END, DISABLED, Button
#=====================不可修改 全局变量=========================================
WINDOWSIZE = (450, 450)  # 游戏窗口大小
LINECOLOR = (0, 0, 0)  # 棋盘线的颜色
TEXTCOLOR = (0, 0, 0)  # 标题文本颜色
BLACKGROUND = (255, 255, 255)  # 游戏背景颜色
BLACK = (0, 0, 0)
BLUE = (0, 191, 255)
YELLOW = (255, 255, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
WHITE = (255, 255, 255)
SIZE = (50, 50)  # 棋子大小
AYSTSIZE = (240, 240)  # 爱因斯坦背景头像图片大小
POSAYST = (365, 0)  # 爱因斯坦头像位置
STEP = 60  # 步长：棋子走一步移动的距离
TEXTSIZE = 30  # 标题文字大小
TIPSIZE = 15  # 提示文字大小
COUNT = -1  # 记录当前回合
START = 65  # 棋盘左上角起始点（70，70）
REDWIN = 1  # 代表RED方赢
BLUEWIN = 2  # 代表玩家BLUE方赢
LEFT = 'left'
RIGHT = 'right'
UP = 'up'
DOWN = 'down'
LEFTUP = 'leftup'
RIGHTDOWN = 'rightdown'
RESULT = [0, 0]  # 记录比赛结果
WINSIZE = (400, 90)  # 显示比赛结果窗口大小
INFTY = 10000
#===============================================================

#======加锁修改全局变量 负责pygame tkinter通信 最好不要动==============
SLEEPTIME = 0
FUNCTION = 0   # -1初始化设置playernum  0悬空等待  1每人运行3次   2
playernum = 0
currentnum = 0
start = 0
#================================================================


#====================== 不加锁全局变量，用于保存用户信息，需要刷新================
clients = list()
finalroundclients = list()
FINALROUND = 8
NEXTSTAGE = []
#=================================================================



#=====================================日志记录==================================
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(name)s- %(levelname)s - %(message)s', filename='battle.log')
logger = logging.getLogger()
ch = logging.StreamHandler() #日志输出到屏幕控制台
ch.setLevel(logging.INFO) #设置日志等级
formatter = logging.Formatter('%(asctime)s %(name)s- %(levelname)s - %(message)s') #定义日志输出格式
ch.setFormatter(formatter) #选择一个格式
logger.addHandler(ch) #增加指定的handler
#==============================================================================


class Status(object):
    def __init__(self):
        self.map = None
        self.value = None
        self.pawn = None
        self.pro = None
        self.parent = None
        self.pPawn = None
        self.pMove = None
        self.pDice = None
        self.cPawn = None
        self.cPawnSecond = None
        self.cPM = [[],[],[],[],[],[]]
        self.cPMSecond = [[],[],[],[],[],[]]
    def print(self):
        print(self.cPM)

class App(threading.Thread):
    entryIDs = []
    entryWins= []
    height = 40
    width = 3
    def __init__(self):
        global refreshQ
        threading.Thread.__init__(self)
        self.start()

    def callback(self):
        self.root.quit()

    #实际上是battle 2
    def startgame(self):
        global playernum
        global start
        global FUNCTION
        global SLEEPTIME
        if FUNCTION != 0 or playernum == 0:
            messagebox.showinfo('BATTLE','OTHER PROCESS IS RUNNING')
            return 'battle'
        lock = Lock()
        lock.acquire()
        FUNCTION = 2
        SLEEPTIME = 0

        lock.release()
        messagebox.showinfo('BATTLE', 'BATTLE START')

    # 初始化-1
    def setup(self):
        global playernum
        global FUNCTION
        if playernum == 0:
            lock = Lock()
            lock.acquire()
            FUNCTION = -1
            playernum = int(self.numsEntry.get())
            lock.release()
            messagebox.showinfo('SETUP', 'PLAYERNUMS '+str(playernum))
        else:
            messagebox.showinfo('SETUP', 'PLAYER NUMBER HAS BEEN SET')

    # 检查 1
    def openlog(self):
        global FUNCTION
        global SLEEPTIME
        global playernum
        if FUNCTION != 0 or playernum == 0:
            messagebox.showinfo('JUDGE', 'OTHER PROCESS IS RUNNING')
            return 'JUDGE'

        lock = Lock()
        lock.acquire()
        FUNCTION = 1
        SLEEPTIME = 0
        lock.release()

        # 实际负责判题
        messagebox.showinfo('JUDGE', 'EVERYONE PLAYS 3 TIMES')

    # 淘汰赛 3
    def knockedout(self):
        global FUNCTION
        global SLEEPTIME
        global playernum
        global currentnum
        global clients
        global finalroundclients
        if FUNCTION != 0 or playernum == 0:
            messagebox.showinfo('KNOCKEDOUT','OTHER PROCESS IS RUNNING')
            return 'knocked out'
        messagebox.showinfo('KNOCKEDOUT', 'KNOCKED OUT BATTLE')
        # 决赛人数，最多八强，故准备4种颜色
        global FINALROUND
        FINALROUNDCOLOR = ['red','blue','yellow','green']

        rank = clients.copy()
        # 排序选出前八
        if currentnum == playernum:
            for i in range(playernum - 1):
                for j in range(playernum - i - 1):
                    if (rank[j].wins < rank[j + 1].wins):
                        rank[j], rank[j + 1] = rank[j + 1], rank[j]
        # 清除表格
        for i in range(currentnum):
            self.entryIDs[i].delete('0', END)
            self.entryWins[i].delete('0', END)
        # 添加颜色,重新生成最终用户列表
        finalroundclients.clear()
        for i in range(FINALROUND):
            # self.entryIDs[i].delete('0', END)
            finalroundclients.append(rank[i])
            self.entryIDs[i].insert(END, rank[i].ID)
            # self.entryWins[i].delete('0', END)
            self.entryWins[i].insert(END, 'BATTLE GROUP '+str(i%4))
            self.entryIDs[i].config({"background": FINALROUNDCOLOR[i%4]})
            self.entryWins[i].config({"background": FINALROUNDCOLOR[i%4]})
        lock = Lock()
        lock.acquire()
        FUNCTION = 3
        SLEEPTIME = 1
        lock.release()

    # 退出
    def quit(self):
        global FUNCTION
        global SLEEPTIME
        if FUNCTION != 0:
            messagebox.showinfo('QUIT','OTHER PROCESS IS RUNNING')
            return 'quit'
        lock = Lock()
        lock.acquire()
        FUNCTION = 4
        SLEEPTIME = 1
        lock.release()
        #self.root.quit()

    # 根据排名刷新
    def refresh(self):
        global playernum
        global currentnum
        global clients
        rank = clients.copy()
        if currentnum == playernum:
            for i in range(playernum-1):
                for j in range(playernum-i-1):
                    if (rank[j].wins < rank[j+1].wins):
                        rank[j],rank[j+1]=rank[j+1],rank[j]
        for i in range(currentnum):
            self.entryIDs[i].delete('0', END)
            self.entryIDs[i].insert(END, rank[i].ID)
            self.entryWins[i].delete('0', END)
            self.entryWins[i].insert(END, rank[i].wins)

    def finalRefresh0(self, deleteitem, message):
        global playernum
        global currentnum
        global clients
        global finalroundclients
        # self.entryIDs[deleteitem].delete('0', END)
        self.entryWins[deleteitem].delete('0', END)
        self.entryWins[deleteitem].insert(END, str(message))
        self.entryIDs[deleteitem].config({"background": "White"})
        self.entryWins[deleteitem].config({"background": "White"})

    # 重置界面
    def finalRefresh1(self):
        global playernum
        global currentnum
        global clients
        global FINALROUND
        global finalroundclients
        global NEXTSTAGE

        for i in range(playernum):
            self.entryIDs[i].delete('0', END)
            self.entryWins[i].delete('0', END)
            self.entryIDs[i].config({"background": "White"})
            self.entryWins[i].config({"background": "White"})
        # self.entryWins[NEXTSTAGE[0]].insert(END, '冠军')
        # self.entryWins[NEXTSTAGE[1]].insert(END, '亚军')
        # self.entryWins[NEXTSTAGE[2]].insert(END, '季军')
        # self.entryWins[NEXTSTAGE[3]].insert(END, '第四名')


    def run(self):
        self.root = Tk()
        self.mainpane = ttk.PanedWindow(self.root, orient=VERTICAL)
        controlFrame = ttk.Labelframe(self.mainpane, text='controlpanel')
        tableFrame = ttk.Labelframe(self.mainpane, text='tablepanel')

        self.mainpane.add(controlFrame)
        self.mainpane.add(tableFrame)
        self.mainpane.pack()
        self.numsEntry = Entry(controlFrame, text="")
        self.numsEntry.grid(row=0, column=0)
        self.numsEntry.insert(0, '8')

        Label(tableFrame, text='RANK').grid(row=0, column=0)
        Label(tableFrame, text='ID').grid(row=0, column=1)
        Label(tableFrame, text='WINS').grid(row=0, column=2)
        #排名，不刷新
        for i in range(self.height):
            b = Entry(tableFrame, text="")
            b.grid(row=i + 1, column=0)
            b.insert(END, str(i + 1))
            b.config(state=DISABLED)
        #ID
        for i in range(self.height):
            b = Entry(tableFrame, text="")
            b.grid(row=i + 1, column=1)
            # b.insert(END, str(i))
            # b.config(state=DISABLED)
            self.entryIDs.append(b)


        for i in range(self.height):
            b = Entry(tableFrame, text="")
            b.grid(row=i + 1, column=2)
            # b.insert(END, str(i + 1) + '  ' + str(2))
            # b.config(state=DISABLED)
            self.entryWins.append(b)

        setupButton = Button(controlFrame, text='SETUP', command=self.setup)
        judgeButton = Button(controlFrame, text='JUDGE', command=self.openlog)
        battleButton = Button(controlFrame, text='BATTLE', command=self.startgame)
        knockedoutButton = Button(controlFrame, text='KNOCKEDOUT', command=self.knockedout)
        quitButton = Button(controlFrame, text='QUIT', command=self.quit)

        setupButton.grid(row=0, column=1, columnspan=2)
        judgeButton.grid(row=0, column=3, columnspan=2)
        battleButton.grid(row=0, column=5, columnspan=2)
        knockedoutButton.grid(row=0, column=7, columnspan=2)
        quitButton.grid(row=0, column=9, columnspan=2)

        self.root.mainloop()

class Player:

    ID = 'ID'
    wins = 0
    def __init__(self, id, sock):
        self.ID = id
        self.clientsock = sock

def init():
    global IMAGE,tip,screen,font,maplib,Lyr,Lyb,Lx,S,matchPro
    pygame.init()
    S = Status()
    screen = pygame.display.set_mode(WINDOWSIZE, 0, 32)  # 设置游戏窗口
    pygame.display.set_caption('Einstein Chess-TA Server')  # 设置Caption
    font = pygame.font.SysFont("Cambria Math", TEXTSIZE,
                               bold=False, italic=False)  # 设置标题字体格式
    tip = pygame.font.SysFont("arial", TIPSIZE, bold=False, italic=False)  # 设置提示字体
    IMAGE = {
        'R1': pygame.transform.scale(pygame.image.load('picture/white/R1.png').convert(), SIZE),
        'R2': pygame.transform.scale(pygame.image.load('picture/white/R2.png').convert(), SIZE),
        'R3': pygame.transform.scale(pygame.image.load('picture/white/R3.png').convert(), SIZE),
        'R4': pygame.transform.scale(pygame.image.load('picture/white/R4.png').convert(), SIZE),
        'R5': pygame.transform.scale(pygame.image.load('picture/white/R5.png').convert(), SIZE),
        'R6': pygame.transform.scale(pygame.image.load('picture/white/R6.png').convert(), SIZE),
        'B1': pygame.transform.scale(pygame.image.load('picture/white/B1.png').convert(), SIZE),
        'B2': pygame.transform.scale(pygame.image.load('picture/white/B2.png').convert(), SIZE),
        'B3': pygame.transform.scale(pygame.image.load('picture/white/B3.png').convert(), SIZE),
        'B4': pygame.transform.scale(pygame.image.load('picture/white/B4.png').convert(), SIZE),
        'B5': pygame.transform.scale(pygame.image.load('picture/white/B5.png').convert(), SIZE),
        'B6': pygame.transform.scale(pygame.image.load('picture/white/B6.png').convert(), SIZE),
        'Y1': pygame.transform.scale(pygame.image.load('picture/white/Y1.png').convert(), SIZE),
        'Y2': pygame.transform.scale(pygame.image.load('picture/white/Y2.png').convert(), SIZE),
        'Y3': pygame.transform.scale(pygame.image.load('picture/white/Y3.png').convert(), SIZE),
        'Y4': pygame.transform.scale(pygame.image.load('picture/white/Y4.png').convert(), SIZE),
        'Y5': pygame.transform.scale(pygame.image.load('picture/white/Y5.png').convert(), SIZE),
        'Y6': pygame.transform.scale(pygame.image.load('picture/white/Y6.png').convert(), SIZE),
        '1': pygame.transform.scale(pygame.image.load('picture/white/1.png').convert(), SIZE),
        '2': pygame.transform.scale(pygame.image.load('picture/white/2.png').convert(), SIZE),
        '3': pygame.transform.scale(pygame.image.load('picture/white/3.png').convert(), SIZE),
        '4': pygame.transform.scale(pygame.image.load('picture/white/4.png').convert(), SIZE),
        '5': pygame.transform.scale(pygame.image.load('picture/white/5.png').convert(), SIZE),
        '6': pygame.transform.scale(pygame.image.load('picture/white/6.png').convert(), SIZE),
        'BLUEWIN': pygame.transform.scale(pygame.image.load('picture/white/BLUEWIN.png').convert(), WINSIZE),
        'REDWIN': pygame.transform.scale(pygame.image.load('picture/white/REDWIN.png').convert(), WINSIZE),
    }
    # 布局库
    maplib = [[6, 2, 4, 1, 5, 3],
              [6, 5, 2, 1, 4, 3],
              [1, 5, 4, 6, 2, 3],
              [1, 6, 3, 5, 2, 4],
              [1, 6, 4, 3, 2, 5],
              [6, 1, 2, 5, 4, 3],
              [6, 1, 3, 5, 4, 2],
              [1, 6, 4, 2, 3, 5],
              [1, 5, 2, 6, 3, 4],
              [1, 6, 5, 2, 3, 4],
              [1, 2, 5, 6, 3, 4],
              [6, 2, 5, 1, 4, 3],
              [1, 6, 3, 2, 4, 5],
              [6, 2, 3, 1, 5, 4],
              [1, 6, 3, 4, 2, 5],
              [1, 5, 4, 6, 3, 2]
              ]
    resetInfo()
    Lyr = []
    Lyb = []
    Lx = []
    matchPro = 0.85

####################### 下棋图像显示 ########################################

def loadImage(name, pos, size=SIZE):
    filename = "picture/white/" + name
    screen.blit(pygame.transform.scale(
        pygame.image.load(filename).convert(), size), pos)

# mode 0->init  other->finish game 实际填写玩家数量
def drawStartScreen(mode = 0):  # 开始界面
    screen.fill(WHITE)
    loadImage("AYST.png", (100, 40), AYSTSIZE)
    if mode == 0:
        drawText('PORT 50006 IS WAITING FOR CONNECTION', font, TEXTCOLOR, screen, 5.5, 0.1)
    else:
        drawText('PROCESS FINISHED, CLICK BUTTONS', font, TEXTCOLOR, screen, 5.5, 1)
    pygame.display.update()


    # waitForPlayerToPressKey()

def drawWinScreen(result):  # 比赛结束，显示结果界面
    if result == BLUEWIN:
        loadImage("BLUEWIN.png", (20, 130), WINSIZE)
    if result == REDWIN:
        loadImage("REDWIN.png", (20, 130), WINSIZE)
    # waitForPlayerToPressKey()
    pygame.display.update()
    # sleep(SLEEPTIME)
    pygame.time.delay(SLEEPTIME * 1000)

def showWinRate(RedWinRate, BlueWinRate, x):
    global Lyr, Lyb, Lx
    yr = (100 - RedWinRate)/(100/3.0) + 0.6
    yb = (100 - BlueWinRate)/(100/3.0) + 0.6
    x = x/(1000/5) + 4.2
    Lyr.append(copy.deepcopy(yr))
    Lyb.append(copy.deepcopy(yb))
    Lx.append(copy.deepcopy(x))
    for i in range(0, len(Lyr)-1):
        pygame.draw.line(
            screen, RED, (100*Lx[i], 100*Lyr[i]), (100*Lx[i], 100*Lyr[i+1]))
        pygame.draw.line(
            screen, BLUE, (100*Lx[i], 100*Lyb[i]), (100*Lx[i], 100*Lyb[i+1]))

def drawGameScreen(conn0, conn1):  # 游戏比赛界面
    global S

    screen.fill(WHITE)
    # 画棋盘
    for i in range(6):
        x = y = 60*(i+1)
        pygame.draw.line(screen, LINECOLOR, (60, y), (360, y))
        pygame.draw.line(screen, LINECOLOR, (x, 60), (x, 360))


    drawText('RED : '+str(conn0.ID), font, RED, screen, 6, 1)
    drawText('BLUE : '+str(conn1.ID), font, BLUE, screen, 6.5, 1)


    # 画棋子
    for i in range(5):
        for j in range(5):
            if S.map[i][j] != 0:
                drawPawn(S.map[i][j], i, j)
    pygame.display.update()
    pygame.display.update()


def drawGameScreen1(Red, conn1):  # 游戏比赛界面
    global S

    screen.fill(WHITE)
    # 画棋盘
    for i in range(6):
        x = y = 60 * (i + 1)
        pygame.draw.line(screen, LINECOLOR, (60, y), (360, y))
        pygame.draw.line(screen, LINECOLOR, (x, 60), (x, 360))

    drawText('RED : ' + str(Red), font, RED, screen, 6, 1)
    drawText('BLUE : ' + str(conn1.ID), font, BLUE, screen, 6.5, 1)

    # 画棋子
    for i in range(5):
        for j in range(5):
            if S.map[i][j] != 0:
                drawPawn(S.map[i][j], i, j)
    pygame.display.update()
    pygame.display.update()


def drawMovePawn(n, ans):  # 可选择移动的棋子
    x = -1
    y = 2
    for v in ans:
        drawPawn(v, x, y)
        y += 1
    if n <= 6:
        loadImage(str(n)+'.png', (310, 5))
    else:
        loadImage(str(n-6)+'.png', (310, 5))
    pygame.display.update()

def drawPawn(value, row, col, size=SIZE):  # 在（row，col）处，画值为value的棋子
    pos_x = col * STEP + START
    pos_y = row * STEP + START
    Pos = (pos_x, pos_y)
    if value <= 6:
        s = 'R' + str(value)
    elif value > 6:
        s = 'B' + str(value-6)
    loadImage(s+'.png', Pos, size)

def drawText(text, font, color, surface, row, col):  # 处理需要描绘的文字：text：文本；font：格式；
    row += 0.2
    x = col * STEP
    y = row * STEP
    textobj = font.render(text, True, color, WHITE)
    textrect = textobj.get_rect()
    textrect.topleft = (x, y)
    surface.blit(textobj, textrect)

##################################################################

##################### 下棋逻辑计算 ##################################

def selectPawn(S,n=0):  # 掷骰子，挑选可以移动的棋子
    global COUNT
    if n == 0:
        COUNT += 1
        if COUNT % 2 == 0:
            n = random.randint(1, 6)
        else:
            n = random.randint(7, 12)
        ans = findNearby(n, S.pawn)
    else:
        ans = findNearby(n, S.pawn)
    return n, ans

def terminate():  # 退出游戏
    pygame.quit()
    sys.exit()

def makeMove(p, PawnMoveTo):  # 移动棋子，更新地图信息，和棋子存活情况
    row, col = getLocation(p, S.map)
    x = y = 0
    if PawnMoveTo == LEFT:
        y = -1
    elif PawnMoveTo == RIGHT:
        y = +1
    elif PawnMoveTo == UP:
        x = -1
    elif PawnMoveTo == DOWN:
        x = +1
    elif PawnMoveTo == LEFTUP:
        x = -1
        y = -1
    elif PawnMoveTo == RIGHTDOWN:
        x = +1
        y = +1
    else:
        return False
    # 移动无效
    if notInMap(row+x, col+y):
        return False
    S.map[row][col] = 0
    row = row + x
    col = col + y
    # 是否吃掉自己或对方的棋
    if S.map[row][col] != 0:
        i = S.pawn.index(S.map[row][col])
        S.pawn[i] = 0
    S.map[row][col] = p
    return True

def notInMap(x, y):  # 检测棋子是否在棋盘内移动
    if x in range(0, 5) and y in range(0, 5):
        return False
    return True

def showSelected(p):  # 用红色标记，显示被挑选的棋子
    row, col = getLocation(p, S.map)
    pos_x = col * STEP + START
    pos_y = row * STEP + START
    Pos = (pos_x, pos_y)
    if p > 6:
        s = 'Y' + str(p-6)
    else:
        s = 'Y' + str(p)
    loadImage(s+'.png', Pos)
    # screen.blit(IMAGE[s],Pos)
    pygame.display.update()

def isEnd(S):  # 检测比赛是否结束
    if S.map[0][0] > 6:
        return BLUEWIN
    elif S.map[4][4] > 0 and S.map[4][4] <= 6:
        return REDWIN
    cnt = 0
    for i in range(0, 6):
        if S.pawn[i] == 0:
            cnt += 1
    if cnt == 6:
        return BLUEWIN
    cnt = 0
    for i in range(6, 12):
        if S.pawn[i] == 0:
            cnt += 1
    if cnt == 6:
        return REDWIN
    return False

def resetInfo():  # 重置比赛信息
    S.map = getNewMap()
    S.pawn = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]  # 棋子初始化
    S.pro = [1.0/6, 1.0/6, 1.0/6, 1.0/6, 1.0/6, 1.0 /
           6, 1.0/6, 1.0/6, 1.0/6, 1.0/6, 1.0/6, 1.0/6]
    value = getLocValue(S)
    S.value = getPawnValue(S.pro, value)

def getNewMap():  # 换新图
    r = random.sample(maplib, 1)[0]
    b = random.sample(maplib, 1)[0]
    newMap = [
        [r[0], r[3],  r[5],     0,    0],
        [r[1], r[4],     0,     0,    0],
        [r[2],   0,     0,     0, b[2]+6],
        [0,   0,     0, b[4]+6, b[1]+6],
        [0,   0, b[5]+6, b[3]+6, b[0]+6]
    ]
    return newMap

def getLocValue(S):  # 棋子所在位置的价值
    blueValue = [[99, 10,  6,  3,  1],
                 [10,  8,  4,  2,  1],
                 [6,  4,  4,  2,  1],
                 [3,  2,  2,  2,  1],
                 [1,  1,  1,  1,  1]]
    redValue = [[1,  1,  1,  1,  1],
                [1,  2,  2,  2,  3],
                [1,  2,  4,  4,  6],
                [1,  2,  4,  8, 10],
                [1,  3,  6, 10, 99]]
    V = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    for p in range(1, 13):
        if S.pawn[p-1] != 0:
            row, col = getLocation(p, S.map)
            if p <= 6:
                V[p-1] = redValue[row][col]
            else:
                V[p-1] = blueValue[row][col]
    return V

def getPawnValue(pro, value):  # 棋子价值
    V = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    for i in range(0, 12):
        V[i] = pro[i] * value[i]
    return V

def findNearby(n, nowPawn):  # 寻找可以移动的棋子
    ans = []
    # 如果有对应棋子
    if nowPawn[n-1] != 0:
        ans.append(n)
    #没有对应棋子
    elif n > 6:
        for i in range(n-1, 6, -1):
            if i in nowPawn:
                ans.append(i)
                break
        for i in range(n+1, 13):
            if i in nowPawn:
                ans.append(i)
                break
    elif n <= 6:
        for i in range(n-1, 0, -1):
            if i in nowPawn:
                ans.append(i)
                break
        for i in range(n+1, 7):
            if i in nowPawn:
                ans.append(i)
                break
    return ans

def getLocation(p, Map):  # 返回传入地图下，棋子p的坐标
    for i in range(5):
        for j in range(5):
            if Map[i][j] == p:
                return i, j

def tryMakeMove(p, PawnMoveTo, S):  # 尝试移动，并且返回移动后的棋局地图与棋子存活情况
    newS = copy.deepcopy(S)
    row, col = getLocation(p, newS.map)
    x = y = 0
    if PawnMoveTo == LEFT:
        y = -1
    elif PawnMoveTo == RIGHT:
        y = +1
    elif PawnMoveTo == UP:
        x = -1
    elif PawnMoveTo == DOWN:
        x = +1
    elif PawnMoveTo == LEFTUP:
        x = -1
        y = -1
    elif PawnMoveTo == RIGHTDOWN:
        x = +1
        y = +1
    # 移动无效
    if notInMap(row+x, col+y):
        return False
    newS.map[row][col] = 0
    row = row + x
    col = col + y
    if newS.map[row][col] != 0:
        i = newS.pawn.index(newS.map[row][col])
        newS.pawn[i] = 0
    newS.map[row][col] = p
    newS.parent = S
    newS.pPawn = p
    newS.pMove = PawnMoveTo
    if p < 7:
        newS.cPawn = [INFTY,INFTY,INFTY,INFTY,INFTY,INFTY]
        newS.cPawnSecond = [INFTY,INFTY,INFTY,INFTY,INFTY,INFTY]
    else:
        newS.cPawn = [-INFTY,-INFTY,-INFTY,-INFTY,-INFTY,-INFTY]
        newS.cPawnSecond = [-INFTY,-INFTY,-INFTY,-INFTY,-INFTY,-INFTY]
    return newS

#########################################################



########################## SOCKET TO MOVE & OUTPUT #########################################
# 20190302 socket 移动棋子,如果走错直接输
def socketToMove(conn,n, ans, S):
    message = str(S.map) + '|' + str(n)
    conn.sendall(message.encode('UTF-8'))
    try:
        conn.settimeout(5)
        data, address = conn.recvfrom(1024)
    except socket.error as e:
        logger.info(str(e))
        return -1, 'timeout'
    text = (data.decode('UTF-8')[:-1]).split('|')
    try:
        p = int(text[0])
        moveTo = text[1]
    except TypeError as tp:
        return -1, 'not move'

    if (p in ans):
        if p > 0 and p < 7:
            if moveTo == DOWN or moveTo == RIGHT or moveTo == RIGHTDOWN:
                newS = tryMakeMove(p, moveTo, S)
                if newS is not False:
                    return p, moveTo
        elif p > 6 and p < 13:
            if moveTo == UP or moveTo == LEFT or moveTo == LEFTUP:
                newS = tryMakeMove(p, moveTo, S)
                if newS is not False:
                    return p, moveTo
    return -1, 'not move'


def outputResult(filename):
    global clients
    rank = clients.copy()
    if currentnum == playernum:
        for i in range(playernum - 1):
            for j in range(playernum - i - 1):
                if (rank[j].wins < rank[j + 1].wins):
                    rank[j], rank[j + 1] = rank[j + 1], rank[j]
    try:
        with open(str((int(time.time())))+str(filename),mode='w', encoding='utf8') as f:
            f.writelines('ID,WINS\n')
            for c in rank:
                f.writelines(str(c.ID) + '  , ' + str(c.wins)+str('\n'))
        logger.info('WRITE INTO '+filename)
    except Exception as ex:
        logger.error('write file error : '+str(ex))


# 清楚clients列表中成绩wins  仅用于JUDGE   BATTLE 淘汰赛不使用 clients列表
def flushscore():
    global clients
    global playernum
    for i in range(playernum):
        clients[i].wins = 0

#######################################################################



#######################  JUDGE AI  #####################################

def searchNearbyBlueMaxValue(p, S):  # 搜索附近蓝方最有价值的棋子
    nearby = []
    row, col = getLocation(p, S.map)
    if row+1 < 5:
        if S.map[row+1][col] > 6:
            nearby.append(S.value[S.map[row+1][col]-1])
    if col+1 < 5:
        if S.map[row][col+1] > 6:
            nearby.append(S.value[S.map[row][col+1]-1])
    if row+1 < 5 and col+1 < 5:
        if S.map[row+1][col+1] > 6:
            nearby.append(S.value[S.map[row+1][col+1]-1])
    if nearby == []:
        return 0

    expValue = 0
    for v in nearby:
        expValue += v/sum(nearby)
    return expValue

def searchNearbyRedMaxValue(p, S):   # 搜索附近红方最有价值的棋子
    nearby = []
    row, col = getLocation(p, S.map)
    if row-1 >= 0:
        if S.map[row-1][col] <= 6 and S.map[row-1][col] > 0:
            nearby.append(S.value[S.map[row-1][col]-1])
    if col-1 >= 0:
        if S.map[row][col-1] <= 6 and S.map[row][col-1] > 0:
            nearby.append(S.value[S.map[row][col-1]-1])
    if row-1 >= 0 and col-1 >= 0:
        if S.map[row-1][col-1] <= 6 and S.map[row-1][col-1] > 0:
            nearby.append(S.value[S.map[row-1][col-1]-1])
    if nearby == []:
        return 0
    expValue = 0
    for v in nearby:
        expValue += v/sum(nearby)
    return expValue
def getThread(S):  # 获得红方对蓝方的威胁值，蓝方对红方的威胁值
    redToBlueOfThread = 0
    blueToRedOfThread = 0
    for p in range(1, 13):
        if S.pawn[p-1] != 0:
            if p <= 6:
                nearbyBlueMaxValue = searchNearbyBlueMaxValue(p, S)
                redToBlueOfThread += S.pro[p-1] * nearbyBlueMaxValue
            else:
                nearbyRedMaxValue = searchNearbyRedMaxValue(p, S)
                blueToRedOfThread += S.pro[p-1] * nearbyRedMaxValue
    return redToBlueOfThread, blueToRedOfThread

def getScore(S, k=2.2, lam=5):
    redToBlueOfThread, blueToRedOfThread = getThread(S)
    expRed = expBlue = 0
    for i in range(0, 12):
        if i < 6:
            expRed += S.value[i]
        else:
            expBlue += S.value[i]
    theValue = lam * ( k * expRed - expBlue) - blueToRedOfThread + redToBlueOfThread
    return theValue

def getTheNextStepStatus(SL):
    NL = []
    if SL[0].pPawn > 6:
        move = ['right','down','rightdown']
        o = 0
    else:
        move = ['left','up','leftup']
        o = 6
    for s in SL:
        for i in range(1,7):
            n,ans = selectPawn(s,i+o)
            for p in ans:
                for m in move:
                    newStatus = tryMakeMove(p,m,s);
                    if newStatus is not False:
                        newStatus.pDice = i
                        NL.append(newStatus)
    return NL
def getSum(L):
    value = 0
    for i in L:
        if i != INFTY and i != -INFTY:
            value += i
    return (1/6)*value
def MinimaxGoBack(KL):
    for s in KL[-1]:
        score = getScore(s)
        if s.pPawn > 6:
            if score < s.parent.cPawn[(s.pDice%6)-1]:
                s.parent.cPawn[s.pDice%6 - 1] = score
        else:
            if score > s.parent.cPawn[s.pDice-1]:
                s.parent.cPawn[s.pDice-1] = score
    for i in range(len(KL)-2,0,-1):
        for s in KL[i]:
            score = getSum(s.cPawn)
            if s.pPawn > 6:
                if score < s.parent.cPawn[s.pDice%6-1]:
                    s.parent.cPawn[s.pDice%6 -1] = score
            else:
                if score > s.parent.cPawn[s.pDice-1]:
                    s.parent.cPawn[s.pDice-1] = score
    return KL[0]

def redByMinimax(ans, k=2.2, lam=5, STEP=2):
    maxValue = theValue = -INFTY
    bestp = 0;
    bestm = '';
    move = ['right','down','rightdown']
    KL = []
    SL = []
    for p in ans:
        for m in move:
            newStatus = tryMakeMove(p,m,S);
            if newStatus is not False:
                SL.append(newStatus)
                if isEnd(newStatus):
                    return p,m
    STEP -= 1
    if len(SL) == 1:
        bestp,bestm = SL[0].pPawn,SL[0].pMove
    else:
        KL.append(SL)
        for i in range(STEP):
            NL = getTheNextStepStatus(KL[-1])
            KL.append(NL)
        KL = MinimaxGoBack(KL)
        for s in KL:
            theValue = getSum(s.cPawn)
            if theValue > maxValue:
                maxValue,bestp,bestm = theValue,s.pPawn,s.pMove
    return bestp,bestm

def playGame(Red, Blue, detail, conn):

    lastInfo = []
    mapNeedRedraw = True  # 是否需要重新绘制地图

    if detail:
        drawGameScreen1(Red, conn)
    while True:
        moveTo = None  # 棋子移动方向
        mapNeedRedraw = False

        # correct = 0 #游戏结果

        n, ans = selectPawn(S)
        if detail:
            drawMovePawn(n, ans)

        # GUI control here
        for event in pygame.event.get():
            if event.type == QUIT:
                terminate()


        if COUNT % 2 == 0:
            if Red == 'BetaCat1.0':
                p, moveTo = redByMinimax(ans)
            if Red == 'Socket':
                try:
                    p, moveTo = socketToMove(conn=conn.clientsock,n=n, ans=ans, S=S)
                    if p == -1:
                        logger.info('RESULT : BLUEWIN')
                        return BLUEWIN
                except socket.error as e:
                    logger.info('RESULT : BLUEWIN')
                    return BLUEWIN
                except ValueError as e1:
                    logger.info('RESULT : BLUEWIN')
                    return BLUEWIN

        if COUNT % 2 == 1:

            if Blue == 'Socket':
                try:
                    p, moveTo = socketToMove(conn=conn.clientsock, n=n, ans=ans, S=S)
                    if p == -1:
                        logger.info('RESULT : REDWIN')
                        return REDWIN
                except socket.error as e:
                    logger.info('RESULT : REDWIN')
                    return REDWIN
                except ValueError as e1:
                    logger.info('RESULT : REDWIN')
                    return BLUEWIN

        if moveTo != None:
            moved = makeMove(p, moveTo)
            lastInfo = [n, p, moveTo]
            if moved:
                mapNeedRedraw = True
        if mapNeedRedraw and detail:  # 如果需要重绘棋局界面，则：
            sleep(SLEEPTIME)
            drawGameScreen1(Red, conn)  # 重绘棋局界面
            logger.info(str(S.map)+' |chess: '+str(p)+' |move : '+moveTo)
            pass

        result = isEnd(S)  # 检查游戏是否结束，返回游戏结果


        if result:
            lastInfo = []
            logger.info('RESULT : REDWIN' if result == 1 else 'RESULT : BLUEWIN')
            return result
############################################################

#=================== BATTLE  PROCESS ========================================


def battle(client0, client1, detail):
    lastInfo = []
    mapNeedRedraw = True  # 是否需要重新绘制地图
    logger.info(str(client0.ID)+'   VS   '+str(client1.ID))
    if detail:
        drawGameScreen(client0, client1)
    while True:

        moveTo = None  # 棋子移动方向
        mapNeedRedraw = False
        n, ans = selectPawn(S)
        if detail:
            drawMovePawn(n, ans)
        for event in pygame.event.get():
            if event.type == QUIT:
                terminate()
        try:
            # sleep(SLEEPTIME)
            pygame.time.delay(SLEEPTIME * 1000)
            if COUNT % 2 == 0:
                p, moveTo = socketToMove(conn=client0.clientsock, n=n, ans=ans, S=S)
                if p == -1:
                    logger.info(str('RESULT : '+client1.ID+' WIN'))
                    return BLUEWIN
        except socket.error as e:
            logger.info(str('ERRORS  ')+str(e) )
            logger.info(str('RESULT : ' + client1.ID + ' WIN'))
            return BLUEWIN
        except ValueError as e1:
            logger.info(str('ERRORS  ')+str(e1))
            logger.info(str('RESULT : ' + client1.ID + ' WIN'))
            return BLUEWIN


        try:
            if COUNT % 2 == 1:
                p, moveTo = socketToMove(conn=client1.clientsock, n=n, ans=ans, S=S)
                if p == -1:
                    str('RESULT : ' + client0.ID + ' WIN')
                    return REDWIN
        except socket.error as e:
            logger.info(str('ERRORS  ') + str(e))
            logger.info(str('RESULT : ' + client0.ID + ' WIN'))
            return REDWIN
        except ValueError as e1:
            logger.info(str('ERRORS  ') + str(e1))
            logger.info(str('RESULT : ' + client0.ID + ' WIN'))
            return REDWIN


        if moveTo != None:
            moved = makeMove(p, moveTo)
            lastInfo = [n, p, moveTo]
            if moved:
                mapNeedRedraw = True
        if mapNeedRedraw and detail:  # 如果需要重绘棋局界面，则：
            drawGameScreen(client0, client1)  # 重绘棋局界面
            logger.info(str(S.map) + ' |id: ' + str(p) + ' |move : ' + moveTo)
            pass
        result = isEnd(S)  # 检查游戏是否结束，返回游戏结果
        if result:
            lastInfo = []
            logger.info(str('RESULT : '+client0.ID+' WIN') if result == 1 else str('RESULT : '+client1.ID+' WIN'))
            return result


#===========================================================

# 各种对战规则， 主界面逻辑，阻塞式
def startgame(port, n, app, detail=True):
    global COUNT
    global playernum
    global clients
    global currentnum
    global FUNCTION
    global FINALROUND
    global finalroundclients
    global NEXTSTAGE
    wins = [0 for i in range(playernum)]
    init()
    if detail:
        drawStartScreen(playernum)  # 游戏开始界面
    RESULT[0] = 0
    RESULT[1] = 0
    cnt = n
    rateline = []

    while(FUNCTION == 0):
        #sleep(1)
        pygame.time.delay(SLEEPTIME * 1000)

    #客户端
    if (FUNCTION == -1):
        # FUNCTION = 0
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.bind(('0.0.0.0', port))

            for i in range(playernum):
                sock.listen()
                conn, addr = sock.accept()
                # 获取用户ID
                playerID = conn.recv(1024).decode('utf8')[:-1]
                clients.append(Player(playerID, conn))
                print('client_{} connected: {}'.format(i, addr))
                logger.info('client_'+str(i)+' connected: '+str(addr))
                currentnum = i+1
                app.refresh()
        FUNCTION = 0 # 防止比赛过程中乱按按钮

    if FUNCTION == 2:
        # FUNCTION = 0
        if playernum == 0:
            return -2

        flushscore()
        for i in range(0, playernum-1):
            for j in range(i+1, playernum):
                count = cnt
                while count:
                    resetInfo()
                    result = battle(clients[i], clients[j], detail)
                    if detail:
                        # pass
                        drawWinScreen(result)
                        if result == REDWIN:
                            clients[i].wins = clients[i].wins+1
                        else:
                            clients[j].wins = clients[j].wins+1
                        app.refresh()

                    RESULT[result - 1] += 1  # 更新比分
                    count -= 1
                    COUNT = 2000 - count - 1  # 先手方交替
                    rateline.append(float(RESULT[0]) / sum(RESULT))
                    if count % 5 == 0:
                        # pass
                        print(sum(RESULT), '\t', round(100 * RESULT[0] / sum(RESULT), 4))
        outputResult('BATTLERESULT.csv')
        FUNCTION = 0

    if FUNCTION == 1:
        # FUNCTION = 0
        if playernum == 0:
            return -1
        flushscore()
        for i in range(playernum):

            count = cnt
            while count:
                resetInfo()
                result = playGame('BetaCat1.0', 'Socket', detail=True, conn=clients[i])
                if detail:
                    # pass
                    drawWinScreen(result)
                    if result == BLUEWIN:
                        clients[i].wins = clients[i].wins + 1
                    app.refresh()

                RESULT[result - 1] += 1  # 更新比分
                count -= 1
                COUNT = 2000 - count - 1  # 先手方交替
                rateline.append(float(RESULT[0]) / sum(RESULT))
                if count % 5 == 0:
                    # pass
                    print(sum(RESULT), '\t', round(100 * RESULT[0] / sum(RESULT), 4))
        outputResult('JUDGERESULT.csv')
        FUNCTION = 0


    if FUNCTION == 3:
        # FUNCTION = 0
        if playernum == 0:
            return -3
        NEXTSTAGE.clear()
        # ROUND1
        for i in range(0, 4):
            finalroundclients[i].wins = 0
            finalroundclients[i+4].wins = 0
            count = 3
            while count:
                resetInfo()
                result = battle(finalroundclients[i], finalroundclients[i + 4], detail)
                if detail:
                    # pass
                    drawWinScreen(result)
                    if result == REDWIN:
                        finalroundclients[i].wins = finalroundclients[i].wins + 1
                        if finalroundclients[i].wins == 2:
                            app.finalRefresh0(i+4, '第一轮淘汰')
                            NEXTSTAGE.append(i)
                            # print('-------------------------next stage---------------------')
                            # print(str(NEXTSTAGE))
                            # app.entryWins[i+4].delete('0', END)
                            # app.entryWins[i+4].insert(END, str('第一轮淘汰'))
                            # app.entryWins[i+4].config({"background": "White"})
                            # app.entryIDs[i+4].config({"background": "White"})
                            logger.info('决赛第一轮: ' + str(finalroundclients[i].ID) + ' 晋级')
                            logger.info('决赛第一轮: '+str(finalroundclients[i+4].ID)+' 淘汰')
                            break
                    else:
                        finalroundclients[i+4].wins = finalroundclients[i+4].wins + 1
                        if finalroundclients[i+4].wins == 2:
                            app.finalRefresh0(i, '第一轮淘汰')
                            NEXTSTAGE.append(i+4)
                            # print('-------------------------next stage---------------------')
                            # print(str(NEXTSTAGE))
                            # app.entryWins[i].delete('0', END)
                            # app.entryWins[i].insert(END, str('第一轮淘汰'))
                            # app.entryWins[i].config({"background": "White"})
                            # app.entryIDs[i].config({"background": "White"})
                            logger.info('决赛第一轮: ' + str(finalroundclients[i+4].ID) + ' 晋级')
                            logger.info('决赛第一轮: ' + str(finalroundclients[i].ID) + ' 淘汰')
                            break
                RESULT[result - 1] += 1  # 更新比分
                count -= 1
                COUNT = 2000 - count - 1  # 先手方交替
                rateline.append(float(RESULT[0]) / sum(RESULT))
        print('-------------------------next stage---------------------')
        print(str(NEXTSTAGE))
        # ROUND2
        FINALSTAGE = []
        for i in range(0, 2):
            finalroundclients[NEXTSTAGE[i]].wins = 0
            finalroundclients[NEXTSTAGE[i+2]].wins = 0
            count = 3
            while count:
                resetInfo()
                result = battle(finalroundclients[NEXTSTAGE[i]], finalroundclients[NEXTSTAGE[i+2]], detail)
                if detail:
                    # pass
                    drawWinScreen(result)
                    if result == REDWIN:
                        finalroundclients[NEXTSTAGE[i]].wins = finalroundclients[NEXTSTAGE[i]].wins + 1
                        if finalroundclients[NEXTSTAGE[i]].wins == 2:
                            sleep(1)
                            app.finalRefresh0(NEXTSTAGE[i+2], '第二轮淘汰')
                            # app.entryWins[NEXTSTAGE[i+2]].delete('0', END)
                            # app.entryWins[NEXTSTAGE[i+2]].insert(END, str('第二轮淘汰'))
                            # app.entryWins[NEXTSTAGE[i+2]].config({"background": "White"})
                            # app.entryIDs[NEXTSTAGE[i+2]].config({"background": "White"})
                            FINALSTAGE.append(NEXTSTAGE[i])
                            FINALSTAGE.append(NEXTSTAGE[i+2])
                            logger.info('决赛第二轮: ' + str(finalroundclients[NEXTSTAGE[i]].ID) + ' 晋级')
                            logger.info('决赛第二轮: ' + str(finalroundclients[NEXTSTAGE[i+2]].ID) + ' 淘汰')
                            break
                    else:
                        finalroundclients[NEXTSTAGE[i+2]].wins = finalroundclients[NEXTSTAGE[i+2]].wins + 1
                        if finalroundclients[NEXTSTAGE[i+2]].wins == 2:
                            sleep(1)
                            app.finalRefresh0(NEXTSTAGE[i], '第二轮淘汰')
                            # app.entryWins[NEXTSTAGE[i]].delete('0', END)
                            # app.entryWins[NEXTSTAGE[i]].insert(END, str('第二轮淘汰'))
                            # app.entryWins[NEXTSTAGE[i]].config({"background": "White"})
                            # app.entryIDs[NEXTSTAGE[i]].config({"background": "White"})
                            FINALSTAGE.append(NEXTSTAGE[i+2])
                            FINALSTAGE.append(NEXTSTAGE[i])
                            logger.info('决赛第二轮: ' + str(finalroundclients[NEXTSTAGE[i+2]].ID) + ' 晋级')
                            logger.info('决赛第二轮: ' + str(finalroundclients[NEXTSTAGE[i]].ID) + ' 淘汰')
                            break
                RESULT[result - 1] += 1  # 更新比分
                count -= 1
                COUNT = 2000 - count - 1  # 先手方交替
                rateline.append(float(RESULT[0]) / sum(RESULT))

        # FINALROUND
        resetInfo()
        app.finalRefresh1()
        FINALRESULT = ()
        app.entryIDs[0].insert(END, finalroundclients[FINALSTAGE[0]].ID)
        app.entryWins[0].insert(END, '冠军争夺战')
        app.entryIDs[1].insert(END, finalroundclients[FINALSTAGE[2]].ID)
        app.entryWins[1].insert(END, '冠军争夺战')

        app.entryIDs[2].insert(END, finalroundclients[FINALSTAGE[1]].ID)
        app.entryWins[2].insert(END, '季军争夺战')
        app.entryIDs[3].insert(END, finalroundclients[FINALSTAGE[3]].ID)
        app.entryWins[3].insert(END, '季军争夺战')

        app.entryIDs[0].config({"background": 'red'})
        app.entryWins[0].config({"background": 'red'})
        app.entryIDs[1].config({"background": 'blue'})
        app.entryWins[1].config({"background": 'blue'})
        app.entryIDs[2].config({"background": 'red'})
        app.entryWins[2].config({"background": 'red'})
        app.entryIDs[3].config({"background": 'blue'})
        app.entryWins[3].config({"background": 'blue'})


        result = battle(finalroundclients[FINALSTAGE[0]], finalroundclients[FINALSTAGE[2]], detail)
        if detail:
            # pass
            drawWinScreen(result)
            app.entryIDs[0].config({"background": 'white'})
            app.entryWins[0].config({"background": 'white'})
            app.entryIDs[1].config({"background": 'white'})
            app.entryWins[1].config({"background": 'white'})
            app.entryIDs[0].delete('0', END)
            app.entryWins[0].delete('0', END)
            app.entryIDs[1].delete('0', END)
            app.entryWins[1].delete('0', END)
            if result == REDWIN:
                app.entryIDs[0].insert(END, finalroundclients[FINALSTAGE[0]].ID)
                app.entryWins[0].insert(END, '冠军')
                app.entryIDs[1].insert(END, finalroundclients[FINALSTAGE[2]].ID)
                app.entryWins[1].insert(END, '亚军')
                logger.info(str(finalroundclients[FINALSTAGE[0]].ID) + '   冠军')
                logger.info(str(finalroundclients[FINALSTAGE[2]].ID) + '   亚军')
            if result == BLUEWIN:
                app.entryIDs[0].insert(END, finalroundclients[FINALSTAGE[2]].ID)
                app.entryWins[0].insert(END, '冠军')
                app.entryIDs[1].insert(END, finalroundclients[FINALSTAGE[0]].ID)
                app.entryWins[1].insert(END, '亚军')
                logger.info(str(finalroundclients[FINALSTAGE[2]].ID) + '   冠军')
                logger.info(str(finalroundclients[FINALSTAGE[0]].ID) + '   亚军')
        resetInfo()
        result = battle(finalroundclients[FINALSTAGE[1]], finalroundclients[FINALSTAGE[3]], detail)
        if detail:
            # pass
            drawWinScreen(result)
            app.entryIDs[2].config({"background": 'white'})
            app.entryWins[2].config({"background": 'white'})
            app.entryIDs[3].config({"background": 'white'})
            app.entryWins[3].config({"background": 'white'})
            app.entryIDs[2].delete('0', END)
            app.entryWins[2].delete('0', END)
            app.entryIDs[3].delete('0', END)
            app.entryWins[3].delete('0', END)
            if result == REDWIN:
                app.entryIDs[2].insert(END, finalroundclients[FINALSTAGE[1]].ID)
                app.entryWins[2].insert(END, '季军')
                app.entryIDs[3].insert(END, finalroundclients[FINALSTAGE[3]].ID)
                app.entryWins[3].insert(END, '第四名')
                logger.info(str(finalroundclients[FINALSTAGE[1]].ID) + '   季军')
                logger.info(str(finalroundclients[FINALSTAGE[3]].ID) + '   第四名')
            if result == BLUEWIN:
                app.entryIDs[2].insert(END, finalroundclients[FINALSTAGE[3]].ID)
                app.entryWins[2].insert(END, '季军')
                app.entryIDs[3].insert(END, finalroundclients[FINALSTAGE[1]].ID)
                app.entryWins[3].insert(END, '第四名')
                logger.info(str(finalroundclients[FINALSTAGE[3]].ID) + '   季军')
                logger.info(str(finalroundclients[FINALSTAGE[1]].ID) + '   第四名')



        FUNCTION = 0

    if FUNCTION == 4:
        app.root.quit()
        for i in range(playernum):
            try:
                # logger.info('rank : '+str(i)+'  '+ clients[i].ID + ' wins '+str( clients[i].wins))
                clients[i].clientsock.sendall('close'.encode('utf8'))
                clients[i].clientsock.close()
            except socket.error as e:
                logger.info(str('ERRORS  ') + str(e))
        rank = clients.copy()
        if currentnum == playernum:
            for i in range(playernum - 1):
                for j in range(playernum - i - 1):
                    if (rank[j].wins < rank[j + 1].wins):
                        rank[j], rank[j + 1] = rank[j + 1], rank[j]
        for i in range(playernum):
            logger.info('rank : ' + str(i+1) + '  ' + rank[i].ID + ' wins ' + str(rank[i].wins))


if __name__ == '__main__':
    # 测试局数
    cnt = 1

    app = App()
    while True:
        result = startgame(port=50006, n=cnt, app=app)
        if FUNCTION == 4:
            #outputResult()
            # app.quit()
            sys.exit()

    sys.exit()


'''
项目规则介绍 
control面板上共1个文本框，5个按钮

文本框：负责输入对战人数，点击SETUP后设置完成，不可修改不可取消（改了也没用—）

SETUP：文本框输入对战人数后，进行设置playernum，仅能设置一次，点击后进入阻塞状态，如果指定数量服务器未全部连接
只能在命令行使用Ctrl-C退出，当全部连接后可以点击QUIT退出（比较简单的办法是先试试看QUIT不行直接命令行Ctrl+C）

JUDGE：对连接服务器的所有客户端测试3次，使用BetaCat1.0作为红方，用户作为蓝方，对战结果保存在
JUDGERESULT.csv文件中，可以用excel打开

BATTLE：对连接到服务器的所有客户端进行循环赛，每2客户端对战3局，结果界面反应总胜利局数

KNOCKEDOUT： 对Battle结果成绩取前8名（如果没有battle结果，取当前列表中前八名）进行淘汰赛  
    第一轮 0-4  1-5  2-6  3-7  分别对战3局
    第二轮 晋级[0,1,2,3]  0-2   1-3  分别对战3局
    第三轮 两局胜利者角逐冠亚军   两局失败者角逐季军和淘汰


QUIT：退出程序，当程序处于阻塞状态时，即主界面游戏正在运行或点击SETUP等待连接客户端时均无法退出，
退出后向全部客户端发送close命令并断开服务器连接




界面实现方法介绍
pygame棋盘界面为主线程， while(FUNCTION == 0) sleep(1) 的方式阻塞，因此在windows下运行时可能产生未响应的提示
无须惊慌
控制和结果界面使用tkinter 多线程python3 threading的方式实现，在其中修改FUNCTION 变量的时候需要加锁

FUNCTION 
    -1=需要setup设置用户
     0=悬空等待状态（阻塞）
     1=JUDGE 每个客户端检查3遍
     2=BATTLE 循环赛
     3=KNOCKEDOUT 淘汰赛
     4=非阻塞条件下退出

'''