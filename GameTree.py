import time
import requests as re

###
num = [[0 for a in range(15)] for a in range(15)]  # 棋盘
board = []  # 直观棋盘
dx = [1, 1, 0, -1, -1, -1, 0, 1]  # x,y方向向量
dy = [0, 1, 1, 1, 0, -1, -1, -1]
is_end = False
go_first = 1  # 先手标志
start = 1  # 轮换下棋标志
ai = 1  # AI下棋标志
L1_max = -100000  # 剪枝阈值
L2_min = 100000


# 数据初始化，把棋盘上的棋子和提示清空
def init():
    global is_end, start, go_first
    is_end = False
    start = 1
    go_first = 1
    # 初始化num[][]
    for i in range(15):
        for j in range(15):
            if num[i][j] != 0:
                num[i][j] = 0
    # 初始化board[][]
    for i in range(0, 15):
        board.append([])
        for j in range(0, 15):
            board[i].append('.')


# 判断该点是否在棋盘范围内
def inBoard(x, y):
    if 0 <= x <= 14 and 0 <= y <= 14:
        return True
    else:
        return False


# 判断该点是否可落子，即是否在棋盘内且没有落子
def downOk(x, y):
    if inBoard(x, y) and num[x][y] == 0:
        return True
    else:
        return False


def sameColor(x, y, i):
    """该点值是否和i值相等，即该点棋子颜色和i相同"""
    if inBoard(x, y) and num[x][y] == i:
        return True
    else:
        return False


# 在给定的方向v(v区分正负)上，和该点同色棋子的个数
def numInline(x, y, v):
    i = x + dx[v]
    j = y + dy[v]
    s = 0
    ref = num[x][y]
    if ref == 0:
        return 0
    while sameColor(i, j, ref):
        s = s + 1
        i = i + dx[v]
        j = j + dy[v]
    return s


# 该点四个方向里(即v不区分正负)，活四局势的个数
def liveFour(x, y):
    key = num[x][y]
    s = 0
    for u in range(4):
        samekey = 1
        samekey, i = numofSamekey(x, y, u, 1, key, samekey)
        if not downOk(x + dx[u] * i, y + dy[u] * i):
            continue
        samekey, i = numofSamekey(x, y, u, -1, key, samekey)
        if not downOk(x + dx[u] * i, y + dy[u] * i):
            continue
        if samekey == 4:
            s = s + 1
    return s


def chengFive(x, y):
    """成五子的数量"""
    key = num[x][y]
    s = 0
    for u in range(8):
        samekey = 0
        flag = True
        i = 1
        while sameColor(x + dx[u] * i, y + dy[u] * i, key) or flag:
            if not sameColor(x + dx[u] * i, y + dy[u] * i, key):
                if flag and inBoard(x + dx[u] * i, y + dy[u] * i) and num[x + dx[u] * i][y + dy[u] * i] != 0:
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
    key = num[x][y]
    s = 0
    for u in range(4):
        samekey = 1
        samekey, i = numofSamekey(x, y, u, 1, key, samekey)
        if not downOk(x + dx[u] * i, y + dy[u] * i):
            continue
        if not downOk(x + dx[u] * (i + 1), y + dy[u] * (i + 1)):
            continue
        samekey, i = numofSamekey(x, y, u, -1, key, samekey)
        if not downOk(x + dx[u] * i, y + dy[u] * i):
            continue
        if not downOk(x + dx[u] * (i - 1), y + dy[u] * (i - 1)):
            continue
        if samekey == 3:
            s += 1
    for u in range(8):
        samekey = 0
        flag = True
        i = 1
        while sameColor(x + dx[u] * i, y + dy[u] * i, key) or flag:
            if not sameColor(x + dx[u] * i, y + dy[u] * i, key):
                if flag and inBoard(x + dx[u] * i, y + dy[u] * i) and num[x + dx[u] * i][y + dy[u] * i] != 0:
                    samekey -= 10
                flag = False
            samekey += 1
            i += 1
        if not downOk(x + dx[u] * i, y + dy[u] * i):
            continue
        if inBoard(x + dx[u] * (i - 1), y + dy[u] * (i - 1)) and num[x + dx[u] * (i - 1)][y + dy[u] * (i - 1)] == 0:
            continue
        samekey, i = numofSamekey(x, y, u, -1, key, samekey)
        if not downOk(x + dx[u] * i, y + dy[u] * i):
            continue
        if samekey == 3:
            s += 1
    return s


