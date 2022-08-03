import json
import time
import requests
import urllib.request

# 定义公钥
Power = 65537
Modulus = 135261828916791946705313569652794581721330948863485438876915508683244111694485850733278569559191167660149469895899348939039437830613284874764820878002628686548956779897196112828969255650312573935871059275664474562666268163936821302832645284397530568872432109324825205567091066297960733513602409443790146687029
dx = [1, 1, 0, -1, -1, -1, 0, 1]  # x,y方向向量
dy = [0, 1, 1, 1, 0, -1, -1, -1]
L1_max = -100000  # 剪枝阈值
L2_min = 100000
board = []  # 棋盘


# 快速幂，用于模幂
def fast_modulus(x):
    base = x[0]
    power = x[1]
    modulus = x[2]
    result = 1  # result = base^power%modulus
    while power > 0:
        if power & 1:
            result = result * base % modulus
        power >>= 1
        base = base * base % modulus
    return result


# 将密码（256进制）转为数字
def str_to_num(a_string):
    result = 0
    length = len(a_string)
    for i in range(0, length):
        result += ord(a_string[i]) * 256 ** (length - i - 1)
    return result


def join_game():
    r = urllib.request.Request(f'http://202.207.12.156:9016/join_game?user={user}&password={password}&data_type=json')
    r_data = urllib.request.urlopen(r)
    res = r_data.read()
    message = json.loads(res)
    id = message['game_id']
    return id


def play_game(coord):
    requests.get(f'http://202.207.12.156:9016/play_game/{game_id}?user={user}&password={password}&coord={coord}')
    print("我方落棋位置：" + coord)


def check_game():
    r = urllib.request.Request(f'http://202.207.12.156:9016/check_game/{game_id}')
    r_data = urllib.request.urlopen(r)
    res = r_data.read()
    string = json.loads(res)
    return string


# 初始定义棋盘
def init():
    for i in range(15):
        board.append([])
        for j in range(15):
            board[i].append(".")


def down(information):
    y = ord(information['last_step'][1]) - 97
    x = ord(information['last_step'][0]) - 97
    print("对方落子位置:", information['last_step'])
    if information['current_stone'] == 'x':
        board[x][y] = 'o'
    else:
        board[x][y] = 'x'


# 判断该点是否在棋盘范围内
def inBoard(x, y):
    if 0 <= x <= 14 and 0 <= y <= 14:
        return True
    else:
        return False


# 判断该点是否可落子，即是否在棋盘内且没有落子
def downOk(x, y):
    if (inBoard(x, y) and board[x][y] == '.'):
        return True
    else:
        return False


# 该点值是否和i值相等，即该点棋子颜色和i相同
def sameColor(x, y, i):
    if (inBoard(x, y) and board[x][y] == i):
        return True
    else:
        return False


# 在给定的方向v(v区分正负)上，和该点同色棋子的个数
def numInline(x, y, v):
    i = x + dx[v]
    j = y + dy[v]
    s = 0
    ref = board[x][y]
    if (ref == '.'):
        return 0
    while (sameColor(i, j, ref)):
        s = s + 1
        i = i + dx[v]
        j = j + dy[v]
    return s


# 判断是否对方比自己先有活四
def judgeLiveFour():
    pass


# 游戏是否有五子连线
def gameOver(x, y):
    for u in range(4):
        if ((numInline(x, y, u) + numInline(x, y, u + 4)) >= 4):
            return True
    return False


# 统计在u方向上，和key值相同的点的个数，即和key同色的连子个数
def numofSamekey(x, y, u, i, key, sk):
    if (i == 1):
        while (sameColor(x + dx[u] * i, y + dy[u] * i, key) and
               x + dx[u] * i < 15 and y + dy[u] * i < 15 and
               x + dx[u] * i >= 0 and y + dy[u] * i >= 0):
            sk += 1
            i += 1
    elif (i == -1):
        while (sameColor(x + dx[u] * i, y + dy[u] * i, key) and
               x + dx[u] * i < 15 and y + dy[u] * i < 15 and
               x + dx[u] * i >= 0 and y + dy[u] * i >= 0):
            sk += 1
            i -= 1
    return sk, i


