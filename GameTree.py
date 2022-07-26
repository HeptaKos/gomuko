import requests
import time
import numpy as np
user="20_chy"
password="0x4b9f557d322a5e08fcc1160a2f9462273dd15d53fda92e8ade8785fb4401817dc808ad43828559c3751915d295e1c1cb71457c326e15a0c99bca13739a00894eff4db25c7f691cd3ce836ac5a5fb6d00ee8d6cd4ff72e8e5f90f9ea524d98e10c46000bac87dc67aab0993ad8cc712153f3d1e8602e802780d10adc0ab0b493f"
params={"user":user,"password":password,"data_type":"json"}
url_join = "http://202.207.12.156:9015/join_game"
res = str(requests.get(url_join, params).json()["game_id"])
url_play="http://202.207.12.156:9015/play_game/"+res
url_check="http://202.207.12.156:9015/check_game/"+res
'''
从这里开始都是getScore的子函数
'''
dx = [1,1,0,-1,-1,-1,0,1] #x,y方向向量
dy = [0,1,1,1,0,-1,-1,-1]
def inBoard(x,y):
    if(x>=0 and x<15 and y>=0 and y<15): return True
    else: return False
#判断该点是否可落子，即是否在棋盘内且没有落子
def downOk(x,y):
    if(inBoard(x,y) and N[x][y]=='.'): return True
    else: return False
#该点值是否和i值相等，即该点棋子颜色和i相同
def sameColor(x,y,i):
    if(inBoard(x,y) and N[x][y]==i): return True
    else: return False
#在给定的方向v(v区分正负)上，和该点同色棋子的个数
def numInline(x,y,v):
    i=x+dx[v]; j=y+dy[v]
    s=0; ref=N[x][y]
    if(ref=='.'): return 0
    while(sameColor(i,j,ref)):
        s=s+1; i=i+dx[v]; j=j+dy[v]
    return s
#该点四个方向里(即v不区分正负)，活四局势的个数
def liveFour(x,y):
    key=N[x][y]; s=0
    for u in range(4):
        samekey=1
        samekey,i=numofSamekey(x,y,u,1,key,samekey)
        if(not downOk(x+dx[u]*i,y+dy[u]*i)):
            continue
        samekey,i=numofSamekey(x,y,u,-1,key,samekey)
        if(not downOk(x+dx[u]*i,y+dy[u]*i)):
            continue
        if(samekey==4):
            s=s+1
    return s
#该点八个方向里(即v区分正负)，冲四局势的个数
def chongFour(x,y):
    key=N[x][y]; s=0
    for u in range(8):
        samekey=0; flag=True; i=1
        while(sameColor(x+dx[u]*i,y+dy[u]*i,key) or flag):
            if(not sameColor(x+dx[u]*i,y+dy[u]*i,key)):
                if(flag and inBoard(x+dx[u]*i,y+dy[u]*i) and N[x+dx[u]*i][y+dy[u]*i]!='.'):
                    samekey-=10
                flag=False
            samekey+=1
            i+=1
        i-=1
        if(not inBoard(x+dx[u]*i,y+dy[u]*i)):
            continue
        samekey,i=numofSamekey(x,y,u,-1,key,samekey)
        if(samekey==4):
            s+=1
    return s-liveFour(x,y)*2
#该点四个方向里活三，以及八个方向里断三的个数
def liveThree(x,y):
    key=N[x][y]; s=0
    for u in range(4):
        samekey=1
        samekey,i=numofSamekey(x,y,u,1,key,samekey)
        if(not downOk(x+dx[u]*i,y+dy[u]*i)):
            continue
        if(not downOk(x+dx[u]*(i+1),y+dy[u]*(i+1))):
            continue
        samekey,i=numofSamekey(x,y,u,-1,key,samekey)
        if(not downOk(x+dx[u]*i,y+dy[u]*i)):
            continue
        if(not downOk(x+dx[u]*(i-1),y+dy[u]*(i-1))):
            continue
        if(samekey==3):
            s+=1
    for u in range(8):
        samekey=0; flag=True; i=1
        while(sameColor(x+dx[u]*i,y+dy[u]*i,key) or flag):
            if(not sameColor(x+dx[u]*i,y+dy[u]*i,key)):
                if(flag and inBoard(x+dx[u]*i,y+dy[u]*i) and N[x+dx[u]*i][y+dy[u]*i]!='.'):
                    samekey-=10
                flag=False
            samekey+=1
            i+=1
        if(not downOk(x+dx[u]*i,y+dy[u]*i)):
            continue
        if(inBoard(x+dx[u]*(i-1),y+dy[u]*(i-1)) and N[x+dx[u]*(i-1)][y+dy[u]*(i-1)]=='.'):
            continue
        samekey,i=numofSamekey(x,y,u,-1,key,samekey)
        if(not downOk(x+dx[u]*i,y+dy[u]*i)):
            continue
        if(samekey==3):
            s+=1
    return s
#该点在四个方向里，是否有六子或以上连线
def overLine(x,y):
    flag=False
    for u in range(4):
        if((numInline(x,y,u)+numInline(x,y,u+4))>4):
            flag=True
    return flag