# 该点四个方向里(即v不区分正负)，活二局势的个数
def liveTwo(x, y):
    key = num[x][y];
    s = 0
    for u in range(4):
        samekey = 1
        samekey, i = numofSamekey(x, y, u, 1, key, samekey)
        if not downOk(x + dx[u] * i, y + dy[u] * i):
            continue
        samekey, i = numofSamekey(x, y, u, -1, key, samekey)
        if not downOk(x + dx[u] * i, y + dy[u] * i):
            continue
        if samekey == 2:
            s = s + 1
    return s


# 该点四个方向里(即v不区分正负)，眠二局势的个数
def SleepTwo(x, y):
    key = num[x][y]
    s = 0
    for u in range(4):
        sign = 0
        samekey = 1
        samekey, i = numofSamekey(x, y, u, 1, key, samekey)
        if not downOk(x + dx[u] * i, y + dy[u] * i):
            sign += 1
        samekey, i = numofSamekey(x, y, u, -1, key, samekey)
        if not downOk(x + dx[u] * i, y + dy[u] * i):
            sign += 1
        if samekey == 2 and sign == 1:
            s = s + 1
    return s


# 该点四个方向里(即v不区分正负)，眠三局势的个数
def SleepThree(x, y):
    key = num[x][y]
    s = 0
    for u in range(4):
        sign = 0
        samekey = 1
        samekey, i = numofSamekey(x, y, u, 1, key, samekey)
        if not downOk(x + dx[u] * i, y + dy[u] * i):
            sign += 1
        samekey, i = numofSamekey(x, y, u, -1, key, samekey)
        if not downOk(x + dx[u] * i, y + dy[u] * i):
            sign += 1
        if samekey == 3 and sign == 1:
            s = s + 1
    return s


# 该点在四个方向里，是否有六子或以上连线
def overLine(x, y):
    flag = False
    for u in range(4):
        if (numInline(x, y, u) + numInline(x, y, u + 4)) > 4:
            flag = True
    return flag


def numofSamekey(x, y, u, i, key, sk):
    """统计在u方向上，和key值相同的点的个数，即和key同色的连子个数"""
    if i == 1:
        while sameColor(x + dx[u] * i, y + dy[u] * i, key):
            sk += 1
            i += 1
    elif i == -1:
        while sameColor(x + dx[u] * i, y + dy[u] * i, key):
            sk += 1
            i -= 1
    return sk, i


# 游戏是否结束，如果有五子连线或出现禁手
def gameOver(x, y):
    global is_end
    for u in range(4):
        if (numInline(x, y, u) + numInline(x, y, u + 4)) >= 4:
            is_end = True
            return True
    return False


# 对该点落子后的局势进行估分
def getScore(x, y):
    global is_end
    if gameOver(x, y):
        is_end = False
        return 10000
    score = liveFour(x,y)*3000+(chongFour(x,y)+liveThree(x,y))*1800+SleepThree(x,y)*400+liveTwo(x,y)*300+SleepTwo(x,y)*200
    for u in range(8):
        if inBoard(x + dx[u], y + dy[u]) and num[x + dx[u]][y + dy[u]] != 0:
            score = score + 1
    return score


# 博弈树第一层
def AI1():
    global L1_max
    L1_max = -100000
    if num[7][7] == 0 and go_first == ai:
        return go(7, 7)
    keyi = -1
    keyj = -1
    for x in [7, 8, 9, 6, 10, 5, 11, 4, 12, 3, 13, 2, 14, 1, 0]:
        for y in [7, 8, 9, 6, 10, 5, 11, 4, 12, 3, 13, 2, 14, 1, 0]:
            if not downOk(x, y):
                continue
            num[x][y] = ai
            tempp = getScore(x, y)
            if tempp == 0:
                num[x][y] = 0
                continue
            if tempp == 10000:
                return go(x, y)
            tempp = AI2()
            num[x][y] = 0
            if tempp > L1_max:  # 取极大
                L1_max = tempp
                keyi = x
                keyj = y
    go(keyi, keyj)


# 博弈树第二层
def AI2():
    global L2_min
    L2_min = 100000
    for x in [7, 8, 9, 6, 10, 5, 11, 4, 12, 3, 13, 2, 14, 1, 0]:
        for y in [7, 8, 9, 6, 10, 5, 11, 4, 12, 3, 13, 2, 14, 1, 0]:
            if not downOk(x, y):
                continue
            num[x][y] = 3 - ai
            tempp = getScore(x, y)
            if tempp == 0:
                num[x][y] = 0
                continue
            if tempp == 10000:
                num[x][y] = 0
                return -10000
            tempp = AI3(tempp)
            if tempp < L1_max:  # L1层剪枝
                num[x][y] = 0
                return -10000
            num[x][y] = 0
            if tempp < L2_min:  # 取极小
                L2_min = tempp
    return L2_min