# 该点四个方向里(即v不区分正负)，活四局势的个数
def liveFour(x, y):
    key = board[x][y]
    s = 0
    for u in range(4):
        samekey = 1
        samekey, i = numofSamekey(x, y, u, 1, key, samekey)
        if (not downOk(x + dx[u] * i, y + dy[u] * i)):
            continue
        samekey, i = numofSamekey(x, y, u, -1, key, samekey)
        if (not downOk(x + dx[u] * i, y + dy[u] * i)):
            continue
        if (samekey == 4):
            s = s + 1
    return s


def chengFive(x, y):
    """成五子的数量"""
    key = board[x][y]
    s = 0
    for u in range(8):
        samekey = 0
        flag = True
        i = 1
        while sameColor(x + dx[u] * i, y + dy[u] * i, key) or flag:
            if not sameColor(x + dx[u] * i, y + dy[u] * i, key):
                if flag and inBoard(x + dx[u] * i, y + dy[u] * i) and board[x + dx[u] * i][y + dy[u] * i] != '.':
                    samekey -= 10
                flag = False
            samekey += 1
            i += 1
        i -= 1
        if not inBoard(x + dx[u] * i, y + dy[u] * i):
            continue
        samekey, i = numofSamekey(x, y, u, -1, key, samekey)
        if samekey == 4:
            s += 1
    return s


def chongFour(x, y):
    """该点八个方向里(即v区分正负)，冲四局势的个数"""
    return chengFive(x, y) - liveFour(x, y) * 2


# 该点四个方向里活三，以及八个方向里断三的个数
def liveThree(x, y):
    key = board[x][y]
    s = 0
    # .MMM.
    for u in range(4):
        samekey = 1
        samekey, i = numofSamekey(x, y, u, 1, key, samekey)
        if (not downOk(x + dx[u] * i, y + dy[u] * i)):
            continue
        if (not downOk(x + dx[u] * (i + 1), y + dy[u] * (i + 1))):
            continue
        samekey, i = numofSamekey(x, y, u, -1, key, samekey)
        if (not downOk(x + dx[u] * i, y + dy[u] * i)):
            continue
        if (not downOk(x + dx[u] * (i - 1), y + dy[u] * (i - 1))):
            continue
        if (samekey == 3):
            s += 1

    for u in range(8):
        samekey = 0
        flag = True
        i = 1
        while (sameColor(x + dx[u] * i, y + dy[u] * i, key) or flag):
            if (not sameColor(x + dx[u] * i, y + dy[u] * i, key)):
                if (flag and inBoard(x + dx[u] * i, y + dy[u] * i) and board[x + dx[u] * i][y + dy[u] * i] != '.'):
                    samekey -= 10
                flag = False
            samekey += 1
            i += 1
        if (not downOk(x + dx[u] * i, y + dy[u] * i)):
            continue
        if (inBoard(x + dx[u] * (i - 1), y + dy[u] * (i - 1)) and board[x + dx[u] * (i - 1)][
            y + dy[u] * (i - 1)] == '.'):
            continue
        samekey, i = numofSamekey(x, y, u, -1, key, samekey)
        if (not downOk(x + dx[u] * i, y + dy[u] * i)):
            continue
        if (samekey == 3):
            s += 1
    return s


def get_around(x, y):
    key = board[x][y]
    around = ['', '', '', '']  # 存放棋子周围四条线的信息,—— \ | /
    for i in range(0, 9):
        # 横线 ——
        if (y - 4 + i) in range(0, 15):
            if board[x][y - 4 + i] == key:
                around[0] += 'a'  # 我方棋子
            elif board[x][y - 4 + i] != key and board[x][y - 4 + i] != '.':
                around[0] += 'b'  # 对方棋子
            else:
                around[0] += '_'  # 空位置
        else:
            around[0] += ' '  # 越界
        # 竖线 |
        if (x - 4 + i) in range(0, 15):
            if board[x - 4 + i][y] == key:
                around[2] += 'a'
            elif board[x - 4 + i][y] != key and board[x - 4 + i][y] != '.':
                around[2] += 'b'
            else:
                around[2] += '_'
        else:
            around[2] += ' '
        # 向右斜线 \
        if ((x - 4 + i) in range(0, 15)) and ((y - 4 + i) in range(0, 15)):
            if board[x - 4 + i][y - 4 + i] == key:
                around[1] += 'a'
            elif board[x - 4 + i][y - 4 + i] != key and board[x - 4 + i][y - 4 + i] != '.':
                around[1] += 'b'
            else:
                around[1] += '_'
        else:
            around[1] += ' '
        # 向左斜线 /
        if ((x - 4 + i) in range(0, 15)) and ((y + 4 - i) in range(0, 15)):
            if board[x - 4 + i][y + 4 - i] == key:
                around[3] += 'a'
            elif board[x - 4 + i][y + 4 - i] != key and board[x - 4 + i][y + 4 - i] != '.':
                around[3] += 'b'
            else:
                around[3] += '_'
        else:
            around[3] += ' '
    return around