#统计在u方向上，和key值相同的点的个数，即和key同色的连子个数
def numofSamekey(x,y,u,i,key,sk):
    if(i==1):
        while(sameColor(x+dx[u]*i,y+dy[u]*i,key)):
            sk+=1
            i+=1
    elif(i==-1):
        while(sameColor(x+dx[u]*i,y+dy[u]*i,key)):
            sk+=1
            i-=1
    return sk,i
#游戏是否结束，如果有五子连线或出现禁手
def gameOver(x,y):
    global is_end
    for u in range(4):
        if((numInline(x,y,u)+numInline(x,y,u+4))>=4):
            is_end=True
            return True
    return False
'''
到这里结束了
'''
#对该点落子后的局势进行估分
def getScore(x,y):
    global is_end
    if(gameOver(x,y)):
        is_end=False
        return 10000
    score=liveFour(x,y)*1000+(chongFour(x,y)+liveThree(x,y))*100
    for u in range(8):
        if(inBoard(x+dx[u],y+dy[u]) and N[x+dx[u]][y+dy[u]]!='.'):
            score=score+1
    return score
def in_mp():
    global N,st
    N=[['.']*15 for i  in range(15)]
    st=0
#构建空棋盘


def fall(x,y):
    global st,H,B
    x=ord(x)-ord('a')
    y=ord(y)-ord('a')
    st=st+1
    if st % 2==1:
        N[x][y]=H
    else:
        N[x][y]=B
#根据字母坐标落子


def print_board():
    for i in range(0,15):
        for j in range(0,15):
            if N[i][j]=='M':
                print('o',end=' ')
            elif N[i][j]=='O':
                print('x',end=' ')
            else:
                print(N[i][j],end=' ')
        print()
#打印棋盘

def myturn_update():
    global H,B,st
    if len(step)%4==0:
        H='M'
        B='O'
    else:
        H='O'
        B='M'
    st=0
    for i in range(0,len(step)-1,2):
        fall(step[i],step[i+1])
#我回合的更新
def opponent_update():
    global H,B,st
    if len(step)%4==0:
        B='M'
        H='O'
    else:
        B='O'
        H='M'
    st=0
    for i in range(0,len(step)-1,2):
        fall(step[i],step[i+1])
#对手回合的更新
def putchess(x,y):
    X=chr(x+97)
    Y=chr(y+97)
    params={"user":user,"password":password,"coord":X+Y}
    print(requests.get(url_play,params).text)
#落子X，Y
def T1():
    global L1_max
    L1_max=-100000
    keyi=-1; keyj=-1
    for x in range(15):
        for y in range(15):
            if(N[x][y]!='.'):
                continue
            N[x][y]='M'
            tempp=getScore(x,y)
            if(tempp==0):
                N[x][y]='.'; continue
            if(tempp==10000):
                return putchess(x,y)
            tempp=AI2()
            N[x][y]='.'
            if(tempp>L1_max): #取极大
                L1_max=tempp; keyi=x; keyj=y
    putchess(keyi,keyj)
#博弈树第二层
def AI2():
    global L2_min
    L2_min=100000
    for x in range(15):
        for y in range(15):
            if(N[x][y]!='.'):
                continue
            N[x][y]='O'
            tempp=getScore(x,y)
            if(tempp==0):
                N[x][y]='.'; continue
            if(tempp==10000):
                N[x][y]='.'; return -10000
            tempp=AI3(tempp)
            if(tempp<L1_max): #L1层剪枝
                N[x][y]='.'; return -10000
            N[x][y]='.'
            if(tempp<L2_min): #取极小
                L2_min=tempp
    return L2_min
#博弈树第三层
def AI3(p2):
    keyp=-100000
    for x in range(15):
        for y in range(15):
            if(N[x][y]!='.'):
                continue
            N[x][y]='M'
            tempp=getScore(x,y)
            if(tempp==0):
                N[x][y]='.'; continue
            if(tempp==10000):
                N[x][y]='.'; return 10000
            if(tempp-p2*2>L2_min): #L2层剪枝
                N[x][y]='.'; return 10000
            N[x][y]='.'
            if(tempp-p2*2>keyp): #取极大
                keyp=tempp-p2*2
    return keyp

ans=''
in_mp()
step=""
st=0
wait_time=0
status=requests.get(url_check).json()
while status['ready'] == 'False':
    print('waiting for game:' , wait_time)
    wait_time+=1
    time.sleep(1)
    status = requests.get(url_check).json()

print("我执:",status['creator_stone'])

while status['win_step']=='':
    print("thinking")
    score_max=0
    X=0
    Y=0
    time.sleep(2)
    status=requests.get(url_check,{'data_type': 'json'}).json()
    print("keep thinging")
    if status['board'] == '' and user == status['current_turn']:
        putchess(7,7)
    if  step != status['board']:
        step=status['board']
        print(len(step))
        if user == status['current_turn']:
            myturn_update()
            print_board()
            print("该我落子")
            T1()
        else:
            opponent_update()
            print_board()
            print("对方的回合")

print(status['winner'])
