import time
import urllib
import urllib.request
import urllib.response
import json


type = {"CMMMM": 10000, "MCMMM": 10000, "MMCMM": 10000, "MMMCM": 10000, "MMMMC": 10000,"OOOOC": 6000, "COOOO": 6000, "OOCOO": 6000, ".CMMM.": 5000, ".MCMM.": 5000, ".MMCM.": 5000, ".MMMC.": 5000
        ,"COOO.": 2500, ".OOOC": 2500, ".OOCO.": 2500, ".OCOO.": 2500,
        "OCMMM.": 2000, "OMCMM.": 2000, "OMMCM.": 2000, "OMMMC.": 2000, ".CMMMO": 2000, ".MCMMO": 2000,
        ".MMCMO": 2000, ".MMMCO": 2000,"COOO..":2100 , "..OOOC":2100 ,".COOO.":2100 , ".OOOC.":2100 ,
        ".MMC.": 400, ".MCM.": 400, ".CMM.": 400,".OOC": 400, "COO.": 400, "MOOOC": 400, "COOOM": 400,
        ".MMCO": 200, ".MCMO": 200, ".CMMO": 200, "OMMC.": 200, "OMCM.": 200, "OCMM.": 200, "MOOC": 200,
        "COOM": 200,".MC.": 50, ".CM.": 50
        }

def score(mytype):
    sum1 = 0
    for item, value in type.items():
        if item in mytype:
            sum1 = sum1 + value
    return int(sum1)



def join_game():
    req = urllib.request.Request(f'http://202.207.12.156:9015/join_game?user={user}&password={password}&data_type=json')
    res_data = urllib.request.urlopen(req)
    res = res_data.read()
    id = json.loads(res)['game_id']
    return id


def check_game():
    req = urllib.request.Request(f'http://202.207.12.156:9015/check_game/{game_id}')
    res_data = urllib.request.urlopen(req)
    res = res_data.read()
    str1 = json.loads(res)
    return str1


def play_game(coord):

    req = urllib.request.urlopen(
        f'http://202.207.12.156:9015/play_game/{game_id}?user={user}&password={password}&coord={coord}')



def draw_board():
    for i in range(15):
        board.append([])
        for j in range(15):
            board[i].append(".")


def game_transform(mes):
    if mes['current_stone'] == "x":
        for i in range(0, len(mes['board']), 2):
            a = ord(mes['board'][i]) - 97
            b = ord(mes['board'][i + 1]) - 97
            if board[a][b] == "x":
                board[a][b] = "M"
            elif board[a][b] == "o":
                board[a][b] = "O"
    else:
        for i in range(0, len(mes['board']), 2):
            a = ord(mes['board'][i]) - 97
            b = ord(mes['board'][i + 1]) - 97
            if board[a][b] == "x":
                board[a][b] = "O"
            elif board[a][b] == "o":
                board[a][b] = "M"


def judge(a, b):
    a = a
    b = b
    str1 = []
    sum=0
    for j in range(-4, 5):
        if 0 <= b + j <= 14:
           str1.append(board[a][b + j])
        else:
            continue
    str1 = "".join(str1)
    sum = sum + score(str1)
    str2 = []
    for j in range(-4, 5):
        if 0 <= a + j <= 14:
            str2.append(board[a + j][b])
        else:
            continue
    str2 = "".join(str2)
    sum = sum + score(str2)
    str3 = []
    for j in range(-4, 5):
        if 0 <= a + j <= 14 and 0 <= b + j <= 14:
            str3.append(board[a + j][b + j])
        else:
            continue
    str3 = "".join(str3)
    sum = sum + score(str3)
    str4 = []
    for j in range(-4, 5):
        if 0 <= a - j <= 14 and 0 <= b + j <= 14:
            str4.append(board[a - j][b + j])
        else:
            continue
    str4 = "".join(str4)
    sum = sum + score(str4)
    return sum


def playing(mes):
    num1 = ord(mes['last_step'][0]) - 97
    num2 = ord(mes['last_step'][1]) - 97
    if mes['current_stone'] == "x":
        board[num1][num2] = "o"
    else:
        board[num1][num2] = "x"

def play(message):
    if message['current_turn'] != user:
        print("Waiting for the opponent...")
        return
    else:
        print("Let me think twice...")
        if message['board'] == '':
            play_game("hh")
            board[7][7] = message['current_stone']
        else:
            playing(message)
            game_transform(message)
            sum_max = 0
            site1 = 0
            site2 = 0
            for num1 in range(15):
                for num2 in range(15):
                    max1 = 0
                    if board[num1][num2] == ".":
                        board[num1][num2] = "C"
                        max1 = max1 + judge(num1, num2)
                        board[num1][num2] = "."
                    if sum_max < max1:
                        sum_max = max1
                        site1 = num1
                        site2 = num2
            str1 = chr(site1 + 97) + chr(site2 + 97)
            play_game(str1)
            board[site1][site2] = message['current_stone']




user = "qiyixian"
password = "0x8886fc42c8708611cfefa172d25a8c436f201c7d175f97b08afad585f315a2e28f381f20eaf98189c7468fd93f51ba112c7fbe19308bcc9d6295615c0bd86739568289cbe355153e986e22911f6fb2fa01c6de067563d48a8251ec495e8f0dd835d2f02419aed2e7e3635cf28e9a2d337930f2f87fd7d41742b1a2ed7f16c052"
game_id = join_game()
board = []
draw_board()

while 1:
    mess = check_game()
    print(mess)
    if mess['winner'] != "None":
        print("winner:" + mess['winner'])
        break
    else:
        if mess['ready'] == "False":
            continue
        else:
            play(mess)
    time.sleep(6)