Rule_sleep3 = ["baaa__", "__aaab", "baa_a_", "_a_aab", "ba_aa_", "_aa_ab", "b_aaa_b", "a__aa","aa__a", "a_a_a"]


Rule_sleep2 = ["baa___", "___aab", "ba_a__","__a_ab", "ba__a_","_a__ab", "a___a", "ba___ab", "b_a__ab",
               "ba__a_b", "b__a_ab", "ba_a__b", "b__a_ab", "b__aa_b", "b_aa__b", "b_a_a_b"]


Rule_live2 = ["__aa__", "_a_a_", "_a__a_"]


def SleepThree(x, y):
    """该点四个方向里(即v不区分正负)，眠三局势的个数"""
    s = 0
    around_message = get_around(x, y)
    for mode in Rule_sleep3:
        for i in range(4):
            if mode in around_message[i]:
                s += 1
    return s


def SleepTwo(x, y):
    """该点四个方向里(即v不区分正负)，眠二局势的个数"""
    s = 0
    around_message = get_around(x, y)
    for mode in Rule_sleep2:
        for i in range(4):
            if mode in around_message[i]:
                s += 1
    return s


def liveTwo(x, y):
    """该点四个方向里(即v不区分正负)，活二局势的个数"""
    s = 0
    around_message = get_around(x, y)
    for mode in Rule_live2:
        for i in range(4):
            if mode in around_message[i]:
                s += 1
    return s


# 该点在四个方向里，是否有六子或以上连线
def overLine(x, y):
    flag = False
    for u in range(4):
        if ((numInline(x, y, u) + numInline(x, y, u + 4)) > 4):
            flag = True
    return flag


# 对该点落子后的局势进行估分
def getScore(x, y):
    if gameOver(x, y):
        return 10000
    score = overLine(x, y) * 10000 + liveFour(x, y) * 5000 + chongFour(x, y) * 1500 + liveThree(x,
                                                                                                y) * 1000 + SleepThree(
        x, y) * 500 + liveTwo(x, y) * 100 + SleepTwo(x, y) * 20
    for u in range(8):
        if inBoard(x + dx[u], y + dy[u]) and board[x + dx[u]][y + dy[u]] != '.':
            score = score + 1
    return score


# 落子
def go(x, y):
    play_game(chr(x + 97) + chr(y + 97))
    board[x][y] = information['current_stone']
    board[x][y] = information['current_stone']
    score1 = gameOver(x, y)
    score2 = liveFour(x, y)
    score3 = chongFour(x, y)
    score4 = liveThree(x, y)
    score5 = SleepThree(x, y)
    score6 = liveTwo(x, y)
    score7 = SleepTwo(x, y)
    print(f"连五{score1}  活四{score2}  冲四{score3}  活三{score4}  眠三{score5}  活二{score6}  眠二{score7}")