# 博弈树第三层
def AI3(p2):
    keyp = -100000
    for x in [7, 8, 9, 6, 10, 5, 11, 4, 12, 3, 13, 2, 14, 1, 0]:
        for y in [7, 8, 9, 6, 10, 5, 11, 4, 12, 3, 13, 2, 14, 1, 0]:
            if not downOk(x, y):
                continue
            num[x][y] = ai
            tempp = getScore(x, y)
            if tempp == 0:
                num[x][y] = 0
                continue
            if tempp == 10000:
                num[x][y] = 0
                return 10000
            if tempp - p2 * 2 > L2_min:  # L2层剪枝
                num[x][y] = 0
                return 10000
            num[x][y] = 0
            if tempp - p2 * 2 > keyp:  # 取极大
                keyp = tempp - p2 * 2
    return keyp


# 落下一子并且判断游戏是否结束
def go(x, y):
    global is_end
    if start == ai:
        num[x][y] = ai
        print(f"我方AI落子：{x},{y}")
        maxCoord = ''
        maxCoord += chr(x + 97) + chr(y + 97)
        play_game(maxCoord)
        if go_first == ai:
            board[x][y] = 'x'  # 我方先手执x棋子，对方相反
        else:
            board[x][y] = 'o'  # 我方后手执o棋子，对方相反
    else:
        num[x][y] = 3 - ai
        print(f"对方落子：{x},{y}")
        if go_first == ai:
            board[x][y] = 'o'
        else:
            board[x][y] = 'x'
    if gameOver(x, y):
        if start == ai:
            print("我方AI胜利")
        else:
            print("对方胜利")


# 展示棋盘
def show_board(aboard):
    for index_i in range(0, 15):
        for index_j in range(0, 15):
            print(aboard[index_i][index_j], end="")
        print()


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


# join_game
def join_game():
    data = {
        'user': username,
        'password': password,
        'data_type': 'json'
    }
    result = re.get("http://202.207.12.156:9015/join_game", params=data)
    return result


# check_game
def check_game():
    result = re.get(url_check_game)
    return result


# play_game
def play_game(coord):
    data = {
        'user': username,
        'password': password,
        'data_type': 'json',
        'coord': coord
    }
    result = re.get(url_play_game, params=data)
    print(result.text)
    return result


# 主程序入口
if __name__ == '__main__':
    # 设置用户名和密码
    username = 'xxx'
    Base = str_to_num('xxx')  # 密码
    Power = 65537
    Modulus = 135261828916791946705313569652794581721330948863485438876915508683244111694485850733278569559191167660149469895899348939039437830613284874764820878002628686548956779897196112828969255650312573935871059275664474562666268163936821302832645284397530568872432109324825205567091066297960733513602409443790146687029
    temp = fast_modulus([Base, Power, Modulus])
    password = str(hex(temp))  # 加密后的密码
    # 获取对战的房间号、网址
    game_id = join_game().json()["game_id"]
    url_play_game = "http://202.207.12.156:9015/play_game/" + str(game_id)
    url_check_game = "http://202.207.12.156:9015/check_game/" + str(game_id)

    init()  # 初始化
    # 等待对手
    state = check_game().json()
    print("等待对手中，等待状态", state['ready'], end=" ")
    while state['ready'] == "False":
        state = check_game().json()
        print("等待对手中，等待状态：", state['ready'], end=" ")
        time.sleep(5)
    # 对战初始时进行一些定义
    if state['current_turn'] == username:  # 第一步由我方AI开始
        print(f"第一步由我方AI下棋")
        opponent = state['opponent_name']
        start = 1
        go_first = 1
    else:  # 第一步由对方开始
        opponent = state['creator']
        print(f"第一步由对方{opponent}下棋")
        start = 2
        go_first = 2
    # 正式进入对战
    while state['ready'] == "True":
        if start == ai:
            print("我方AI正在下棋")
            AI1()
            print("我方AI下棋后的棋盘")
            show_board(board)
        else:
            print(f"对方 {opponent} 正在下棋")
            while True:
                if state['current_turn'] == username:
                    last_step = state['last_step']
                    position_x = ord(last_step[0]) - ord('a')
                    position_y = ord(last_step[1]) - ord('a')
                    go(position_x, position_y)
                    break
                else:
                    time.sleep(2)
                    state = check_game().json()
            print("对方下棋后的棋盘")
            show_board(board)
        start = 3 - start
        time.sleep(5)
        state = check_game().json()

        if state['winner'] != "None":
            print(f" {state['winner']}获胜")
            break