# 博弈树第一层
def AI1():
    global L1_max
    L1_max = -100000
    if (board[7][7] == '.' and information['board'] == ""):
        return go(7, 7)
    # 黑棋开盘
    elif information['step'] == '2':
        xx = ord(information['last_step'][0]) - 97
        yy = ord(information['last_step'][1]) - 97
        print(board[xx][yy])
        print(check45(yy, xx))
        print(check90(yy, xx))
        if "xo" in check45(yy, xx):
            return go(xx, yy + 2)
        if "ox" in check90(yy, xx):
            return go(xx + 1, yy)
    # 白棋挡
    elif information['step'] == '1':
        xx = ord(information['last_step'][0]) - 97
        yy = ord(information['last_step'][1]) - 97
        return go(xx + 1, yy - 1)
    elif information['step'] == '3':
        xx = ord(information['last_step'][0]) - 97
        yy = ord(information['last_step'][1]) - 97
        if "xx" in check135(yy, xx):
            return go(xx - 2, yy - 2)

    keyi = -1
    keyj = -1
    for x in [7, 6, 8, 5, 9, 4, 10, 3, 11, 2, 12, 1, 13, 0, 14]:
        for y in [7, 6, 8, 5, 9, 4, 10, 3, 11, 2, 12, 1, 13, 0, 14]:
            if (not downOk(x, y)):
                continue
            if information['current_stone'] == 'x':
                board[x][y] = 'x'
            else:
                board[x][y] = 'o'
            tempp = getScore(x, y)
            if (tempp == 0):
                board[x][y] = '.'
                continue
            if (tempp == 10000):
                return go(x, y)
            tempp = AI2()
            board[x][y] = '.'
            if (tempp > L1_max):  # 取极大
                L1_max = tempp
                keyi = x
                keyj = y
    go(keyi, keyj)


# 博弈树第二层
def AI2():
    global L2_min
    L2_min = 100000
    for x in [7, 6, 8, 5, 9, 4, 10, 3, 11, 2, 12, 1, 13, 0, 14]:
        for y in [7, 6, 8, 5, 9, 4, 10, 3, 11, 2, 12, 1, 13, 0, 14]:
            if (not downOk(x, y)):
                continue
            if information['current_stone'] == 'x':
                board[x][y] = 'o'
            else:
                board[x][y] = 'x'
            tempp = getScore(x, y)
            if (tempp == 0):
                board[x][y] = '.'
                continue
            if (tempp == 10000):
                board[x][y] = '.'
                return -10000
            tempp = AI3(tempp)
            if (tempp < L1_max):  # L1层剪枝
                board[x][y] = '.'
                return -10000
            board[x][y] = '.'
            if (tempp < L2_min):  # 取极小
                L2_min = tempp
    return L2_min


# 博弈树第三层
def AI3(p2):
    keyp = -100000
    for x in [7, 6, 8, 5, 9, 4, 10, 3, 11, 2, 12, 1, 13, 0, 14]:
        for y in [7, 6, 8, 5, 9, 4, 10, 3, 11, 2, 12, 1, 13, 0, 14]:
            if (not downOk(x, y)):
                continue
            if information['current_stone'] == 'x':
                board[x][y] = 'x'
            else:
                board[x][y] = 'o'
            tempp = getScore(x, y)
            if (tempp == 0):
                board[x][y] = '.'
                continue
            if (tempp == 10000):
                board[x][y] = '.'
                return 10000
            if (tempp - p2 * 2 > L2_min):  # L2层剪枝
                board[x][y] = '.'
                return 10000
            board[x][y] = '.'
            if (tempp - p2 * 2 > keyp):  # 取极大
                keyp = tempp - p2 * 2
    return keyp


# 横向判断 0°
def check0(y, x):
    list0 = []
    for k in range(-4, 5):
        if 0 <= k + x < 15:
            list0.append(board[k + x][y])
    str0 = "".join(list0)
    return str0


# 纵向判断 90°
def check90(y, x):
    list90 = []
    for k in range(-4, 5):
        if 0 <= k + y < 15:
            list90.append(board[x][y + k])
    str90 = "".join(list90)
    return str90


# 45°判断
def check45(y, x):
    list45 = []
    for k in range(-4, 5):
        if 0 <= k + x < 15 and 0 <= y - k < 15:
            list45.append(board[k + x][y - k])
    str45 = "".join(list45)
    return str45


# 135°判断
def check135(y, x):
    list135 = []
    for k in range(-4, 5):
        if 0 <= x + k < 15 and 0 <= y + k < 15:
            list135.append(board[x + k][y + k])
    str135 = "".join(list135)
    return str135


user = ''
Base = str_to_num('')  # 密码
temp = fast_modulus([Base, Power, Modulus])
password = str(hex(temp))  # 加密后的密码
game_id = join_game()
init()
while 1:
    information = check_game()
    print(information)
    if information['winner'] != 'None':
        print(information['winner'] + "获胜！")
        break
    else:
        if information['ready'] == "True":
            if information['current_turn'] != user:
                print("当前为对方落子，请您等待")
            else:
                if information['board'] != "":
                    down(information)
                AI1()
        time.sleep(5)
